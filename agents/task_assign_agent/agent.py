"""
ADK root agent for the Task Advisor.

This agent exposes a single tool that runs the full Python pipeline:
- Parse tasks (via ParseTasksAgent)
- Score and shortlist deterministically
- Let the Planning Agent decide the final shortlist and nice-to-have tasks
- Return the final plan JSON
"""

import os
import sys

# Ensure the project root is on sys.path so that `src` can be imported
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
    
from google.adk.agents import Agent

from typing import Dict, Any


# Import your existing Python-level orchestrator
from src.task_advisor import run_task_advisor


def log_debug(msg: str) -> None:
    """Lightweight debug logger for the root agent."""
    print(f"==== [root_agent] {msg}")

def run_task_assign_tool(
    raw_tasks_str: str,
    available_minutes: int = 60,
    energy_level: str = "medium",
) -> Dict[str, Any]:
    """
    Tool wrapper that runs the full task advisor pipeline.

    Args:
        raw_tasks_str: Task list provided by the user (JSON-like text).
        available_minutes: Time budget for this session.
        energy_level: User's current energy level ("low", "medium", "high").

    Returns:
        dict: A dictionary containing  information.
        - shortlist
        - nice_to_have
        - summary
    """
    log_debug(
        f"Calling run_task_advisor with available_minutes={available_minutes}, "
        f"energy_level={energy_level}"
    )
    plan_json = run_task_advisor(
        tasks=None,
        raw_tasks_str=raw_tasks_str,
        available_minutes=available_minutes,
        energy_level=energy_level,
    )
    log_debug("Received plan_json from run_task_advisor.")
    return plan_json


root_agent = Agent(
    model="gemini-2.5-flash-lite",
    name="task_advisor_root",
    description="Helps users turn a messy task list into a prioritized short plan for productivity.",
    instruction=(
        '''You are TaskAssigner, an AI agent that helps users choose the best tasks to work on
        based on their available time, energy level, and task list. You orchestrate the
        task-advisor pipeline by calling the tool `run_task_assign_tool`.

        Your responsibilities:

        1. **Parse User Input**
        - If the user gives tasks as JSON, CSV, list format, bullet points, or messy text,
            extract the list of tasks.
        - Identify fields like importance, urgency, desire, and est_minutes.
        - If some values are missing, pass raw text to the parser tool. Do NOT guess.

        2. **Collect Planning Context**
        - You must know:
                • available_minutes  
                • energy_level  
                • user task list  
        - If anything is missing, ask *only one* clarifying question.
        - If the user supplies everything in one message (e.g. “I have 30 minutes, low
            energy, and these tasks…”), proceed immediately.

        3. **Call the Tool**
        - Use:
                run_task_assign_tool(
                raw_tasks_str = <string form of tasks provided by user>,
                available_minutes = <integer>,
                energy_level = <string>
                )
        - The tool returns a structured JSON plan.

        4. **Present the Final Answer**
        - Summarize the plan for the user clearly.
        - Show the shortlist first, then nice-to-have tasks, then the summary.
        - Do not show internal debug logs.
        - DO NOT return raw JSON unless the user explicitly asks.

        5. **Error Handling**
        - If tool output is malformed or inconsistent, ask the user to reformat tasks.
        - If tasks are unparseable, say so and request correction.

        Your goal is to help the user quickly choose the best tasks for their current
        time and energy, while keeping the interaction simple and easy to understand.'''
    ),
    tools=[run_task_assign_tool],
)