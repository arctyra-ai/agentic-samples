# MCP (Model Context Protocol)

## What is MCP?

MCP is an open protocol that standardizes how AI systems connect to external tools and data sources. Created by Anthropic and donated to the Linux Foundation, MCP is now supported by OpenAI, Google, Microsoft, and thousands of developers.

Think of MCP as USB-C for AI: one standard interface that works with any model and any tool.

## Architecture

MCP uses a client-server architecture:

- **MCP Client**: Your agent. It discovers and calls tools.
- **MCP Server**: A tool provider. It exposes tools, resources, and prompts.
- **Transport**: The communication layer (stdio, SSE, or HTTP).

## Three Primitives

### Tools
Actions the agent can take. Each tool has a name, description, and input schema.
```json
{
  "name": "query_database",
  "description": "Execute a SQL query",
  "inputSchema": {"type": "object", "properties": {"sql": {"type": "string"}}}
}
```

### Resources
Data the agent can read. Like a file system or database that the agent can query.

### Prompts
Reusable prompt templates that the server provides to the client.

## Why MCP Over Custom Integrations

Before MCP, connecting an agent to a database required writing custom code for that specific database and that specific agent framework. With MCP, you write one MCP server for the database, and any MCP-compatible agent can use it.

Benefits:
- Write once, use everywhere
- No vendor lock-in (switch LLM providers without rewriting integrations)
- Growing ecosystem of pre-built servers
- Standardized security and authentication patterns

## Connecting to an MCP Server

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(command="npx", args=["-y", "@modelcontextprotocol/server-sqlite", "db.sqlite"])
read, write = await stdio_client(server_params)
session = ClientSession(read, write)
await session.initialize()

# Discover tools
tools = await session.list_tools()

# Call a tool
result = await session.call_tool("query", {"sql": "SELECT * FROM users"})
```

## Building an MCP Server

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("my-server")

@app.list_tools()
async def list_tools():
    return [Tool(name="hello", description="Say hello", inputSchema={"type": "object"})]

@app.call_tool()
async def call_tool(name, arguments):
    return [TextContent(type="text", text="Hello!")]
```
