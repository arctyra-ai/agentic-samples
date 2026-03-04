#!/usr/bin/env python3
"""
Week 6: State Schemas for LangGraph TODO System
Defines the TypedDict used as the state object flowing through the graph.
"""

from typing import TypedDict


class TodoState(TypedDict):
    """State schema for the LangGraph TODO workflow.

    Fields:
        user_input: Raw user input string
        parsed_intent: Human-readable description of what the user wants
        action_type: Classified action (add, list, delete, mark_complete, search, update, unknown)
        task_data: Extracted parameters for the action (title, task_id, priority, etc.)
        validation_result: Output from validation node (is_valid, warnings, suggestions)
        execution_result: Output from execution node (success, data)
        error: Error message if any step failed, empty string otherwise
    """
    user_input: str
    parsed_intent: str
    action_type: str
    task_data: dict
    validation_result: dict
    execution_result: dict
    error: str


def create_initial_state(user_input: str) -> TodoState:
    """Factory function to create a clean initial state"""
    return {
        "user_input": user_input,
        "parsed_intent": "",
        "action_type": "",
        "task_data": {},
        "validation_result": {},
        "execution_result": {},
        "error": ""
    }
