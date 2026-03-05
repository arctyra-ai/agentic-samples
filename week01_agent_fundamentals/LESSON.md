# Week 1 Lesson: Agent Fundamentals

## What You Are Building

This week you build a file operations agent -- a program that accepts natural language requests like "find all Python files containing TODO comments" and fulfills them by calling tools. The agent decides which tools to use, interprets the results, and responds in plain English.

This is the foundational pattern behind every AI agent system. ChatGPT plugins, Claude's tool use, GitHub Copilot's workspace commands, and enterprise agent platforms all use the same loop you will implement this week. Employers listing "agentic AI" in job postings expect you to understand this loop, not as a concept, but as something you can build, debug, and extend.

By the end of this week you will have a working agent that makes real API calls to Claude, executes tools on your local filesystem, handles errors gracefully, and tracks exactly how much each interaction costs.

## Core Concepts

### The Agent Loop

Every agent follows the same cycle: send a message to the LLM with available tools, check if the LLM wants to call a tool, execute the tool if so, send the result back, and repeat until the LLM responds with text only (no tool calls). That final text response is the agent's answer.

```python
messages = [{"role": "user", "content": user_request}]

for _ in range(max_iterations):
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        messages=messages,
        tools=tools,
        max_tokens=4096,
    )

    # If no tool calls, the agent is done
    if response.stop_reason == "end_turn":
        print(response.content[0].text)
        break

    # Otherwise, execute each tool call and feed results back
    for block in response.content:
        if block.type == "tool_use":
            result = execute_tool(block.name, block.input)
            # ... append tool result to messages and continue loop
```

The key insight: the LLM decides what to do. You provide the tools and their descriptions. The LLM reads the descriptions, picks the right tool, and generates the arguments. Your code just executes whatever the LLM asks for and returns the result.

### Tool Definitions

A tool definition tells the LLM what the tool does and what arguments it accepts. The quality of your description directly determines whether the LLM picks the right tool. Vague descriptions cause wrong tool selections.

```python
{
    "name": "search_in_files",
    "description": "Search for a text pattern across all files in a directory. Returns matching lines with file paths and line numbers.",
    "input_schema": {
        "type": "object",
        "properties": {
            "directory": {"type": "string", "description": "Directory to search in"},
            "pattern": {"type": "string", "description": "Text to search for (case-insensitive)"},
        },
        "required": ["directory", "pattern"],
    },
}
```

Watch for: if the LLM keeps picking `read_file` when you meant it to use `search_in_files`, the problem is almost always in the description, not in the LLM. Make descriptions specific about what the tool returns and when to use it.

### Tool Results and Multi-Turn Messages

The Anthropic API requires a specific message format for tool results. The assistant message contains `tool_use` blocks, and the next user message contains matching `tool_result` blocks. The IDs must match.

```python
# Assistant says it wants to call a tool
assistant_message = {
    "role": "assistant",
    "content": [
        {"type": "tool_use", "id": "toolu_01abc", "name": "list_files", "input": {"directory": "/tmp"}}
    ]
}

# You execute the tool and send the result back
tool_result_message = {
    "role": "user",
    "content": [
        {"type": "tool_result", "tool_use_id": "toolu_01abc", "content": '{"files": ["a.py", "b.py"]}'}
    ]
}
```

Watch for: if you forget to include the `tool_use_id` in the result, or if the IDs do not match, the API will return an error. This is the most common bug in first-time agent implementations.

### Cost Tracking

Every API call has a cost based on input and output tokens. The `LLMClient` wrapper in `shared/llm_client.py` tracks this automatically. An agent that makes 5 tool calls in a single interaction might cost $0.01-0.05 depending on context length.

```python
client = LLMClient(provider="anthropic", budget_usd=0.50)
# ... agent loop runs ...
print(client.usage.summary())
# {"total_calls": 5, "total_input_tokens": 3200, "total_output_tokens": 800, "estimated_cost_usd": 0.018}
```

Setting a budget limit is not optional in production. Without it, a misbehaving agent can burn through hundreds of dollars in minutes. The `budget_usd` parameter causes the client to raise an exception when the limit is reached.

### Path Sandboxing

When an LLM controls file operations, it can request any path. The sandbox restricts all file access to a specific directory, preventing the LLM from reading `/etc/passwd` or writing to system files. This is a security pattern you will see in every production agent that touches a filesystem.

```python
def _validate_path(filepath: str) -> Path:
    resolved = os.path.realpath(filepath)
    sandbox = os.path.realpath(SANDBOX_ROOT)
    if not resolved.startswith(sandbox + os.sep) and resolved != sandbox:
        raise ValueError(f"Access denied: {filepath} is outside {sandbox}")
    return Path(resolved)
```

## How the Pieces Connect

This week's agent loop is the same loop used in every subsequent week. Week 2 adds tool chaining (output of one tool feeds into the next). Week 3 replaces hardcoded tool definitions with dynamically discovered tools from MCP servers. Weeks 7-9 run multiple agent loops in parallel and combine their results. But the core loop -- send message, check for tool use, execute, repeat -- never changes.

The `LLMClient` in `shared/llm_client.py` is reused in every week. Understanding how it wraps the Anthropic API, tracks tokens, and enforces budgets will save you debugging time for the rest of the curriculum.

## Now Build It

Open `README.md` for the exercise specification, success criteria, and run/test commands. Copy `agent_starter.py` to `agent.py` and begin implementing the TODOs. Run the tests as you go -- they validate each tool independently before testing the full agent loop.
