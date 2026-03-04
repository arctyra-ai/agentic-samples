#!/usr/bin/env python3
"""
Week 1: Single Agent TODO Assistant
Complete working example with tool calling and conversation memory
"""

import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ============================================================================
# PART 1: Define Tools
# ============================================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Add a new task to the TODO list",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title (required)"},
                    "description": {"type": "string", "description": "Task description (optional)"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mark_complete",
            "description": "Mark a task as complete",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "Task ID to mark complete"}
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "Task ID to delete"}
                },
                "required": ["task_id"]
            }
        }
    }
]

# ============================================================================
# PART 2: In-Memory Task Storage
# ============================================================================

tasks = []
next_id = 1

def add_task(title, description=""):
    """Add a new task"""
    global next_id
    if not title or not isinstance(title, str):
        return {"error": "Title must be non-empty string"}
    
    task = {
        "id": next_id,
        "title": title,
        "description": description,
        "completed": False
    }
    tasks.append(task)
    next_id += 1
    return {"success": True, "task": task}

def list_tasks():
    """List all tasks"""
    if not tasks:
        return {"tasks": [], "message": "No tasks yet"}
    
    result = []
    for task in tasks:
        status = "✓" if task["completed"] else "○"
        result.append({
            "id": task["id"],
            "title": task["title"],
            "description": task["description"],
            "completed": task["completed"],
            "display": f"{status} [{task['id']}] {task['title']}: {task['description']}"
        })
    return {"tasks": result}

def mark_complete(task_id):
    """Mark task as complete"""
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = True
            return {"success": True, "message": f"Task {task_id} marked complete", "task": task}
    return {"error": f"Task {task_id} not found"}

def delete_task(task_id):
    """Delete a task"""
    global tasks
    original_count = len(tasks)
    tasks = [t for t in tasks if t["id"] != task_id]
    
    if len(tasks) < original_count:
        return {"success": True, "message": f"Task {task_id} deleted"}
    else:
        return {"error": f"Task {task_id} not found"}

def process_tool_call(tool_name, tool_input):
    """Execute a tool and return result"""
    print(f"  → Calling {tool_name}")
    
    try:
        if tool_name == "add_task":
            result = add_task(tool_input.get("title"), tool_input.get("description", ""))
        elif tool_name == "list_tasks":
            result = list_tasks()
        elif tool_name == "mark_complete":
            result = mark_complete(tool_input.get("task_id"))
        elif tool_name == "delete_task":
            result = delete_task(tool_input.get("task_id"))
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
        
        return json.dumps(result)
    
    except Exception as e:
        return json.dumps({"error": str(e)})

# ============================================================================
# PART 3: Single-Turn Agent (Test)
# ============================================================================

def single_turn_agent(user_message):
    """
    Single-turn agent loop:
    1. Send user message to OpenAI with tools
    2. If tools are called, execute them
    3. Return final response
    """
    print(f"\n📝 User: {user_message}")
    
    messages = [
        {"role": "user", "content": user_message}
    ]
    
    # Call OpenAI with tools
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto"
    )
    
    # Check if tools were called
    assistant_message = response.choice[0].message
    
    if assistant_message.tool_calls:
        print(f"🤖 Agent decided to use tools:")
        
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            tool_input = json.loads(tool_call.function.arguments)
            
            # Execute tool
            result = process_tool_call(tool_name, tool_input)
            print(f"  ✓ Result: {result[:100]}...")  # Truncate for readability
        
        return True  # Tool was called
    else:
        # Agent responded with text
        print(f"🤖 Agent: {assistant_message.content}")
        return False

# ============================================================================
# PART 4: Multi-Turn Agent (Interactive)
# ============================================================================

def multi_turn_agent():
    """
    Multi-turn agent that maintains conversation history.
    Type 'exit' to quit, 'tasks' to list tasks, 'trace' to see decisions.
    """
    messages = []
    
    print("\n" + "="*60)
    print("  TODO Agent - Multi-Turn Conversation")
    print("="*60)
    print("\nTry these commands:")
    print("  'Add a task: Buy milk'")
    print("  'List all my tasks'")
    print("  'Mark task 1 complete'")
    print("  'Delete task 2'")
    print("  'tasks' - Show all tasks")
    print("  'exit' - Quit")
    print("-"*60 + "\n")
    
    while True:
        user_input = input("You: ").strip()
        
        # Check for special commands
        if user_input.lower() == "exit":
            print("Goodbye! 👋")
            break
        
        if user_input.lower() == "tasks":
            print(f"\n📋 Current Tasks:")
            task_list = list_tasks()
            if task_list["tasks"]:
                for task_info in task_list["tasks"]:
                    print(f"  {task_info['display']}")
            else:
                print("  No tasks yet")
            print()
            continue
        
        if not user_input:
            continue
        
        # Add to conversation history
        messages.append({"role": "user", "content": user_input})
        
        # Call OpenAI with conversation history and tools
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )
        
        assistant_message = response.choice[0].message
        
        # Add assistant's message to history
        messages.append({
            "role": "assistant",
            "content": assistant_message.content or ""
        })
        
        # Process tool calls
        if assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_input = json.loads(tool_call.function.arguments)
                
                result = process_tool_call(tool_name, tool_input)
                
                # Add tool result to conversation
                messages.append({
                    "role": "user",
                    "content": f"Tool result: {result}"
                })
                
                print(f"  ✓ {tool_name} executed")
        
        # Print assistant's response
        if assistant_message.content:
            print(f"Agent: {assistant_message.content}\n")

# ============================================================================
# PART 5: Tests
# ============================================================================

def run_tests():
    """Run single-turn tests"""
    print("\n" + "="*60)
    print("  Running Tests")
    print("="*60)
    
    test_cases = [
        ("Add a task called 'Buy groceries' with description 'Milk, eggs, bread'", True),
        ("List all my tasks", True),
        ("Mark task 1 as complete", True),
        ("Show me task 1", False),  # No tool for this
        ("Delete task 1", True),
        ("How many tasks do I have?", False),  # No direct tool
    ]
    
    for message, expects_tool_call in test_cases:
        had_tool_call = single_turn_agent(message)
        status = "✓ PASS" if had_tool_call == expects_tool_call else "✗ FAIL"
        print(f"{status}\n")

# ============================================================================
# PART 6: Main
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run tests
        run_tests()
    else:
        # Start interactive multi-turn agent
        multi_turn_agent()
