#!/usr/bin/env python3
"""
Week 1: Test Cases for Single Agent TODO Assistant
Tests tool definitions, task CRUD operations, and agent loop basics.
No API calls required - tests local logic only.
"""

import unittest
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestTaskStorage(unittest.TestCase):
    """Test in-memory task storage operations"""

    def setUp(self):
        """Reset task storage before each test"""
        # Import and reset the module-level state
        import single_agent_todo as agent
        agent.tasks = []
        agent.next_id = 1
        self.agent = agent

    def test_add_task(self):
        """add_task creates a task and returns confirmation"""
        result = self.agent.add_task("Buy groceries", "Milk, eggs, bread")
        self.assertIn("Buy groceries", result)
        self.assertEqual(len(self.agent.tasks), 1)
        self.assertEqual(self.agent.tasks[0]["title"], "Buy groceries")
        self.assertEqual(self.agent.tasks[0]["description"], "Milk, eggs, bread")
        self.assertFalse(self.agent.tasks[0]["completed"])

    def test_add_task_no_description(self):
        """add_task works with title only"""
        result = self.agent.add_task("Simple task")
        self.assertIn("Simple task", result)
        self.assertEqual(self.agent.tasks[0]["description"], "")

    def test_add_multiple_tasks(self):
        """Multiple tasks get sequential IDs"""
        self.agent.add_task("Task 1")
        self.agent.add_task("Task 2")
        self.agent.add_task("Task 3")
        self.assertEqual(len(self.agent.tasks), 3)
        self.assertEqual(self.agent.tasks[0]["id"], 1)
        self.assertEqual(self.agent.tasks[1]["id"], 2)
        self.assertEqual(self.agent.tasks[2]["id"], 3)

    def test_list_tasks_empty(self):
        """list_tasks returns message when no tasks exist"""
        result = self.agent.list_tasks()
        self.assertIn("No tasks", result)

    def test_list_tasks_with_items(self):
        """list_tasks returns formatted task list"""
        self.agent.add_task("Task A")
        self.agent.add_task("Task B")
        result = self.agent.list_tasks()
        self.assertIn("Task A", result)
        self.assertIn("Task B", result)

    def test_mark_complete(self):
        """mark_complete sets task completed flag"""
        self.agent.add_task("Test task")
        result = self.agent.mark_complete(1)
        self.assertIn("complete", result.lower())
        self.assertTrue(self.agent.tasks[0]["completed"])

    def test_mark_complete_nonexistent(self):
        """mark_complete handles missing task ID"""
        result = self.agent.mark_complete(999)
        self.assertIn("not found", result.lower())

    def test_delete_task(self):
        """delete_task removes task from list"""
        self.agent.add_task("To delete")
        self.assertEqual(len(self.agent.tasks), 1)
        result = self.agent.delete_task(1)
        self.assertIn("deleted", result.lower())
        self.assertEqual(len(self.agent.tasks), 0)

    def test_delete_nonexistent(self):
        """delete_task on missing ID does not crash"""
        result = self.agent.delete_task(999)
        # Should not raise an exception
        self.assertIsInstance(result, str)


class TestToolDefinitions(unittest.TestCase):
    """Test that tool definitions are well-formed"""

    def setUp(self):
        from tools import TOOLS
        self.tools = TOOLS

    def test_four_tools_defined(self):
        """Exactly 4 tools should be defined"""
        self.assertEqual(len(self.tools), 4)

    def test_tool_names(self):
        """All expected tool names present"""
        names = {t["function"]["name"] for t in self.tools}
        expected = {"add_task", "list_tasks", "mark_complete", "delete_task"}
        self.assertEqual(names, expected)

    def test_tool_schema_valid(self):
        """Each tool has type, function, name, description, parameters"""
        for tool in self.tools:
            self.assertEqual(tool["type"], "function")
            func = tool["function"]
            self.assertIn("name", func)
            self.assertIn("description", func)
            self.assertIn("parameters", func)
            self.assertEqual(func["parameters"]["type"], "object")

    def test_add_task_requires_title(self):
        """add_task tool requires 'title' parameter"""
        add_tool = next(t for t in self.tools if t["function"]["name"] == "add_task")
        self.assertIn("title", add_tool["function"]["parameters"]["required"])


class TestProcessToolCall(unittest.TestCase):
    """Test the process_tool_call dispatcher"""

    def setUp(self):
        import single_agent_todo as agent
        agent.tasks = []
        agent.next_id = 1
        self.agent = agent

    def test_dispatch_add_task(self):
        """process_tool_call routes to add_task"""
        result = self.agent.process_tool_call("add_task", {"title": "Test"})
        self.assertIn("Test", result)

    def test_dispatch_list_tasks(self):
        """process_tool_call routes to list_tasks"""
        result = self.agent.process_tool_call("list_tasks", {})
        self.assertIn("No tasks", result)

    def test_dispatch_unknown_tool(self):
        """process_tool_call handles unknown tool name"""
        result = self.agent.process_tool_call("nonexistent_tool", {})
        self.assertIn("Unknown tool", result)

    def test_roundtrip_add_list_complete_delete(self):
        """Full CRUD cycle through process_tool_call"""
        # Add
        self.agent.process_tool_call("add_task", {"title": "Roundtrip task", "description": "Testing"})
        self.assertEqual(len(self.agent.tasks), 1)

        # List
        result = self.agent.process_tool_call("list_tasks", {})
        self.assertIn("Roundtrip task", result)

        # Complete
        self.agent.process_tool_call("mark_complete", {"task_id": 1})
        self.assertTrue(self.agent.tasks[0]["completed"])

        # Delete
        self.agent.process_tool_call("delete_task", {"task_id": 1})
        self.assertEqual(len(self.agent.tasks), 0)


if __name__ == "__main__":
    unittest.main()
