"""Tests for Week 1: File Operations Agent.

Tests tool implementations locally (no API calls required)
and agent behavior (requires ANTHROPIC_API_KEY).
"""

import json
import os
import tempfile
import pytest
from pathlib import Path

from agent import execute_tool, TOOLS, run_agent


# --- Tool Implementation Tests (no API key needed) ---

@pytest.fixture
def temp_dir():
    """Create a temporary directory with test files and set sandbox."""
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "hello.py").write_text("# TODO: fix this\\nprint('hello')\\n")
        (Path(d) / "readme.md").write_text("# My Project\\nThis is a test project.\\n")
        (Path(d) / "data.csv").write_text("name,age\\nAlice,30\\nBob,25\\n")
        (Path(d) / "sub").mkdir()
        (Path(d) / "sub" / "nested.py").write_text("# nested file\\nimport os\\n")
        # Set sandbox so tool functions can access this temp directory
        from agent import set_sandbox
        set_sandbox(d)
        yield d


class TestListFiles:
    def test_lists_all_files(self, temp_dir):
        result = json.loads(execute_tool("list_files", {"directory": temp_dir}))
        assert result["count"] == 3  # excludes subdirectory contents
        names = [f["name"] for f in result["files"]]
        assert "hello.py" in names
        assert "readme.md" in names

    def test_filters_by_pattern(self, temp_dir):
        result = json.loads(execute_tool("list_files", {"directory": temp_dir, "pattern": "*.py"}))
        assert result["count"] == 1
        assert result["files"][0]["name"] == "hello.py"

    def test_nonexistent_directory(self):
        result = json.loads(execute_tool("list_files", {"directory": "/nonexistent/path"}))
        assert "error" in result


class TestReadFile:
    def test_reads_content(self, temp_dir):
        result = execute_tool("read_file", {"filepath": f"{temp_dir}/readme.md"})
        assert "My Project" in result

    def test_nonexistent_file(self):
        result = json.loads(execute_tool("read_file", {"filepath": "/no/such/file.txt"}))
        assert "error" in result


class TestSearchInFiles:
    def test_finds_pattern(self, temp_dir):
        result = json.loads(execute_tool("search_in_files", {
            "directory": temp_dir, "pattern": "TODO"
        }))
        assert result["total_matches"] >= 1
        assert "hello.py" in result["matches"][0]["file"]

    def test_case_insensitive(self, temp_dir):
        result = json.loads(execute_tool("search_in_files", {
            "directory": temp_dir, "pattern": "todo"
        }))
        assert result["total_matches"] >= 1

    def test_no_matches(self, temp_dir):
        result = json.loads(execute_tool("search_in_files", {
            "directory": temp_dir, "pattern": "ZZZZNOTFOUND"
        }))
        assert result["total_matches"] == 0

    def test_searches_recursively(self, temp_dir):
        result = json.loads(execute_tool("search_in_files", {
            "directory": temp_dir, "pattern": "nested"
        }))
        assert result["total_matches"] >= 1


class TestGetFileInfo:
    def test_returns_metadata(self, temp_dir):
        result = json.loads(execute_tool("get_file_info", {"filepath": f"{temp_dir}/hello.py"}))
        assert result["size_bytes"] > 0
        assert result["line_count"] >= 1

    def test_nonexistent(self):
        result = json.loads(execute_tool("get_file_info", {"filepath": "/no/file"}))
        assert "error" in result


class TestWriteSummary:
    def test_writes_file(self, temp_dir):
        outpath = f"{temp_dir}/summary.txt"
        result = json.loads(execute_tool("write_summary", {
            "filepath": outpath, "content": "Test summary"
        }))
        assert result["status"] == "written"
        assert Path(outpath).read_text() == "Test summary"


class TestPathSandbox:
    def test_blocks_path_outside_sandbox(self, temp_dir):
        from agent import set_sandbox, _validate_path
        set_sandbox(temp_dir)
        with pytest.raises(ValueError, match="Access denied"):
            _validate_path("/etc/passwd")

    def test_allows_path_inside_sandbox(self, temp_dir):
        import os
        from agent import set_sandbox, _validate_path
        set_sandbox(temp_dir)
        result = _validate_path(f"{temp_dir}/hello.py")
        # Use realpath for comparison (macOS resolves /var -> /private/var)
        assert str(result).startswith(os.path.realpath(temp_dir))

    def test_blocks_traversal_attack(self, temp_dir):
        from agent import set_sandbox, _validate_path
        set_sandbox(temp_dir)
        with pytest.raises(ValueError, match="Access denied"):
            _validate_path(f"{temp_dir}/../../etc/passwd")


class TestToolDefinitions:
    def test_all_tools_have_required_fields(self):
        for tool in TOOLS:
            assert "name" in tool
            assert "description" in tool
            assert "input_schema" in tool
            assert len(tool["description"]) > 10, f"Tool {tool['name']} has too-short description"

    def test_five_tools_defined(self):
        assert len(TOOLS) == 5

    def test_unknown_tool_returns_error(self):
        result = json.loads(execute_tool("nonexistent_tool", {}))
        assert "error" in result


# --- Agent Integration Tests (require API key) ---

@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set"
)
class TestAgentIntegration:
    def test_agent_lists_files(self, temp_dir):
        result = run_agent("List all files in this directory", temp_dir, max_iterations=5)
        assert result["response"]
        assert any(tc["tool"] == "list_files" for tc in result["tool_calls"])

    def test_agent_searches(self, temp_dir):
        result = run_agent("Find files containing TODO", temp_dir, max_iterations=5)
        assert result["response"]
        assert any(tc["tool"] == "search_in_files" for tc in result["tool_calls"])

    def test_agent_tracks_cost(self, temp_dir):
        result = run_agent("How many files are here?", temp_dir, max_iterations=3)
        assert result["usage"]["total_calls"] >= 1
        assert result["usage"]["estimated_cost_usd"] >= 0

    def test_agent_max_iterations(self, temp_dir):
        result = run_agent("List files", temp_dir, max_iterations=1)
        # Should still return something (either result or max-iter message)
        assert result["response"] is not None
