# Training Program: Claude Code Edition

**Switch from OpenAI to Claude Code for agentic AI development**

This guide shows how to adapt the training program to use Claude Code and the Anthropic API instead of OpenAI.

---

## Why Claude Code for This Training?

| Aspect | OpenAI (Original) | Claude Code (Recommended) |
|--------|-------------------|--------------------------|
| **Tool Integration** | Manual tool definitions | MCP (Model Context Protocol) - built-in |
| **Agent Paradigm** | Function calling | Agentic reasoning loops |
| **Async Tasks** | Limited native support | Built for parallel/sequential |
| **Context Window** | 128K (GPT-4) | 200K (Claude 3.5) |
| **Cost** | Higher per token | Competitive |
| **Use Case Fit** | Chat-first | Task automation-first |
| **IDE Integration** | Via LangChain | Native in Cursor |

**Result:** Claude Code is purpose-built for the multi-agent voting system you're building.

---

## Installation & Setup

### Option A: Claude Code CLI (Recommended)

```bash
# Install Claude Code
pip install claude-code

# Verify installation
claude-code --version

# Configure API key
export ANTHROPIC_API_KEY=your_key_here

# Or create .env file
echo "ANTHROPIC_API_KEY=your_key_here" > .env
```

### Option B: Direct Anthropic SDK (For Custom Integration)

```bash
# Install only what you need
pip install anthropic python-dotenv

# Verify
python -c "from anthropic import Anthropic; print('✓ Ready')"
```

### Updated requirements.txt

Replace the original with:

```txt
# Core
python-dotenv==1.0.0

# Anthropic (Claude models)
anthropic==0.28.0

# LangChain with Claude support (optional, for advanced workflows)
langchain==0.1.0
langchain-core==0.1.0
langchain-anthropic==0.1.0
langgraph==0.0.20

# MCP (Model Context Protocol - for tool integration)
mcp==0.5.0

# Testing
pytest==7.4.0

# Optional: IDE integration
cursor==latest
```

Install:
```bash
pip install -r requirements.txt
```

---

## Updated: Week 1 with Claude Code

### Original Week 1 (OpenAI)
```python
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=TOOLS
)
```

### Claude Code Version
```python
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Claude naturally reasons about tools without explicit definitions
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",  # Latest Claude model
    max_tokens=2048,
    system="You are a helpful TODO assistant. You have access to these tools: add_task, list_tasks, mark_complete, delete_task",
    messages=messages,
    tools=TOOLS  # Same tool definitions work
)
```

---

## Week 1 Complete Code: Claude Version

```python
#!/usr/bin/env python3
"""
Week 1: Single Agent TODO with Claude Code
"""

import json
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# Initialize Claude client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Define tools (same as OpenAI format)
TOOLS = [
    {
        "name": "add_task",
        "description": "Add a new task to the TODO list",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Task title"},
                "description": {"type": "string", "description": "Task description"}
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
                "task_id": {"type": "integer", "description": "Task ID"}
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
                "task_id": {"type": "integer", "description": "Task ID"}
            },
            "required": ["task_id"]
        }
    }
]

# Task storage
tasks = []
next_id = 1

def add_task(title, description=""):
    global next_id
    task = {"id": next_id, "title": title, "description": description, "completed": False}
    tasks.append(task)
    next_id += 1
    return {"success": True, "task": task}

def list_tasks():
    return {"tasks": tasks}

def mark_complete(task_id):
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = True
            return {"success": True, "task": task}
    return {"error": "Task not found"}

def delete_task(task_id):
    global tasks
    original_len = len(tasks)
    tasks = [t for t in tasks if t["id"] != task_id]
    return {"success": len(tasks) < original_len}

def process_tool_call(tool_name, tool_input):
    """Execute tool based on Claude's request"""
    if tool_name == "add_task":
        return add_task(tool_input.get("title"), tool_input.get("description", ""))
    elif tool_name == "list_tasks":
        return list_tasks()
    elif tool_name == "mark_complete":
        return mark_complete(tool_input.get("task_id"))
    elif tool_name == "delete_task":
        return delete_task(tool_input.get("task_id"))
    return {"error": "Unknown tool"}

def multi_turn_agent():
    """Interactive TODO agent using Claude"""
    messages = []
    
    print("\n" + "="*60)
    print("  Claude TODO Agent")
    print("="*60 + "\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        # Add user message
        messages.append({"role": "user", "content": user_input})
        
        # Call Claude (note: different parameter names than OpenAI)
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system="You are a helpful TODO assistant. Use the available tools to help manage tasks.",
            tools=TOOLS,
            messages=messages
        )
        
        # Process response
        assistant_message = {"role": "assistant", "content": response.content}
        messages.append(assistant_message)
        
        # Handle tool use
        tool_results = []
        for content_block in response.content:
            if content_block.type == "tool_use":
                tool_name = content_block.name
                tool_input = content_block.input
                
                result = process_tool_call(tool_name, tool_input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": content_block.id,
                    "content": json.dumps(result)
                })
                
                print(f"  → {tool_name}")
            
            elif content_block.type == "text":
                if content_block.text:
                    print(f"Agent: {content_block.text}\n")
        
        # If tools were used, add results and continue conversation
        if tool_results:
            messages.append({"role": "user", "content": tool_results})

if __name__ == "__main__":
    multi_turn_agent()
```

