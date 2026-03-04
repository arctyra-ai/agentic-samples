#!/usr/bin/env python3
"""
Week 4: CrewAI Multi-Agent TODO System
Three agents (Task Manager, Storage Specialist, Data Validator) with role-based
architecture and task dependency chaining.
"""

import json
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Add week2 to path for memory
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "week2"))

from crewai import Agent, Task, Crew
from memory import TaskMemory

# Initialize shared memory
memory = TaskMemory("tasks.json")


# ============================================================================
# Define Agents with Explicit Roles
# ============================================================================

task_manager = Agent(
    role="Task Manager",
    goal="Understand user intent and break down requests into specific actions",
    backstory=(
        "You are an expert at parsing user requests and understanding what "
        "tasks need to be executed. You identify the action type (add, list, "
        "delete, update, search) and extract relevant parameters."
    ),
    tools=[],
    verbose=True
)

storage_agent = Agent(
    role="Storage Specialist",
    goal="Execute CRUD operations on tasks safely and correctly",
    backstory=(
        "You are responsible for managing task storage. You execute operations "
        "and ensure data integrity. You report results clearly."
    ),
    tools=[],
    verbose=True
)

validator_agent = Agent(
    role="Data Validator",
    goal="Ensure all operations are valid before they are executed",
    backstory=(
        "You validate all operations and catch errors before they cause "
        "problems. You check for empty titles, duplicate tasks, invalid IDs, "
        "and destructive operations that need confirmation."
    ),
    tools=[],
    verbose=True
)


# ============================================================================
# Define Tasks with Dependencies
# ============================================================================

parse_task = Task(
    description=(
        "Parse the user request and identify the action to take.\n"
        "User input: {user_input}\n"
        "Identify: action_type, parameters (title, task_id, priority, etc.)"
    ),
    agent=task_manager,
    expected_output="JSON with action_type and parameters"
)

validate_task = Task(
    description=(
        "Validate the proposed action from the Task Manager.\n"
        "Check: Is the action valid? Are parameters complete? Any safety concerns?\n"
        "Parsed action: {action}"
    ),
    agent=validator_agent,
    expected_output="Validation result: approve/reject with reasoning",
    context=[parse_task]
)

execute_task = Task(
    description=(
        "Execute the validated action on the task storage.\n"
        "Action details: {action}\n"
        "Only execute if validation approved."
    ),
    agent=storage_agent,
    expected_output="Execution result or rejection message",
    context=[validate_task]
)


# ============================================================================
# Create Crew
# ============================================================================

crew = Crew(
    agents=[task_manager, validator_agent, storage_agent],
    tasks=[parse_task, validate_task, execute_task],
    verbose=True
)


def run_crewai_system(user_input):
    """Run CrewAI crew with user input"""
    result = crew.kickoff(inputs={
        "user_input": user_input,
        "action": "Will be determined by parse task"
    })
    return result


if __name__ == "__main__":
    print("=" * 60)
    print("  CrewAI TODO System - Week 4")
    print("=" * 60)
    print()

    test_inputs = [
        "Add a task called 'Review pull request' with high priority",
        "List all my pending tasks",
        "Delete task 1",
    ]

    for user_input in test_inputs:
        print(f"\n{'='*60}")
        print(f"User: {user_input}")
        print(f"{'='*60}")
        result = run_crewai_system(user_input)
        print(f"\nFinal Result: {result}")
