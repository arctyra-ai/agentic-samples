"""Tests for Week 7: Multi-Agent Code Review."""

import json
import pytest
from code_review_agents import (
    create_review_state, _parse_findings, _merge_usage, ReviewState,
)


class TestState:
    def test_creates_review_state(self):
        state = create_review_state("print('hi')", "test.py")
        assert state["code"] == "print('hi')"
        assert state["filename"] == "test.py"
        assert state["analyzer_findings"] == []
        assert state["security_findings"] == []
        assert state["improvement_suggestions"] == []

    def test_initial_token_usage(self):
        state = create_review_state("x = 1")
        assert state["token_usage"]["calls"] == 0


class TestParseFindings:
    def test_parses_json_array(self):
        text = 'Here are findings: [{"severity": "high", "description": "bug"}]'
        findings = _parse_findings(text)
        assert len(findings) == 1
        assert findings[0]["severity"] == "high"

    def test_handles_empty_array(self):
        findings = _parse_findings("[]")
        assert findings == []

    def test_handles_unparseable(self):
        findings = _parse_findings("No JSON here")
        assert len(findings) == 1
        assert findings[0].get("parse_error") is True

    def test_parses_multiple_findings(self):
        text = '[{"line": 1, "type": "bug"}, {"line": 5, "type": "smell"}]'
        findings = _parse_findings(text)
        assert len(findings) == 2


class TestMergeUsage:
    def test_merges_token_counts(self):
        existing = {"total_input": 100, "total_output": 50, "calls": 1}
        new = {"total_input_tokens": 200, "total_output_tokens": 100, "total_calls": 2}
        merged = _merge_usage(existing, new)
        assert merged["total_input"] == 300
        assert merged["total_output"] == 150
        assert merged["calls"] == 3

    def test_handles_empty_existing(self):
        merged = _merge_usage({}, {"total_input_tokens": 10, "total_output_tokens": 5, "total_calls": 1})
        assert merged["total_input"] == 10
