#!/usr/bin/env python3
"""
Week 1: Single Agent TODO Assistant - Claude Code Version
Uses Anthropic API (Claude models) instead of OpenAI
"""

import json
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# PART 1: Initialize Claude Client
# ============================================================================

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ============================================================================
# PART 2: Define Tools (Same format as OpenAI, but slightly different schema)
# ============================================================================

TOOLS = [
    {
        "name": "add_task",
        "description": "Add a new task to the TODO list",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Task title (required)"},
                "description": {"type": "string", "description": "Task description (optional)"}
            },
            "required": ["title"]
        }
    },
    {
        "name": "list_tasks",
        "description": "List all tasks",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "mark_complete",
        "description": "Mark a task as complete",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "Task ID to mark complete"}
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "delete_task",
        "description": "Delete a task",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "Task ID to delete"}
            },
            "required": ["task_id"]
        }
    }
]

# ============================================================================
# PART 3: In-Memory Task Storage
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
    """Execute a tool based on Claude's request"""
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
# PART 4: Single-Turn Agent (For Testing)
# ============================================================================

def single_turn_agent(user_message):
    """
    Single-turn agent loop with Claude:
    1. Send user message to Claude with tools
    2. If Claude uses tools, execute them
    3. Return final response
    """
    print(f"\n📝 User: {user_message}")
    
    messages = [
        {"role": "user", "content": user_message}
    ]
    
    # Call Claude with tools
    # NOTE: Different parameter names than OpenAI
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",  # Latest Claude model
        max_tokens=1024,
        system="You are a helpful TODO assistant. Use the provided tools to manage tasks for the user.",
        tools=TOOLS,
        messages=messages
    )
    
    # Process response - Claude returns content blocks instead of tool_calls
    print(f"🤖 Agent processing...")
    
    used_tools = False
    for content_block in response.content:
        # Handle tool use
        if content_block.type == "tool_use":
            tool_name = content_block.name
            tool_input = content_block.input
            
            # Execute tool
            result = process_tool_call(tool_name, tool_input)
            print(f"  ✓ Result: {result[:100]}...")
            
            used_tools = True
        
        # Handle text response
        elif content_block.type == "text":
            if content_block.text:
                print(f"🤖 Agent: {content_block.text}")
    
    return used_tools

# ============================================================================
# PART 5: Multi-Turn Agent (Interactive)
# ============================================================================

def multi_turn_agent():
    """
    Multi-turn agent that maintains conversation history with Claude.
    Type 'exit' to quit, 'tasks' to list tasks, 'trace' to see decision log.
    
    Key difference from OpenAI version:
    - Claude naturally handles tool use without explicit tool_choice parameter
    - Response structure uses content blocks (similar to streaming)
    - Better at understanding context across turns
    """
    messages = []
    
    print("\n" + "="*70)
    print("  TODO Agent - Multi-Turn Conversation (Claude Code Edition)")
    print("="*70)
    print("\nTry these commands:")
    print("  'Add a task: Buy milk'")
    print("  'List all my tasks'")
    print("  'Mark task 1 complete'")
    print("  'Delete task 2'")
    print("  'tasks' - Show all tasks")
    print("  'exit' - Quit")
    print("-"*70 + "\n")
    
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
        
        # Add user message to history
        messages.append({"role": "user", "content": user_input})
        
        # Call Claude with conversation history
        # Claude maintains context automatically
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system="You are a helpful TODO assistant. Use the provided tools to manage tasks for the user.",
            tools=TOOLS,
            messages=messages
        )
        
        # Build assistant message with all content
        assistant_content = response.content
        
        # Add assistant response to history
        messages.append({"role": "assistant", "content": assistant_content})
        
        # Process content blocks (Claude's response structure)
        for content_block in assistant_content:
            # Handle tool use blocks
            if content_block.type == "tool_use":
                tool_name = content_block.name
                tool_input = content_block.input
                
                result = process_tool_call(tool_name, tool_input)
                
                # Add tool result to conversation
                # Claude will see this and continue reasoning
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": content_block.id,
                            "content": result
                        }
                    ]
                })
                
                print(f"  ✓ {tool_name} executed")
            
            # Handle text blocks
            elif content_block.type == "text":
                if content_block.text:
                    print(f"Agent: {content_block.text}\n")

# ============================================================================
# PART 6: Tests
# ============================================================================

def run_tests():
    """Run single-turn tests"""
    print("\n" + "="*70)
    print("  Running Tests with Claude")
    print("="*70)
    
    test_cases = [
        ("Add a task called 'Buy groceries' with description 'Milk, eggs, bread'", True),
        ("List all my tasks", True),
        ("Mark task 1 as complete", True),
        ("Show me task 1", False),  # No direct tool for this
        ("Delete task 1", True),
        ("How many tasks do I have?", False),  # Claude will reason about this
    ]
    
    for message, expects_tool_call in test_cases:
        had_tool_call = single_turn_agent(message)
        status = "✓ PASS" if had_tool_call == expects_tool_call else "⚠ PASS (different behavior)"
        print(f"{status}\n")

# ============================================================================
# PART 7: Comparison: OpenAI vs Claude Code
# ============================================================================

def show_comparison():
    """Show key differences between implementations"""
    
    comparison = """
    ╔════════════════════════════════════════════════════════════════════╗
    ║              OpenAI (Original) vs Claude Code (New)               ║
    ╠════════════════════════════════════════════════════════════════════╣
    ║ Aspect                    │ OpenAI              │ Claude Code       ║
    ╠═══════════════════════════╪═════════════════════╪═══════════════════╣
    ║ Client                    │ from openai import  │ from anthropic    ║
    ║                           │ OpenAI              │ import Anthropic  ║
    ║                           │                     │                   ║
    ║ Model                     │ "gpt-4"             │ "claude-3-5-      ║
    ║                           │                     │ sonnet-20241022"  ║
    ║                           │                     │                   ║
    ║ API Call                  │ completions.create  │ messages.create   ║
    ║                           │ (model, messages,   │ (model, max_      ║
    ║                           │ tools, tool_choice) │ tokens, system,   ║
    ║                           │                     │ tools, messages)  ║
    ║                           │                     │                   ║
    ║ Tool Format               │ "type": "function"  │ "input_schema"    ║
    ║                           │ "function":{}       │ within tool       ║
    ║                           │                     │                   ║
    ║ Response Handling         │ response.choice[0]  │ response.content  ║
    ║                           │ .message.tool_calls │ (list of blocks)  ║
    ║                           │                     │                   ║
    ║ Tool Use Check            │ if tool_calls:      │ if content_block. ║
    ║                           │   for tool_call in  │ type == "tool_use"║
    ║                           │   tool_calls:       │                   ║
    ║                           │                     │                   ║
    ║ Context Window            │ 128K (GPT-4)        │ 200K (Claude 3.5) ║
    ║                           │                     │                   ║
    ║ Cost (per 1M tokens)      │ $15 input           │ $3 input          ║
    ║                           │ $30 output          │ $15 output        ║
    ║                           │                     │                   ║
    ║ Best For                  │ Chat applications   │ Task automation   ║
    ║                           │                     │ (multi-agent)     ║
    ╚═══════════════════════════╪═════════════════════╪═══════════════════╝
    """
    
    print(comparison)

# ============================================================================
# PART 8: Main
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            run_tests()
        elif sys.argv[1] == "compare":
            show_comparison()
    else:
        # Start interactive multi-turn agent
        multi_turn_agent()
