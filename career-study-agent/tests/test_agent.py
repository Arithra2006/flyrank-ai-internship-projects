"""
tests/test_agent.py

Evaluation scenarios for the Career & Study Prioritization Agent, matching
the 6 cases described in the project spec. These call the real Anthropic API
(via PrioritizationAgent), so they require a valid LLM_API_KEY in the
environment and will consume API credits when run.

I have not run these against a live API key in this environment, so treat
them as a starting harness to run and refine yourself, not as pre-verified
passing tests.

Run with:  python -m pytest tests/test_agent.py -v
       or: python tests/test_agent.py   (runs as a plain script)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database as db
from agent import PrioritizationAgent


def reset_test_db():
    """Wipe and reseed the DB so each scenario starts from known state."""
    if os.path.exists(db.DB_PATH):
        os.remove(db.DB_PATH)
    db.init_db()
    db.seed_example_data()


def run_case(agent, label, prompt):
    print(f"\n=== {label} ===")
    print(f"USER: {prompt}")
    result = agent.chat(prompt)
    print(f"AGENT: {result['reply']}")
    return result


def test_scenarios():
    reset_test_db()
    agent = PrioritizationAgent()

    # 1. Basic daily prioritization
    run_case(agent, "Basic Daily Prioritization",
              "I have 3 hours today. What should I work on?")

    # 2. Conflicting deadlines — not enough time for everything
    run_case(agent, "Conflicting Deadlines",
              "I only have 20 minutes today but I have several things due soon. What should I do?")

    # 3. Changing priorities — new urgent task appears
    db.add_task("Urgent client fix", "Internship", "High", "2026-08-02", 45,
                 description="Production bug needs fixing today")
    run_case(agent, "Changing Priorities",
              "Something urgent just came up — an internship bug fix due tomorrow. "
              "I have 2 hours today, what should I prioritize now?")

    # 4. No clear plan — vague request
    run_case(agent, "No Clear Plan",
              "I don't really know what to do today, can you help?")

    # 5. Unrealistic workload — very little time, many tasks
    run_case(agent, "Unrealistic Workload",
              "I have 10 minutes today. Plan out how I'll finish everything.")

    # 6. Incomplete information — no available time given
    run_case(agent, "Incomplete Information",
              "What should I prioritize?")

    print("\nAll scenarios executed. Manually review output above against expectations:")
    print("- Case 1: plan should fit within 180 minutes, reference real seeded tasks.")
    print("- Case 2: plan should fit within 20 minutes, likely only one task.")
    print("- Case 3: new urgent task should be reflected/prioritized appropriately.")
    print("- Case 4: agent should still use real task/goal data, not generic advice.")
    print("- Case 5: agent should NOT overcommit beyond 10 minutes; should say so explicitly.")
    print("- Case 6: agent should ask for available time rather than assuming it.")


if __name__ == "__main__":
    test_scenarios()
