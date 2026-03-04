"""Week 1 STARTER: File Operations Agent

TODO: Implement the agent loop and tool functions.
Copy this file to agent.py and fill in the TODO sections.
Compare your implementation against agent.py (the reference solution).
"""

import os
import sys
import json
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.llm_client import LLMClient

load_dotenv()

# --- Tool Definitions ---
# TODO: Define 5 tools with clear descriptions and input schemas.
# Tools needed: list_files, read_file, search_in_files, get_file_info, write_summary
# Each tool needs: name, description (specific enough for LLM to select correctly),
# and input_schema (JSON Schema format).

TOOLS = [
    # TODO: Add your tool definitions here
    # Example structure:
    # {
    #     "name": "list_files",
    #     "description": "...",
    #     "input_schema": {
    #         "type": "object",
    #         "properties": { ... },
    #         "required": [ ... ],
    #     },
    # },
]


# --- Tool Implementations ---

def execute_tool(name: str, tool_input: dict) -> str:
    """Execute a tool and return result as string.

    TODO: Implement each tool function.
    - list_files: Use Path.glob() to list files. Return JSON with file names, sizes, types.
    - read_file: Read file content. Handle errors (not found, binary files). Truncate if > 10000 chars.
    - search_in_files: Search for a pattern across files. Return matching lines with file paths.
    - get_file_info: Return file metadata (size, modified date, line count).
    - write_summary: Write content to a file. Create parent directories if needed.

    Every tool should return a JSON string. Errors should also be JSON: {"error": "message"}
    """
    try:
        if name == "list_files":
            pass  # TODO
        elif name == "read_file":
            pass  # TODO
        elif name == "search_in_files":
            pass  # TODO
        elif name == "get_file_info":
            pass  # TODO
        elif name == "write_summary":
            pass  # TODO
        else:
            return json.dumps({"error": f"Unknown tool: {name}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


# --- Agent Loop ---

def run_agent(user_request: str, target_dir: str, max_iterations: int = 10) -> dict:
    """Run the file operations agent.

    TODO: Implement the agent loop.
    1. Create an LLMClient with a budget
    2. Set up the system prompt (tell the agent its working directory)
    3. Initialize messages with the user request
    4. Loop up to max_iterations:
       a. Call client.chat() with messages and TOOLS
       b. Check for tool_use blocks in the response
       c. If no tool calls -> agent is done, return the text response
       d. If tool calls -> execute each tool, append results to messages
    5. Return dict with: response (str), tool_calls (list), usage (dict)

    Key: The message format for tool results must follow the Anthropic API spec:
    - Assistant message contains tool_use blocks
    - User message contains tool_result blocks matching tool_use IDs
    """
    client = LLMClient(provider="anthropic", budget_usd=0.50)

    # TODO: Implement the agent loop
    pass


# --- Interactive CLI ---

def main():
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    target_dir = str(Path(target_dir).resolve())

    print("=" * 60)
    print("  File Operations Agent")
    print(f"  Working directory: {target_dir}")
    print("=" * 60)
    print("\nExamples: 'Show me all Python files', 'Find files containing TODO'")
    print("Type 'quit' to exit.\n")

    while True:
        try:
            request = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not request or request.lower() in ("quit", "exit", "q"):
            break

        result = run_agent(request, target_dir)
        print(f"\nAgent: {result['response']}")
        print(f"  [{result['usage']['total_calls']} API calls, ${result['usage']['estimated_cost_usd']:.4f}]\n")


if __name__ == "__main__":
    main()
