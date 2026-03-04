"""Tests for Week 3: MCP Foundations."""

import json
import os
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_agent import create_mock_router, execute_mock_tool, run_mcp_agent
from shared.mcp_utils import MCPTool, MCPToolRouter, MCPServerConnection


class TestMCPToolRouter:
    def test_creates_empty_router(self):
        router = MCPToolRouter()
        assert router.tool_count() == 0
        assert router.server_count() == 0

    def test_adds_connection(self):
        router = MCPToolRouter()
        tool = MCPTool(name="test", description="A test tool",
                       input_schema={"type": "object"}, server_name="srv")
        conn = MCPServerConnection(name="srv", tools=[tool])
        router.add_connection(conn)
        assert router.server_count() == 1
        assert router.tool_count() == 1

    def test_get_all_tools_anthropic_format(self):
        router = create_mock_router()
        tools = router.get_all_tools()
        assert len(tools) == 5  # 3 filesystem + 2 sqlite
        for tool in tools:
            assert "name" in tool
            assert "__" in tool["name"]  # prefixed
            assert "description" in tool
            assert "input_schema" in tool

    def test_tool_names_are_prefixed(self):
        router = create_mock_router()
        tools = router.get_all_tools()
        names = [t["name"] for t in tools]
        assert "filesystem__read_file" in names
        assert "sqlite__query" in names

    def test_multi_server_tool_count(self):
        router = create_mock_router()
        assert router.server_count() == 2
        assert router.tool_count() == 5


class TestMockToolExecution:
    def test_filesystem_list(self):
        result = json.loads(execute_mock_tool("filesystem__list_directory", {"path": "."}))
        assert "entries" in result
        assert len(result["entries"]) > 0

    def test_filesystem_read(self):
        result = execute_mock_tool("filesystem__read_file", {"path": "test.py"})
        assert "Contents of" in result

    def test_sqlite_list_tables(self):
        result = json.loads(execute_mock_tool("sqlite__list_tables", {}))
        assert "tables" in result

    def test_sqlite_query(self):
        result = json.loads(execute_mock_tool("sqlite__query", {"sql": "SELECT 1"}))
        assert "rows" in result

    def test_unknown_tool(self):
        result = json.loads(execute_mock_tool("unknown__tool", {}))
        assert "error" in result


class TestDynamicToolDiscovery:
    def test_no_hardcoded_tools_in_agent(self):
        """Agent should work with whatever tools the router provides."""
        router = MCPToolRouter()
        tool = MCPTool(name="custom_tool", description="A custom tool",
                       input_schema={"type": "object", "properties": {}},
                       server_name="custom")
        conn = MCPServerConnection(name="custom", tools=[tool])
        router.add_connection(conn)
        tools = router.get_all_tools()
        assert len(tools) == 1
        assert tools[0]["name"] == "custom__custom_tool"

    def test_removing_server_removes_tools(self):
        router = create_mock_router()
        assert router.tool_count() == 5
        del router.connections["sqlite"]
        assert router.tool_count() == 3


@pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY not set")
class TestAgentWithMCP:
    def test_agent_uses_mcp_tools(self):
        router = create_mock_router()
        result = run_mcp_agent("List the files", router, max_iterations=5)
        assert result["response"]
        assert len(result["tools_available"]) == 5

    def test_agent_discovers_tools_dynamically(self):
        router = create_mock_router()
        result = run_mcp_agent("What tables are in the database?", router, max_iterations=5)
        assert any("sqlite" in tc["tool"] for tc in result["tool_calls"])
