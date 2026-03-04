#!/usr/bin/env python3
"""
Week 3: Agent with Error Handling, Self-Correction, and Retries
Builds on Week 2's multi-tool agent with robust error recovery.
"""

import json
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Add parent week2 to path for memory imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "week2"))

from logging_config import (
    log_user_input, log_tool_call, log_tool_result,
    log_error, log_decision, logger
)
from memory import TaskMemory, ConversationMemory

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

memory = TaskMemory("tasks.json")
conversation = ConversationMemory()

# Import TOOLS from week2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "week2"))
from multi_tool_agent import TOOLS


def process_tool_call(tool_name, tool_input):
    """Execute tool with error handling (duplicated here for standalone use)"""
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
            return f"Task {task['id']} marked complete"
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
        raise
    except Exception as e:
        raise


def safe_tool_call(tool_name, tool_input):
    """Execute tool with error handling and retries"""
    max_retries = 2
    attempt = 0

    while attempt < max_retries:
        try:
            log_tool_call(tool_name, tool_input)
            result = process_tool_call(tool_name, tool_input)
            log_tool_result(tool_name, result, success=True)
            return result

        except ValueError as e:
            attempt += 1
            error_msg = str(e)

            if "not found" in error_msg.lower() and attempt < max_retries:
                log_error("NOT_FOUND", error_msg, "Retrying with corrected input")
                continue
            elif "invalid" in error_msg.lower():
                log_error("VALIDATION", error_msg, "Agent should rephrase input")
                return f"I could not complete that action: {error_msg}. Could you clarify?"
            elif "already exists" in error_msg.lower():
                log_error("DUPLICATE", error_msg, "Informing user of duplicate")
                return f"That task already exists. Try a different title."

            log_error("VALUE_ERROR", error_msg, "Terminating this action")
            return f"Error: {error_msg}"

        except Exception as e:
            attempt += 1
            error_msg = f"Unexpected error: {str(e)}"
            log_error("UNEXPECTED_ERROR", error_msg, "Attempting recovery")

            if attempt < max_retries:
                continue
            else:
                return "I encountered an unexpected error. Please try again."

    return "Failed to complete action after retries."


def agent_self_correct(agent_response, tool_results):
    """
    Agent reviews its own response for consistency.
    Example: Agent says "Task 5 completed" but tool said "Task 5 not found"
    """
    if not agent_response:
        return agent_response

    response_lower = agent_response.lower()
    results_lower = str(tool_results).lower()

    # Check for success claim when tool reported failure
    if "completed" in response_lower and "not found" in results_lower:
        log_decision(
            "Agent claimed success but tool indicated failure",
            "Self-correcting response"
        )
        return "I apologize, that task does not exist. Let me list your current tasks."

    if "deleted" in response_lower and "not found" in results_lower:
        log_decision(
            "Agent claimed deletion but task was not found",
            "Self-correcting response"
        )
        return "That task could not be found for deletion. Would you like to see your task list?"

    if "added" in response_lower and "already exists" in results_lower:
        log_decision(
            "Agent claimed addition but task was duplicate",
            "Self-correcting response"
        )
        return "A task with that name already exists. Try a different title."

    return agent_response


def robust_multi_turn_agent():
    """Multi-turn agent with comprehensive error handling and self-correction"""
    messages = []

    print("=" * 60)
    print("  Robust TODO Agent - Week 3 (Error Handling)")
    print("=" * 60)
    print("\nType 'exit' to quit, 'trace' to see decision log.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        if user_input.lower() == "trace":
            trace = logger.get_trace(last_n=5)
            if not trace:
                print("  No events logged yet.\n")
            else:
                for entry in trace:
                    print(f"  [{entry['event_type']}] {entry['data']}")
                print()
            continue

        log_user_input(user_input)
        messages.append({"role": "user", "content": user_input})

        try:
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
                all_results = []
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_input = json.loads(tool_call.function.arguments)

                    result = safe_tool_call(tool_name, tool_input)
                    all_results.append(result)

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })

                    print(f"  [{tool_name}] {result}")

                # Self-correct if needed
                if assistant_message.content:
                    corrected = agent_self_correct(assistant_message.content, all_results)
                    if corrected != assistant_message.content:
                        print(f"Agent (corrected): {corrected}\n")
                        continue

                # Get final response
                followup = client.chat.completions.create(
                    model="gpt-4",
                    messages=messages
                )
                final_text = followup.choices[0].message.content
                # Self-correct final response too
                final_text = agent_self_correct(final_text, all_results)
                messages.append({"role": "assistant", "content": final_text})
                print(f"Agent: {final_text}\n")
            else:
                print(f"Agent: {assistant_message.content}\n")

        except Exception as e:
            log_error("AGENT_CALL_ERROR", str(e), "Prompting user to retry")
            print(f"Agent error: {str(e)}. Please try again.\n")


if __name__ == "__main__":
    robust_multi_turn_agent()
