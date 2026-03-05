"""Week 1: File Operations Agent

An agent that reads, searches, summarizes, and organizes files in a directory.
Demonstrates: tool calling, agent loop, multi-turn, error handling, cost tracking.
"""

import os
import sys
import json
import glob
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

# Add parent to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.llm_client import LLMClient

load_dotenv()

# --- Tool Definitions ---

TOOLS = [
    {
        "name": "list_files",
        "description": "List files in a directory. Returns filenames, sizes, and types. Use pattern to filter (e.g., '*.py' for Python files).",
        "input_schema": {
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "Absolute or relative path to directory"},
                "pattern": {"type": "string", "description": "Glob pattern to filter files (e.g., '*.py', '*.md'). Default: '*'"},
            },
            "required": ["directory"],
        },
    },
    {
        "name": "read_file",
        "description": "Read the full contents of a text file. Returns the file content as a string. Use for text files only.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Path to the file to read"},
            },
            "required": ["filepath"],
        },
    },
    {
        "name": "search_in_files",
        "description": "Search for a text pattern across all files in a directory. Returns matching lines with file paths and line numbers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "Directory to search in"},
                "pattern": {"type": "string", "description": "Text or pattern to search for (case-insensitive)"},
                "file_pattern": {"type": "string", "description": "File glob pattern to limit search (e.g., '*.py'). Default: '*'"},
            },
            "required": ["directory", "pattern"],
        },
    },
    {
        "name": "get_file_info",
        "description": "Get detailed metadata about a file: size in bytes, last modified date, line count, file type.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Path to the file"},
            },
            "required": ["filepath"],
        },
    },
    {
        "name": "write_summary",
        "description": "Write a text summary to a file. Creates or overwrites the file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Path for the output file"},
                "content": {"type": "string", "description": "Summary content to write"},
            },
            "required": ["filepath", "content"],
        },
    },
]


# --- Tool Implementations ---

# --- Path Sandboxing ---

_SANDBOX_ROOT: str = "."


def set_sandbox(directory: str):
    """Set the sandbox root. All file operations are restricted to this directory."""
    global _SANDBOX_ROOT
    _SANDBOX_ROOT = str(Path(directory).resolve())


def _validate_path(filepath: str) -> Path:
    """Validate that a path is within the sandbox. Raises ValueError if not.

    Uses os.path.realpath for symlink resolution (handles macOS /var -> /private/var).
    """
    resolved = os.path.realpath(filepath)
    sandbox = os.path.realpath(_SANDBOX_ROOT)
    if not resolved.startswith(sandbox + os.sep) and resolved != sandbox:
        raise ValueError(
            f"Access denied: {filepath} is outside the working directory. "
            f"Operations are restricted to {sandbox}"
        )
    return Path(resolved)


