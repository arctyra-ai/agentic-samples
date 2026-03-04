#!/usr/bin/env python3
"""
Week 6: Test Cases for LangGraph State Graphs
Tests state schema, node functions, conditional routing, and graph execution.
No API calls required - tests local logic only.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from state_schemas import TodoState, create_initial_state


class TestStateSchema(unittest.TestCase):
    """Test TodoState TypedDict and initial state factory"""

    def test_create_initial_state(self):
        state = create_initial_state("Add a task")
        self.assertEqual(state["user_input"], "Add a task")
        self.assertEqual(state["parsed_intent"], "")
        self.assertEqual(state["action_type"], "")
        self.assertEqual(state["task_data"], {})
        self.assertEqual(state["validation_result"], {})
        self.assertEqual(state["execution_result"], {})
        self.assertEqual(state["error"], "")

    def test_all_keys_present(self):
        state = create_initial_state("test")
        expected_keys = {"user_input", "parsed_intent", "action_type",
                        "task_data", "validation_result", "execution_result", "error"}
        self.assertEqual(set(state.keys()), expected_keys)


class TestNodeFunctions(unittest.TestCase):
    """Test individual node functions from langgraph_system"""

    def setUp(self):
        """Import node functions - these should work without API keys"""
        try:
            from langgraph_system import parse_input, validate_action, execute_action, handle_error
            self.parse_input = parse_input
            self.validate_action = validate_action
            self.execute_action = execute_action
            self.handle_error = handle_error
            self.available = True
        except ImportError:
            self.available = False

    def test_parse_add(self):
        if not self.available:
            self.skipTest("langgraph_system not importable")
        state = create_initial_state("Add a task called Buy milk")
        result = self.parse_input(state)
        self.assertEqual(result["action_type"], "add")
        self.assertIn("add", result["parsed_intent"].lower())

    def test_parse_list(self):
        if not self.available:
            self.skipTest("langgraph_system not importable")
        state = create_initial_state("Show all my tasks")
        result = self.parse_input(state)
        self.assertEqual(result["action_type"], "list")

    def test_parse_delete(self):
        if not self.available:
            self.skipTest("langgraph_system not importable")
        state = create_initial_state("Delete task 3")
        result = self.parse_input(state)
        self.assertEqual(result["action_type"], "delete")

    def test_parse_unknown(self):
        if not self.available:
            self.skipTest("langgraph_system not importable")
        state = create_initial_state("What is the weather?")
        result = self.parse_input(state)
        self.assertEqual(result["action_type"], "unknown")

    def test_validate_valid_action(self):
        if not self.available:
            self.skipTest("langgraph_system not importable")
        state = create_initial_state("Add task")
        state["action_type"] = "add"
        result = self.validate_action(state)
        self.assertTrue(result["validation_result"]["is_valid"])

    def test_validate_unknown_action(self):
        if not self.available:
            self.skipTest("langgraph_system not importable")
        state = create_initial_state("bad input")
        state["action_type"] = "unknown"
        result = self.validate_action(state)
        self.assertFalse(result["validation_result"]["is_valid"])

    def test_validate_delete_has_warning(self):
        if not self.available:
            self.skipTest("langgraph_system not importable")
        state = create_initial_state("Delete task")
        state["action_type"] = "delete"
        result = self.validate_action(state)
        self.assertTrue(len(result["validation_result"]["warnings"]) > 0)

    def test_handle_error(self):
        if not self.available:
            self.skipTest("langgraph_system not importable")
        state = create_initial_state("bad")
        result = self.handle_error(state)
        self.assertIn("fail", result["error"].lower())


class TestConditionalRouting(unittest.TestCase):
    """Test the should_proceed conditional edge function"""

    def setUp(self):
        try:
            from langgraph_system import should_proceed
            self.should_proceed = should_proceed
            self.available = True
        except ImportError:
            self.available = False

    def test_routes_to_execute_when_valid(self):
        if not self.available:
            self.skipTest("langgraph_system not importable")
        state = create_initial_state("test")
        state["validation_result"] = {"is_valid": True}
        self.assertEqual(self.should_proceed(state), "execute")

    def test_routes_to_error_when_invalid(self):
        if not self.available:
            self.skipTest("langgraph_system not importable")
        state = create_initial_state("test")
        state["validation_result"] = {"is_valid": False}
        self.assertEqual(self.should_proceed(state), "error_handling")

    def test_routes_to_error_when_no_validation(self):
        if not self.available:
            self.skipTest("langgraph_system not importable")
        state = create_initial_state("test")
        state["validation_result"] = {}
        self.assertEqual(self.should_proceed(state), "error_handling")


class TestGraphCompilation(unittest.TestCase):
    """Test that the graph compiles and can be invoked"""

    def test_graph_compiles(self):
        try:
            from langgraph_system import graph
            self.assertIsNotNone(graph)
        except ImportError:
            self.skipTest("langgraph not installed")

    def test_graph_has_expected_nodes(self):
        try:
            from langgraph_system import graph
            node_names = set(graph.get_graph().nodes.keys())
            expected = {"parse", "validate", "execute", "error_handler"}
            # LangGraph may add __start__ and __end__ nodes
            self.assertTrue(expected.issubset(node_names),
                          f"Missing nodes: {expected - node_names}")
        except ImportError:
            self.skipTest("langgraph not installed")


if __name__ == "__main__":
    unittest.main()
