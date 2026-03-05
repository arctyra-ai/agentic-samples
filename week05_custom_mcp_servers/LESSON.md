# Week 5 Lesson: Custom MCP Servers

## What You Are Building

This week you build the other side of MCP: a server. Your server wraps a SQLite database and exposes project/task management operations as MCP tools. Any MCP-compatible agent can connect to your server and manage projects through natural language.

Week 3 taught you to consume MCP servers. This week you produce one. Together, these two skills cover the full MCP ecosystem. In practice, organizations build custom MCP servers for their internal systems -- databases, APIs, monitoring tools, deployment pipelines -- so that agents can interact with them through a standard protocol instead of custom code.

By the end of this week you will have a working MCP server with 6 tools, input validation, structured error handling, and persistent SQLite storage.

## Core Concepts

### MCP Server Structure

An MCP server does three things: register tools (tell clients what it can do), handle tool calls (execute the requested operation), and return results (structured data or errors).

```python
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("project-manager")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(name="create_project", description="...", inputSchema={...}),
        Tool(name="list_projects", description="...", inputSchema={...}),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    result = handle_tool(name, arguments)
    return [TextContent(type="text", text=result)]
```

The `list_tools` handler is called when a client connects and asks what is available. The `call_tool` handler is called for every tool invocation. Your business logic goes in `handle_tool`.

### Designing Tool Schemas

Each tool needs an input schema (JSON Schema format) that tells the client exactly what arguments are accepted. Good schemas include types, descriptions, enums for constrained values, and required field lists.

```python
{
    "name": "add_task",
    "description": "Add a task to a project",
    "inputSchema": {
        "type": "object",
        "properties": {
            "project_name": {"type": "string", "description": "Name of the project"},
            "title": {"type": "string", "description": "Task title"},
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "description": "Task priority"
            },
        },
        "required": ["project_name", "title"],
    },
}
```

The `enum` constraint on priority means the LLM will only generate one of the three valid values. Without it, the LLM might send "urgent", "critical", or "p0" -- all reasonable but not what your database expects. Schemas prevent this class of error entirely.

### Input Validation

Never trust tool inputs. Even with schemas, validate before executing. The LLM can send empty strings, nonexistent references, or edge cases the schema does not catch.

```python
def _create_project(db, args) -> str:
    name = args["name"].strip()
    if not name:
        return json.dumps({"error": "Project name cannot be empty"})
    try:
        db.execute("INSERT INTO projects (name) VALUES (?)", (name,))
        db.commit()
        return json.dumps({"status": "created", "project": name})
    except sqlite3.IntegrityError:
        return json.dumps({"error": f"Project '{name}' already exists"})
```

Every tool should return JSON. Success cases and error cases both return structured JSON. This lets the LLM read the error and try a different approach (e.g., if a project already exists, it might decide to add tasks to the existing one instead of creating a new one).

Watch for: returning bare Python exception messages (`str(e)`) exposes internal implementation details. Craft specific error messages that help the LLM recover.

### Parameterized SQL

All SQL queries must use parameterized placeholders (`?` in SQLite), never string formatting. This prevents SQL injection -- the single most common web application vulnerability.

```python
# Correct: parameterized
db.execute("SELECT * FROM projects WHERE name = ?", (name,))

# Wrong: string formatting (SQL injection vulnerability)
db.execute(f"SELECT * FROM projects WHERE name = '{name}'")
```

If the LLM sends `name = "'; DROP TABLE projects; --"`, the parameterized version treats it as a literal string. The string-formatted version executes the DROP TABLE command. Week 7's code review agent is specifically trained to detect this pattern.

### Testing Without MCP SDK

The exercise separates tool logic from MCP protocol handling. The `handle_tool` function works with plain Python -- no MCP SDK needed. You can test, debug, and run in standalone mode. The MCP server wrapper is added only when running as an actual MCP server.

```python
# Works without MCP installed
result = handle_tool("create_project", {"name": "Test"})
print(result)  # {"status": "created", "project": "Test"}
```

This separation is a design pattern worth remembering: keep business logic independent of the framework.

## How the Pieces Connect

This server is the kind of integration your capstone project (Weeks 11-12) will include. The capstone requires at least one MCP server connecting your multi-agent system to an external service. The SQLite patterns here (CRUD operations, input validation, parameterized queries) transfer directly to any database-backed MCP server.

The tool schema design skills carry forward to Weeks 7-9 where you design tools for code review agents. The validation and error handling patterns become critical when multiple agents call your tools concurrently.

## Now Build It

Open `README.md` for the exercise specification. Copy `project_mcp_server_starter.py` to `project_mcp_server.py` and implement the TODOs. Start with the database schema, then implement tools one at a time, testing each with `pytest test_mcp_server.py -v` as you go. The standalone mode (`python project_mcp_server.py`) runs a demo sequence without needing the MCP SDK.
