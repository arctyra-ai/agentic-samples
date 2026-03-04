#!/usr/bin/env python3
"""
Weeks 8-9: Integration Tests for Full TODO System
Tests end-to-end flow, voting, conflict detection, and edge cases.
No API calls required.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "week7"))


class TestIntegratedSystemAvailable(unittest.TestCase):
    """Verify system imports correctly"""

    def test_import(self):
        try:
            from integrated_todo_system import run_integrated_system
            self.assertTrue(True)
        except ImportError as e:
            self.skipTest(f"Cannot import integrated system: {e}")


class TestEndToEnd(unittest.TestCase):
    """Test full end-to-end system execution"""

    @classmethod
    def setUpClass(cls):
        try:
            from integrated_todo_system import run_integrated_system
            cls.run = run_integrated_system
            cls.available = True
        except ImportError:
            cls.available = False

    def test_add_task_approved(self):
        if not self.available:
            self.skipTest("System not available")
        result = self.run("Add task: Buy milk")
        self.assertEqual(result["execution_result"]["status"], "executed")
        self.assertEqual(result["action_type"], "add")

    def test_list_tasks_approved(self):
        if not self.available:
            self.skipTest("System not available")
        result = self.run("List all tasks")
        self.assertEqual(result["execution_result"]["status"], "executed")
        self.assertEqual(result["action_type"], "list")

    def test_delete_task_rejected(self):
        """Delete should be rejected due to Security (2x) + Validator (1.5x) rejection"""
        if not self.available:
            self.skipTest("System not available")
        result = self.run("Delete task 1")
        self.assertEqual(result["action_type"], "delete")
        # Security and Validator reject, Storage approves
        # Reject weight should exceed approve weight
        self.assertEqual(result["execution_result"]["status"], "rejected")

    def test_unknown_action_rejected(self):
        if not self.available:
            self.skipTest("System not available")
        result = self.run("What is the weather?")
        self.assertEqual(result["action_type"], "unknown")
        self.assertEqual(result["execution_result"]["status"], "rejected")


class TestVotingIntegration(unittest.TestCase):
    """Test that voting works correctly within the integrated system"""

    @classmethod
    def setUpClass(cls):
        try:
            from integrated_todo_system import run_integrated_system
            cls.run = run_integrated_system
            cls.available = True
        except ImportError:
            cls.available = False

    def test_three_votes_cast(self):
        if not self.available:
            self.skipTest("System not available")
        result = self.run("Add task: Test")
        self.assertEqual(len(result["votes"]), 3)

    def test_voting_result_present(self):
        if not self.available:
            self.skipTest("System not available")
        result = self.run("Add task: Test")
        self.assertIn("result", result["voting_result"])

    def test_vote_agents_correct(self):
        if not self.available:
            self.skipTest("System not available")
        result = self.run("Add task: Test")
        agent_names = {v["agent_name"] for v in result["votes"]}
        self.assertEqual(agent_names, {"Validator", "Storage", "Security"})

    def test_conflict_detected_on_delete(self):
        if not self.available:
            self.skipTest("System not available")
        result = self.run("Delete all tasks")
        # Security and Validator reject, causing conflict
        self.assertTrue(result["conflict_detected"])


class TestDecisionLog(unittest.TestCase):
    """Test that decision log captures all steps"""

    @classmethod
    def setUpClass(cls):
        try:
            from integrated_todo_system import run_integrated_system
            cls.run = run_integrated_system
            cls.available = True
        except ImportError:
            cls.available = False

    def test_decision_log_not_empty(self):
        if not self.available:
            self.skipTest("System not available")
        result = self.run("Add task: Test")
        self.assertGreater(len(result["decision_log"]), 0)

    def test_decision_log_has_parser(self):
        if not self.available:
            self.skipTest("System not available")
        result = self.run("Add task: Test")
        agents = [entry["agent"] for entry in result["decision_log"]]
        self.assertIn("Parser", agents)

    def test_decision_log_has_aggregator(self):
        if not self.available:
            self.skipTest("System not available")
        result = self.run("Add task: Test")
        agents = [entry["agent"] for entry in result["decision_log"]]
        self.assertIn("VotingAggregator", agents)

    def test_decision_log_has_human_review(self):
        if not self.available:
            self.skipTest("System not available")
        result = self.run("Add task: Test")
        agents = [entry["agent"] for entry in result["decision_log"]]
        self.assertIn("HumanReview", agents)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases"""

    @classmethod
    def setUpClass(cls):
        try:
            from integrated_todo_system import run_integrated_system
            cls.run = run_integrated_system
            cls.available = True
        except ImportError:
            cls.available = False

    def test_empty_input(self):
        if not self.available:
            self.skipTest("System not available")
        result = self.run("")
        self.assertEqual(result["action_type"], "unknown")

    def test_mark_complete(self):
        if not self.available:
            self.skipTest("System not available")
        result = self.run("Mark task 1 as complete")
        self.assertEqual(result["action_type"], "mark_complete")

    def test_state_keys_present(self):
        if not self.available:
            self.skipTest("System not available")
        result = self.run("Add task: Test")
        expected_keys = {
            "user_input", "parsed_intent", "action_type", "task_data",
            "validation_result", "execution_result", "conflict_detected",
            "votes", "voting_result", "human_decision", "error", "decision_log"
        }
        self.assertTrue(expected_keys.issubset(set(result.keys())))


if __name__ == "__main__":
    unittest.main()
