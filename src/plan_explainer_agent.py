"""
Plan Explainer Agent

 Uses the existing deterministic planning steps (score_tasks, choose_shortlist,
 assemble_plan_data) and then asks Gemini to refine and explain the resulting plan.

 In this implementation, the "planning agent" is a lightweight LLM-driven tool
 built with the google-genai client, rather than a full ADK Agent.
 The actual ADK Agent—the root orchestrator—lives in
 `agents/task_advisor_agent/agent.py` and invokes this module as one of its tools.
"""

import json
from pprint import pformat
import os

from dotenv import load_dotenv
from google import genai

# Import your existing logic
try:
    from main import (
        SAMPLE_TASKS,
        score_tasks,
        choose_shortlist,
        assemble_plan_data,
        log_debug,
        DEBUG,
    )
except ImportError:
    from src.main import (
        SAMPLE_TASKS,
        score_tasks,
        choose_shortlist,
        assemble_plan_data,
        log_debug,
        DEBUG,
    )

MODEL_NAME = "gemini-2.5-flash-lite"

PLAN_AGENT_INSTRUCTION = (
    "You are a Task Prioritization Advisor.\n"
    "You receive a JSON object describing:\n"
    "- all tasks with scores and attributes (all_tasks)\n"
    "- an optional suggested_shortlist chosen by a deterministic planner\n"
    "- the user's available time (available_minutes) and energy level\n\n"
    "Your job is to:\n"
    "1) Choose the actual shortlist of tasks yourself, based primarily on\n"
    "   all_tasks, available_minutes, and energy_level.\n"
    "2) You may use suggested_shortlist as a hint, but you are free to adjust\n"
    "   tasks and ordering if it would clearly improve the plan.\n"
    "3) Suggest 0–2 'nice to have' tasks if there is extra time or energy.\n\n"
    "Constraints:\n"
    "- The total estimated minutes of the shortlist should roughly fit within\n"
    "  available_minutes.\n"
    "- You MUST respond with a single valid JSON object only.\n"
    "- Do NOT include any text before or after the JSON.\n"
    "- Do NOT wrap the JSON in Markdown code fences (no ```json ... ```).\n"
    "- The JSON must have exactly these fields:\n"
    "  - 'shortlist': list of {title, reason, est_minutes, score}\n"
    "  - 'nice_to_have': list of {title, reason, est_minutes, score}\n"
    "  - 'summary': a short string explaining the overall plan.\n"
)

# Lazy-initialized global client so this works both when run directly
# and when imported as a tool from the root ADK agent.
_client: genai.Client | None = None


def get_client() -> genai.Client:
    """Return a cached google-genai client, loading the API key from .env."""
    global _client
    if _client is None:
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        log_debug(f"[plan_explainer_agent] API Key Loaded: {bool(api_key)}")
        if not api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY is not set. Please add it to your .env or environment."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def build_demo_plan_data() -> dict:
    """
    Reuse the deterministic pipeline to create plan_data
    that we can hand to the model when running this file directly.
    """
    scored = score_tasks(SAMPLE_TASKS)
    suggested_shortlist = choose_shortlist(scored, available_minutes=60)
    plan_data = assemble_plan_data(
        all_tasks=scored,
        available_minutes=60,
        energy_level="medium",
        suggested_shortlist=suggested_shortlist,
    )
    log_debug(
        "Plan data assembled in plan_explainer_agent:\n" + pformat(plan_data, indent=2)
    )
    return plan_data


def _strip_markdown_fences(raw_text: str) -> str:
    """
    Remove accidental ```json ... ``` or ``` ... ``` fences around the JSON.
    The instructions explicitly tell the model not to use fences, but
    this is a safety net.
    """
    text = raw_text.strip()
    if text.startswith("```"):
        # Drop the first line (``` or ```json)
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1 :]
        # Drop trailing ```
        if text.strip().endswith("```"):
            text = text.rsplit("```", 1)[0]
    return text.strip()


def call_planning_agent(plan_data: dict) -> dict:
    """
    Send plan_data to the planning LLM (Gemini) and return the parsed JSON result.

    This function is designed to be used both:
    - from the root ADK agent (as a tool), and
    - from this module's main() for direct testing.
    """
    # Build the user prompt. The system-like behavior is encoded in
    # PLAN_AGENT_INSTRUCTION for simplicity.
    user_prompt = (
        PLAN_AGENT_INSTRUCTION
        + "\n\nHere is the current plan data as JSON.\n"
        + "Use it to construct your JSON response as described in the instructions.\n\n"
        + "PLAN_DATA_JSON:\n"
        + json.dumps(plan_data, indent=2)
    )

    log_debug("[User → Model]")
    log_debug(user_prompt)

    client = get_client()
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=user_prompt,
    )

    raw_text = (response.text or "").strip()
    log_debug("[Model Explanation]")
    log_debug(raw_text)

    cleaned = _strip_markdown_fences(raw_text)

    # Try to parse the JSON. If it fails, log and re-raise for visibility.
    try:
        plan_json = json.loads(cleaned)
    except json.JSONDecodeError as e:
        log_debug("ERROR: Failed to parse JSON from model response.")
        log_debug(f"Raw cleaned text was:\n{cleaned}")
        raise e

    log_debug("[Parsed JSON Plan]")
    log_debug(json.dumps(plan_json, indent=2))
    return plan_json


def print_final_plan(plan_json: dict) -> None:
    """Pretty-print the final plan for CLI usage and debugging."""
    print("\nShortlist tasks chosen by the agent:")
    for t in plan_json.get("shortlist", []):
        print(
            f"- {t.get('title')} "
            f"(est={t.get('est_minutes')} min, score={t.get('score')})"
        )

    print("\n\n=== Final Task Plan ===")

    # Shortlist section
    print("\nShortlist (focus tasks):")
    for t in plan_json.get("shortlist", []):
        title = t.get("title")
        est = t.get("est_minutes")
        score = t.get("score")
        reason = t.get("reason")
        print(f"- {title} [{est} min, score={score}]")
        print(f"  Reason: {reason}")

    # Nice-to-have section
    nice_to_have = plan_json.get("nice_to_have", [])
    if nice_to_have:
        print("\nNice-to-have tasks (optional):")
        for t in nice_to_have:
            title = t.get("title")
            est = t.get("est_minutes")
            score = t.get("score")
            reason = t.get("reason")
            print(f"- {title} [{est} min, score={score}]")
            print(f"  Reason: {reason}")
    else:
        print("\nNo nice-to-have tasks suggested for this session.")

    # Summary
    summary = plan_json.get("summary")
    if summary:
        print("\nSummary:")
        print(summary)


def main():
    """
    Small CLI harness so you can run:

        python -m src.plan_explainer_agent

    or

        python src/plan_explainer_agent.py

    to see a demo explanation using SAMPLE_TASKS.
    """
    # Build deterministic plan_data from SAMPLE_TASKS
    plan_data = build_demo_plan_data()

    # Call the LLM-powered planning tool
    plan_json = call_planning_agent(plan_data)

    # Pretty-print the result
    print_final_plan(plan_json)


if __name__ == "__main__":
    main()
