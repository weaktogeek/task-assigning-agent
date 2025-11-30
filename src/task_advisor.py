"""
Task Advisor Root Orchestrator

This module provides a single entrypoint:
    run_task_advisor(tasks=None, raw_tasks_str=None,
                      available_minutes=60, energy_level="medium")

Right now:
- tasks defaults to SAMPLE_TASKS
- raw_tasks_str is reserved for Phase 1 Step 3 (parse-tasks agent)

This file will become the root orchestrator for the ADK agent system.
"""

from dotenv import load_dotenv
import os

def log_debug(msg: str):
    print(f"==== {msg}")

try:
    # Script-style import (when running: python src/task_advisor.py)
    from main import SAMPLE_TASKS, score_tasks, choose_shortlist, assemble_plan_data
    from plan_explainer_agent import call_planning_agent, print_final_plan
    from parse_tasks_agent import call_parse_tasks_agent
except ImportError:
    # Package-style import (when imported as src.task_advisor)
    from src.main import SAMPLE_TASKS, score_tasks, choose_shortlist, assemble_plan_data
    from src.plan_explainer_agent import call_planning_agent, print_final_plan
    from src.parse_tasks_agent import call_parse_tasks_agent


def run_task_advisor(
    tasks=None,
    raw_tasks_str=None,
    available_minutes=60,
    energy_level="medium"
):
    """
    Root orchestrator for the Task Advisor (Python-level).
    This will later be replaced or wrapped by the ADK root agent.

    Parameters:
        tasks: list of task dicts (optional)
        raw_tasks_str: string containing raw task input (reserved for Step 3)
        available_minutes: int
        energy_level: str
    """

    # Phase 1-Step 4: 
    # If no tasks provided, use SAMPLE_TASKS. But if raw_tasks_str is provided, 
    # use the Parse Tasks Agent to normalize it.
    if tasks is None:
        if raw_tasks_str is not None:
            # Use the Parse Tasks Agent to normalize the raw input
            tasks = call_parse_tasks_agent(raw_tasks_str)
        else:
            # Fallback to built-in sample tasks
            tasks = SAMPLE_TASKS

    log_debug("Scoring tasks...")
    # ---- Step A: Score tasks (deterministic) ----
    scored = score_tasks(tasks)

    log_debug("Choosing shortlist...")
    # ---- Step B: Choose shortlist (deterministic, for now) ----
    shortlist = choose_shortlist(scored, available_minutes=available_minutes)

    log_debug("Assembling plan data...")
    # ---- Step C: Build plan_data ----
    plan_data = assemble_plan_data(
        all_tasks=scored,
        available_minutes=available_minutes,
        energy_level=energy_level,
        suggested_shortlist=shortlist,
    )

    log_debug("Calling planning agent...")
    # ---- Step D: Call the planning agent ----
    plan_json = call_planning_agent(plan_data)

    # ---- Step E: Pretty-print output ----
    log_debug("Final plan generated:")
    print_final_plan(plan_json)

    return plan_json


def main():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    log_debug(f"API Key Loaded: {bool(api_key)}")

    # Demo: use raw JSON string and let the ParseTasksAgent normalize it
    raw_tasks_str = """
    [
      {"title": "Email accountant", "importance": 3, "urgency": 3, "est_minutes": 20},
      {"title": "Take a break", "importance": 2, "urgency": 2},
      {"title": "Practice DSA", "desire": 3, "est_minutes": 30}
    ]
    """

    run_task_advisor(
        tasks=None,
        raw_tasks_str=raw_tasks_str,
        available_minutes=60,
        energy_level="medium",
    )


if __name__ == "__main__":
    main()