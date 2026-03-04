#!/usr/bin/env python3
"""
Weeks 10-12: Integration Tests for Software Dev Agent System
Tests full workflow, voting, dependencies, and output structure.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "week7"))


class TestSoftwareDevSystem(unittest.TestCase):
    """Test the full software dev agent system"""

    @classmethod
    def setUpClass(cls):
        try:
            from software_dev_agents import run_software_dev_system
            cls.run = run_software_dev_system
            cls.available = True
        except ImportError as e:
            cls.available = False
            cls.import_error = str(e)

    def test_full_workflow(self):
        """Test complete workflow produces all components"""
        if not self.available:
            self.skipTest(f"Import failed: {self.import_error}")
        result = self.run("Build a task app")

        self.assertIsNotNone(result["database_design"])
        self.assertTrue(len(result["database_design"]) > 0)
        self.assertIsNotNone(result["backend_code"])
        self.assertTrue(len(result["backend_code"]) > 0)
        self.assertIsNotNone(result["frontend_code"])
        self.assertTrue(len(result["frontend_code"]) > 0)
        self.assertGreater(len(result["decision_log"]), 0)

    def test_voting_occurs(self):
        """Test that votes are cast during workflow"""
        if not self.available:
            self.skipTest(f"Import failed: {self.import_error}")
        result = self.run("Build a task app")

        self.assertGreater(len(result["votes"]), 0)
        self.assertIn(result["voting_result"]["result"],
                     ["APPROVED", "REJECTED", "TIE"])

    def test_dependencies_respected(self):
        """Test task dependency ordering"""
        if not self.available:
            self.skipTest(f"Import failed: {self.import_error}")
        result = self.run("Build a task app")

        tasks = result["orchestrator_tasks"]

        # Backend should depend on Database
        backend = next(t for t in tasks if t["name"] == "backend_code")
        self.assertIn(1, backend["depends_on"])

        # Frontend should depend on Backend
        frontend = next(t for t in tasks if t["name"] == "frontend_code")
        self.assertIn(2, frontend["depends_on"])

        # Security should depend on Backend and Frontend
        security = next(t for t in tasks if t["name"] == "security_audit")
        self.assertIn(2, security["depends_on"])
        self.assertIn(3, security["depends_on"])

    def test_security_audit_present(self):
        """Test security audit is generated"""
        if not self.available:
            self.skipTest(f"Import failed: {self.import_error}")
        result = self.run("Build a task app")

        audit = result["security_audit"]
        self.assertIn("warnings", audit)
        self.assertIn("recommendations", audit)

    def test_qa_report_present(self):
        """Test QA report is generated"""
        if not self.available:
            self.skipTest(f"Import failed: {self.import_error}")
        result = self.run("Build a task app")

        report = result["qa_report"]
        self.assertIn("test_coverage", report)
        self.assertIn("edge_cases", report)

    def test_final_output_complete(self):
        """Test final output contains all components"""
        if not self.available:
            self.skipTest(f"Import failed: {self.import_error}")
        result = self.run("Build a task app")

        final = result["final_output"]
        self.assertIn("database", final)
        self.assertIn("backend", final)
        self.assertIn("frontend", final)
        self.assertIn("security_audit", final)
        self.assertIn("qa_report", final)
        self.assertIn("approval", final)

    def test_decision_log_has_all_agents(self):
        """Test that every agent appears in the decision log"""
        if not self.available:
            self.skipTest(f"Import failed: {self.import_error}")
        result = self.run("Build a task app")

        agents = {entry["agent"] for entry in result["decision_log"]}
        expected = {"Orchestrator", "Database", "Backend", "Frontend",
                   "Security", "QA", "VotingAggregator"}
        self.assertTrue(expected.issubset(agents),
                       f"Missing agents in log: {expected - agents}")

    def test_no_circular_dependencies(self):
        """Verify dependency graph is a DAG"""
        if not self.available:
            self.skipTest(f"Import failed: {self.import_error}")
        result = self.run("Build a task app")

        tasks = {t["id"]: t for t in result["orchestrator_tasks"]}
        visited = set()
        path = set()

        def has_cycle(task_id):
            if task_id in path:
                return True
            if task_id in visited:
                return False
            visited.add(task_id)
            path.add(task_id)
            for dep_id in tasks[task_id].get("depends_on", []):
                if has_cycle(dep_id):
                    return True
            path.discard(task_id)
            return False

        for task_id in tasks:
            self.assertFalse(has_cycle(task_id),
                           f"Circular dependency found at task {task_id}")


if __name__ == "__main__":
    unittest.main()
