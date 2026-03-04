"""Week 3 STARTER: MCP Agent

TODO: Build an agent that discovers tools dynamically from MCP servers.
Copy this file to mcp_agent.py and fill in the TODO sections.
"""

import sys
import json
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.llm_client import LLMClient
from shared.mcp_utils import MCPToolRouter, MCPServerConnection, MCPTool

load_dotenv()


def create_mock_router() -> MCPToolRouter:
    """Create a mock router with filesystem and SQLite servers for testing.

    TODO: Create MCPTool instances for each server and add them to the router.
    Filesystem server tools: read_file, list_directory, search_files
    SQLite server tools: query, list_tables
    Each tool needs: name, description, input_schema, server_name
    """
    router = MCPToolRouter()
    # TODO: Create filesystem tools and connection
    # TODO: Create SQLite tools and connection
    # TODO: Add connections to router
    return router


def execute_mock_tool(prefixed_name: str, arguments: dict) -> str:
    """Mock tool execution for testing without real MCP servers.

    TODO: Handle each prefixed tool name (e.g., "filesystem__list_directory")
    and return plausible JSON results.
    Return {"error": "..."} for unknown tools.
    """
    # TODO: Implement mock responses for each tool
    return json.dumps({"error": f"Unknown tool: {prefixed_name}"})


def run_mcp_agent(user_request: str, router: MCPToolRouter,
                  tool_executor=None, max_iterations: int = 10) -> dict:
    """Run an agent that uses tools discovered from MCP servers.

    TODO: Implement the agent loop. Key difference from Week 1:
    - Tools come from router.get_all_tools() (dynamic, not hardcoded)
    - Tool names are prefixed: "servername__toolname"
    - The agent adapts to whatever servers are connected

    Return: dict with response, tool_calls, tools_available, usage
    """
    client = LLMClient(provider="anthropic", budget_usd=0.50)
    tool_executor = tool_executor or execute_mock_tool
    tools = router.get_all_tools()

    # TODO: Implement agent loop using dynamically discovered tools
    pass


if __name__ == "__main__":
    router = create_mock_router()
    print(f"Connected to {router.server_count()} servers with {router.tool_count()} tools")
    request = sys.argv[1] if len(sys.argv) > 1 else "List all files and show me the database tables"
    result = run_mcp_agent(request, router)
    print(f"Response: {result['response']}")
