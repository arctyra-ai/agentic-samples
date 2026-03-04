#!/usr/bin/env python3
"""
Week 3: Test Cases for Error Handling & Logging
Tests StructuredLogger, safe_tool_call retries, and agent self-correction.
No API calls required.
"""

import unittest
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "week2"))

from logging_config import StructuredLogger
from agent_with_errors import agent_self_correct


class TestStructuredLogger(unittest.TestCase):
    """Test the StructuredLogger class"""

    def setUp(self):
        self.tmpfile = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmpfile.close()
        self.logger = StructuredLogger(self.tmpfile.name)

    def tearDown(self):
        os.unlink(self.tmpfile.name)

    def test_log_event_creates_entry(self):
        self.logger.log_event("TEST_EVENT", {"key": "value"})
        self.assertEqual(len(self.logger.logs), 1)
        self.assertEqual(self.logger.logs[0]["event_type"], "TEST_EVENT")

    def test_log_event_has_timestamp(self):
        self.logger.log_event("TEST", {"data": 1})
        self.assertIn("timestamp", self.logger.logs[0])

    def test_logs_persist_to_disk(self):
        self.logger.log_event("PERSIST_TEST", {"data": "check"})
        # Reload from disk
        reloaded = StructuredLogger(self.tmpfile.name)
        self.assertEqual(len(reloaded.logs), 1)
        self.assertEqual(reloaded.logs[0]["data"]["data"], "check")

    def test_get_trace_all(self):
        self.logger.log_event("A", {})
        self.logger.log_event("B", {})
        self.logger.log_event("C", {})
        trace = self.logger.get_trace()
        self.assertEqual(len(trace), 3)

    def test_get_trace_last_n(self):
        for i in range(10):
            self.logger.log_event(f"EVENT_{i}", {"index": i})
        trace = self.logger.get_trace(last_n=3)
        self.assertEqual(len(trace), 3)
        self.assertEqual(trace[0]["data"]["index"], 7)

    def test_clear(self):
        self.logger.log_event("TO_CLEAR", {})
        self.logger.clear()
        self.assertEqual(len(self.logger.logs), 0)
        # Verify disk is also cleared
        reloaded = StructuredLogger(self.tmpfile.name)
        self.assertEqual(len(reloaded.logs), 0)

    def test_multiple_event_types(self):
        self.logger.log_event("USER_INPUT", {"message": "hello"})
        self.logger.log_event("TOOL_CALL", {"tool": "add_task"})
        self.logger.log_event("ERROR", {"type": "NOT_FOUND"})
        types = [e["event_type"] for e in self.logger.logs]
        self.assertEqual(types, ["USER_INPUT", "TOOL_CALL", "ERROR"])


class TestAgentSelfCorrect(unittest.TestCase):
    """Test self-correction logic"""

    def test_no_correction_needed(self):
        result = agent_self_correct("Task 1 has been added.", "Task created: Task 1")
        self.assertEqual(result, "Task 1 has been added.")

    def test_correct_false_completion(self):
        result = agent_self_correct(
            "Task 5 has been completed successfully.",
            "Error: Task 5 not found"
        )
        self.assertIn("does not exist", result.lower())

    def test_correct_false_deletion(self):
        result = agent_self_correct(
            "I've deleted task 3 for you.",
            "Error: Task 3 not found"
        )
        self.assertIn("could not be found", result.lower())

    def test_correct_false_addition(self):
        result = agent_self_correct(
            "I've added that task for you.",
            "Error: Task 'Buy milk' already exists"
        )
        self.assertIn("already exists", result.lower())

    def test_none_response_passthrough(self):
        result = agent_self_correct(None, "some result")
        self.assertIsNone(result)

    def test_empty_response_passthrough(self):
        result = agent_self_correct("", "some result")
        self.assertEqual(result, "")


class TestSafeToolCall(unittest.TestCase):
    """Test safe_tool_call retry and error handling logic"""

    def setUp(self):
        self.tmpfile = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmpfile.close()
        # Patch the module-level memory
        import agent_with_errors as agent
        from memory import TaskMemory
        agent.memory = TaskMemory(self.tmpfile.name)
        # Reset logger
        agent.logger.logs = []
        self.agent = agent

    def tearDown(self):
        os.unlink(self.tmpfile.name)

    def test_successful_call_logged(self):
        result = self.agent.safe_tool_call("add_task", {"title": "Log test"})
        self.assertIn("Log test", result)
        # Check that TOOL_CALL and TOOL_RESULT events exist
        event_types = [e["event_type"] for e in self.agent.logger.logs]
        self.assertIn("TOOL_CALL", event_types)
        self.assertIn("TOOL_RESULT", event_types)

    def test_not_found_error_handled(self):
        result = self.agent.safe_tool_call("mark_complete", {"task_id": 999})
        self.assertIn("Error", result)

    def test_duplicate_error_handled(self):
        self.agent.safe_tool_call("add_task", {"title": "Dup task"})
        result = self.agent.safe_tool_call("add_task", {"title": "Dup task"})
        self.assertIn("already exists", result.lower())

    def test_unknown_tool_handled(self):
        result = self.agent.safe_tool_call("nonexistent_tool", {})
        # Should not crash
        self.assertIsInstance(result, str)

    def test_stats_call(self):
        result = self.agent.safe_tool_call("get_stats", {})
        stats = json.loads(result)
        self.assertIn("total", stats)


if __name__ == "__main__":
    unittest.main()
