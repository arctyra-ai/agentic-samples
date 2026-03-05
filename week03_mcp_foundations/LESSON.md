# Week 3 Lesson: MCP Foundations

## What You Are Building

This week you refactor the Week 1 file agent so that its tools come from MCP servers instead of hardcoded Python functions. The agent will connect to multiple MCP servers at startup, discover what tools are available, and use them -- without knowing in advance what those tools are.

MCP (Model Context Protocol) is the industry standard for connecting AI agents to external tools and data. Anthropic created it, then OpenAI, Google, Microsoft, and AWS adopted it. By end of 2026, 75% of API gateway vendors are expected to integrate MCP. If you build agents professionally, you will encounter MCP. Understanding the client side (this week) and the server side (Week 5) covers both halves of the protocol.

The key shift from Weeks 1-2: your agent code no longer contains any tool definitions. Tools are discovered at runtime from whatever servers are connected. Add a new MCP server, and the agent immediately has new capabilities -- zero code changes.

## Core Concepts

### MCP Architecture

MCP has three components:

- **Client**: Your agent. Connects to servers, discovers tools, calls them.
- **Server**: A tool provider. Exposes tools (actions), resources (data), and prompts (templates).
- **Transport**: How they communicate. Stdio (local processes) or HTTP/SSE (remote services).

The protocol is request-response over JSON-RPC. The client sends "list tools" and gets back tool definitions. The client sends "call tool X with arguments Y" and gets back the result. That is the entire interaction.

```
Agent (MCP Client)
    ├── connects to → Filesystem Server (tools: read_file, list_directory, search_files)
    ├── connects to → SQLite Server (tools: query, list_tables)
    └── connects to → [any future server] (tools: discovered at runtime)
```

### Dynamic Tool Discovery

Instead of hardcoding tools in your agent, you ask MCP servers what they offer:

```python
# Connect to a server
session = await connect_to_mcp_server("npx", ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"])

# Discover tools (you don't know what these are in advance)
tools_response = await session.list_tools()
for tool in tools_response.tools:
    print(f"{tool.name}: {tool.description}")
    # Output: read_file: Read contents of a file
    #         list_directory: List files in a directory
    #         ...
```

The agent converts these discovered tools into the format the Anthropic API expects, then uses them exactly like the hardcoded tools from Week 1. The difference is that adding a new server adds new tools without touching the agent code.

### Multi-Server Routing

When an agent connects to multiple MCP servers, it needs to know which server handles each tool call. The `MCPToolRouter` solves this by prefixing tool names with the server name:

```python
router = MCPToolRouter()
router.add_connection(filesystem_server)  # tools: read_file, list_directory
router.add_connection(sqlite_server)      # tools: query, list_tables

# Agent sees these tools:
# filesystem__read_file, filesystem__list_directory, sqlite__query, sqlite__list_tables

# When the LLM calls "sqlite__query", the router knows to send it to the SQLite server
result = await router.call_tool("sqlite__query", {"sql": "SELECT * FROM users"})
```

The double-underscore prefix convention is a common pattern in MCP client implementations. It keeps tool names unique across servers and makes routing deterministic.

Watch for: if you forget the prefix when calling tools, or if two servers have tools with the same name, routing will fail. The router handles this by requiring the prefix on every call.

### Why MCP Over Custom Integrations

Before MCP, connecting an agent to a database required writing a custom tool function specific to that database and that agent framework. Connecting to 10 services meant writing 10 custom integrations. Each one had different error handling, authentication, and data formats.

With MCP, you write one MCP server per service. Any MCP-compatible agent can use it. Switch from Claude to GPT-4? The MCP servers do not change. Add a new agent framework? It connects to your existing servers. This is why the industry is converging on MCP -- it eliminates the N-times-M integration problem.

### Mock Servers for Testing

In this exercise, you use mock servers (Python objects that simulate MCP responses) so you can develop and test without installing actual MCP server packages. This is a standard development pattern: mock the external dependency, build against the mock, then swap in the real thing.

```python
def execute_mock_tool(prefixed_name: str, arguments: dict) -> str:
    if prefixed_name == "filesystem__list_directory":
        return json.dumps({"entries": [{"name": "README.md", "type": "file"}]})
    elif prefixed_name == "sqlite__query":
        return json.dumps({"rows": [{"id": 1, "name": "example"}]})
```

The agent code is identical whether it talks to mock servers or real ones. Only the tool executor function changes.

## How the Pieces Connect

This week introduces the separation between agent logic and tool implementation that persists through the rest of the curriculum. Week 5 builds the server side -- you will create a custom MCP server from scratch. Weeks 7-9 use MCP-discovered tools in multi-agent systems. The capstone (Weeks 11-12) requires at least one MCP integration.

The `shared/mcp_utils.py` module you use this week contains the `MCPToolRouter` and connection utilities used throughout later weeks. Understanding its API now saves significant time later.

## Now Build It

Open `README.md` for the exercise specification. Copy `mcp_agent_starter.py` to `mcp_agent.py` and implement the TODOs. Focus on: creating the mock router with tools from two servers, implementing mock tool execution, and building the agent loop that uses dynamically discovered tools. Run `pytest test_mcp.py -v` to validate.
