#!/usr/bin/env python3
"""
Week 5: CrewAI with Conflict Detection and Resolution
Extends Week 4 with a 4th agent (Review Manager) and conflict handling.
"""

import json
import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "week2"))

from crewai import Agent, Task, Crew
from conflict_detection import ConflictDetector, AgentOpinion, ConflictType
from memory import TaskMemory

memory = TaskMemory("tasks.json")


# ============================================================================
# Define Agents (4 total)
# ============================================================================

parser = Agent(
    role="Intent Parser",
    goal="Understand user intent and extract structured action data",
    backstory="Expert at natural language understanding and intent classification"
)

validator = Agent(
    role="Validator",
    goal="Check if the proposed action is safe and valid",
    backstory="Safety expert who prevents destructive or invalid operations"
)

storage = Agent(
    role="Storage Agent",
    goal="Execute CRUD operations on task storage",
    backstory="Data operations expert focused on reliable execution"
)

reviewer = Agent(
    role="Review Manager",
    goal="Make final decision when agents disagree",
    backstory="Impartial decision maker who weighs all agent perspectives"
)


# ============================================================================
# Define Tasks with Dependencies
# ============================================================================

parse_intent = Task(
    description="Parse user request: {user_request}\nOutput action_type and parameters as JSON.",
    agent=parser,
    expected_output="JSON with parsed intent and action"
)

check_safety = Task(
    description=(
        "Check if this action is safe to execute.\n"
        "Parsed intent from parser: Use context from previous task.\n"
        "Assess: Is it destructive? Does it need confirmation? Are parameters valid?"
    ),
    agent=validator,
    expected_output="Safety assessment: approve / reject / concern with reasoning",
    context=[parse_intent]
)

execute_if_safe = Task(
    description=(
        "Execute the action if safety check approves.\n"
        "If validator raised concerns, do NOT execute - pass to reviewer."
    ),
    agent=storage,
    expected_output="Execution result or deferral to reviewer",
    context=[check_safety]
)

resolve_conflict = Task(
    description=(
        "Review the disagreement between validator and storage agent.\n"
        "Consider both perspectives and make a final decision.\n"
        "Output: approve (execute) or reject (cancel) with reasoning."
    ),
    agent=reviewer,
    expected_output="Final decision: approve or reject with full reasoning",
    context=[check_safety, execute_if_safe]
)


# ============================================================================
# Create Crew
# ============================================================================

crew = Crew(
    agents=[parser, validator, storage, reviewer],
    tasks=[parse_intent, check_safety, execute_if_safe, resolve_conflict],
    verbose=True
)


def run_with_conflict_detection(user_request):
    """Run crew and detect conflicts in the output"""
    print(f"\nProcessing: {user_request}")
    print("-" * 40)

    result = crew.kickoff(inputs={
        "user_request": user_request,
        "parsed_intent": "Will be determined by parser"
    })

    return result


if __name__ == "__main__":
    print("=" * 60)
    print("  CrewAI with Conflict Detection - Week 5")
    print("=" * 60)

    # Test scenarios
    scenarios = [
        "Add a task: Write unit tests for the login module",
        "Delete all tasks",
        "Mark task 999 as complete",
    ]

    for scenario in scenarios:
        print(f"\n{'='*60}")
        result = run_with_conflict_detection(scenario)
        print(f"\nFinal: {result}")
