#!/usr/bin/env python3
"""
Week 1: Tool Definitions for TODO Agent
Extracted from single_agent_todo.py for modular use
"""

# Tool definitions for OpenAI function calling format
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Add a new task to the TODO list",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "description": {"type": "string", "description": "Task description"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mark_complete",
            "description": "Mark a task as complete",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "Task ID"}
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "Task ID"}
                },
                "required": ["task_id"]
            }
        }
    }
]

# Tool name to function mapping helper
TOOL_NAMES = [t["function"]["name"] for t in TOOLS]


def get_tool_by_name(name: str) -> dict:
    """Look up a tool definition by name"""
    for tool in TOOLS:
        if tool["function"]["name"] == name:
            return tool
    return None
