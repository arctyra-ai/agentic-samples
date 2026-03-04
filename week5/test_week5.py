#!/usr/bin/env python3
"""
Week 5: Test Cases for Conflict Detection System
Tests ConflictDetector, AgentOpinion, and resolution logic.
No API calls required.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conflict_detection import (
    ConflictDetector, AgentOpinion, ConflictType, ConflictResolution
)


class TestConflictDetection(unittest.TestCase):
    """Test conflict detection logic"""

    def setUp(self):
        self.detector = ConflictDetector()

    def test_no_conflict_when_unanimous_approve(self):
        opinions = [
            AgentOpinion("Agent1", "approve", "Looks good", 0.9),
            AgentOpinion("Agent2", "approve", "All clear", 0.8),
        ]
        self.assertFalse(self.detector.detect_conflict(opinions))

    def test_no_conflict_when_unanimous_reject(self):
        opinions = [
            AgentOpinion("Agent1", "reject", "Bad input", 0.9),
            AgentOpinion("Agent2", "reject", "Invalid", 0.8),
        ]
        self.assertFalse(self.detector.detect_conflict(opinions))

    def test_conflict_when_mixed_positions(self):
        opinions = [
            AgentOpinion("Storage", "approve", "Ready to execute", 0.9),
            AgentOpinion("Validator", "reject", "Destructive operation", 0.95),
        ]
        self.assertTrue(self.detector.detect_conflict(opinions))

    def test_conflict_with_concern(self):
        opinions = [
            AgentOpinion("Storage", "approve", "Ready", 0.9),
            AgentOpinion("Validator", "concern", "Needs review", 0.7),
        ]
        self.assertTrue(self.detector.detect_conflict(opinions))

    def test_three_way_disagreement(self):
        opinions = [
            AgentOpinion("A", "approve", "OK", 0.8),
            AgentOpinion("B", "reject", "No", 0.9),
            AgentOpinion("C", "concern", "Maybe", 0.5),
        ]
        self.assertTrue(self.detector.detect_conflict(opinions))


class TestConflictLogging(unittest.TestCase):
    """Test conflict logging"""

    def setUp(self):
        self.detector = ConflictDetector()

    def test_log_stores_conflict(self):
        opinions = [
            AgentOpinion("A", "approve", "OK", 0.8),
            AgentOpinion("B", "reject", "No", 0.9),
        ]
        self.detector.log_conflict(ConflictType.DATA_CONFLICT, opinions)
        conflicts = self.detector.get_conflicts()
        self.assertEqual(len(conflicts), 1)

    def test_log_contains_type(self):
        opinions = [AgentOpinion("A", "approve", "OK", 0.8)]
        self.detector.log_conflict(ConflictType.SECURITY_ISSUE, opinions)
        self.assertEqual(self.detector.conflicts[0]["type"], "security_issue")

    def test_log_contains_opinions(self):
        opinions = [
            AgentOpinion("Storage", "approve", "Ready", 0.9),
            AgentOpinion("Validator", "reject", "Bad", 0.95),
        ]
        self.detector.log_conflict(ConflictType.VALIDATION_REJECTED, opinions)
        logged_opinions = self.detector.conflicts[0]["opinions"]
        self.assertEqual(len(logged_opinions), 2)
        self.assertEqual(logged_opinions[0]["agent_name"], "Storage")

    def test_log_contains_timestamp(self):
        opinions = [AgentOpinion("A", "approve", "OK", 0.8)]
        self.detector.log_conflict(ConflictType.DATA_CONFLICT, opinions)
        self.assertIn("timestamp", self.detector.conflicts[0])

    def test_multiple_conflicts_logged(self):
        for i in range(5):
            opinions = [AgentOpinion(f"Agent{i}", "approve", "OK", 0.8)]
            self.detector.log_conflict(ConflictType.DATA_CONFLICT, opinions)
        self.assertEqual(len(self.detector.get_conflicts()), 5)


class TestConflictResolution(unittest.TestCase):
    """Test simple resolution logic"""

    def setUp(self):
        self.detector = ConflictDetector()

    def test_majority_approve(self):
        opinions = [
            AgentOpinion("A", "approve", "OK", 0.7),
            AgentOpinion("B", "approve", "OK", 0.6),
            AgentOpinion("C", "reject", "No", 0.5),
        ]
        resolution = self.detector.resolve_simple(opinions)
        self.assertEqual(resolution.action, "proceed")
        self.assertFalse(resolution.requires_human_review)

    def test_high_confidence_rejection_escalates(self):
        opinions = [
            AgentOpinion("A", "approve", "OK", 0.7),
            AgentOpinion("B", "reject", "Security risk", 0.95),
        ]
        resolution = self.detector.resolve_simple(opinions)
        self.assertEqual(resolution.action, "escalate")
        self.assertTrue(resolution.requires_human_review)

    def test_high_confidence_concern_escalates(self):
        opinions = [
            AgentOpinion("A", "approve", "OK", 0.8),
            AgentOpinion("B", "concern", "Destructive", 0.92),
        ]
        resolution = self.detector.resolve_simple(opinions)
        self.assertTrue(resolution.requires_human_review)

    def test_no_majority_escalates(self):
        opinions = [
            AgentOpinion("A", "approve", "OK", 0.5),
            AgentOpinion("B", "reject", "No", 0.5),
        ]
        resolution = self.detector.resolve_simple(opinions)
        self.assertTrue(resolution.requires_human_review)

    def test_all_approve_no_escalation(self):
        opinions = [
            AgentOpinion("A", "approve", "OK", 0.8),
            AgentOpinion("B", "approve", "Fine", 0.7),
            AgentOpinion("C", "approve", "Proceed", 0.6),
        ]
        resolution = self.detector.resolve_simple(opinions)
        self.assertEqual(resolution.action, "proceed")
        self.assertFalse(resolution.requires_human_review)


class TestAgentOpinion(unittest.TestCase):
    """Test AgentOpinion dataclass"""

    def test_fields(self):
        op = AgentOpinion("TestAgent", "approve", "Looks good", 0.85)
        self.assertEqual(op.agent_name, "TestAgent")
        self.assertEqual(op.position, "approve")
        self.assertEqual(op.reasoning, "Looks good")
        self.assertEqual(op.confidence, 0.85)


class TestConflictType(unittest.TestCase):
    """Test ConflictType enum"""

    def test_all_types_exist(self):
        types = [ct.value for ct in ConflictType]
        self.assertIn("validation_rejected", types)
        self.assertIn("data_conflict", types)
        self.assertIn("performance_concern", types)
        self.assertIn("security_issue", types)


if __name__ == "__main__":
    unittest.main()
