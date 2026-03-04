#!/usr/bin/env python3
"""
Week 4: Test Cases for CrewAI Multi-Agent TODO System
Tests agent definitions, task dependencies, and config loading.
Does NOT require API keys - tests structure only.
"""

import unittest
import os
import sys
import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestAgentDefinitions(unittest.TestCase):
    """Test that agents are correctly defined"""

    def test_three_agents_defined(self):
        """System should have exactly 3 agents"""
        from crewai_orchestrator import task_manager, storage_agent, validator_agent
        agents = [task_manager, storage_agent, validator_agent]
        self.assertEqual(len(agents), 3)

    def test_agent_roles_distinct(self):
        """Each agent should have a unique role"""
        from crewai_orchestrator import task_manager, storage_agent, validator_agent
        roles = {
            task_manager.role,
            storage_agent.role,
            validator_agent.role
        }
        self.assertEqual(len(roles), 3)

    def test_agent_goals_not_empty(self):
        """Each agent must have a non-empty goal"""
        from crewai_orchestrator import task_manager, storage_agent, validator_agent
        for agent in [task_manager, storage_agent, validator_agent]:
            self.assertTrue(len(agent.goal) > 0, f"{agent.role} has empty goal")

    def test_agent_backstories_not_empty(self):
        """Each agent must have a non-empty backstory"""
        from crewai_orchestrator import task_manager, storage_agent, validator_agent
        for agent in [task_manager, storage_agent, validator_agent]:
            self.assertTrue(len(agent.backstory) > 0, f"{agent.role} has empty backstory")


class TestTaskDefinitions(unittest.TestCase):
    """Test task dependency chain"""

    def test_three_tasks_defined(self):
        """System should have exactly 3 tasks"""
        from crewai_orchestrator import parse_task, validate_task, execute_task
        tasks = [parse_task, validate_task, execute_task]
        self.assertEqual(len(tasks), 3)

    def test_validate_depends_on_parse(self):
        """validate_task should depend on parse_task"""
        from crewai_orchestrator import parse_task, validate_task
        self.assertIn(parse_task, validate_task.context)

    def test_execute_depends_on_validate(self):
        """execute_task should depend on validate_task"""
        from crewai_orchestrator import validate_task, execute_task
        self.assertIn(validate_task, execute_task.context)

    def test_parse_has_no_dependencies(self):
        """parse_task should have no context dependencies"""
        from crewai_orchestrator import parse_task
        # parse_task.context should be empty or None
        self.assertTrue(
            parse_task.context is None or len(parse_task.context) == 0,
            "parse_task should not depend on other tasks"
        )


class TestCrewComposition(unittest.TestCase):
    """Test crew is properly assembled"""

    def test_crew_has_all_agents(self):
        from crewai_orchestrator import crew
        self.assertEqual(len(crew.agents), 3)

    def test_crew_has_all_tasks(self):
        from crewai_orchestrator import crew
        self.assertEqual(len(crew.tasks), 3)

    def test_crew_verbose_enabled(self):
        from crewai_orchestrator import crew
        self.assertTrue(crew.verbose)


class TestYAMLConfig(unittest.TestCase):
    """Test YAML configuration file"""

    def setUp(self):
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agents_config.yaml")
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def test_three_agents_in_config(self):
        self.assertEqual(len(self.config["agents"]), 3)

    def test_three_tasks_in_config(self):
        self.assertEqual(len(self.config["tasks"]), 3)

    def test_agent_keys_present(self):
        for name, agent in self.config["agents"].items():
            self.assertIn("role", agent, f"Agent '{name}' missing 'role'")
            self.assertIn("goal", agent, f"Agent '{name}' missing 'goal'")
            self.assertIn("backstory", agent, f"Agent '{name}' missing 'backstory'")

    def test_task_dependencies_valid(self):
        """All depends_on references should point to existing tasks"""
        task_names = set(self.config["tasks"].keys())
        for name, task in self.config["tasks"].items():
            deps = task.get("depends_on", [])
            for dep in deps:
                self.assertIn(dep, task_names, f"Task '{name}' depends on unknown task '{dep}'")

    def test_no_circular_dependencies(self):
        """Dependencies should form a DAG (no cycles)"""
        tasks = self.config["tasks"]
        visited = set()
        path = set()

        def has_cycle(task_name):
            if task_name in path:
                return True
            if task_name in visited:
                return False
            visited.add(task_name)
            path.add(task_name)
            for dep in tasks[task_name].get("depends_on", []):
                if has_cycle(dep):
                    return True
            path.discard(task_name)
            return False

        for task_name in tasks:
            self.assertFalse(has_cycle(task_name), f"Circular dependency detected involving '{task_name}'")


if __name__ == "__main__":
    unittest.main()
