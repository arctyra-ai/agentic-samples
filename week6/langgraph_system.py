#!/usr/bin/env python3
"""
Week 6: LangGraph State Graphs
Complete TODO system using LangGraph with conditional edges and state management
"""

import json
import os
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

load_dotenv()

# ============================================================================
# PART 1: Define State Schema
# ============================================================================

class TodoState(TypedDict):
    """Shared state flowing through the graph"""
    user_input: str              # Original user request
    parsed_intent: str           # What action user wants (add, list, delete, etc.)
    action_type: str             # Classified action type
    task_data: dict              # Data needed to execute action
    validation_result: dict      # Result of validation
    execution_result: dict       # Result of execution
    error: str                   # Any error message
    decision_log: list           # Trace of decisions made

# ============================================================================
# PART 2: Task Storage (persistent)
# ============================================================================

tasks = []
next_task_id = 1

def add_task(title, description=""):
    """Add task to storage"""
    global next_task_id
    task = {
        "id": next_task_id,
        "title": title,
        "description": description,
        "completed": False
    }
    tasks.append(task)
    next_task_id += 1
    return task

def list_tasks():
    """Get all tasks"""
    return tasks

def mark_complete(task_id):
    """Mark task as complete"""
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = True
            return task
    return None

def delete_task(task_id):
    """Delete task"""
    global tasks
    original_len = len(tasks)
    tasks = [t for t in tasks if t["id"] != task_id]
    return len(tasks) < original_len

# ============================================================================
# PART 3: Graph Nodes (Processing Functions)
# ============================================================================

def parse_input_node(state: TodoState) -> TodoState:
    """Node 1: Parse user input to understand intent"""
    user_input = state["user_input"].lower()
    
    # Simple intent classification
    if any(word in user_input for word in ["add", "create", "new"]):
        action_type = "add"
        parsed_intent = "Creating new task"
    elif any(word in user_input for word in ["list", "show", "all", "tasks"]):
        action_type = "list"
        parsed_intent = "Listing all tasks"
    elif any(word in user_input for word in ["delete", "remove", "rm"]):
        action_type = "delete"
        parsed_intent = "Deleting task"
    elif any(word in user_input for word in ["complete", "done", "finish", "check"]):
        action_type = "complete"
        parsed_intent = "Marking task complete"
    else:
        action_type = "unknown"
        parsed_intent = "Unknown action"
    
    new_state = {
        **state,
        "parsed_intent": parsed_intent,
        "action_type": action_type
    }
    
    new_state["decision_log"].append({
        "node": "parse_input",
        "parsed_intent": parsed_intent,
        "action_type": action_type
    })
    
    return new_state

def validate_action_node(state: TodoState) -> TodoState:
    """Node 2: Validate the proposed action"""
    action_type = state.get("action_type", "")
    user_input = state.get("user_input", "")
    
    validation_result = {
        "is_valid": True,
        "issues": [],
        "warnings": []
    }
    
    # Validation rules
    if action_type == "unknown":
        validation_result["is_valid"] = False
        validation_result["issues"].append("Could not understand the request")
    
    elif action_type == "add":
        # Need to extract task title
        if "task" in user_input or "add" in user_input:
            # Extract title (simple extraction)
            parts = user_input.split(":")
            if len(parts) > 1:
                state["task_data"] = {"title": parts[1].strip()}
            else:
                state["task_data"] = {"title": "New Task"}
        else:
            validation_result["is_valid"] = False
            validation_result["issues"].append("Please specify task title")
    
    elif action_type == "delete":
        validation_result["warnings"].append("This will permanently delete the task")
        # Try to extract task ID
        parts = user_input.split()
        for part in parts:
            if part.isdigit():
                state["task_data"] = {"task_id": int(part)}
                break
    
    elif action_type == "complete":
        # Try to extract task ID
        parts = user_input.split()
        for part in parts:
            if part.isdigit():
                state["task_data"] = {"task_id": int(part)}
                break
        if "task_id" not in state.get("task_data", {}):
            validation_result["is_valid"] = False
            validation_result["issues"].append("Please specify task ID")
    
    new_state = {
        **state,
        "validation_result": validation_result
    }
    
    new_state["decision_log"].append({
        "node": "validate_action",
        "is_valid": validation_result["is_valid"],
        "issues": validation_result["issues"]
    })
    
    return new_state

def execute_action_node(state: TodoState) -> TodoState:
    """Node 3: Execute the validated action"""
    action_type = state.get("action_type", "")
    task_data = state.get("task_data", {})
    
    try:
        if action_type == "add":
            task = add_task(
                title=task_data.get("title", "New Task"),
                description=task_data.get("description", "")
            )
            execution_result = {
                "success": True,
                "message": f"Task added: {task['title']}",
                "task": task
            }
        
        elif action_type == "list":
            all_tasks = list_tasks()
            execution_result = {
                "success": True,
                "message": f"Found {len(all_tasks)} task(s)",
                "tasks": all_tasks
            }
        
        elif action_type == "delete":
            task_id = task_data.get("task_id")
            if task_id and delete_task(task_id):
                execution_result = {
                    "success": True,
                    "message": f"Task {task_id} deleted"
                }
            else:
                execution_result = {
                    "success": False,
                    "message": f"Task {task_id} not found"
                }
        
        elif action_type == "complete":
            task_id = task_data.get("task_id")
            task = mark_complete(task_id) if task_id else None
            if task:
                execution_result = {
                    "success": True,
                    "message": f"Marked task {task_id} complete",
                    "task": task
                }
            else:
                execution_result = {
                    "success": False,
                    "message": f"Task {task_id} not found"
                }
        
        else:
            execution_result = {
                "success": False,
                "message": "Unknown action"
            }
    
    except Exception as e:
        execution_result = {
            "success": False,
            "message": f"Error: {str(e)}"
        }
    
    new_state = {
        **state,
        "execution_result": execution_result
    }
    
    new_state["decision_log"].append({
        "node": "execute_action",
        "success": execution_result["success"],
        "message": execution_result.get("message", "")
    })
    
    return new_state

