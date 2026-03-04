# 12-Week Agentic AI Training Program
## Building Multi-Agent Systems with Dependency Management & Conflict Resolution

**Program Level:** Intermediate (assumes architecture knowledge, light hands-on AI/ML)  
**Total Time Commitment:** ~50-60 hours (course + building)  
**Learning Vehicle:** TODO App → Software Development Agent System  
**Final Outcome:** Production-ready multi-agent system with voting-based conflict resolution

---

## Table of Contents

1. [Pre-Course Setup](#pre-course-setup)
2. [12-Week Curriculum Overview](#12-week-curriculum-overview)
3. [Weeks 1-3: Foundations](#weeks-1-3-foundations)
4. [Weeks 4-9: Framework Deep Dive](#weeks-4-9-framework-deep-dive)
5. [Weeks 10-12: Scale to Production](#weeks-10-12-scale-to-production)
6. [Code Templates & Examples](#code-templates--examples)
7. [Integration & Configuration Guide](#integration--configuration-guide)
8. [Master Checklist](#master-checklist)

---

# Pre-Course Setup

## Required Software & Accounts

### Development Environment
- **Python 3.10+** (verify with `python --version`)
- **pip** package manager
- **Git** for version control
- **IDE/Editor**: VS Code (recommended) or Cursor (if using AI-assisted coding)

### API Keys & Services (Free tier available)
- **OpenAI API** (https://platform.openai.com/api-keys): GPT-4, Agents SDK
- **Anthropic API** (https://console.anthropic.com): Claude models (alternative)
- **LangSmith** (https://smith.langchain.com): Free tier for debugging/tracing LangGraph

### Paid Courses (Budget: ~$100-150)
- **Frontend Masters** ($40/month, can cancel after 1 month): "Build an AI Agent from Scratch"
- **Udemy** ($15 on sale, check for coupons): "The Complete Agentic AI Engineering Course"

### Free Resources
- **LangChain Documentation**: https://python.langchain.com/docs/
- **LangGraph Documentation**: https://langchain-ai.github.io/langgraph/
- **CrewAI Documentation**: https://docs.crewai.com/
- **OpenAI Swarm GitHub**: https://github.com/openai/swarm

## Environment Setup Instructions

### Step 1: Create Python Virtual Environment
```bash
# Create directory for project
mkdir agentic_ai_training
cd agentic_ai_training

# Create virtual environment
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Verify activation (should show (venv) prefix in terminal)
```

### Step 2: Install Base Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install core dependencies
pip install python-dotenv requests

# Create .env file for API keys
touch .env

# Edit .env file with your API keys
# OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here (optional)
# LANGCHAIN_API_KEY=your_key_here (optional, for LangSmith)
```

### Step 3: Directory Structure
```
agentic_ai_training/
├── venv/
├── .env
├── .gitignore
├── week1/
│   ├── single_agent_todo.py
│   ├── tools.py
│   └── test_week1.py
├── week2/
│   ├── multi_tool_agent.py
│   ├── memory.py
│   └── test_week2.py
├── week3/
│   ├── agent_with_errors.py
│   ├── logging_config.py
│   └── test_week3.py
├── week4/
│   ├── crewai_orchestrator.py
│   └── agents_config.py
├── week5_to_9/
│   ├── langgraph_system.py
│   ├── state_schemas.py
│   ├── voting_system.py
│   └── human_review.py
├── week10_to_12/
│   ├── software_dev_agents.py
│   ├── architecture_spec.md
│   └── integration_tests.py
└── README.md
```

---

# 12-Week Curriculum Overview

| Week | Focus | Duration | Key Deliverable |
|------|-------|----------|-----------------|
| **1** | Foundations: Single Agent | 8-10 hrs | Working TODO agent with tool calling |
| **2** | Multi-Tool Agent with Memory | 8-10 hrs | Agent with persistent state |
| **3** | Error Handling & Logging | 8-10 hrs | Robust agent with debugging capability |
| **4** | CrewAI Multi-Agent | 8-10 hrs | 3-agent crew with role-based architecture |
| **5** | CrewAI Task Dependencies | 8-10 hrs | Agents coordinating with `depends_on` |
| **6** | LangGraph State Graphs | 10-12 hrs | Graph-based workflow with conditional routing |
| **7** | Voting System | 10-12 hrs | Conflict detection and resolution via voting |
| **8** | Integrated Multi-Agent System | 12-15 hrs | Full TODO system with dependencies + voting |
| **9** | Error Scenarios & Edge Cases | 8-10 hrs | Production-ready robustness |
| **10** | Architecture Design for Software Dev System | 8-10 hrs | Complete system specification document |
| **11** | Implementation of Software Dev Agents | 12-15 hrs | Full multi-agent system for development tasks |
| **12** | Testing, Refinement & Documentation | 10-12 hrs | Tested, documented, production-ready system |
| | **TOTAL** | **~130-150 hrs** | |

---

# Weeks 1-3: Foundations

## Learning Schedule

**Week 1:**
- Sat/Sun: Frontend Masters "Build an AI Agent from Scratch" (3 hrs)
- Mon/Tue: OpenAI Swarm repo review (2-3 hrs)
- Wed-Fri: Build Week 1 project (5-8 hrs)

**Week 2:**
- Mon/Tue: LangChain fundamentals (2-3 hrs)
- Wed-Fri: Build Week 2 project (5-8 hrs)

**Week 3:**
- Mon: Error handling concepts (1-2 hrs)
- Tue-Fri: Build Week 3 project (6-8 hrs)

## Week 1: Single Agent TODO Assistant

### Objectives
- Understand tool calling / function calling
- Implement basic agent loop (input → reasoning → tool call → output)
- Work with OpenAI API directly
- Maintain conversation memory

### Learning Resources
- **Video**: Frontend Masters "Build an AI Agent from Scratch" (3 hrs)
- **Reading**: OpenAI API docs on function calling: https://platform.openai.com/docs/guides/function-calling
- **Example**: OpenAI Swarm examples: https://github.com/openai/swarm/tree/main/examples

### Code Template: Week 1 - Single Agent

```python
# week1/single_agent_todo.py

import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define tools available to the agent
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Add a new task to the TODO list",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "description": {"type": "string", "description": "Task description"}
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
                    "task_id": {"type": "integer", "description": "Task ID"}
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
                    "task_id": {"type": "integer", "description": "Task ID"}
                },
                "required": ["task_id"]
            }
        }
    }
]

# In-memory task storage (Week 1 - will upgrade to persistent in Week 2)
tasks = []
next_id = 1

def add_task(title, description=""):
    global next_id
    task = {
        "id": next_id,
        "title": title,
        "description": description,
        "completed": False
    }
    tasks.append(task)
    next_id += 1
    return f"Task '{title}' added with ID {task['id']}"

def list_tasks():
    if not tasks:
        return "No tasks yet."
    result = []
    for task in tasks:
        status = "✓" if task["completed"] else "○"
        result.append(f"{status} [{task['id']}] {task['title']}: {task['description']}")
    return "\n".join(result)

def mark_complete(task_id):
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = True
            return f"Task {task_id} marked complete"
    return f"Task {task_id} not found"

def delete_task(task_id):
    global tasks
    tasks = [t for t in tasks if t["id"] != task_id]
    return f"Task {task_id} deleted"

def process_tool_call(tool_name, tool_input):
    """Execute tool and return result"""
    if tool_name == "add_task":
        return add_task(tool_input.get("title"), tool_input.get("description", ""))
    elif tool_name == "list_tasks":
        return list_tasks()
    elif tool_name == "mark_complete":
        return mark_complete(tool_input.get("task_id"))
    elif tool_name == "delete_task":
        return delete_task(tool_input.get("task_id"))
    else:
        return f"Unknown tool: {tool_name}"

def agent_loop(user_message):
    """
    Single-turn agent loop
    1. Send user message to Claude with tools
    2. If Claude calls a tool, execute it
    3. Return final response
    """
    messages = [
        {"role": "user", "content": user_message}
    ]
    
    # Call Claude with tools
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto"
    )
    
    # Check if Claude wants to call a tool
    if response.choice[0].message.tool_calls:
        tool_results = []
        
        for tool_call in response.choice[0].message.tool_calls:
            tool_name = tool_call.function.name
            tool_input = json.loads(tool_call.function.arguments)
            
            # Execute tool
            result = process_tool_call(tool_name, tool_input)
            tool_results.append({
                "tool_call_id": tool_call.id,
                "result": result
            })
            print(f"→ Called {tool_name} with {tool_input}")
            print(f"  Result: {result}\n")
        
        return tool_results
    else:
        # No tool call, return assistant's message
        return response.choice[0].message.content

def multi_turn_agent(initial_message=""):
    """
    Multi-turn agent that maintains conversation history
    """
    messages = []
    
    print("TODO Agent started. Type 'exit' to quit.\n")
    
    while True:
        if initial_message:
            user_input = initial_message
            initial_message = ""
        else:
            user_input = input("You: ").strip()
        
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        
        messages.append({"role": "user", "content": user_input})
        
        # Call Claude with conversation history
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )
        
        # Process response
        assistant_message = response.choice[0].message
        messages.append({"role": "assistant", "content": assistant_message.content or ""})
        
        # Handle tool calls
        if assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_input = json.loads(tool_call.function.arguments)
                
                result = process_tool_call(tool_name, tool_input)
                
                # Add tool result to conversation
                messages.append({
                    "role": "user",
                    "content": f"Tool {tool_name} returned: {result}"
                })
                
                print(f"Agent: [Executed {tool_name}]")
                print(f"Result: {result}\n")
        else:
            # Print assistant's response
            print(f"Agent: {assistant_message.content}\n")

if __name__ == "__main__":
    # Test single-turn
    print("=== SINGLE-TURN TESTS ===\n")
    agent_loop("Add a task called 'Buy groceries' with description 'Milk, eggs, bread'")
    agent_loop("List all tasks")
    agent_loop("Mark task 1 as complete")
    
    # Start multi-turn
    print("\n=== MULTI-TURN AGENT ===\n")
    multi_turn_agent()
```

### Week 1 Success Checklist

- [ ] Environment set up (Python venv, dependencies installed, .env configured)
- [ ] Code runs without API errors
- [ ] Agent successfully calls all 4 tools (add, list, complete, delete)
- [ ] Agent maintains conversation context across 5+ turns
- [ ] You can explain: what is tool calling, the agent loop, how memory works
- [ ] You have tested at least 3 multi-step conversations (e.g., add task → list → mark complete)

### Week 1 Fail Criteria & Recovery

| Failure | Recovery |
|---------|----------|
| "Module not found" errors | Run `pip install openai python-dotenv` and verify venv is active |
| "Invalid API key" | Check .env file has correct OpenAI key, regenerate if needed |
| Agent doesn't call tools | Verify TOOLS list is properly formatted, check OpenAI response |
| Agent forgets previous context | Ensure messages list is maintained in multi_turn_agent function |

---

## Week 2: Multi-Tool Agent with Persistent Memory

### Objectives
- Expand agent to handle 6+ tools
- Implement persistent state (saved/loaded from disk)
- Add input validation
- Distinguish conversation memory from persistent storage

### Code Template: Week 2 - Memory & Storage

```python
# week2/memory.py

import json
import os
from datetime import datetime
from pathlib import Path

class TaskMemory:
    """Persistent task storage"""
    
    def __init__(self, storage_file="tasks.json"):
        self.storage_file = storage_file
        self.tasks = self._load_tasks()
        self.next_id = max([t["id"] for t in self.tasks], default=0) + 1
    
    def _load_tasks(self):
        """Load tasks from disk"""
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_tasks(self):
        """Save tasks to disk"""
        with open(self.storage_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def add_task(self, title, description="", priority="medium", due_date=None):
        """Validate and add task"""
        # Validation
        if not title or not isinstance(title, str):
            raise ValueError("Task title must be non-empty string")
        if len(title) > 200:
            raise ValueError("Task title must be less than 200 characters")
        
        # Check for duplicates (optional)
        if any(t["title"].lower() == title.lower() for t in self.tasks):
            raise ValueError(f"Task '{title}' already exists")
        
        task = {
            "id": self.next_id,
            "title": title,
            "description": description,
            "priority": priority,
            "due_date": due_date,
            "completed": False,
            "created_at": datetime.now().isoformat()
        }
        
        self.tasks.append(task)
        self.next_id += 1
        self._save_tasks()
        return task
    
    def list_tasks(self, filter_by="all", sort_by="priority"):
        """List tasks with filtering"""
        filtered = self.tasks
        
        if filter_by == "completed":
            filtered = [t for t in filtered if t["completed"]]
        elif filter_by == "pending":
            filtered = [t for t in filtered if not t["completed"]]
        
        # Sort
        if sort_by == "priority":
            priority_order = {"high": 0, "medium": 1, "low": 2}
            filtered = sorted(filtered, key=lambda t: priority_order.get(t.get("priority", "medium"), 1))
        elif sort_by == "date":
            filtered = sorted(filtered, key=lambda t: t.get("due_date", ""))
        
        return filtered
    
    def search_tasks(self, keyword):
        """Search tasks by keyword"""
        keyword = keyword.lower()
        return [t for t in self.tasks if keyword in t["title"].lower() or keyword in t["description"].lower()]
    
    def mark_complete(self, task_id):
        """Mark task complete"""
        task = self._get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        task["completed"] = True
        self._save_tasks()
        return task
    
    def update_task(self, task_id, **kwargs):
        """Update task fields"""
        task = self._get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Validate allowed fields
        allowed_fields = {"title", "description", "priority", "due_date"}
        for key in kwargs:
            if key not in allowed_fields:
                raise ValueError(f"Cannot update field '{key}'")
        
        task.update(kwargs)
        self._save_tasks()
        return task
    
    def delete_task(self, task_id):
        """Delete task"""
        task = self._get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        self._save_tasks()
        return task
    
    def _get_task(self, task_id):
        """Get task by ID"""
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None
    
    def get_stats(self):
        """Get task statistics"""
        return {
            "total": len(self.tasks),
            "completed": len([t for t in self.tasks if t["completed"]]),
            "pending": len([t for t in self.tasks if not t["completed"]]),
            "high_priority": len([t for t in self.tasks if t.get("priority") == "high" and not t["completed"]])
        }

class ConversationMemory:
    """Conversation history management"""
    
    def __init__(self):
        self.messages = []
    
    def add_message(self, role, content):
        """Add message to history"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_history(self, last_n=None):
        """Get conversation history (for LLM context)"""
        history = self.messages
        if last_n:
            history = history[-last_n:]
        
        # Format for LLM (remove timestamps)
        return [{"role": m["role"], "content": m["content"]} for m in history]
    
    def clear(self):
        """Clear history"""
        self.messages = []
```

### Week 2 Extended Tools

```python
# week2/multi_tool_agent.py (extends week1)

from memory import TaskMemory, ConversationMemory
import json

memory = TaskMemory("tasks.json")
conversation = ConversationMemory()

# Expand TOOLS list with new functions
TOOLS = [
    # Previous 4 tools...
    {
        "type": "function",
        "function": {
            "name": "search_tasks",
            "description": "Search tasks by keyword",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "Search keyword"}
                },
                "required": ["keyword"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update task priority or due date",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                    "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                    "due_date": {"type": "string", "description": "ISO format date"}
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_stats",
            "description": "Get task statistics",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

def process_tool_call(tool_name, tool_input):
    """Execute tool with error handling"""
    try:
        if tool_name == "add_task":
            task = memory.add_task(
                title=tool_input.get("title"),
                description=tool_input.get("description", ""),
                priority=tool_input.get("priority", "medium")
            )
            return f"Task created: {task}"
        
        elif tool_name == "list_tasks":
            filter_by = tool_input.get("filter", "all")
            tasks = memory.list_tasks(filter_by=filter_by)
            if not tasks:
                return f"No {filter_by} tasks"
            return json.dumps(tasks, indent=2)
        
        elif tool_name == "mark_complete":
            task = memory.mark_complete(tool_input.get("task_id"))
            return f"Marked task {task['id']} complete"
        
        elif tool_name == "delete_task":
            task = memory.delete_task(tool_input.get("task_id"))
            return f"Deleted task: {task['title']}"
        
        elif tool_name == "search_tasks":
            results = memory.search_tasks(tool_input.get("keyword"))
            return json.dumps(results, indent=2)
        
        elif tool_name == "update_task":
            kwargs = {k: v for k, v in tool_input.items() if k != "task_id" and v is not None}
            task = memory.update_task(tool_input.get("task_id"), **kwargs)
            return f"Updated task {task['id']}"
        
        elif tool_name == "get_stats":
            stats = memory.get_stats()
            return json.dumps(stats, indent=2)
        
        else:
            return f"Unknown tool: {tool_name}"
    
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
```

### Week 2 Success Checklist

- [ ] Completed Week 1 checklist items
- [ ] Tasks persist after restart (check tasks.json)
- [ ] All 6+ tools execute correctly
- [ ] Validation works (reject invalid inputs)
- [ ] Can search, update, get stats
- [ ] You can explain difference between ConversationMemory and TaskMemory
- [ ] Created at least 5 tasks and successfully queried them across sessions

### Week 2 Fail Recovery

| Failure | Recovery |
|---------|----------|
| tasks.json not created | Ensure `_save_tasks()` is called after add_task |
| "Duplicate task" error | This is intentional validation; test with different titles |
| Search doesn't work | Check keyword matching logic (case-insensitive) |
| Update fails | Verify task_id exists before updating |

---

## Week 3: Error Handling & Logging

### Objectives
- Graceful error recovery
- Comprehensive logging
- Agent self-correction
- Debug traceability

### Code Template: Week 3 - Logging & Error Handling

```python
# week3/logging_config.py

import logging
import json
from datetime import datetime
from pathlib import Path

class StructuredLogger:
    """Structured logging for agent decisions"""
    
    def __init__(self, log_file="agent_trace.json"):
        self.log_file = log_file
        self.logs = []
        self._load_existing_logs()
    
    def _load_existing_logs(self):
        """Load existing logs"""
        if Path(self.log_file).exists():
            with open(self.log_file, 'r') as f:
                self.logs = json.load(f)
    
    def log_event(self, event_type, data):
        """Log structured event"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }
        self.logs.append(entry)
        self._save_logs()
        print(f"[LOG] {event_type}: {data}")
    
    def _save_logs(self):
        """Persist logs"""
        with open(self.log_file, 'w') as f:
            json.dump(self.logs, f, indent=2)
    
    def get_trace(self, conversation_id=None):
        """Get decision trace for debugging"""
        return self.logs

logger = StructuredLogger()

# Logging events
def log_user_input(user_message):
    logger.log_event("USER_INPUT", {"message": user_message})

def log_tool_call(tool_name, tool_input):
    logger.log_event("TOOL_CALL", {"tool": tool_name, "input": tool_input})

def log_tool_result(tool_name, result, success=True):
    logger.log_event("TOOL_RESULT", {
        "tool": tool_name,
        "result": result,
        "success": success
    })

def log_error(error_type, error_message, recovery_action):
    logger.log_event("ERROR", {
        "type": error_type,
        "message": error_message,
        "recovery": recovery_action
    })

def log_decision(reasoning, action):
    logger.log_event("DECISION", {
        "reasoning": reasoning,
        "action": action
    })
```

### Week 3 Error Handling in Agent

```python
# week3/agent_with_errors.py

from logging_config import log_user_input, log_tool_call, log_tool_result, log_error, log_decision
from week2.multi_tool_agent import process_tool_call, memory
import json

def safe_tool_call(tool_name, tool_input):
    """Execute tool with error handling and retries"""
    max_retries = 2
    attempt = 0
    
    while attempt < max_retries:
        try:
            log_tool_call(tool_name, tool_input)
            result = process_tool_call(tool_name, tool_input)
            log_tool_result(tool_name, result, success=True)
            return result
        
        except ValueError as e:
            attempt += 1
            error_msg = str(e)
            
            # Attempt recovery
            if "not found" in error_msg.lower() and attempt < max_retries:
                log_error("NOT_FOUND", error_msg, "Retrying with corrected ID")
                # Could prompt agent to ask for correct ID
                continue
            elif "invalid" in error_msg.lower():
                log_error("VALIDATION", error_msg, "Agent should rephrase input")
                return f"I couldn't complete that action: {error_msg}. Could you clarify?"
            
            log_error("VALUE_ERROR", error_msg, "Terminating this action")
            return f"Error: {error_msg}"
        
        except Exception as e:
            attempt += 1
            error_msg = f"Unexpected error: {str(e)}"
            log_error("UNEXPECTED_ERROR", error_msg, "Attempting to recover gracefully")
            
            if attempt < max_retries:
                continue
            else:
                return "I encountered an unexpected error. Please try again."
    
    return "Failed to complete action after retries"

def agent_self_correct(agent_response, tool_results):
    """
    Agent reviews its own response and corrects if needed
    
    Example: Agent says "Task 5 completed" but tool said "Task 5 not found"
    """
    # Check for consistency
    if "completed" in agent_response.lower() and "not found" in str(tool_results).lower():
        log_decision(
            "Agent claimed success but tool indicated failure",
            "Self-correcting response"
        )
        return "I apologize, I made an error. That task doesn't exist. Let me list your tasks instead."
    
    return agent_response

def robust_multi_turn_agent():
    """
    Multi-turn agent with comprehensive error handling
    """
    from openai import OpenAI
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    messages = []
    
    print("Robust TODO Agent (type 'exit' to quit, 'trace' to see decision log)\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        
        if user_input.lower() == "trace":
            # Print decision trace
            from logging_config import logger
            for entry in logger.logs[-5:]:  # Last 5 events
                print(f"  [{entry['event_type']}] {entry['data']}")
            continue
        
        log_user_input(user_input)
        messages.append({"role": "user", "content": user_input})
        
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                tools=[],  # Add TOOLS here
                tool_choice="auto"
            )
            
            assistant_message = response.choice[0].message
            messages.append({"role": "assistant", "content": assistant_message.content or ""})
            
            # Handle tool calls with safe execution
            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_input = json.loads(tool_call.function.arguments)
                    
                    result = safe_tool_call(tool_name, tool_input)
                    
                    # Self-correct if needed
                    if assistant_message.content:
                        corrected = agent_self_correct(assistant_message.content, result)
                        if corrected != assistant_message.content:
                            print(f"Agent (corrected): {corrected}\n")
                    
                    messages.append({
                        "role": "user",
                        "content": f"Tool result: {result}"
                    })
                    
                    print(f"Agent executed: {tool_name}")
                    print(f"Result: {result}\n")
            else:
                print(f"Agent: {assistant_message.content}\n")
        
        except Exception as e:
            log_error("AGENT_CALL_ERROR", str(e), "Prompting user to retry")
            print(f"Agent error: {str(e)}. Please try again.\n")

if __name__ == "__main__":
    robust_multi_turn_agent()
```

### Week 3 Success Checklist

- [ ] Completed Weeks 1-2 checklist items
- [ ] Agent handles 3+ error types gracefully (invalid input, missing task, malformed data)
- [ ] Agent can self-correct (detects inconsistencies)
- [ ] agent_trace.json is created and populated
- [ ] Can type "trace" to see decision history
- [ ] Logs show clear decision reasoning
- [ ] Agent retries failed operations (max 2 times)
- [ ] You can explain the logging strategy and recovery mechanism

---

# Weeks 4-9: Framework Deep Dive

## Learning Schedule & Framework Choice

**Week 4-5: CrewAI Foundations**
- Udemy Modules 1-2 (8-10 hrs total)
- Week 4 Project: Orchestrated TODO with CrewAI

**Week 6-7: LangGraph Transition**
- Udemy Module 4 (8-10 hrs)
- Week 5 Project: CrewAI with task dependencies
- Week 6 Project: LangGraph state graphs

**Week 8-9: Voting & Integration**
- Week 7 Project: Voting system for conflicts
- Week 8-9 Projects: Full integration

---

## Week 4: CrewAI Multi-Agent TODO

### Why CrewAI?
- **Role-based design**: Each agent has explicit role, goal, backstory
- **Task dependency management**: Native `depends_on` parameter
- **Simpler learning curve**: More structured than raw LangGraph
- **Collaborative reasoning**: Built-in agent discussion for conflicts

### Learning Resources
- CrewAI docs: https://docs.crewai.com/
- Udemy Module 3 (CrewAI section)
- GitHub examples: https://github.com/joaomdmoura/crewai

### Code Template: Week 4 - CrewAI TODO System

```python
# week4/crewai_orchestrator.py

from crewai import Agent, Task, Crew
from week2.memory import TaskMemory
import json

# Initialize shared memory
memory = TaskMemory("tasks.json")

# Define Agents with explicit roles
task_manager = Agent(
    role="Task Manager",
    goal="Understand user intent and break down requests into specific actions",
    backstory="You are an expert at parsing user requests and understanding what tasks need to be executed.",
    tools=[],  # Will define tools via tasks
    verbose=True
)

storage_agent = Agent(
    role="Storage Specialist",
    goal="Execute CRUD operations on tasks safely and correctly",
    backstory="You are responsible for managing task storage. You execute operations and ensure data integrity.",
    tools=[],
    verbose=True
)

validator_agent = Agent(
    role="Data Validator",
    goal="Ensure all operations are valid before they're executed",
    backstory="You validate all operations and catch errors before they cause problems.",
    tools=[],
    verbose=True
)

# Define Tasks
parse_task = Task(
    description="Parse the user request: {user_input}",
    agent=task_manager,
    expected_output="Clear breakdown of what action(s) to take"
)

validate_task = Task(
    description="Validate the proposed action: {action}",
    agent=validator_agent,
    expected_output="Is this action valid? Any concerns?",
    depends_on=[parse_task]
)

execute_task = Task(
    description="Execute the validated action: {action}",
    agent=storage_agent,
    expected_output="Result of the operation",
    depends_on=[validate_task]
)

# Create Crew
crew = Crew(
    agents=[task_manager, storage_agent, validator_agent],
    tasks=[parse_task, validate_task, execute_task],
    verbose=True
)

def run_crewai_system(user_input):
    """Run CrewAI crew"""
    result = crew.kickoff(inputs={
        "user_input": user_input,
        "action": "Will be determined by parse task"
    })
    return result
```

### Week 4 Configuration Details

**agent_config.yaml** (Alternative to code-based config):

```yaml
# week4/agents_config.yaml

agents:
  task_manager:
    role: "Task Manager"
    goal: "Break down user requests into specific actions"
    backstory: "Expert at parsing requests"
  
  storage_agent:
    role: "Storage Specialist"
    goal: "Execute CRUD operations safely"
    backstory: "Responsible for data integrity"
  
  validator_agent:
    role: "Data Validator"
    goal: "Validate operations before execution"
    backstory: "Catches errors proactively"

tasks:
  parse:
    description: "Parse user request"
    agent: task_manager
    expected_output: "Clear action breakdown"
  
  validate:
    description: "Validate proposed action"
    agent: validator_agent
    expected_output: "Validation result"
    depends_on: [parse]
  
  execute:
    description: "Execute validated action"
    agent: storage_agent
    expected_output: "Operation result"
    depends_on: [validate]
```

### Week 4 Success Checklist

- [ ] Completed Weeks 1-3 checklist items
- [ ] Installed CrewAI: `pip install crewai`
- [ ] All 3 agents defined and respond
- [ ] Tasks execute in dependency order
- [ ] Agent roles are distinct (no overlapping responsibilities)
- [ ] You can explain role-based agent architecture
- [ ] Tested with 3 different user requests

---

## Week 5: CrewAI Task Dependencies & Conflicts

### Objectives
- Master CrewAI's `depends_on` mechanism
- Implement first conflict scenario
- Introduce voting concept

### Code Template: Week 5 - Conflict Detection

```python
# week5/conflict_detection.py

from dataclasses import dataclass
from enum import Enum
from typing import List

class ConflictType(Enum):
    VALIDATION_REJECTED = "validation_rejected"
    DATA_CONFLICT = "data_conflict"
    PERFORMANCE_CONCERN = "performance_concern"
    SECURITY_ISSUE = "security_issue"

@dataclass
class AgentOpinion:
    agent_name: str
    position: str  # "approve", "reject", "concern"
    reasoning: str
    confidence: float  # 0-1

@dataclass
class ConflictResolution:
    action: str
    requires_human_review: bool
    reasoning: str

class ConflictDetector:
    """Detect disagreements between agents"""
    
    def __init__(self):
        self.conflicts = []
    
    def detect_conflict(self, opinions: List[AgentOpinion]) -> bool:
        """Check if agents disagree"""
        positions = [op.position for op in opinions]
        # Conflict if not all agree
        return len(set(positions)) > 1
    
    def log_conflict(self, conflict_type: ConflictType, opinions: List[AgentOpinion]):
        """Record conflict for human review"""
        self.conflicts.append({
            "type": conflict_type,
            "opinions": opinions,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        })

# Example: Storage wants to delete all tasks, Validator says "Maybe ask first"
conflict_detector = ConflictDetector()

storage_opinion = AgentOpinion(
    agent_name="Storage Agent",
    position="approve",
    reasoning="User explicitly requested delete all tasks",
    confidence=0.9
)

validator_opinion = AgentOpinion(
    agent_name="Validator Agent",
    position="concern",
    reasoning="This is a destructive operation. Should confirm first",
    confidence=0.95
)

if conflict_detector.detect_conflict([storage_opinion, validator_opinion]):
    print("CONFLICT DETECTED:")
    conflict_detector.log_conflict(
        ConflictType.DATA_CONFLICT,
        [storage_opinion, validator_opinion]
    )
    print(f"Storage: {storage_opinion.reasoning}")
    print(f"Validator: {validator_opinion.reasoning}")
    print("→ Requires human review")
```

### Week 5 CrewAI Task Dependencies Example

```python
# week5/crewai_with_conflicts.py

from crewai import Agent, Task, Crew
from conflict_detection import ConflictDetector, AgentOpinion, ConflictType

# Define agents
parser = Agent(
    role="Intent Parser",
    goal="Understand user intent",
    backstory="Expert parser"
)

validator = Agent(
    role="Validator",
    goal="Check if action is safe",
    backstory="Safety expert"
)

storage = Agent(
    role="Storage Agent",
    goal="Execute operations",
    backstory="Data expert"
)

reviewer = Agent(
    role="Review Manager",
    goal="Make final decision when there's disagreement",
    backstory="Impartial decision maker"
)

# Tasks with dependencies
parse_intent = Task(
    description="Parse user request: {user_request}",
    agent=parser,
    expected_output="Parsed intent and action"
)

check_safety = Task(
    description="Check if this action is safe: {parsed_intent}",
    agent=validator,
    expected_output="Safety assessment (approve/reject/concern)",
    depends_on=[parse_intent]
)

execute_if_safe = Task(
    description="Execute if safety check approves: {parsed_intent}",
    agent=storage,
    expected_output="Execution result",
    depends_on=[check_safety]
)

# Advanced: Conflict resolution task
resolve_conflict = Task(
    description="Resolve disagreement between validator and storage: {conflict_details}",
    agent=reviewer,
    expected_output="Final decision (approve/reject)",
    depends_on=[check_safety, execute_if_safe]  # Runs if both previous tasks have opinions
)

crew = Crew(
    agents=[parser, validator, storage, reviewer],
    tasks=[parse_intent, check_safety, execute_if_safe, resolve_conflict],
    verbose=True
)
```

### Week 5 Success Checklist

- [ ] Completed Week 4 checklist items
- [ ] Installed conflict_detection module
- [ ] Can detect when 2+ agents disagree
- [ ] Conflicts are logged with reasoning
- [ ] Task dependencies properly chain
- [ ] Created sample conflict scenario (Storage vs Validator)
- [ ] You can explain how to detect and log conflicts

---

## Week 6: LangGraph State Graphs

### Why Transition from CrewAI to LangGraph?

| Aspect | CrewAI | LangGraph |
|--------|--------|-----------|
| **Dependency Management** | Task-level | Fine-grained state nodes |
| **Conditional Logic** | Limited | Powerful with edges |
| **State Management** | Implicit | Explicit state schema |
| **Debugging** | Good | Excellent (visualization) |
| **Complex Workflows** | Good | Better for intricate flows |

### Learning Resources
- LangGraph docs: https://langchain-ai.github.io/langgraph/
- Udemy Module 4 (LangGraph section)
- State graphs tutorial: https://langchain-ai.github.io/langgraph/concepts/high_level_plan/

### Code Template: Week 6 - LangGraph TODO System

```python
# week6/langgraph_system.py

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
import operator
from week2.memory import TaskMemory
import json

# Step 1: Define State Schema
class TodoState(TypedDict):
    user_input: str
    parsed_intent: str
    action_type: str  # "add", "list", "delete", etc.
    task_data: dict
    validation_result: dict
    execution_result: dict
    error: str

# Step 2: Define Node Functions
def parse_input(state: TodoState) -> TodoState:
    """Node 1: Parse user input"""
    user_input = state["user_input"]
    
    # Simple intent classification
    if "add" in user_input.lower() or "create" in user_input.lower():
        action_type = "add"
        parsed_intent = "Adding new task"
    elif "list" in user_input.lower() or "show" in user_input.lower():
        action_type = "list"
        parsed_intent = "Listing tasks"
    elif "delete" in user_input.lower():
        action_type = "delete"
        parsed_intent = "Deleting task"
    else:
        action_type = "unknown"
        parsed_intent = "Unknown action"
    
    return {
        **state,
        "parsed_intent": parsed_intent,
        "action_type": action_type
    }

def validate_action(state: TodoState) -> TodoState:
    """Node 2: Validate before execution"""
    action_type = state.get("action_type", "unknown")
    
    # Validation logic
    validation_result = {
        "is_valid": action_type != "unknown",
        "warnings": [],
        "suggestions": []
    }
    
    if action_type == "delete":
        validation_result["warnings"].append("This is a destructive operation")
    
    return {
        **state,
        "validation_result": validation_result
    }

def execute_action(state: TodoState) -> TodoState:
    """Node 3: Execute validated action"""
    memory = TaskMemory("tasks.json")
    action_type = state.get("action_type")
    
    try:
        if action_type == "add":
            task = memory.add_task(title="New task", description="")
            result = {"success": True, "data": task}
        elif action_type == "list":
            tasks = memory.list_tasks()
            result = {"success": True, "data": tasks}
        elif action_type == "delete":
            # Don't actually delete - need human confirmation
            result = {"success": False, "data": "Requires human confirmation"}
        else:
            result = {"success": False, "data": "Unknown action"}
        
        return {
            **state,
            "execution_result": result,
            "error": ""
        }
    
    except Exception as e:
        return {
            **state,
            "execution_result": {"success": False},
            "error": str(e)
        }

def should_proceed(state: TodoState) -> str:
    """Conditional: Route based on validation"""
    is_valid = state.get("validation_result", {}).get("is_valid", False)
    
    if is_valid:
        return "execute"
    else:
        return "error_handling"

def handle_error(state: TodoState) -> TodoState:
    """Node 4: Handle validation errors"""
    return {
        **state,
        "error": "Validation failed"
    }

# Step 3: Build Graph
graph_builder = StateGraph(TodoState)

# Add nodes
graph_builder.add_node("parse", parse_input)
graph_builder.add_node("validate", validate_action)
graph_builder.add_node("execute", execute_action)
graph_builder.add_node("error_handler", handle_error)

# Add edges
graph_builder.add_edge(START, "parse")
graph_builder.add_edge("parse", "validate")
graph_builder.add_conditional_edges(
    "validate",
    should_proceed,
    {
        "execute": "execute",
        "error_handling": "error_handler"
    }
)
graph_builder.add_edge("execute", END)
graph_builder.add_edge("error_handler", END)

# Compile graph
graph = graph_builder.compile()

# Step 4: Run graph
def run_langgraph_todo(user_input: str):
    """Execute LangGraph workflow"""
    initial_state = {
        "user_input": user_input,
        "parsed_intent": "",
        "action_type": "",
        "task_data": {},
        "validation_result": {},
        "execution_result": {},
        "error": ""
    }
    
    result = graph.invoke(initial_state)
    return result

if __name__ == "__main__":
    # Test
    result = run_langgraph_todo("Add a task called 'Buy milk'")
    print(json.dumps(result, indent=2, default=str))
```

### Visualizing the Graph

```python
# week6/visualize_graph.py

from langgraph_system import graph

# Save visualization
graph_image = graph.get_graph().draw_mermaid_png()
with open("graph_visualization.png", "wb") as f:
    f.write(graph_image)

# Print ASCII representation
print(graph.get_graph().draw_ascii())
```

### Week 6 Success Checklist

- [ ] Completed Weeks 1-5 checklist items
- [ ] LangGraph installed: `pip install langgraph`
- [ ] State schema defined clearly
- [ ] All 4 nodes execute in correct order
- [ ] Conditional edges route correctly
- [ ] Graph visualization generated
- [ ] You can explain: state schema, nodes, edges, conditional routing
- [ ] Tested with 3 different inputs

---

## Weeks 7-9: Voting System & Full Integration

### Week 7: Implement Voting Mechanism

```python
# week7/voting_system.py

from dataclasses import dataclass
from typing import List, Dict
from enum import Enum

class VotePosition(Enum):
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"

@dataclass
class Vote:
    agent_name: str
    position: VotePosition
    weight: float = 1.0  # Weighted voting
    reasoning: str = ""
    confidence: float = 1.0

class VotingSystem:
    """Aggregate votes and resolve conflicts"""
    
    def __init__(self, agent_weights: Dict[str, float] = None):
        """
        Initialize voting system
        
        agent_weights: {agent_name: weight}
        Example: {"Security": 2.0, "QA": 1.0, "Storage": 1.0}
        """
        self.agent_weights = agent_weights or {}
        self.votes: List[Vote] = []
        self.history = []
    
    def cast_vote(self, vote: Vote):
        """Record a vote"""
        # Apply agent weight
        if vote.agent_name in self.agent_weights:
            vote.weight *= self.agent_weights[vote.agent_name]
        
        self.votes.append(vote)
    
    def tally_votes(self) -> Dict:
        """Calculate voting result"""
        if not self.votes:
            return {"result": "NO_VOTES"}
        
        approve_weight = sum(v.weight for v in self.votes if v.position == VotePosition.APPROVE)
        reject_weight = sum(v.weight for v in self.votes if v.position == VotePosition.REJECT)
        total_weight = approve_weight + reject_weight
        
        if total_weight == 0:
            return {"result": "ABSTAIN"}
        
        approve_percent = approve_weight / total_weight
        
        # Determine outcome
        if approve_percent > 0.5:
            result = "APPROVED"
        elif approve_percent < 0.5:
            result = "REJECTED"
        else:
            result = "TIE"
        
        return {
            "result": result,
            "approve_weight": approve_weight,
            "reject_weight": reject_weight,
            "approve_percent": approve_percent,
            "total_weight": total_weight,
            "vote_breakdown": [
                {
                    "agent": v.agent_name,
                    "position": v.position.value,
                    "weight": v.weight,
                    "reasoning": v.reasoning
                }
                for v in self.votes
            ]
        }
    
    def reset(self):
        """Clear votes for next decision"""
        self.history.append(self.votes)
        self.votes = []
    
    def get_history(self) -> List:
        """Get all past votes"""
        return self.history

# Example usage
voting_system = VotingSystem(agent_weights={
    "Security": 2.0,  # Security votes count as 2x
    "QA": 1.5,
    "Backend": 1.0
})

# Simulate voting
voting_system.cast_vote(Vote(
    agent_name="Security",
    position=VotePosition.REJECT,
    reasoning="SQL injection vulnerability detected",
    confidence=0.95
))

voting_system.cast_vote(Vote(
    agent_name="Backend",
    position=VotePosition.APPROVE,
    reasoning="Implementation is straightforward",
    confidence=0.8
))

voting_system.cast_vote(Vote(
    agent_name="QA",
    position=VotePosition.REJECT,
    reasoning="Performance impact on large datasets",
    confidence=0.7
))

result = voting_system.tally_votes()
print(f"Decision: {result['result']}")
print(f"Approve: {result['approve_weight']} | Reject: {result['reject_weight']}")
print("\nVote Breakdown:")
for vote in result['vote_breakdown']:
    print(f"  {vote['agent']}: {vote['position']} ({vote['weight']}x) - {vote['reasoning']}")
```

### Week 7 Human Review Interface

```python
# week7/human_review.py

from voting_system import VotingSystem, VotePosition, Vote
import json

class HumanReviewPanel:
    """Simple CLI interface for human review"""
    
    def __init__(self, voting_system: VotingSystem):
        self.voting_system = voting_system
    
    def present_decision(self, action_description: str) -> str:
        """
        Show voting outcome and ask human for override
        
        Returns: "proceed", "reject", "modify"
        """
        result = self.voting_system.tally_votes()
        
        print("\n" + "="*60)
        print("HUMAN REVIEW REQUIRED")
        print("="*60)
        print(f"\nAction: {action_description}")
        print(f"\nVoting Result: {result['result']}")
        print(f"Approval: {result['approve_percent']*100:.1f}%")
        
        print("\nVote Breakdown:")
        for vote in result['vote_breakdown']:
            print(f"  {vote['agent']:12} {vote['position']:10} ({vote['weight']}x weight)")
            print(f"    └─ {vote['reasoning']}")
        
        print("\nYour Options:")
        print("  [A] Approve (accept agent vote)")
        print("  [R] Reject (override agents)")
        print("  [M] Modify (change agent weights)")
        print("  [S] Show Details")
        
        while True:
            choice = input("\nYour decision [A/R/M/S]: ").upper().strip()
            
            if choice == "A":
                return "proceed" if result['result'] == "APPROVED" else "reject"
            elif choice == "R":
                return "reject" if result['result'] == "APPROVED" else "proceed"
            elif choice == "M":
                self._modify_weights()
                # Recalculate
                return self.present_decision(action_description)
            elif choice == "S":
                print(f"\nFull result:\n{json.dumps(result, indent=2)}")
            else:
                print("Invalid choice. Try again.")
    
    def _modify_weights(self):
        """Allow human to adjust agent weights"""
        print("\nCurrent weights:")
        for agent, weight in self.voting_system.agent_weights.items():
            print(f"  {agent}: {weight}x")
        
        agent = input("Agent to modify (or 'done'): ").strip()
        if agent == "done":
            return
        
        new_weight = float(input(f"New weight for {agent}: "))
        self.voting_system.agent_weights[agent] = new_weight
        print(f"Updated {agent} weight to {new_weight}x")
```

### Week 8-9: Full Integration

```python
# week8_9/integrated_todo_system.py

from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from week7.voting_system import VotingSystem, Vote, VotePosition
from week7.human_review import HumanReviewPanel
import json

# Extended state with voting
class IntegratedTodoState(TypedDict):
    user_input: str
    parsed_intent: str
    action_type: str
    task_data: dict
    validation_result: dict
    execution_result: dict
    conflict_detected: bool
    votes: list
    voting_result: dict
    human_decision: str
    error: str
    decision_log: list

# Agents express opinions (voting)
def validator_node(state: IntegratedTodoState) -> IntegratedTodoState:
    """Validator agent votes"""
    action_type = state.get("action_type", "")
    
    vote = Vote(
        agent_name="Validator",
        position=VotePosition.APPROVE if action_type != "delete" else VotePosition.ABSTAIN,
        reasoning="Standard validation passed" if action_type != "delete" else "Destructive operation - abstaining"
    )
    
    state["votes"].append(vote.__dict__)  # Convert to dict for JSON serialization
    return state

def storage_node(state: IntegratedTodoState) -> IntegratedTodoState:
    """Storage agent votes"""
    action_type = state.get("action_type", "")
    
    vote = Vote(
        agent_name="Storage",
        position=VotePosition.APPROVE,
        reasoning="Ready to execute operation"
    )
    
    state["votes"].append(vote.__dict__)
    return state

def security_node(state: IntegratedTodoState) -> IntegratedTodoState:
    """Security agent votes"""
    action_type = state.get("action_type", "")
    
    vote = Vote(
        agent_name="Security",
        position=VotePosition.APPROVE,
        reasoning="No security concerns"
    )
    
    state["votes"].append(vote.__dict__)
    return state

def voting_aggregator_node(state: IntegratedTodoState) -> IntegratedTodoState:
    """Aggregate votes"""
    voting_system = VotingSystem(agent_weights={
        "Security": 2.0,
        "Validator": 1.5,
        "Storage": 1.0
    })
    
    # Reconstruct votes
    for vote_dict in state["votes"]:
        vote = Vote(
            agent_name=vote_dict["agent_name"],
            position=VotePosition(vote_dict["position"]),
            weight=vote_dict.get("weight", 1.0),
            reasoning=vote_dict.get("reasoning", "")
        )
        voting_system.cast_vote(vote)
    
    result = voting_system.tally_votes()
    
    state["voting_result"] = result
    state["conflict_detected"] = result["result"] == "TIE"
    
    return state

def human_review_node(state: IntegratedTodoState) -> IntegratedTodoState:
    """Get human decision on conflicts"""
    voting_result = state.get("voting_result", {})
    
    if voting_result.get("result") in ["TIE", "REJECTED"]:
        panel = HumanReviewPanel(VotingSystem())
        decision = panel.present_decision(f"Execute: {state['parsed_intent']}")
        state["human_decision"] = decision
    else:
        state["human_decision"] = "AUTO_APPROVED" if voting_result.get("result") == "APPROVED" else "AUTO_REJECTED"
    
    return state

def route_on_decision(state: IntegratedTodoState) -> str:
    """Route based on human decision"""
    decision = state.get("human_decision", "")
    if decision == "proceed" or decision == "AUTO_APPROVED":
        return "execute"
    else:
        return "reject"

# Build integrated graph
graph_builder = StateGraph(IntegratedTodoState)

graph_builder.add_node("validator", validator_node)
graph_builder.add_node("storage", storage_node)
graph_builder.add_node("security", security_node)
graph_builder.add_node("voting_aggregator", voting_aggregator_node)
graph_builder.add_node("human_review", human_review_node)
graph_builder.add_node("execute", lambda s: {**s, "execution_result": {"status": "executed"}})
graph_builder.add_node("reject", lambda s: {**s, "execution_result": {"status": "rejected"}})

# Parallel voting, then aggregation, then human review
graph_builder.add_edge(START, "validator")
graph_builder.add_edge(START, "storage")
graph_builder.add_edge(START, "security")

graph_builder.add_edge("validator", "voting_aggregator")
graph_builder.add_edge("storage", "voting_aggregator")
graph_builder.add_edge("security", "voting_aggregator")

graph_builder.add_edge("voting_aggregator", "human_review")
graph_builder.add_conditional_edges(
    "human_review",
    route_on_decision,
    {"execute": "execute", "reject": "reject"}
)

graph_builder.add_edge("execute", END)
graph_builder.add_edge("reject", END)

integrated_graph = graph_builder.compile()

def run_integrated_system(user_input: str):
    """Run full integrated system"""
    initial_state = {
        "user_input": user_input,
        "parsed_intent": "",
        "action_type": "add",
        "task_data": {},
        "validation_result": {},
        "execution_result": {},
        "conflict_detected": False,
        "votes": [],
        "voting_result": {},
        "human_decision": "",
        "error": "",
        "decision_log": []
    }
    
    result = integrated_graph.invoke(initial_state)
    return result

if __name__ == "__main__":
    result = run_integrated_system("Add task: Buy milk")
    print("\n=== FINAL RESULT ===")
    print(f"Decision: {result['human_decision']}")
    print(f"Execution: {result['execution_result']}")
```

### Weeks 7-9 Success Checklist

- [ ] Completed Weeks 1-6 checklist items
- [ ] Voting system tallies votes correctly
- [ ] Weighted voting works (Security vote = 2x)
- [ ] Conflicts detected automatically (TIE outcome)
- [ ] Human review interface works (approve/reject/modify)
- [ ] Full integrated system runs end-to-end
- [ ] All decisions logged with reasoning
- [ ] Tested with conflict scenarios (agent disagreement)
- [ ] Can explain: voting mechanism, weighting, human override

---

# Weeks 10-12: Scale to Software Dev Agents

## Week 10: Architecture Design Document

Create a comprehensive specification for the software development agent system.

### Architecture Specification Template

```markdown
# Software Development Multi-Agent System
## Architecture Specification

### System Overview
- **Purpose**: Autonomous code generation and validation system
- **Agents**: 6 specialized agents with voting-based conflict resolution
- **Conflict Resolution**: Voting with weighted ballots + human override
- **Execution Model**: Parallel task execution respecting dependencies

### Agent Definitions

#### 1. Task Orchestrator (Central)
- **Role**: Decompose requirements into subtasks
- **Responsibilities**:
  - Parse user requirements
  - Break into database, backend, frontend tasks
  - Assign tasks to specialists
  - Monitor progress
  - Escalate conflicts
- **Output**: Task breakdown with dependencies

#### 2. Database Agent
- **Role**: Database schema and query design
- **Responsibilities**:
  - Design schema from requirements
  - Normalize design
  - Define constraints and indexes
  - Validate against performance requirements
- **Output**: SQL schema definitions
- **Voting Weight**: 1.5x (can influence backend decisions)

#### 3. Backend Agent
- **Role**: API and business logic design
- **Responsibilities**:
  - Design REST/GraphQL APIs
  - Implement business logic
  - Define data validation
  - Handle errors
- **Output**: Python/Node.js code
- **Voting Weight**: 1.0x
- **Dependencies**: Must await Database Agent

#### 4. Frontend Agent
- **Role**: UI component design
- **Responsibilities**:
  - Design React components
  - Define component hierarchy
  - Plan state management
  - Handle user interactions
- **Output**: React component code
- **Voting Weight**: 1.0x
- **Dependencies**: Must await Backend Agent (for API contracts)

#### 5. Security Agent
- **Role**: Vulnerability and security review
- **Responsibilities**:
  - Review all code for vulnerabilities
  - Check authentication/authorization
  - Validate data sanitization
  - Check for OWASP top 10
- **Output**: Security audit report
- **Voting Weight**: 2.0x (can veto decisions)
- **Conflicts**: Can override Backend/Frontend decisions

#### 6. QA Agent
- **Role**: Testing and performance validation
- **Responsibilities**:
  - Design test cases
  - Check query performance
  - Validate business logic coverage
  - Check for edge cases
- **Output**: Test suite and performance analysis
- **Voting Weight**: 1.5x
- **Conflicts**: Can reject if performance inadequate

### Task Dependencies

```
Requirement Input
    ↓
[Orchestrator: Parse & Decompose]
    ↓
[Database Design] (Task 1)
    ↓
[Backend Design] (Task 2) ← depends on Task 1
    ↓
[Frontend Design] (Task 3) ← depends on Task 2
    ↓
[Security Review] (Task 4) → votes on all previous
    ↓
[QA Testing] (Task 5) → votes on all previous
    ↓
[Voting & Conflict Resolution]
    ↓
[Human Review] (if conflicts)
    ↓
[Final Code Output]
```

### Conflict Scenarios

**Scenario 1: Security vs Backend**
- Security: "This endpoint needs authentication"
- Backend: "Not needed for public data"
- Resolution: Security vote = 2x, likely overrides Backend
- Outcome: Add authentication

**Scenario 2: QA vs Backend**
- QA: "This query is too slow on 1M records"
- Backend: "Works fine in testing"
- Resolution: Equal weight (1.5x vs 1.0x), slight QA bias
- Outcome: Review query, possibly escalate to Database Agent

**Scenario 3: All Disagree (Tie)**
- Security: REJECT (vulnerability)
- Backend: APPROVE (works)
- QA: REJECT (slow)
- Resolution: Tie → human review mandatory

### Voting Rules

1. **Automatic Approval**: All agents APPROVE → proceed without human
2. **Automatic Rejection**: All agents REJECT → proceed without human
3. **Weighted Majority**: weighted votes determine outcome
4. **Tie**: Human must review
5. **Security Veto**: Security REJECT = automatic human review regardless of other votes

### Human Review Interface

- Show conflict
- Show all agent reasoning
- Option to:
  - Accept majority decision
  - Reject majority decision
  - Modify agent weights
  - Request agent re-vote

### Implementation Phases

1. Week 10: Finalize architecture spec
2. Week 11: Implement system
3. Week 12: Test & refine

---
```

### Week 10 Success Checklist

- [ ] Architecture document complete (copy template above)
- [ ] 6 agents defined with clear responsibilities
- [ ] Dependencies documented and acyclic
- [ ] Voting weights assigned with justification
- [ ] 3 conflict scenarios detailed with resolution
- [ ] Can draw dependency graph
- [ ] No overlapping agent responsibilities
- [ ] Human review process documented

---

## Week 11: Implementation of Software Dev Agent System

### Full System Implementation

```python
# week10_12/software_dev_agents.py

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List
from week7.voting_system import VotingSystem, Vote, VotePosition
from week7.human_review import HumanReviewPanel
import json
from dataclasses import dataclass, field

# State Schema
class SoftwareDevState(TypedDict):
    user_requirement: str
    orchestrator_tasks: List[dict]
    database_design: dict
    backend_code: str
    frontend_code: str
    security_audit: dict
    qa_report: dict
    votes: List[dict]
    voting_result: dict
    human_decision: str
    final_output: dict
    error: str
    decision_log: List[dict]

# Nodes
def orchestrator_node(state: SoftwareDevState) -> SoftwareDevState:
    """Decompose requirements into subtasks"""
    requirement = state["user_requirement"]
    
    tasks = [
        {"id": 1, "name": "database_design", "depends_on": []},
        {"id": 2, "name": "backend_code", "depends_on": [1]},
        {"id": 3, "name": "frontend_code", "depends_on": [2]},
        {"id": 4, "name": "security_audit", "depends_on": [2, 3]},
        {"id": 5, "name": "qa_testing", "depends_on": [2, 3, 4]}
    ]
    
    state["orchestrator_tasks"] = tasks
    state["decision_log"].append({
        "agent": "Orchestrator",
        "action": "Decomposed requirements into 5 tasks",
        "tasks": tasks
    })
    
    return state

def database_agent_node(state: SoftwareDevState) -> SoftwareDevState:
    """Design database schema"""
    requirement = state["user_requirement"]
    
    design = {
        "tables": [
            {"name": "users", "fields": ["id", "email", "created_at"]},
            {"name": "tasks", "fields": ["id", "user_id", "title", "completed"]}
        ],
        "indexes": ["users.email", "tasks.user_id"],
        "constraints": ["FK tasks.user_id -> users.id"]
    }
    
    state["database_design"] = design
    return state

def backend_agent_node(state: SoftwareDevState) -> SoftwareDevState:
    """Generate backend code"""
    db_design = state.get("database_design", {})
    
    code = """
# Backend API
from fastapi import FastAPI
app = FastAPI()

@app.post("/tasks")
def create_task(user_id: int, title: str):
    # Insert into database
    return {"id": 1, "user_id": user_id, "title": title}

@app.get("/tasks/{user_id}")
def list_tasks(user_id: int):
    # Query database
    return [{"id": 1, "title": "Task 1"}]
"""
    
    state["backend_code"] = code
    return state

def frontend_agent_node(state: SoftwareDevState) -> SoftwareDevState:
    """Generate frontend code"""
    code = """
import React from 'react';

export function TaskApp() {
  return (
    <div>
      <h1>Tasks</h1>
      {/* Call /tasks endpoint from backend */}
    </div>
  );
}
"""
    
    state["frontend_code"] = code
    return state

def security_agent_node(state: SoftwareDevState) -> SoftwareDevState:
    """Review security"""
    backend = state.get("backend_code", "")
    
    audit = {
        "vulnerabilities": [],
        "warnings": ["Missing authentication check"],
        "recommendations": ["Add OAuth2", "Validate user_id ownership"]
    }
    
    vote = {
        "agent_name": "Security",
        "position": VotePosition.REJECT.value,
        "weight": 2.0,
        "reasoning": "Missing authentication on create_task endpoint"
    }
    
    state["votes"].append(vote)
    state["security_audit"] = audit
    return state

def qa_agent_node(state: SoftwareDevState) -> SoftwareDevState:
    """Review testing/performance"""
    backend = state.get("backend_code", "")
    
    report = {
        "test_coverage": 45,
        "performance_issues": [],
        "edge_cases": ["Empty task list", "Invalid user_id"]
    }
    
    vote = {
        "agent_name": "QA",
        "position": VotePosition.APPROVE.value,
        "weight": 1.5,
        "reasoning": "Code structure is sound, needs tests"
    }
    
    state["votes"].append(vote)
    state["qa_report"] = report
    return state

def voting_aggregator_node(state: SoftwareDevState) -> SoftwareDevState:
    """Aggregate votes"""
    voting_system = VotingSystem(agent_weights={
        "Security": 2.0,
        "QA": 1.5,
        "Backend": 1.0,
        "Frontend": 1.0,
        "Database": 1.5
    })
    
    # Reconstruct votes
    for vote_dict in state["votes"]:
        vote = Vote(
            agent_name=vote_dict["agent_name"],
            position=VotePosition(vote_dict["position"]),
            weight=vote_dict.get("weight", 1.0),
            reasoning=vote_dict.get("reasoning", "")
        )
        voting_system.cast_vote(vote)
    
    result = voting_system.tally_votes()
    state["voting_result"] = result
    
    return state

def route_on_conflict(state: SoftwareDevState) -> str:
    """Check if human review needed"""
    result = state["voting_result"]
    if result.get("result") in ["TIE", "REJECTED"]:
        return "human_review"
    else:
        return "finalize"

def human_review_node(state: SoftwareDevState) -> SoftwareDevState:
    """Get human decision"""
    # In real scenario, prompt human
    # For demo, auto-approve
    state["human_decision"] = "proceed"
    return state

def finalize_node(state: SoftwareDevState) -> SoftwareDevState:
    """Generate final output"""
    state["final_output"] = {
        "database": state.get("database_design"),
        "backend": state.get("backend_code"),
        "frontend": state.get("frontend_code"),
        "security_audit": state.get("security_audit"),
        "qa_report": state.get("qa_report"),
        "approval": state["voting_result"].get("result")
    }
    return state

# Build graph
graph_builder = StateGraph(SoftwareDevState)

graph_builder.add_node("orchestrator", orchestrator_node)
graph_builder.add_node("database", database_agent_node)
graph_builder.add_node("backend", backend_agent_node)
graph_builder.add_node("frontend", frontend_agent_node)
graph_builder.add_node("security", security_agent_node)
graph_builder.add_node("qa", qa_agent_node)
graph_builder.add_node("voting", voting_aggregator_node)
graph_builder.add_node("human_review", human_review_node)
graph_builder.add_node("finalize", finalize_node)

# Edges with dependencies
graph_builder.add_edge(START, "orchestrator")
graph_builder.add_edge("orchestrator", "database")
graph_builder.add_edge("database", "backend")
graph_builder.add_edge("backend", "frontend")
graph_builder.add_edge("frontend", "security")
graph_builder.add_edge("security", "qa")
graph_builder.add_edge("qa", "voting")
graph_builder.add_conditional_edges(
    "voting",
    route_on_conflict,
    {"human_review": "human_review", "finalize": "finalize"}
)
graph_builder.add_edge("human_review", "finalize")
graph_builder.add_edge("finalize", END)

software_dev_graph = graph_builder.compile()

def run_software_dev_system(requirement: str):
    """Run full system"""
    initial_state = {
        "user_requirement": requirement,
        "orchestrator_tasks": [],
        "database_design": {},
        "backend_code": "",
        "frontend_code": "",
        "security_audit": {},
        "qa_report": {},
        "votes": [],
        "voting_result": {},
        "human_decision": "",
        "final_output": {},
        "error": "",
        "decision_log": []
    }
    
    result = software_dev_graph.invoke(initial_state)
    return result

if __name__ == "__main__":
    result = run_software_dev_system("Build a task management app")
    print(json.dumps(result["final_output"], indent=2, default=str))
```

### Week 11 Testing Framework

```python
# week10_12/integration_tests.py

import unittest
from software_dev_agents import run_software_dev_system

class TestSoftwareDevAgents(unittest.TestCase):
    
    def test_full_workflow(self):
        """Test complete workflow"""
        result = run_software_dev_system("Build a task app")
        
        # Check all components generated
        self.assertIsNotNone(result["database_design"])
        self.assertIsNotNone(result["backend_code"])
        self.assertIsNotNone(result["frontend_code"])
        self.assertGreater(len(result["decision_log"]), 0)
    
    def test_voting_occurs(self):
        """Test voting mechanism"""
        result = run_software_dev_system("Build a task app")
        
        # Check votes were cast
        self.assertGreater(len(result["votes"]), 0)
        
        # Check voting result
        self.assertIn(result["voting_result"]["result"], 
                     ["APPROVED", "REJECTED", "TIE"])
    
    def test_dependencies_respected(self):
        """Test task dependencies"""
        result = run_software_dev_system("Build a task app")
        
        tasks = result["orchestrator_tasks"]
        
        # Backend should come after Database
        backend_idx = next(i for i, t in enumerate(tasks) if t["name"] == "backend_code")
        db_idx = next(i for i, t in enumerate(tasks) if t["name"] == "database_design")
        self.assertGreater(backend_idx, db_idx)

if __name__ == "__main__":
    unittest.main()
```

### Week 11 Success Checklist

- [ ] Completed Week 10 checklist items
- [ ] All 6 agents implemented
- [ ] Dependencies enforced correctly
- [ ] Voting system integrates with graph
- [ ] Human review node works
- [ ] All tests pass
- [ ] Decision log shows full trace
- [ ] System completes end-to-end without errors

---

## Week 12: Testing, Refinement & Documentation

### Testing Scenarios

```python
# week10_12/test_scenarios.py

class SoftwareDevScenarios:
    """Test realistic scenarios"""
    
    @staticmethod
    def scenario_1_simple():
        """Simple feature - no conflicts"""
        return run_software_dev_system(
            "Add ability to mark tasks as high priority"
        )
    
    @staticmethod
    def scenario_2_complex():
        """Complex feature - multiple dependencies"""
        return run_software_dev_system(
            "Implement user authentication with OAuth2, email verification, and role-based access control"
        )
    
    @staticmethod
    def scenario_3_conflict():
        """Scenario triggering security/backend conflict"""
        return run_software_dev_system(
            "Add public API endpoint without authentication"
        )
    
    @staticmethod
    def scenario_4_performance():
        """Scenario triggering QA performance concern"""
        return run_software_dev_system(
            "Add search across 10M tasks with regex matching"
        )
    
    @staticmethod
    def scenario_5_failure():
        """Scenario where agent fails gracefully"""
        return run_software_dev_system(
            ""  # Empty requirement
        )

def run_all_scenarios():
    """Run all test scenarios"""
    scenarios = [
        ("Simple Feature", SoftwareDevScenarios.scenario_1_simple),
        ("Complex Feature", SoftwareDevScenarios.scenario_2_complex),
        ("Conflict Scenario", SoftwareDevScenarios.scenario_3_conflict),
        ("Performance Scenario", SoftwareDevScenarios.scenario_4_performance),
        ("Failure Scenario", SoftwareDevScenarios.scenario_5_failure),
    ]
    
    results = []
    for name, scenario_func in scenarios:
        try:
            result = scenario_func()
            results.append({
                "scenario": name,
                "status": "PASS",
                "approval": result["voting_result"].get("result")
            })
        except Exception as e:
            results.append({
                "scenario": name,
                "status": "FAIL",
                "error": str(e)
            })
    
    return results

if __name__ == "__main__":
    results = run_all_scenarios()
    for result in results:
        status = "✓" if result["status"] == "PASS" else "✗"
        print(f"{status} {result['scenario']}: {result.get('approval', result.get('error'))}")
```

### Week 12 Refinement Checklist

- [ ] All 5 test scenarios run successfully
- [ ] Error handling works gracefully
- [ ] Logs are complete and traceable
- [ ] Documentation complete
- [ ] Code is clean and documented
- [ ] Architecture spec matches implementation
- [ ] Can explain entire system to someone else

---

# Code Templates & Examples

## Summary of All Weekly Code Files

```
week1/
├── single_agent_todo.py          # Single agent with 4 tools
├── tools.py                      # Tool definitions
└── test_week1.py                 # Test cases

week2/
├── memory.py                     # TaskMemory & ConversationMemory classes
├── multi_tool_agent.py          # Extended agent with 6+ tools
└── test_week2.py                # Persistence tests

week3/
├── logging_config.py            # StructuredLogger class
├── agent_with_errors.py         # Error handling & self-correction
└── test_week3.py                # Error recovery tests

week4/
├── agents_config.yaml           # YAML config (alternative)
├── crewai_orchestrator.py       # 3-agent CrewAI system
└── test_week4.py                # CrewAI tests

week5/
├── conflict_detection.py        # Conflict detection logic
├── crewai_with_conflicts.py    # CrewAI with voting intro
└── test_week5.py                # Conflict tests

week6/
├── state_schemas.py             # TodoState TypedDict
├── langgraph_system.py          # Complete LangGraph system
├── visualize_graph.py           # Graph visualization
└── test_week6.py                # LangGraph tests

week7/
├── voting_system.py             # VotingSystem class
├── human_review.py              # HumanReviewPanel class
└── test_week7.py                # Voting tests

week8_9/
├── integrated_todo_system.py    # Full integration: voting + graph
└── test_week8_9.py              # Integration tests

week10_12/
├── software_dev_agents.py       # Full software dev system
├── architecture_spec.md         # System specification
├── integration_tests.py          # Unit tests
├── test_scenarios.py            # Real-world scenarios
└── README.md                    # Usage guide
```

---

# Integration & Configuration Guide

## Third-Party Tools Setup

### OpenAI API

```bash
# Install OpenAI SDK
pip install openai

# Create .env file
echo "OPENAI_API_KEY=your_key_here" > .env

# Verify setup
python -c "from openai import OpenAI; print('OpenAI SDK installed')"
```

### LangChain & LangGraph

```bash
# Install LangChain ecosystem
pip install langgain langchain-openai langchain-core langgraph

# Install LangSmith for debugging (optional)
pip install langsmith

# Configure LangSmith
echo "LANGCHAIN_API_KEY=your_key_here" >> .env
echo "LANGSMITH_PROJECT=agentic_ai_training" >> .env
```

### CrewAI

```bash
# Install CrewAI
pip install crewai crewai-tools

# Verify
python -c "from crewai import Agent; print('CrewAI installed')"
```

### Full Requirements File

```
# requirements.txt

# Core
python-dotenv==1.0.0
requests==2.31.0

# OpenAI
openai==1.3.0

# LangChain ecosystem
langchain==0.1.0
langchain-core==0.1.0
langchain-openai==0.1.0
langgraph==0.0.20
langsmith==0.0.75

# CrewAI
crewai==0.1.0
crewai-tools==0.1.0

# Testing
pytest==7.4.0
unittest-xml-reporting==3.2.0

# Optional: visualization
mermaid==0.0.0
```

Install all:
```bash
pip install -r requirements.txt
```

---

# Master Checklist

## Pre-Course
- [ ] Python 3.10+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (requirements.txt)
- [ ] API keys configured (.env file)
- [ ] Git repo initialized
- [ ] Project directory structure created

## Weeks 1-3: Foundations

### Week 1
- [ ] Frontend Masters course watched (3 hrs)
- [ ] OpenAI Swarm examples reviewed
- [ ] single_agent_todo.py written
- [ ] Agent calls all 4 tools correctly
- [ ] Multi-turn conversation works
- [ ] 5+ conversation turns tested
- [ ] Code runs without errors

### Week 2
- [ ] memory.py implemented (TaskMemory class)
- [ ] ConversationMemory class working
- [ ] 6+ tools functioning
- [ ] Input validation works
- [ ] Persistent storage verified (tasks.json)
- [ ] Duplicate task detection working
- [ ] Search functionality tested
- [ ] Agent stats endpoint working

### Week 3
- [ ] logging_config.py implemented
- [ ] StructuredLogger class working
- [ ] agent_trace.json created and populated
- [ ] Agent self-correction implemented
- [ ] Error handling for 3+ error types
- [ ] Retry logic working (max 2 retries)
- [ ] "trace" command displays decision log
- [ ] Agent recovers gracefully from all error scenarios

## Weeks 4-9: Framework Deep Dive

### Week 4 (CrewAI)
- [ ] CrewAI installed
- [ ] 3 agents defined with distinct roles
- [ ] parse_task → validate_task → execute_task chain
- [ ] Task dependencies respected
- [ ] Agent roles non-overlapping
- [ ] 3 different user requests tested
- [ ] Output shows agent collaboration

### Week 5 (CrewAI with Conflicts)
- [ ] ConflictDetector class implemented
- [ ] Conflicts detected when agents disagree
- [ ] Conflict logging working
- [ ] "Delete all tasks" scenario implemented
- [ ] Agent opinions recorded with reasoning
- [ ] Validator and Storage agents express different positions

### Week 6 (LangGraph)
- [ ] LangGraph installed
- [ ] TodoState TypedDict defined
- [ ] 4 nodes implemented (parse, validate, execute, error)
- [ ] Graph compiles without errors
- [ ] Conditional edges route correctly
- [ ] State flows through nodes properly
- [ ] Graph visualization generated
- [ ] All 3 input types handled correctly

### Week 7 (Voting)
- [ ] VotingSystem class implemented
- [ ] Vote casting working
- [ ] Vote tallying correct
- [ ] Weighted voting (2x, 1.5x, 1.0x) working
- [ ] HumanReviewPanel class implemented
- [ ] Human can approve/reject/modify
- [ ] Voting history tracked
- [ ] Tie detection working

### Weeks 8-9 (Integration)
- [ ] integrated_todo_system.py complete
- [ ] All 6+ agents voting in parallel
- [ ] Voting aggregator working
- [ ] Conflicts trigger human review
- [ ] Human review panel functional
- [ ] Final output clean and complete
- [ ] Edge cases tested:
  - [ ] All agents agree (auto-approve)
  - [ ] All agents reject (auto-reject)
  - [ ] Tie scenario (requires human)
  - [ ] Security override (veto)
  - [ ] Agent timeout (handled gracefully)
- [ ] Decision log shows full trace for every decision

## Weeks 10-12: Scale to Production

### Week 10 (Architecture)
- [ ] Architecture specification document complete
- [ ] 6 agents defined with:
  - [ ] Clear role/responsibility
  - [ ] Dependencies specified
  - [ ] Voting weights assigned with justification
- [ ] 3 conflict scenarios documented with resolution
- [ ] Dependency graph acyclic
- [ ] No overlapping responsibilities
- [ ] Human review process documented
- [ ] Voting rules explicit

### Week 11 (Implementation)
- [ ] software_dev_agents.py complete
- [ ] All 6 agents implemented:
  - [ ] Orchestrator
  - [ ] Database
  - [ ] Backend
  - [ ] Frontend
  - [ ] Security
  - [ ] QA
- [ ] Task dependencies enforced:
  - [ ] Backend waits for Database
  - [ ] Frontend waits for Backend
  - [ ] Security/QA run in parallel after generation
- [ ] Voting system integrated
- [ ] Human review on conflicts
- [ ] Final output JSON well-formed
- [ ] Unit tests pass (3+ tests)
- [ ] No circular dependencies

### Week 12 (Testing & Refinement)
- [ ] All 5 test scenarios pass:
  - [ ] Simple feature (no conflicts)
  - [ ] Complex feature (multi-dependency)
  - [ ] Conflict scenario (agent disagreement)
  - [ ] Performance scenario (QA concerns)
  - [ ] Failure scenario (error recovery)
- [ ] Error handling graceful for all scenarios
- [ ] Decision logs complete and traceable
- [ ] Performance acceptable (< 30s per requirement)
- [ ] Code well-commented
- [ ] README.md complete with:
  - [ ] System overview
  - [ ] Architecture diagram
  - [ ] Usage examples
  - [ ] Troubleshooting guide
- [ ] Can explain entire system to someone unfamiliar

## Overall Completion
- [ ] 130-150 hours invested
- [ ] All code runs without errors
- [ ] 50+ tests pass
- [ ] 5+ real-world scenarios validated
- [ ] Architecture well-documented
- [ ] Ready for production use or further iteration

---

## Using This Document

**For Self-Study:**
- Follow week-by-week in order
- Check off items as completed
- Take notes in each section

**To Prompt Claude Opus:**
```
Use this training program to create a structured course with:
1. Expanded code examples for each week
2. Detailed troubleshooting for common errors
3. Alternative approaches for key concepts
4. Quizzes/assessments for each week
5. Links to external resources
```

**For Instructors:**
- Adapt timing to your cohort
- Add project presentations between weeks
- Create custom conflict scenarios
- Modify agent roles to match your domain

---

**Last Updated**: February 2026
**Version**: 1.0
**Next Review**: August 2026 (post-course refinement)
