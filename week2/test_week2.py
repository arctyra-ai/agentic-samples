#!/usr/bin/env python3
"""
Week 2: Test Cases for Multi-Tool Agent with Persistent Memory
Tests TaskMemory persistence, validation, search, stats, and ConversationMemory.
No API calls required.
"""

import unittest
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory import TaskMemory, ConversationMemory


class TestTaskMemoryBasicOps(unittest.TestCase):
    """Test basic CRUD operations on TaskMemory"""

    def setUp(self):
        self.tmpfile = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmpfile.close()
        self.memory = TaskMemory(self.tmpfile.name)

    def tearDown(self):
        os.unlink(self.tmpfile.name)

    def test_add_task(self):
        task = self.memory.add_task("Buy milk", "2% milk", priority="high")
        self.assertEqual(task["title"], "Buy milk")
        self.assertEqual(task["priority"], "high")
        self.assertFalse(task["completed"])
        self.assertIn("created_at", task)

    def test_add_task_default_priority(self):
        task = self.memory.add_task("Default priority task")
        self.assertEqual(task["priority"], "medium")

    def test_list_tasks_all(self):
        self.memory.add_task("Task A", priority="low")
        self.memory.add_task("Task B", priority="high")
        tasks = self.memory.list_tasks(filter_by="all")
        self.assertEqual(len(tasks), 2)

    def test_list_tasks_filter_completed(self):
        self.memory.add_task("Task A")
        self.memory.add_task("Task B")
        self.memory.mark_complete(1)
        completed = self.memory.list_tasks(filter_by="completed")
        pending = self.memory.list_tasks(filter_by="pending")
        self.assertEqual(len(completed), 1)
        self.assertEqual(len(pending), 1)

    def test_list_tasks_sort_priority(self):
        self.memory.add_task("Low task", priority="low")
        self.memory.add_task("High task", priority="high")
        self.memory.add_task("Med task", priority="medium")
        tasks = self.memory.list_tasks(sort_by="priority")
        self.assertEqual(tasks[0]["priority"], "high")
        self.assertEqual(tasks[2]["priority"], "low")

    def test_mark_complete(self):
        self.memory.add_task("Complete me")
        task = self.memory.mark_complete(1)
        self.assertTrue(task["completed"])

    def test_mark_complete_nonexistent(self):
        with self.assertRaises(ValueError):
            self.memory.mark_complete(999)

    def test_delete_task(self):
        self.memory.add_task("Delete me")
        deleted = self.memory.delete_task(1)
        self.assertEqual(deleted["title"], "Delete me")
        self.assertEqual(len(self.memory.tasks), 0)

    def test_delete_nonexistent(self):
        with self.assertRaises(ValueError):
            self.memory.delete_task(999)

    def test_update_task(self):
        self.memory.add_task("Update me", priority="low")
        updated = self.memory.update_task(1, priority="high")
        self.assertEqual(updated["priority"], "high")

    def test_update_invalid_field(self):
        self.memory.add_task("Test")
        with self.assertRaises(ValueError):
            self.memory.update_task(1, invalid_field="bad")


class TestTaskMemoryValidation(unittest.TestCase):
    """Test input validation"""

    def setUp(self):
        self.tmpfile = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmpfile.close()
        self.memory = TaskMemory(self.tmpfile.name)

    def tearDown(self):
        os.unlink(self.tmpfile.name)

    def test_empty_title_rejected(self):
        with self.assertRaises(ValueError):
            self.memory.add_task("")

    def test_none_title_rejected(self):
        with self.assertRaises(ValueError):
            self.memory.add_task(None)

    def test_long_title_rejected(self):
        with self.assertRaises(ValueError):
            self.memory.add_task("x" * 201)

    def test_duplicate_title_rejected(self):
        self.memory.add_task("Unique task")
        with self.assertRaises(ValueError):
            self.memory.add_task("Unique task")

    def test_duplicate_case_insensitive(self):
        self.memory.add_task("My Task")
        with self.assertRaises(ValueError):
            self.memory.add_task("my task")


class TestTaskMemoryPersistence(unittest.TestCase):
    """Test that tasks persist across instances"""

    def setUp(self):
        self.tmpfile = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmpfile.close()

    def tearDown(self):
        os.unlink(self.tmpfile.name)

    def test_tasks_persist_after_reload(self):
        mem1 = TaskMemory(self.tmpfile.name)
        mem1.add_task("Persistent task")
        mem1.add_task("Another task")

        mem2 = TaskMemory(self.tmpfile.name)
        self.assertEqual(len(mem2.tasks), 2)
        self.assertEqual(mem2.tasks[0]["title"], "Persistent task")

    def test_next_id_persists(self):
        mem1 = TaskMemory(self.tmpfile.name)
        mem1.add_task("Task 1")
        mem1.add_task("Task 2")

        mem2 = TaskMemory(self.tmpfile.name)
        task = mem2.add_task("Task 3")
        self.assertEqual(task["id"], 3)


