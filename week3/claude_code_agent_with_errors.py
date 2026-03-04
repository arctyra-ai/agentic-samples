#!/usr/bin/env python3
"""
Week 3: Agent with Error Handling - Claude Code Edition
Uses Anthropic API with safe_tool_call, retries, and self-correction.
"""

import json
import os
import sys
from dotenv import load_dotenv
from anthropic import Anthropic

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "week2"))

from logging_config import (
    log_user_input, log_tool_call, log_tool_result,
    log_error, log_decision, logger
)
from memory import TaskMemory, ConversationMemory

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-20250514"

memory = TaskMemory("tasks.json")
conversation = ConversationMemory()

# Import tools (Anthropic format) from week2 claude variant
from claude_code_multi_tool_agent import TOOLS, process_tool_call


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
                log_error("NOT_FOUND", error_msg, "Retrying")
                continue
            elif "already exists" in error_msg.lower():
                log_error("DUPLICATE", error_msg, "Informing user")
                return f"That task already exists. Try a different title."
            log_error("VALUE_ERROR", error_msg, "Terminating action")
            return f"Error: {error_msg}"
        except Exception as e:
            attempt += 1
            log_error("UNEXPECTED", str(e), "Attempting recovery")
            if attempt >= max_retries:
                return "Unexpected error after retries. Please try again."

    return "Failed after retries."


def agent_self_correct(agent_response, tool_results):
    """Check agent response for inconsistencies with tool results"""
    if not agent_response:
        return agent_response

    response_lower = agent_response.lower()
    results_lower = str(tool_results).lower()

    if "completed" in response_lower and "not found" in results_lower:
        log_decision("Success claimed but tool reported not found", "Self-correcting")
        return "That task does not exist. Let me list your current tasks."

    if "deleted" in response_lower and "not found" in results_lower:
        log_decision("Deletion claimed but task not found", "Self-correcting")
        return "That task could not be found for deletion."

    if "added" in response_lower and "already exists" in results_lower:
        log_decision("Addition claimed but duplicate detected", "Self-correcting")
        return "A task with that name already exists. Try a different title."

    return agent_response


def robust_multi_turn_agent():
    """Multi-turn Claude agent with error handling and self-correction"""
    messages = []

    system_prompt = (
        "You are a helpful TODO list assistant with error handling. "
        "Use tools to manage tasks. If a tool returns an error, "
        "acknowledge it and suggest alternatives."
    )

    print("=" * 60)
    print("  Robust TODO Agent - Week 3 (Claude Code Edition)")
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
            response = client.messages.create(
                model=MODEL,
                max_tokens=1024,
                system=system_prompt,
                tools=TOOLS,
                messages=messages
            )

            # Handle tool use loop
            all_results = []
            while response.stop_reason == "tool_use":
                tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
                text_blocks = [b for b in response.content if b.type == "text"]

                for block in text_blocks:
                    if block.text:
                        print(f"Agent: {block.text}")

                messages.append({"role": "assistant", "content": response.content})

                tool_results = []
                for tool_block in tool_use_blocks:
                    result = safe_tool_call(tool_block.name, tool_block.input)
                    all_results.append(result)
                    print(f"  [{tool_block.name}] {result}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_block.id,
                        "content": result
                    })

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
                corrected = agent_self_correct(final_text, all_results)
                messages.append({"role": "assistant", "content": corrected})
                conversation.add_message("assistant", corrected)
                print(f"Agent: {corrected}\n")

        except Exception as e:
            log_error("AGENT_CALL_ERROR", str(e), "Prompting retry")
            print(f"Agent error: {str(e)}. Please try again.\n")


if __name__ == "__main__":
    robust_multi_turn_agent()
