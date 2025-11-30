"""
Parse Tasks Agent

JSON-only MVP:
- Takes a raw JSON string of tasks
- Asks Gemini to normalize it into the internal task schema:
    {
      "title": str,
      "importance": int (1–3),
      "urgency": int (1–3),
      "desire": int (1–3),
      "est_minutes": int
    }
- Returns a Python list[dict] of normalized tasks.
"""

import json
import os

from dotenv import load_dotenv
from google import genai

def log_debug(msg: str):
    print(f"==== {msg}")

MODEL_NAME = "gemini-2.5-flash-lite"


def call_parse_tasks_agent(raw_tasks_str: str):
    """
    Call the LLM-based parse/normalize agent on a raw JSON task string.

    Returns:
        list of task dicts in the internal schema.
    """
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    client = genai.Client()

    system_instruction = (
        "You are a Task List Normalizer.\n"
        "You receive a JSON-like representation of tasks.\n"
        "You MUST return ONLY a clean JSON array of task objects, each with:\n"
        "  - title (string)\n"
        "  - importance (integer 1-3)\n"
        "  - urgency (integer 1-3)\n"
        "  - desire (integer 1-3)\n"
        "  - est_minutes (integer, estimated minutes to complete)\n"
        "If any fields are missing, infer reasonable defaults.\n"
        "Respond ONLY with the JSON array, no extra text, no explanations,\n"
        "and do NOT wrap it in Markdown code fences.\n"
    )

    user_prompt = (
        "Here is the raw task input:\n\n"
        + raw_tasks_str
    )

    log_debug("[ParseTasksAgent → Model]")
    log_debug(user_prompt)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            {
                "role": "user",
                "parts": [{"text": system_instruction + "\n\n" + user_prompt}],
            }
        ],
    )

    raw_text = response.text.strip()
    log_debug("[ParseTasksAgent ← Raw Model Response]")
    log_debug(raw_text)

    # If the model still uses ``` fences, strip them
    if raw_text.startswith("```"):
        first_newline = raw_text.find("\n")
        if first_newline != -1:
            raw_text = raw_text[first_newline + 1 :]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3].strip()

    tasks = json.loads(raw_text)

    log_debug("[ParseTasksAgent → Parsed Tasks]")
    log_debug(json.dumps(tasks, indent=2))

    return tasks


def main():
    raw_tasks_str = """
    [
      {"title": "Email accountant", "importance": 3, "urgency": 3, "est_minutes": 20},
      {"title": "Take a break", "importance": 2, "urgency": 2},
      {"title": "Practice DSA", "desire": 3, "est_minutes": 30}
    ]
    """

    tasks = call_parse_tasks_agent(raw_tasks_str)
    log_debug("Final normalized tasks (Python list):")
    for t in tasks:
        log_debug(f"- {t}")

if __name__ == "__main__":
    main()