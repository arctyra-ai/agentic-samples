"""Tests for Week 2: Research Assistant Agent."""

import json
import pytest
import tempfile
from pathlib import Path
from research_agent import (
    execute_tool, TOOLS, SessionMemory, ResearchReport, Source, ReportSection,
)


class TestToolDefinitions:
    def test_six_tools_defined(self):
        assert len(TOOLS) == 6

    def test_all_tools_have_descriptions(self):
        for tool in TOOLS:
            assert len(tool["description"]) > 20, f"{tool['name']} needs a better description"

    def test_tool_names_unique(self):
        names = [t["name"] for t in TOOLS]
        assert len(names) == len(set(names))


class TestToolExecution:
    def test_web_search_returns_results(self):
        result = json.loads(execute_tool("web_search", {"query": "test query"}))
        assert "results" in result
        assert len(result["results"]) > 0

    def test_read_url_returns_content(self):
        result = json.loads(execute_tool("read_url", {"url": "https://example.com"}))
        assert "content" in result

    def test_extract_key_points_returns_list(self):
        result = json.loads(execute_tool("extract_key_points", {"text": "Some text here"}))
        assert "key_points" in result
        assert len(result["key_points"]) > 0

    def test_compare_sources_returns_analysis(self):
        result = json.loads(execute_tool("compare_sources", {"findings": [{"a": 1}]}))
        assert "agreements" in result
        assert "contradictions" in result

    def test_generate_outline_returns_sections(self):
        result = json.loads(execute_tool("generate_outline", {
            "question": "test", "findings": ["finding 1"]
        }))
        assert "sections" in result
        assert len(result["sections"]) >= 2

    def test_write_section_returns_content(self):
        result = json.loads(execute_tool("write_section", {
            "heading": "Test", "key_points": ["Point 1"]
        }))
        assert "content" in result

    def test_unknown_tool_error(self):
        result = json.loads(execute_tool("fake_tool", {}))
        assert "error" in result


class TestSessionMemory:
    def test_creates_new_session(self):
        with tempfile.TemporaryDirectory() as d:
            session = SessionMemory("test_session", sessions_dir=d)
            assert session.state["session_id"] == "test_session"
            assert session.state["messages"] == []

    def test_persists_to_disk(self):
        with tempfile.TemporaryDirectory() as d:
            session = SessionMemory("persist_test", sessions_dir=d)
            session.add_finding({"key": "value"})

            # Reload from disk
            session2 = SessionMemory("persist_test", sessions_dir=d)
            assert len(session2.state["findings"]) == 1
            assert session2.state["findings"][0]["key"] == "value"

    def test_add_source(self):
        with tempfile.TemporaryDirectory() as d:
            session = SessionMemory("source_test", sessions_dir=d)
            session.add_source({"title": "Test", "url": "http://test.com"})
            assert len(session.state["sources"]) == 1

    def test_add_report(self):
        with tempfile.TemporaryDirectory() as d:
            session = SessionMemory("report_test", sessions_dir=d)
            session.add_report({"question": "test?"})
            assert len(session.state["reports"]) == 1


class TestStructuredOutput:
    def test_research_report_validates(self):
        report = ResearchReport(
            question="What is MCP?",
            sources=[Source(title="Article", url="http://a.com", snippet="About MCP", relevance=0.9)],
            sections=[ReportSection(heading="Overview", content="MCP is...", source_indices=[0])],
            confidence=0.85,
            follow_up_questions=["How does MCP compare to REST?"],
        )
        assert report.confidence == 0.85
        assert len(report.sources) == 1

    def test_report_rejects_invalid_confidence(self):
        with pytest.raises(Exception):
            ResearchReport(
                question="test", sources=[], sections=[],
                confidence=1.5,  # out of range
            )

    def test_report_serializes_to_json(self):
        report = ResearchReport(
            question="test", sources=[], sections=[],
            confidence=0.5, follow_up_questions=[],
        )
        data = report.model_dump()
        assert isinstance(json.dumps(data), str)
