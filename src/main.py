# Master debug flag for the entire script.
DEBUG = False

from pprint import pformat

def log_debug(msg: str):
    """Print debug messages only when DEBUG is True."""
    if DEBUG:
        print(f"[DEBUG] {msg}")


# Sample tasks for testing the prioritization system.
# Each task includes ratings (1 = low, 2 = medium, 3 = high) for:
# - Importance: How critical the task is to your goals or responsibilities.
# - Urgency: How quickly the task needs attention.
# - Desire: How motivated you feel to complete the task.
# Tasks also include an estimated completion time in minutes.
SAMPLE_TASKS = [
    {"title": "Email accountant", "importance": 3, "urgency": 3, "desire": 1, "est_minutes": 20},
    {"title": "Practice DSA", "importance": 2, "urgency": 1, "desire": 3, "est_minutes": 30},
    {"title": "Take a break", "importance": 2, "urgency": 2, "desire": 2, "est_minutes": 20},
]

# Function to calculate the priority score of a task.
#
# The score is determined using a weighted formula that factors in
# importance, urgency, and personal preference. The combination of
# urgency and importance aligns with common prioritization frameworks
# such as the Eisenhower Matrix.
# Additionally, the user's desire to do a task is included to slightly
# influence the final ranking.
def compute_priority_score(task):
    """
    Computes a numeric priority score for a task.
    The formula is intentionally transparent so the scoring logic is easy to understand.
    Importance and urgency are emphasized through a multiplicative factor,
    with the task's "desire" score added to slightly influence the final result.
    """
    return (
        ((1.5 * task["importance"]) *
        (1 * task["urgency"])) +
        (1 * task["desire"])
    )


def score_tasks(tasks):
    """
    Add a `score` to each task and return them sorted by score (descending).
    """
    scored = []
    for t in tasks:
        t_copy = dict(t)
        t_copy["score"] = compute_priority_score(t_copy)
        scored.append(t_copy)

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


def choose_shortlist(scored_tasks, available_minutes=60):
    """
    Choose a shortlist of tasks that fit within the given time budget.
    Full debug prints an explaination of each decision.
    """
    remaining = available_minutes
    shortlist = []

    log_debug(f"Starting shortlist selection with {available_minutes} minutes.")
    for t in scored_tasks:
        title = t['title']
        est = t['est_minutes']
        score = t['score']

        log_debug(f"Considering: {title} (score={score}, est={est} min)")
        
        if est <= remaining:
            shortlist.append(t)
            remaining -= est
            log_debug(f"-> SELECTED. {remaining} minutes remaining.")
        else:
            log_debug(f"-> SKIPPED (not enough time). Still {remaining} minutes left.")

    log_debug(f"Selection complete. Final remaining minutes: {remaining}.")
    return shortlist


def assemble_plan_data(
    all_tasks,
    available_minutes,
    energy_level,
    suggested_shortlist=None,
):
    """
    Build the plan_data dict that will be sent to the planning agent.

    - all_tasks: full scored task list
    - available_minutes: time budget
    - energy_level: string like "low", "medium", "high"
    - suggested_shortlist: optional shortlist chosen by the deterministic planner
      (the agent may use this as a hint, but it's not authoritative)
    """
    plan_data = {
        "available_minutes": available_minutes,
        "energy_level": energy_level,
        "all_tasks": all_tasks,
    }

    if suggested_shortlist is not None:
        plan_data["suggested_shortlist"] = suggested_shortlist
        log_debug(
            f"Constructed plan data with {len(suggested_shortlist)} suggested shortlist tasks."
        )
    else:
        log_debug("Constructed plan data with no suggested shortlist.")

    return plan_data

# Main function
if __name__ == "__main__":
    print("=== Raw Tasks ===")
    for t in SAMPLE_TASKS:
        print("-", t["title"])

    scored = score_tasks(SAMPLE_TASKS)

    print("\n=== Scored & Sorted Tasks (debug) ===")
    for t in scored:
        print(
            f"{t['score']:>4} - {t['title']} | "
            f"imp={t['importance']} urg={t['urgency']} "
            f"des={t['desire']} drag={t.get('drag', 'NA')} "
            f"est={t['est_minutes']} min"
        )
    
    print("\n=== Shortlist (deterministic, debug) ===")
    shortlist = choose_shortlist(scored, available_minutes=60)

    for t in shortlist:
        print(f"- {t['title']} ({t['est_minutes']} min, score={t['score']})")
    
    log_debug(f"Final list: {[t['title'] for t in shortlist]}")

    print("\n=== Working on Plan Data (debug) ===")
    plan_data = assemble_plan_data(
        shortlist=shortlist,
        all_tasks=scored,
        available_minutes=60,
        energy_level="medium",
    )
    log_debug("Plan data:\n" + pformat(plan_data, indent=2))