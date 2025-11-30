"""
Entrypoint for ADK (file-based mode).
This file loads the real agent defined in agents/task_advisor_agent/agent.py
and exposes it as a module-level variable for `adk run`.
"""

from agents.task_assign_agent.agent import root_agent