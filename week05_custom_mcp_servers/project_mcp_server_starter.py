"""Week 5 STARTER: Custom MCP Server

TODO: Build an MCP server that wraps SQLite for project/task management.
Copy this file to project_mcp_server.py and fill in the TODO sections.
"""

import json
import sqlite3
from pathlib import Path

DB_PATH = "projects.db"


def get_db(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Get database connection, creating tables if needed.

    TODO: Create two tables:
    - projects: id (autoincrement), name (unique), description, status, created_at
    - tasks: id (autoincrement), project_id (FK), title, status, priority, created_at
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # TODO: CREATE TABLE IF NOT EXISTS for both tables
    conn.commit()
    return conn


def handle_tool(name: str, arguments: dict, db_path: str = DB_PATH) -> str:
    """Execute a tool and return result as JSON string.

    TODO: Implement 6 tools:
    - create_project: Insert project. Reject empty names and duplicates.
    - list_projects: SELECT all projects with task counts (use LEFT JOIN).
    - add_task: Insert task. Validate project exists and title is non-empty.
    - update_task: Update task status. Validate task exists.
    - get_project_status: Return project details + all tasks + summary counts.
    - search_tasks: Search tasks by keyword (LIKE query). Join with project name.

    Every response should be a JSON string.
    Errors should be: {"error": "specific message"}
    """
    db = get_db(db_path)
    try:
        if name == "create_project":
            pass  # TODO
        elif name == "list_projects":
            pass  # TODO
        elif name == "add_task":
            pass  # TODO
        elif name == "update_task":
            pass  # TODO
        elif name == "get_project_status":
            pass  # TODO
        elif name == "search_tasks":
            pass  # TODO
        else:
            return json.dumps({"error": f"Unknown tool: {name}"})
    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        db.close()


if __name__ == "__main__":
    db_path = "test_projects.db"
    Path(db_path).unlink(missing_ok=True)
    print(handle_tool("create_project", {"name": "Demo", "description": "Test"}, db_path))
    print(handle_tool("add_task", {"project_name": "Demo", "title": "Build server"}, db_path))
    print(handle_tool("get_project_status", {"project_name": "Demo"}, db_path))
    Path(db_path).unlink(missing_ok=True)