def execute_tool(name: str, tool_input: dict) -> str:
    """Execute a tool and return result as string."""
    try:
        if name == "list_files":
            return _list_files(tool_input["directory"], tool_input.get("pattern", "*"))
        elif name == "read_file":
            return _read_file(tool_input["filepath"])
        elif name == "search_in_files":
            return _search_in_files(
                tool_input["directory"],
                tool_input["pattern"],
                tool_input.get("file_pattern", "*"),
            )
        elif name == "get_file_info":
            return _get_file_info(tool_input["filepath"])
        elif name == "write_summary":
            return _write_summary(tool_input["filepath"], tool_input["content"])
        else:
            return json.dumps({"error": f"Unknown tool: {name}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def _list_files(directory: str, pattern: str = "*") -> str:
    p = _validate_path(directory)
    if not p.exists():
        return json.dumps({"error": f"Directory not found: {directory}"})
    if not p.is_dir():
        return json.dumps({"error": f"Not a directory: {directory}"})

    files = []
    for f in sorted(p.glob(pattern)):
        if f.is_file():
            files.append({
                "name": f.name,
                "size_bytes": f.stat().st_size,
                "type": f.suffix or "no extension",
            })
    return json.dumps({"directory": directory, "pattern": pattern, "files": files, "count": len(files)})


def _read_file(filepath: str) -> str:
    p = _validate_path(filepath)
    if not p.exists():
        return json.dumps({"error": f"File not found: {filepath}"})
    if not p.is_file():
        return json.dumps({"error": f"Not a file: {filepath}"})
    try:
        content = p.read_text(encoding="utf-8")
        if len(content) > 10000:
            content = content[:10000] + f"\n... [truncated, {len(content)} total chars]"
        return content
    except UnicodeDecodeError:
        return json.dumps({"error": f"Cannot read binary file: {filepath}"})


def _search_in_files(directory: str, pattern: str, file_pattern: str = "*") -> str:
    p = _validate_path(directory)
    if not p.exists():
        return json.dumps({"error": f"Directory not found: {directory}"})

    matches = []
    pattern_lower = pattern.lower()
    for f in p.rglob(file_pattern):
        if not f.is_file():
            continue
        try:
            for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                if pattern_lower in line.lower():
                    matches.append({
                        "file": str(f.relative_to(p)),
                        "line_number": i,
                        "line": line.strip()[:200],
                    })
        except (UnicodeDecodeError, PermissionError):
            continue

    return json.dumps({"search_pattern": pattern, "matches": matches[:50], "total_matches": len(matches)})


def _get_file_info(filepath: str) -> str:
    p = _validate_path(filepath)
    if not p.exists():
        return json.dumps({"error": f"File not found: {filepath}"})

    stat = p.stat()
    info = {
        "path": str(p),
        "name": p.name,
        "size_bytes": stat.st_size,
        "type": p.suffix or "no extension",
        "modified": str(stat.st_mtime),
    }
    if p.is_file():
        try:
            lines = p.read_text(encoding="utf-8").splitlines()
            info["line_count"] = len(lines)
        except UnicodeDecodeError:
            info["line_count"] = None
            info["binary"] = True
    return json.dumps(info)


def _write_summary(filepath: str, content: str) -> str:
    p = _validate_path(filepath)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return json.dumps({"status": "written", "path": str(p), "size_bytes": len(content.encode("utf-8"))})


# --- Agent Loop ---

def run_agent(user_request: str, target_dir: str, max_iterations: int = 10) -> dict:
    """Run the file operations agent.

    Args:
        user_request: Natural language request from user
        target_dir: Directory the agent operates on
        max_iterations: Safety limit on agent loop iterations

    Returns:
        dict with keys: response (str), tool_calls (list), usage (dict)
    """
    set_sandbox(target_dir)
    client = LLMClient(provider="anthropic", budget_usd=0.50)
    system_prompt = (
        f"You are a file operations assistant. Your working directory is: {target_dir}\n"
        "Use the provided tools to fulfill user requests about files.\n"
        "Be specific about what you find. If a file doesn't exist, say so.\n"
        "When done, provide a clear summary of what you found or did."
    )

    messages = [{"role": "user", "content": user_request}]
    all_tool_calls = []

    for iteration in range(max_iterations):
        response = client.chat(
            messages=messages,
            system=system_prompt,
            tools=TOOLS,
        )

        tool_calls = client.get_tool_calls(response)

        # No tool calls = agent is done
        if not tool_calls:
            return {
                "response": client.get_text(response),
                "tool_calls": all_tool_calls,
                "usage": client.usage.summary(),
            }

        # Build assistant message with all content blocks
        assistant_content = []
        for block in response["content"]:
            if block["type"] == "text" and block.get("text"):
                assistant_content.append({"type": "text", "text": block["text"]})
            elif block["type"] == "tool_use":
                assistant_content.append({
                    "type": "tool_use",
                    "id": block["id"],
                    "name": block["name"],
                    "input": block["input"],
                })

        messages.append({"role": "assistant", "content": assistant_content})

        # Execute each tool call and build tool results
        tool_results = []
        for tc in tool_calls:
            result = execute_tool(tc["name"], tc["input"])
            all_tool_calls.append({
                "tool": tc["name"],
                "input": tc["input"],
                "result_preview": result[:200],
            })
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tc["id"],
                "content": result,
            })

        messages.append({"role": "user", "content": tool_results})

    # Max iterations reached
    return {
        "response": "[Agent reached max iterations without completing]",
        "tool_calls": all_tool_calls,
        "usage": client.usage.summary(),
    }


# --- Interactive CLI ---

def main():
    """Interactive CLI for the file operations agent."""
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    target_dir = str(Path(target_dir).resolve())

    print("=" * 60)
    print("  File Operations Agent")
    print(f"  Working directory: {target_dir}")
    print("=" * 60)
    print()
    print("Examples:")
    print("  Show me all Python files")
    print("  Find files containing TODO comments")
    print("  Summarize the README")
    print("  Which files are largest?")
    print("  Type 'quit' to exit")
    print()

    while True:
        try:
            request = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not request or request.lower() in ("quit", "exit", "q"):
            break

        result = run_agent(request, target_dir)
        print(f"\nAgent: {result['response']}")
        print(f"  [{result['usage']['total_calls']} API calls, "
              f"${result['usage']['estimated_cost_usd']:.4f}]")
        print()


if __name__ == "__main__":
    main()
