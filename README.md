# Office Task Assigning Agent
A Smart, Lightweight AI Agent for Assigning and Prioritizing Daily Office Tasks

# 📌 Problem Statement
In modern office environments, employees juggle a large volume of tasks with varying urgency, importance, deadlines, and effort.However, most people struggle with:
* Deciding what to work on next
* Managing limited time and fluctuating energy levels
* Understanding which tasks provide the highest impact
* Organizing scattered or messy task lists
* Maintaining productivity during busy or stressful periods
Traditional to-do lists fail because they are static and do not adapt to context such as available time, energy, cognitive load, or changing priorities.
This project solves the core challenge of real-time priority decision-making, helping professionals stay focused, improve output quality, and reduce overwhelm.

# 🤖 Why Agents?
Agents are the ideal solution because they:
* Interpret messy, natural-language input from users
* Break down tasks into structured formats, which humans rarely do consistently
* Reason over multiple factors at once (urgency, importance, desire, effort, time)
* Adapt to each user’s context rather than giving generic advice
* Provide actionable recommendations rather than simple lists
* Scale well as workflows become more complex

The combination of deterministic logic + LLM reasoning ensures:
* Consistency
* Transparency
* Human-like flexibility
* Improved decision-making over time
This hybrid approach makes agents exceptionally well-suited for dynamic office task management.

# 🏗 What I Created (Architecture Overview)
The Office Task Assigning Agent is built using a hybrid agentic architecture:
1. Task Parsing Agent (LLM)
* Accepts natural-language or structured task lists
* Normalizes tasks into:{title, importance, urgency, desire, est_minutes}
* Imputes missing fields automatically

2. Deterministic Task Planner
* Scores tasks using weighted logic
* Selects a shortlist based on available time + energy
* Generates structured plan_data

3. AI Planning & Explanation Agent
* Refines the shortlist
* Suggests optional “nice to have” tasks
* Produces natural-language reasoning and summaries

4. Root Orchestrator Agent (Google ADK)
* Manages the flow between sub-agents
* Handles user messages
* Outputs the final human-friendly plan

# 🎥 Demo (How It Works)
### User Input

I've got 30 minutes and low energy. Tasks:
- email manager (importance 3, urgency 2)
- take a break (desire 3)
- write unit test case (urgency 3)

### Agent Output

With 30 minutes and low energy, here's a plan:

Shortlist:

email manager: (15 min est.) - This task has a high score and fits within the available time and energy.
take a break: (10 min est.) - Low energy suggests a break is beneficial and fits within the remaining time.
Summary: Focus on clearing emails and taking a break to manage low energy effectively. The 'write unit test case' task is too long given the available time and low energy.

## Summary:
The agent:
* Parses the tasks
* Scores them
* Refines the top picks
* Explains the reasoning
All in one seamless workflow.

# 🔧 The Build (Tools & Technologies)
This project is built with:
* Google Agent Development Kit (ADK) – agent orchestration + CLI
* Google Gemini (via google-genai client) – LLM-powered reasoning
* Python – deterministic logic and pipeline implementation
* Modular architecture – agents, scoring, planning, pipeline
* Environment variables – API key configuration

### Repository Structure

project-root/
├── agents/
│   └── task_assign_agent/
│       ├── agent.py
│       └── __init__.py
├── src/
│   ├── main.py
│   ├── parse_tasks_agent.py
│   ├── plan_explainer_agent.py
│   └── task_pipeline.py
├── .env
└── README.md


### How to Run
1. Clone the repository : git clone https://github.com/weaktogeek/task-assigning-agent.git
2. cd task-assigning-agent
3. Install dependencies : pip install -r requirements.txt
4. Add your API key in .env : GOOGLE_API_KEY=your-key-here
5. Start the agent CLI : adk run agents/task_assign_agent
   OR
6. Start the agent : adk web agents


# ⏳ If I Had More Time, I Would…
* Add calendar integration (Google/Outlook) to auto-detect availability
* Build UI dashboards for drag-and-drop prioritization
* Support task breakdown for large projects
* Add team coordination mode for distributing work across members
* Implement multi-modal input (voice task capture, attachments, screenshots)
* Improve reasoning with self-critique loops for even better accuracy