def error_handler_node(state: TodoState) -> TodoState:
    """Node 4: Handle validation errors"""
    validation = state.get("validation_result", {})
    
    error_message = "Validation failed: " + ", ".join(validation.get("issues", []))
    
    new_state = {
        **state,
        "error": error_message,
        "execution_result": {
            "success": False,
            "message": error_message
        }
    }
    
    new_state["decision_log"].append({
        "node": "error_handler",
        "error": error_message
    })
    
    return new_state

# ============================================================================
# PART 4: Conditional Routing
# ============================================================================

def should_proceed(state: TodoState) -> str:
    """Decide whether to proceed to execution or handle errors"""
    is_valid = state.get("validation_result", {}).get("is_valid", False)
    
    if is_valid:
        return "execute"  # Go to execute_action node
    else:
        return "error"    # Go to error_handler node

# ============================================================================
# PART 5: Build Graph
# ============================================================================

def build_graph():
    """Construct the LangGraph state graph"""
    
    # Create state graph builder
    builder = StateGraph(TodoState)
    
    # Add nodes
    builder.add_node("parse", parse_input_node)
    builder.add_node("validate", validate_action_node)
    builder.add_node("execute", execute_action_node)
    builder.add_node("error", error_handler_node)
    
    # Add edges (connections between nodes)
    # Entry point
    builder.add_edge(START, "parse")
    
    # Parse → Validate
    builder.add_edge("parse", "validate")
    
    # Validate → (Execute or Error) based on conditional
    builder.add_conditional_edges(
        "validate",
        should_proceed,
        {
            "execute": "execute",
            "error": "error"
        }
    )
    
    # Both paths end
    builder.add_edge("execute", END)
    builder.add_edge("error", END)
    
    # Compile graph
    return builder.compile()

# ============================================================================
# PART 6: Run Graph
# ============================================================================

def run_langgraph_todo(user_input: str, graph):
    """Execute LangGraph workflow"""
    
    initial_state = {
        "user_input": user_input,
        "parsed_intent": "",
        "action_type": "",
        "task_data": {},
        "validation_result": {},
        "execution_result": {},
        "error": "",
        "decision_log": []
    }
    
    # Invoke graph (execute all nodes in sequence)
    final_state = graph.invoke(initial_state)
    
    return final_state

# ============================================================================
# PART 7: Visualization
# ============================================================================

def print_graph_structure(graph):
    """Print ASCII representation of graph"""
    print("\n" + "="*60)
    print("Graph Structure:")
    print("="*60)
    
    graph_str = graph.get_graph().draw_ascii()
    print(graph_str)

# ============================================================================
# PART 8: Demo & Tests
# ============================================================================

def run_demo():
    """Run demo with example inputs"""
    
    # Build the graph once
    graph = build_graph()
    
    # Visualize
    print_graph_structure(graph)
    
    # Test cases
    test_inputs = [
        "Add a task: Buy milk",
        "List all tasks",
        "Mark task 1 complete",
        "Delete task 2",
        "Show me what I have to do",
    ]
    
    print("\n" + "="*60)
    print("Running Test Cases")
    print("="*60)
    
    for user_input in test_inputs:
        print(f"\n📝 Input: {user_input}")
        
        result = run_langgraph_todo(user_input, graph)
        
        print(f"   Parsed Intent: {result['parsed_intent']}")
        print(f"   Action Type: {result['action_type']}")
        print(f"   Valid: {result['validation_result'].get('is_valid', False)}")
        
        if result["execution_result"].get("success"):
            print(f"   ✓ {result['execution_result']['message']}")
        else:
            if result["error"]:
                print(f"   ✗ {result['error']}")
            else:
                print(f"   ✗ {result['execution_result']['message']}")
        
        # Show decision log
        print(f"   Decision Log:")
        for decision in result["decision_log"]:
            print(f"     - {decision}")

def run_interactive():
    """Interactive mode"""
    
    graph = build_graph()
    
    print("\n" + "="*60)
    print("LangGraph TODO Assistant")
    print("="*60)
    print("\nTry: 'add task: Buy milk', 'list', 'complete 1', 'delete 1'")
    print("Type 'tasks' to see all, 'exit' to quit\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        
        if user_input.lower() == "tasks":
            print("📋 Tasks:")
            for task in tasks:
                status = "✓" if task["completed"] else "○"
                print(f"  {status} [{task['id']}] {task['title']}")
            print()
            continue
        
        if not user_input:
            continue
        
        # Run graph
        result = run_langgraph_todo(user_input, graph)
        
        # Print result
        if result["execution_result"].get("success"):
            print(f"Agent: {result['execution_result']['message']}\n")
        else:
            print(f"Agent: {result['error'] or result['execution_result']['message']}\n")

# ============================================================================
# PART 9: Main
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        run_demo()
    else:
        run_interactive()
