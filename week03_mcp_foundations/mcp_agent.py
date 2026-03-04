"""Week 3: MCP Foundations - Agent with MCP Server Integration

Refactors the Week 1 file agent to use MCP for tool discovery and execution.
Demonstrates: MCP client, dynamic tool discovery, multi-server routing.
"""

import sys
import json
import asyncio
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.llm_client import LLMClient
from shared.mcp_utils import (
    connect_to_mcp_server, call_mcp_tool, MCPToolRouter, MCPServerConnection, MCPTool,
)

load_dotenv()


async def setup_mcp_servers() -> MCPToolRouter:
    """Connect to MCP servers and return a router with all available tools.

    To use real MCP servers, update the commands below:
      - Filesystem: npx -y @modelcontextprotocol/server-filesystem /path/to/dir
      - SQLite: npx -y @modelcontextprotocol/server-sqlite /path/to/db.sqlite
    """
    router = MCPToolRouter()

    # Example: connect to filesystem MCP server
    # Uncomment when you have the MCP server packages installed:
    #
    # fs_conn = await connect_to_mcp_server(
    #     "npx", ["-y", "@modelcontextprotocol/server-filesystem", "/tmp/test"],
    #     name="filesystem"
    # )
    # router.add_connection(fs_conn)

    # Example: connect to SQLite MCP server
    # sqlite_conn = await connect_to_mcp_server(
    #     "npx", ["-y", "@modelcontextprotocol/server-sqlite", "test.db"],
    #     name="sqlite"
    # )
    # router.add_connection(sqlite_conn)

    return router


def create_mock_router() -> MCPToolRouter:
    """Create a mock router for testing without real MCP servers."""
    router = MCPToolRouter()

    # Simulate filesystem server tools
    fs_tools = [
        MCPTool(
            name="read_file",
            description="Read contents of a file",
            input_schema={
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
            server_name="filesystem",
        ),
        MCPTool(
            name="list_directory",
            description="List files in a directory",
            input_schema={
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
            server_name="filesystem",
        ),
        MCPTool(
            name="search_files",
            description="Search for text across files",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "pattern": {"type": "string"},
                },
                "required": ["path", "pattern"],
            },
            server_name="filesystem",
        ),
    ]

    fs_conn = MCPServerConnection(name="filesystem", tools=fs_tools)
    router.add_connection(fs_conn)

    # Simulate SQLite server tools
    db_tools = [
        MCPTool(
            name="query",
            description="Execute a SQL query",
            input_schema={
                "type": "object",
                "properties": {"sql": {"type": "string"}},
                "required": ["sql"],
            },
            server_name="sqlite",
        ),
        MCPTool(
            name="list_tables",
            description="List all tables in the database",
            input_schema={"type": "object", "properties": {}},
            server_name="sqlite",
        ),
    ]

    db_conn = MCPServerConnection(name="sqlite", tools=db_tools)
    router.add_connection(db_conn)

    return router


def execute_mock_tool(prefixed_name: str, arguments: dict) -> str:
    """Mock tool execution for testing without real MCP servers."""
    if prefixed_name == "filesystem__list_directory":
        path = arguments.get("path", ".")
        return json.dumps({
            "entries": [
                {"name": "README.md", "type": "file", "size": 1024},
                {"name": "src", "type": "directory"},
                {"name": "main.py", "type": "file", "size": 2048},
            ]
        })
    elif prefixed_name == "filesystem__read_file":
        return f"Contents of {arguments.get('path', 'unknown')}: Sample file content."
    elif prefixed_name == "filesystem__search_files":
        return json.dumps({
            "matches": [{"file": "main.py", "line": 10, "text": f"Found: {arguments.get('pattern', '')}"}]
        })
    elif prefixed_name == "sqlite__list_tables":
        return json.dumps({"tables": ["users", "projects", "tasks"]})
    elif prefixed_name == "sqlite__query":
        return json.dumps({"rows": [{"id": 1, "name": "example"}], "row_count": 1})
    else:
        return json.dumps({"error": f"Unknown tool: {prefixed_name}"})


def run_mcp_agent(
    user_request: str,
    router: MCPToolRouter,
    tool_executor=None,
    max_iterations: int = 10,
) -> dict:
    """Run an agent that uses tools discovered from MCP servers.

    The agent does NOT hardcode any tool names. It discovers available tools
    from the router at runtime.
    """
    client = LLMClient(provider="anthropic", budget_usd=0.50)
    tool_executor = tool_executor or execute_mock_tool

    # Dynamic tool discovery -- agent adapts to whatever servers are connected
    tools = router.get_all_tools()
    server_info = f"Connected servers: {router.server_count()}, Available tools: {router.tool_count()}"

    system_prompt = (
        f"You are an assistant with access to external tools via MCP servers.\n"
        f"{server_info}\n"
        "Use the available tools to fulfill the user's request.\n"
        "Tool names are prefixed with the server name (e.g., filesystem__read_file).\n"
    )

    messages = [{"role": "user", "content": user_request}]
    all_tool_calls = []

    for iteration in range(max_iterations):
        response = client.chat(messages=messages, system=system_prompt, tools=tools)
        tool_calls = client.get_tool_calls(response)

        if not tool_calls:
            return {
                "response": client.get_text(response),
                "tool_calls": all_tool_calls,
                "tools_available": [t["name"] for t in tools],
                "usage": client.usage.summary(),
            }

        assistant_content = []
        for block in response["content"]:
            if block["type"] == "text" and block.get("text"):
                assistant_content.append({"type": "text", "text": block["text"]})
            elif block["type"] == "tool_use":
                assistant_content.append({
                    "type": "tool_use", "id": block["id"],
                    "name": block["name"], "input": block["input"],
                })
        messages.append({"role": "assistant", "content": assistant_content})

        tool_results = []
        for tc in tool_calls:
            result = tool_executor(tc["name"], tc["input"])
            all_tool_calls.append({"tool": tc["name"], "input": tc["input"]})
            tool_results.append({
                "type": "tool_result", "tool_use_id": tc["id"], "content": result,
            })
        messages.append({"role": "user", "content": tool_results})

    return {
        "response": "[Max iterations reached]",
        "tool_calls": all_tool_calls,
        "tools_available": [t["name"] for t in tools],
        "usage": client.usage.summary(),
    }


if __name__ == "__main__":
    router = create_mock_router()
    print(f"Connected to {router.server_count()} servers with {router.tool_count()} tools")
    print(f"Tools: {[t['name'] for t in router.get_all_tools()]}")
    print()

    request = sys.argv[1] if len(sys.argv) > 1 else "List all files and then show me the database tables"
    result = run_mcp_agent(request, router)
    print(f"Response: {result['response']}")
    print(f"Tool calls: {len(result['tool_calls'])}")
    print(f"Cost: ${result['usage']['estimated_cost_usd']:.4f}")