**Key differences:**
- `Anthropic()` instead of `OpenAI()`
- `model="claude-3-5-sonnet-20241022"` instead of `"gpt-4"`
- Tool format uses `input_schema` (not `parameters`)
- Response handling for `tool_use` blocks
- No `tool_choice="auto"` needed - Claude handles this naturally

---

## Week 6: LangGraph with Claude

LangGraph works perfectly with Claude. Just change the model:

```python
# In your LLM calls within nodes:
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    temperature=0,
    max_tokens=2048,
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Use in LangGraph nodes
response = llm.invoke(prompt)
```

**Advantages over OpenAI:**
- 200K context window (vs 128K)
- Better reasoning for complex multi-step workflows
- Superior performance on task decomposition
- Native support for agentic patterns

---

## Week 7-9: Voting System with Claude

The voting system code remains largely the same, but use Claude for:

1. **Agent reasoning** - Let Claude reason about conflicts
2. **Proposal generation** - Claude proposes actions
3. **Voting justification** - Claude explains its position

```python
# Have Claude vote on proposed action
def get_agent_vote(agent_role, proposed_action, context):
    """Use Claude to generate agent vote"""
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        system=f"You are a {agent_role} agent evaluating proposals.",
        messages=[{
            "role": "user",
            "content": f"Should we approve: {proposed_action}?\n\nContext: {context}\n\nRespond with: APPROVE or REJECT"
        }]
    )
    
    text = response.content[0].text
    position = VotePosition.APPROVE if "APPROVE" in text.upper() else VotePosition.REJECT
    
    return Vote(
        agent_name=agent_role,
        position=position,
        reasoning=text[:200]  # Use Claude's reasoning
    )
```

---

## Claude Code CLI Usage

Once installed, you can delegate tasks directly:

```bash
# Run a specific Python file with Claude oversight
claude-code run week1_single_agent_todo.py

# Have Claude fix errors
claude-code debug week1_single_agent_todo.py

# Have Claude optimize code
claude-code optimize week6_langgraph_todo.py

# Have Claude test code
claude-code test week7_voting_system.py
```

---

## MCP Integration (Advanced)

Use Model Context Protocol for tool definitions:

```python
from mcp.client import ClientSession
from mcp.types import TextContent

# Define tools via MCP
async def setup_mcp_tools():
    async with ClientSession() as session:
        # Register your tools
        await session.initialize()
        
        # Claude can now access tools via MCP
        # No manual tool definitions needed
```

Benefits:
- Tools defined once, used everywhere
- Automatic tool discovery
- Better tool composition

---

## Comparison: Code Examples

### Adding a Task (OpenAI)
```python
from openai import OpenAI
client = OpenAI()

messages = [
    {"role": "user", "content": "Add task: Buy milk"}
]

response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=TOOLS,
    tool_choice="auto"
)

# Process: response.choice[0].message.tool_calls
```

### Adding a Task (Claude)
```python
from anthropic import Anthropic
client = Anthropic()

messages = [
    {"role": "user", "content": "Add task: Buy milk"}
]

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=messages,
    tools=TOOLS
)

# Process: [block for block in response.content if block.type == "tool_use"]
```

**Key differences:**
- Claude's response structure (blocks) vs OpenAI's (tool_calls)
- 200K vs 128K context
- Different pricing model

---

## Updated Master Checklist for Claude Code

Replace API-specific items:

**Pre-Course Setup**
- [ ] Python 3.10+ installed
- [ ] Virtual environment created
- [ ] `pip install -r requirements_claude.txt`
- [ ] `.env` file with `ANTHROPIC_API_KEY`
- [ ] Claude Code CLI installed: `pip install claude-code`
- [ ] Verified: `claude-code --version`

