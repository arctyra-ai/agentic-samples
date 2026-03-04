"""MCP client utilities for connecting agents to MCP servers.

Provides helpers for server connection, tool discovery, and tool execution.
"""

import asyncio
import json
from dataclasses import dataclass, field


@dataclass
class MCPTool:
    """Representation of a tool discovered from an MCP server."""
    name: str
    description: str
    input_schema: dict
    server_name: str

    def to_anthropic_format(self) -> dict:
        """Convert to Anthropic API tool format."""
        return {
            "name": f"{self.server_name}__{self.name}",
            "description": f"[{self.server_name}] {self.description}",
            "input_schema": self.input_schema,
        }


@dataclass
class MCPServerConnection:
    """Manages connection to a single MCP server."""
    name: str
    session: object = None
    tools: list[MCPTool] = field(default_factory=list)


async def connect_to_mcp_server(command: str, args: list[str], name: str) -> MCPServerConnection:
    """Connect to an MCP server via stdio transport.

    Args:
        command: The command to start the server (e.g., "npx", "python")
        args: Arguments for the command (e.g., ["-m", "mcp_server"])
        name: Human-readable name for this server connection

    Returns:
        MCPServerConnection with active session and discovered tools
    """
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError:
        raise ImportError(
            "MCP SDK not installed. Run: pip install mcp"
        )

    server_params = StdioServerParameters(command=command, args=args)
    read, write = await stdio_client(server_params)
    session = ClientSession(read, write)
    await session.initialize()

    # Discover tools
    tools_response = await session.list_tools()
    tools = [
        MCPTool(
            name=tool.name,
            description=tool.description or "",
            input_schema=tool.inputSchema,
            server_name=name,
        )
        for tool in tools_response.tools
    ]

    conn = MCPServerConnection(name=name, session=session, tools=tools)
    return conn


async def call_mcp_tool(conn: MCPServerConnection, tool_name: str, arguments: dict) -> str:
    """Call a tool on an MCP server.

    Args:
        conn: Active server connection
        tool_name: Name of the tool to call (without server prefix)
        arguments: Tool input arguments

    Returns:
        Tool result as string
    """
    result = await conn.session.call_tool(tool_name, arguments)
    if result.content:
        return result.content[0].text
    return ""


class MCPToolRouter:
    """Routes tool calls to the correct MCP server.

    When an agent has tools from multiple MCP servers, this router
    determines which server should handle each tool call based on
    the prefixed tool name (server__toolname).
    """

    def __init__(self):
        self.connections: dict[str, MCPServerConnection] = {}

    def add_connection(self, conn: MCPServerConnection):
        self.connections[conn.name] = conn

    def get_all_tools(self) -> list[dict]:
        """Get all tools from all servers in Anthropic API format."""
        tools = []
        for conn in self.connections.values():
            for tool in conn.tools:
                tools.append(tool.to_anthropic_format())
        return tools

    async def call_tool(self, prefixed_name: str, arguments: dict) -> str:
        """Route a tool call to the correct server.

        Args:
            prefixed_name: Tool name in format "servername__toolname"
            arguments: Tool input arguments

        Returns:
            Tool result as string
        """
        if "__" not in prefixed_name:
            raise ValueError(
                f"Tool name must be prefixed with server name: server__tool. Got: {prefixed_name}"
            )

        server_name, tool_name = prefixed_name.split("__", 1)
        if server_name not in self.connections:
            raise ValueError(
                f"No connection to server '{server_name}'. "
                f"Available: {list(self.connections.keys())}"
            )

        return await call_mcp_tool(self.connections[server_name], tool_name, arguments)

    def tool_count(self) -> int:
        return sum(len(c.tools) for c in self.connections.values())

    def server_count(self) -> int:
        return len(self.connections)
