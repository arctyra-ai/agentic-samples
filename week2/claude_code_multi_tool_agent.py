#!/usr/bin/env python3
"""
Week 2: Multi-Tool Agent with Persistent Memory - Claude Code Edition
Uses Anthropic API (Claude models) instead of OpenAI.
"""

import json
import os
from dotenv import load_dotenv
from anthropic import Anthropic
from memory import TaskMemory, ConversationMemory

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-20250514"

# Initialize persistent storage
memory = TaskMemory("tasks.json")
conversation = ConversationMemory()

# ============================================================================
# Tool Definitions (Anthropic format)
# ============================================================================

TOOLS = [
    {
        "name": "add_task",
        "description": "Add a new task to the TODO list",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Task title"},
                "description": {"type": "string", "description": "Task description"},
                "priority": {"type": "string", "enum": ["high", "medium", "low"], "description": "Task priority"}
            },
            "required": ["title"]
        }
    },
    {
        "name": "list_tasks",
        "description": "List all tasks, optionally filtered and sorted",
        "input_schema": {
            "type": "object",
            "properties": {
                "filter_by": {"type": "string", "enum": ["all", "completed", "pending"], "description": "Filter tasks"},
                "sort_by": {"type": "string", "enum": ["priority", "date"], "description": "Sort order"}
            }
        }
    },
    {
        "name": "mark_complete",
        "description": "Mark a task as complete",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "Task ID"}
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "delete_task",
        "description": "Delete a task",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "Task ID"}
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "search_tasks",
        "description": "Search tasks by keyword",
        "input_schema": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "Search keyword"}
            },
            "required": ["keyword"]
        }
    },
    {
        "name": "update_task",
        "description": "Update task priority or due date",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer"},
                "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                "due_date": {"type": "string", "description": "ISO format date"}
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "get_stats",
        "description": "Get task statistics (total, completed, pending, high priority)",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    }
]


# ============================================================================
# Tool Execution
# ============================================================================

def process_tool_call(tool_name, tool_input):
    """Execute tool with error handling"""
    try:
        if tool_name == "add_task":
            task = memory.add_task(
                title=tool_input.get("title"),
                description=tool_input.get("description", ""),
                priority=tool_input.get("priority", "medium")
            )
            return f"Task created: {json.dumps(task, default=str)}"
        elif tool_name == "list_tasks":
            tasks = memory.list_tasks(
                filter_by=tool_input.get("filter_by", "all"),
                sort_by=tool_input.get("sort_by", "priority")
            )
            return json.dumps(tasks, indent=2, default=str) if tasks else "No tasks found."
        elif tool_name == "mark_complete":
            task = memory.mark_complete(tool_input.get("task_id"))
            return f"Task {task['id']} marked complete: {task['title']}"
        elif tool_name == "delete_task":
            task = memory.delete_task(tool_input.get("task_id"))
            return f"Deleted task: {task['title']}"
        elif tool_name == "search_tasks":
            results = memory.search_tasks(tool_input.get("keyword"))
            return json.dumps(results, indent=2, default=str) if results else "No results."
        elif tool_name == "update_task":
            kwargs = {k: v for k, v in tool_input.items() if k != "task_id" and v is not None}
            task = memory.update_task(tool_input.get("task_id"), **kwargs)
            return f"Updated task {task['id']}"
        elif tool_name == "get_stats":
            return json.dumps(memory.get_stats(), indent=2)
        else:
            return f"Unknown tool: {tool_name}"
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


# ============================================================================
# Multi-Turn Agent Loop (Anthropic API)
# ============================================================================

def multi_turn_agent():
    """Multi-turn agent using Claude with tool use"""
    messages = []

    system_prompt = (
        "You are a helpful TODO list assistant. Use the available tools to "
        "manage tasks. Always confirm actions with the user."
    )

    print("=" * 60)
    print("  TODO Agent - Week 2 (Claude Code Edition)")
    print("=" * 60)
    print("\nCommands: add, list, search, update, complete, delete, stats")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        conversation.add_message("user", user_input)
        messages.append({"role": "user", "content": user_input})

        # Call Claude with tools
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=system_prompt,
            tools=TOOLS,
            messages=messages
        )

        # Process response - handle tool use loop
        while response.stop_reason == "tool_use":
            # Extract tool use blocks
            tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
            text_blocks = [b for b in response.content if b.type == "text"]

            # Show any text before tool calls
            for block in text_blocks:
                if block.text:
                    print(f"Agent: {block.text}")

            # Add assistant message to history
            messages.append({"role": "assistant", "content": response.content})

            # Execute each tool call
            tool_results = []
            for tool_block in tool_use_blocks:
                result = process_tool_call(tool_block.name, tool_block.input)
                print(f"  [{tool_block.name}] {result}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": result
                })

            # Send results back to Claude
            messages.append({"role": "user", "content": tool_results})

            response = client.messages.create(
                model=MODEL,
                max_tokens=1024,
                system=system_prompt,
                tools=TOOLS,
                messages=messages
            )

        # Final text response
        final_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                final_text += block.text

        if final_text:
            messages.append({"role": "assistant", "content": final_text})
            conversation.add_message("assistant", final_text)
            print(f"Agent: {final_text}\n")


if __name__ == "__main__":
    multi_turn_agent()
