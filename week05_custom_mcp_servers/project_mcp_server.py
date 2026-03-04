"""Week 5: Custom MCP Server - Project Management

A custom MCP server that wraps a SQLite database for project/task management.
Run as: python project_mcp_server.py

Demonstrates: MCP server creation, tool registration, SQLite persistence, input validation.
"""

import asyncio
import json
import sqlite3
from datetime import datetime
from pathlib import Path

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


DB_PATH = "projects.db"


def get_db(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Get database connection, creating tables if needed."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT DEFAULT '',
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'todo',
            priority TEXT DEFAULT 'medium',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)
    conn.commit()
    return conn


# --- Tool Definitions ---

TOOL_DEFINITIONS = [
    Tool(
        name="create_project",
        description="Create a new project with a name and optional description",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Project name (must be unique)"},
                "description": {"type": "string", "description": "Project description"},
            },
            "required": ["name"],
        },
    ),
    Tool(
        name="list_projects",
        description="List all projects with their status and task counts",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="add_task",
        description="Add a task to a project",
        inputSchema={
            "type": "object",
            "properties": {
                "project_name": {"type": "string", "description": "Name of the project"},
                "title": {"type": "string", "description": "Task title"},
                "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "Task priority"},
            },
            "required": ["project_name", "title"],
        },
    ),
    Tool(
        name="update_task",
        description="Update a task's status (todo, in_progress, done)",
        inputSchema={
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "Task ID"},
                "status": {"type": "string", "enum": ["todo", "in_progress", "done"]},
            },
            "required": ["task_id", "status"],
        },
    ),
    Tool(
        name="get_project_status",
        description="Get detailed status of a project including all tasks",
        inputSchema={
            "type": "object",
            "properties": {
                "project_name": {"type": "string"},
            },
            "required": ["project_name"],
        },
    ),
    Tool(
        name="search_tasks",
        description="Search tasks by keyword across all projects",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search keyword"},
            },
            "required": ["query"],
        },
    ),
]


# --- Tool Implementations ---

def handle_tool(name: str, arguments: dict, db_path: str = DB_PATH) -> str:
    """Execute a tool and return result as JSON string."""
    db = get_db(db_path)
    try:
        if name == "create_project":
            return _create_project(db, arguments)
        elif name == "list_projects":
            return _list_projects(db)
        elif name == "add_task":
            return _add_task(db, arguments)
        elif name == "update_task":
            return _update_task(db, arguments)
        elif name == "get_project_status":
            return _get_project_status(db, arguments)
        elif name == "search_tasks":
            return _search_tasks(db, arguments)
        else:
            return json.dumps({"error": f"Unknown tool: {name}"})
    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        db.close()


def _create_project(db, args) -> str:
    name = args["name"].strip()
    if not name:
        return json.dumps({"error": "Project name cannot be empty"})
    description = args.get("description", "")
    try:
        db.execute("INSERT INTO projects (name, description) VALUES (?, ?)", (name, description))
        db.commit()
        return json.dumps({"status": "created", "project": name})
    except sqlite3.IntegrityError:
        return json.dumps({"error": f"Project '{name}' already exists"})


def _list_projects(db) -> str:
    rows = db.execute("""
        SELECT p.*, COUNT(t.id) as task_count,
               SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END) as done_count
        FROM projects p LEFT JOIN tasks t ON p.id = t.project_id
        GROUP BY p.id ORDER BY p.created_at DESC
    """).fetchall()
    projects = [
        {"id": r["id"], "name": r["name"], "description": r["description"],
         "status": r["status"], "tasks": r["task_count"], "done": r["done_count"] or 0}
        for r in rows
    ]
    return json.dumps({"projects": projects, "count": len(projects)})


def _add_task(db, args) -> str:
    project = db.execute("SELECT id FROM projects WHERE name = ?", (args["project_name"],)).fetchone()
    if not project:
        return json.dumps({"error": f"Project '{args['project_name']}' not found"})
    title = args["title"].strip()
    if not title:
        return json.dumps({"error": "Task title cannot be empty"})
    priority = args.get("priority", "medium")
    db.execute("INSERT INTO tasks (project_id, title, priority) VALUES (?, ?, ?)",
               (project["id"], title, priority))
    db.commit()
    return json.dumps({"status": "added", "project": args["project_name"], "task": title, "priority": priority})


def _update_task(db, args) -> str:
    task = db.execute("SELECT id FROM tasks WHERE id = ?", (args["task_id"],)).fetchone()
    if not task:
        return json.dumps({"error": f"Task {args['task_id']} not found"})
    db.execute("UPDATE tasks SET status = ? WHERE id = ?", (args["status"], args["task_id"]))
    db.commit()
    return json.dumps({"status": "updated", "task_id": args["task_id"], "new_status": args["status"]})


def _get_project_status(db, args) -> str:
    project = db.execute("SELECT * FROM projects WHERE name = ?", (args["project_name"],)).fetchone()
    if not project:
        return json.dumps({"error": f"Project '{args['project_name']}' not found"})
    tasks = db.execute("SELECT * FROM tasks WHERE project_id = ? ORDER BY priority DESC, created_at",
                       (project["id"],)).fetchall()
    return json.dumps({
        "project": dict(project),
        "tasks": [dict(t) for t in tasks],
        "summary": {
            "total": len(tasks),
            "todo": sum(1 for t in tasks if t["status"] == "todo"),
            "in_progress": sum(1 for t in tasks if t["status"] == "in_progress"),
            "done": sum(1 for t in tasks if t["status"] == "done"),
        },
    })


def _search_tasks(db, args) -> str:
    query = f"%{args['query']}%"
    rows = db.execute("""
        SELECT t.*, p.name as project_name FROM tasks t
        JOIN projects p ON t.project_id = p.id
        WHERE t.title LIKE ? ORDER BY t.created_at DESC
    """, (query,)).fetchall()
    return json.dumps({"results": [dict(r) for r in rows], "count": len(rows)})


# --- MCP Server ---

if MCP_AVAILABLE:
    app = Server("project-manager")

    @app.list_tools()
    async def list_tools() -> list[Tool]:
        return TOOL_DEFINITIONS

    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        result = handle_tool(name, arguments)
        return [TextContent(type="text", text=result)]

    async def main():
        async with stdio_server() as (read, write):
            await app.run(read, write, app.create_initialization_options())


if __name__ == "__main__":
    if MCP_AVAILABLE:
        asyncio.run(main())
    else:
        print("MCP SDK not installed. Running in standalone test mode.")
        print()
        db_path = "test_projects.db"
        Path(db_path).unlink(missing_ok=True)

        print(handle_tool("create_project", {"name": "Demo", "description": "Test project"}, db_path))
        print(handle_tool("add_task", {"project_name": "Demo", "title": "Build MCP server", "priority": "high"}, db_path))
        print(handle_tool("add_task", {"project_name": "Demo", "title": "Write tests"}, db_path))
        print(handle_tool("update_task", {"task_id": 1, "status": "done"}, db_path))
        print(handle_tool("get_project_status", {"project_name": "Demo"}, db_path))
        print(handle_tool("search_tasks", {"query": "test"}, db_path))

        Path(db_path).unlink(missing_ok=True)
