"""Tests for Week 5: Custom MCP Server."""

import json
import pytest
import tempfile
from pathlib import Path
from project_mcp_server import handle_tool, get_db, TOOL_DEFINITIONS


@pytest.fixture
def db_path():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    yield path
    Path(path).unlink(missing_ok=True)


class TestToolDefinitions:
    def test_six_tools_defined(self):
        assert len(TOOL_DEFINITIONS) == 6

    def test_all_have_schemas(self):
        for tool in TOOL_DEFINITIONS:
            assert tool.name
            assert tool.description
            assert tool.inputSchema


class TestCreateProject:
    def test_creates_project(self, db_path):
        result = json.loads(handle_tool("create_project", {"name": "Test Project"}, db_path))
        assert result["status"] == "created"

    def test_rejects_duplicate(self, db_path):
        handle_tool("create_project", {"name": "Dup"}, db_path)
        result = json.loads(handle_tool("create_project", {"name": "Dup"}, db_path))
        assert "error" in result
        assert "already exists" in result["error"]

    def test_rejects_empty_name(self, db_path):
        result = json.loads(handle_tool("create_project", {"name": "  "}, db_path))
        assert "error" in result


class TestAddTask:
    def test_adds_task(self, db_path):
        handle_tool("create_project", {"name": "P1"}, db_path)
        result = json.loads(handle_tool("add_task", {
            "project_name": "P1", "title": "Task 1", "priority": "high"
        }, db_path))
        assert result["status"] == "added"
        assert result["priority"] == "high"

    def test_rejects_nonexistent_project(self, db_path):
        result = json.loads(handle_tool("add_task", {
            "project_name": "NoProject", "title": "Task"
        }, db_path))
        assert "error" in result

    def test_rejects_empty_title(self, db_path):
        handle_tool("create_project", {"name": "P1"}, db_path)
        result = json.loads(handle_tool("add_task", {
            "project_name": "P1", "title": ""
        }, db_path))
        assert "error" in result


class TestUpdateTask:
    def test_updates_status(self, db_path):
        handle_tool("create_project", {"name": "P1"}, db_path)
        handle_tool("add_task", {"project_name": "P1", "title": "T1"}, db_path)
        result = json.loads(handle_tool("update_task", {"task_id": 1, "status": "done"}, db_path))
        assert result["new_status"] == "done"

    def test_rejects_nonexistent_task(self, db_path):
        result = json.loads(handle_tool("update_task", {"task_id": 999, "status": "done"}, db_path))
        assert "error" in result


class TestGetProjectStatus:
    def test_returns_summary(self, db_path):
        handle_tool("create_project", {"name": "P1"}, db_path)
        handle_tool("add_task", {"project_name": "P1", "title": "T1"}, db_path)
        handle_tool("add_task", {"project_name": "P1", "title": "T2"}, db_path)
        handle_tool("update_task", {"task_id": 1, "status": "done"}, db_path)

        result = json.loads(handle_tool("get_project_status", {"project_name": "P1"}, db_path))
        assert result["summary"]["total"] == 2
        assert result["summary"]["done"] == 1
        assert result["summary"]["todo"] == 1


class TestSearchTasks:
    def test_finds_matching_tasks(self, db_path):
        handle_tool("create_project", {"name": "P1"}, db_path)
        handle_tool("add_task", {"project_name": "P1", "title": "Build API"}, db_path)
        handle_tool("add_task", {"project_name": "P1", "title": "Write docs"}, db_path)

        result = json.loads(handle_tool("search_tasks", {"query": "API"}, db_path))
        assert result["count"] == 1
        assert "API" in result["results"][0]["title"]

    def test_no_matches(self, db_path):
        handle_tool("create_project", {"name": "P1"}, db_path)
        result = json.loads(handle_tool("search_tasks", {"query": "ZZZZZ"}, db_path))
        assert result["count"] == 0


class TestPersistence:
    def test_data_survives_reconnect(self, db_path):
        handle_tool("create_project", {"name": "Persistent"}, db_path)
        handle_tool("add_task", {"project_name": "Persistent", "title": "Survives"}, db_path)

        # Simulate server restart by creating new connection
        result = json.loads(handle_tool("get_project_status", {"project_name": "Persistent"}, db_path))
        assert result["summary"]["total"] == 1
