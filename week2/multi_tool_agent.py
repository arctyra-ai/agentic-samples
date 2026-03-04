#!/usr/bin/env python3
"""
Week 2: Multi-Tool Agent with Persistent Memory
Extends Week 1 with 7 tools, persistent storage, input validation,
and separate conversation/task memory.
"""

import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from memory import TaskMemory, ConversationMemory

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize persistent storage
memory = TaskMemory("tasks.json")
conversation = ConversationMemory()

# ============================================================================
# Tool Definitions (expanded from Week 1)
# ============================================================================

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
                    "description": {"type": "string", "description": "Task description"},
                    "priority": {"type": "string", "enum": ["high", "medium", "low"], "description": "Task priority"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks, optionally filtered and sorted",
            "parameters": {
                "type": "object",
                "properties": {
                    "filter_by": {"type": "string", "enum": ["all", "completed", "pending"], "description": "Filter tasks"},
                    "sort_by": {"type": "string", "enum": ["priority", "date"], "description": "Sort order"}
                }
            }
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
    },
    {
        "type": "function",
        "function": {
            "name": "search_tasks",
            "description": "Search tasks by keyword",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "Search keyword"}
                },
                "required": ["keyword"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update task priority or due date",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                    "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                    "due_date": {"type": "string", "description": "ISO format date"}
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_stats",
            "description": "Get task statistics (total, completed, pending, high priority)",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]


# ============================================================================
# Tool Execution with Error Handling
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
            if not tasks:
                return "No tasks found."
            return json.dumps(tasks, indent=2, default=str)

        elif tool_name == "mark_complete":
            task = memory.mark_complete(tool_input.get("task_id"))
            return f"Task {task['id']} marked complete: {task['title']}"

        elif tool_name == "delete_task":
            task = memory.delete_task(tool_input.get("task_id"))
            return f"Deleted task: {task['title']}"

        elif tool_name == "search_tasks":
            results = memory.search_tasks(tool_input.get("keyword"))
            if not results:
                return "No tasks match that search."
            return json.dumps(results, indent=2, default=str)

        elif tool_name == "update_task":
            kwargs = {k: v for k, v in tool_input.items() if k != "task_id" and v is not None}
            task = memory.update_task(tool_input.get("task_id"), **kwargs)
            return f"Updated task {task['id']}: {json.dumps(task, default=str)}"

        elif tool_name == "get_stats":
            stats = memory.get_stats()
            return json.dumps(stats, indent=2)

        else:
            return f"Unknown tool: {tool_name}"

    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


# ============================================================================
# Multi-Turn Agent Loop
# ============================================================================

def multi_turn_agent():
    """Multi-turn agent with persistent memory and conversation history"""
    messages = []

    print("=" * 60)
    print("  TODO Agent - Week 2 (Persistent Memory)")
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

        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message
        messages.append({
            "role": "assistant",
            "content": assistant_message.content or "",
            "tool_calls": [tc.model_dump() for tc in (assistant_message.tool_calls or [])]
        })

        if assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_input = json.loads(tool_call.function.arguments)

                result = process_tool_call(tool_name, tool_input)
                print(f"  [{tool_name}] {result}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

            # Get final response after tool execution
            followup = client.chat.completions.create(
                model="gpt-4",
                messages=messages
            )
            final_text = followup.choices[0].message.content
            messages.append({"role": "assistant", "content": final_text})
            conversation.add_message("assistant", final_text)
            print(f"Agent: {final_text}\n")
        else:
            conversation.add_message("assistant", assistant_message.content)
            print(f"Agent: {assistant_message.content}\n")


if __name__ == "__main__":
    multi_turn_agent()