class TestTaskMemorySearch(unittest.TestCase):
    """Test search functionality"""

    def setUp(self):
        self.tmpfile = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmpfile.close()
        self.memory = TaskMemory(self.tmpfile.name)
        self.memory.add_task("Buy groceries", "Milk and eggs")
        self.memory.add_task("Buy birthday gift", "For Mom")
        self.memory.add_task("Clean house", "Kitchen and bathroom")

    def tearDown(self):
        os.unlink(self.tmpfile.name)

    def test_search_by_title(self):
        results = self.memory.search_tasks("buy")
        self.assertEqual(len(results), 2)

    def test_search_by_description(self):
        results = self.memory.search_tasks("milk")
        self.assertEqual(len(results), 1)

    def test_search_no_results(self):
        results = self.memory.search_tasks("nonexistent")
        self.assertEqual(len(results), 0)

    def test_search_case_insensitive(self):
        results = self.memory.search_tasks("BUY")
        self.assertEqual(len(results), 2)


class TestTaskMemoryStats(unittest.TestCase):
    """Test statistics generation"""

    def setUp(self):
        self.tmpfile = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmpfile.close()
        self.memory = TaskMemory(self.tmpfile.name)

    def tearDown(self):
        os.unlink(self.tmpfile.name)

    def test_empty_stats(self):
        stats = self.memory.get_stats()
        self.assertEqual(stats["total"], 0)
        self.assertEqual(stats["completed"], 0)
        self.assertEqual(stats["pending"], 0)
        self.assertEqual(stats["high_priority"], 0)

    def test_stats_after_operations(self):
        self.memory.add_task("Task 1", priority="high")
        self.memory.add_task("Task 2", priority="low")
        self.memory.add_task("Task 3", priority="high")
        self.memory.mark_complete(1)

        stats = self.memory.get_stats()
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["completed"], 1)
        self.assertEqual(stats["pending"], 2)
        self.assertEqual(stats["high_priority"], 1)  # Only pending high-priority


class TestConversationMemory(unittest.TestCase):
    """Test conversation history management"""

    def setUp(self):
        self.conv = ConversationMemory()

    def test_add_and_retrieve(self):
        self.conv.add_message("user", "Hello")
        self.conv.add_message("assistant", "Hi there")
        history = self.conv.get_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[1]["content"], "Hi there")

    def test_get_last_n(self):
        for i in range(10):
            self.conv.add_message("user", f"Message {i}")
        history = self.conv.get_history(last_n=3)
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]["content"], "Message 7")

    def test_no_timestamps_in_output(self):
        self.conv.add_message("user", "Test")
        history = self.conv.get_history()
        self.assertNotIn("timestamp", history[0])

    def test_clear(self):
        self.conv.add_message("user", "Test")
        self.conv.clear()
        self.assertEqual(len(self.conv.get_history()), 0)


class TestProcessToolCall(unittest.TestCase):
    """Test process_tool_call dispatcher from multi_tool_agent"""

    def setUp(self):
        self.tmpfile = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmpfile.close()
        # Patch the module-level memory object
        import multi_tool_agent as agent
        agent.memory = TaskMemory(self.tmpfile.name)
        self.agent = agent

    def tearDown(self):
        os.unlink(self.tmpfile.name)

    def test_dispatch_add(self):
        result = self.agent.process_tool_call("add_task", {"title": "Test"})
        self.assertIn("Test", result)

    def test_dispatch_stats(self):
        result = self.agent.process_tool_call("get_stats", {})
        stats = json.loads(result)
        self.assertEqual(stats["total"], 0)

    def test_dispatch_search(self):
        self.agent.process_tool_call("add_task", {"title": "Searchable item"})
        result = self.agent.process_tool_call("search_tasks", {"keyword": "search"})
        self.assertIn("Searchable item", result)

    def test_dispatch_unknown(self):
        result = self.agent.process_tool_call("fake_tool", {})
        self.assertIn("Unknown tool", result)

    def test_error_returns_message(self):
        result = self.agent.process_tool_call("mark_complete", {"task_id": 999})
        self.assertIn("Error", result)


if __name__ == "__main__":
    unittest.main()
