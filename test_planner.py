"""
Quick test script for the Study Planner Agent.
Run from the project root:

    python test_planner.py
"""

import json
import logging
from dotenv import load_dotenv

load_dotenv()  # Load .env before importing the agent

from backend.agents.study_planner import study_planner_agent  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(name)s | %(message)s",
)

# ---------------------------------------------------------------------------
# Sample state — edit this to try different inputs
# ---------------------------------------------------------------------------

STATE = {
    "key_topics": [
        "Supervised Learning",
        "Unsupervised Learning",
        "Neural Networks",
    ],
    "study_days": 5,
}

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n=== INPUT ===")
    print(json.dumps(STATE, indent=2))

    print("\n=== RUNNING STUDY PLANNER AGENT ===\n")
    result = study_planner_agent(STATE)

    print("\n=== OUTPUT ===")
    print(json.dumps(result, indent=2))

    print("\n=== SUMMARY ===")
    for day in result["study_plan"]:
        topics_str = ", ".join(day["topics"])
        print(
            f"  Day {day['day']:>2} | {day['difficulty']:<6} | "
            f"{day['estimated_hours']}h | {topics_str}"
        )