**Week 1**
- [ ] Installed `anthropic` SDK
- [ ] API key configured
- [ ] `week1_single_agent_todo.py` runs without errors
- [ ] Agent calls tools correctly with Claude
- [ ] Can switch between OpenAI/Claude examples

**Weeks 6-9**
- [ ] LangGraph configured with Claude
- [ ] ChatAnthropic imported and used
- [ ] Voting system works with Claude reasoning
- [ ] Human review interface functional

---

## Cost Comparison

### OpenAI (Original Training)
```
Week 1-3 (testing): ~$2-5
Week 4-6 (frameworks): ~$5-10
Week 7-9 (voting): ~$3-8
Week 10-12 (software dev system): ~$10-20
Total: ~$20-43
```

### Claude Code (Recommended)
```
Week 1-3 (testing): ~$1-3
Week 4-6 (frameworks): ~$3-7
Week 7-9 (voting): ~$2-5
Week 10-12 (software dev system): ~$8-15
Total: ~$14-30

Note: Anthropic offers 15% discount for larger token volumes
Plus: 200K context window reduces prompts needed
```

---

## Migration Guide

If you've started with OpenAI, here's how to switch:

### Step 1: Update imports
```python
# Before
from openai import OpenAI
client = OpenAI(api_key=...)

# After
from anthropic import Anthropic
client = Anthropic(api_key=...)
```

### Step 2: Update API calls
```python
# Before
response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=TOOLS,
    tool_choice="auto"
)

# After
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2048,
    messages=messages,
    tools=TOOLS
)
```

### Step 3: Update response handling
```python
# Before
if response.choice[0].message.tool_calls:
    for tool_call in response.choice[0].message.tool_calls:
        ...

# After
for content_block in response.content:
    if content_block.type == "tool_use":
        ...
```

### Step 4: Test
```bash
python week1_single_agent_todo.py
python week6_langgraph_todo.py demo
python week7_voting_system.py
```

---

## Claude Code Advantages for This Training

1. **Agentic Reasoning**
   - Claude is optimized for multi-step reasoning
   - Better at task decomposition (Week 10-12)
   - Stronger conflict resolution logic (Week 7-9)

2. **Context Window**
   - 200K tokens lets you include full conversation history
   - Better state management across agents
   - Reduces need for summarization

3. **Tool Integration**
   - MCP support out of the box
   - Better tool composition
   - Native async/parallel execution

4. **Ecosystem Alignment**
   - Claude Code CLI built specifically for this pattern
   - Works with Cursor IDE
   - Integrates with Anthropic's full stack

5. **Developer Experience**
   - Simpler API (fewer parameters to manage)
   - Better error messages
   - Built-in thinking (extended thinking mode)

---

## Recommended Setup

Use **Claude Code + LangGraph + Anthropic**:

```bash
# Requirements
pip install anthropic langchain-anthropic langgraph python-dotenv

# Run Claude Code
export ANTHROPIC_API_KEY=your_key
claude-code run week1_single_agent_todo.py

# Use within Cursor IDE for best experience
# Cursor → View → Command Palette → Claude Code
```

---

## Next Steps

1. **Update your `.env`** with `ANTHROPIC_API_KEY`
2. **Install Claude Code CLI**: `pip install claude-code`
3. **Run adapted Week 1** using code above
4. **Use Claude Code for debugging**: `claude-code debug week1_single_agent_todo.py`
5. **Follow remaining weeks** with Claude models

---

## Resources

- **Anthropic API Docs**: https://docs.anthropic.com/
- **Claude Models**: https://docs.anthropic.com/claude/reference/getting-started-with-the-api
- **Claude Code CLI**: https://docs.anthropic.com/en/docs/build-with-claude/code
- **LangChain + Anthropic**: https://python.langchain.com/docs/integrations/chat/anthropic
- **Cursor IDE**: https://cursor.sh (has built-in Claude Code support)

---

## Summary

| Aspect | OpenAI Version | Claude Code Version |
|--------|----------------|-------------------|
| **SDK** | `openai` | `anthropic` |
| **Model** | `gpt-4` | `claude-3-5-sonnet-20241022` |
| **Tools** | Function calling | Native tool use |
| **MCP** | Via LangChain | Built-in |
| **IDE** | LangChain tools | Cursor native |
| **Best for** | Chat applications | Task automation |
| **Cost** | Higher | Lower |
| **Learning curve** | Moderate | Gentle |

**Recommendation:** Use Claude Code version for this training - it's purpose-built for multi-agent task automation.

---

**Ready?** Update your setup and run Week 1 with Claude!
