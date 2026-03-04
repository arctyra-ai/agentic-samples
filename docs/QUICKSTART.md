# Agentic AI Training Program: Quick Start Guide

**Time to get started: 30 minutes**

## What You'll Build
A TODO app powered by AI agents that can:
- Understand natural language requests
- Execute tasks with multiple tools
- Maintain persistent memory
- Validate actions
- Resolve conflicts via voting
- Require human approval for risky operations

## 5-Minute Setup

### 1. Install Python & Create Environment
```bash
# Create project directory
mkdir agentic_ai_training
cd agentic_ai_training

# Create virtual environment
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install --upgrade pip
pip install openai python-dotenv requests langgraph langchain langchain-openai crewai pytest
```

### 3. Configure API Keys
```bash
# Create .env file
cat > .env << EOF
OPENAI_API_KEY=your_openai_api_key_here
LANGCHAIN_API_KEY=your_optional_langsmith_key
EOF

# Edit with your actual keys:
# - OpenAI: https://platform.openai.com/api-keys
# - LangSmith (optional): https://smith.langchain.com
```

### 4. Verify Setup
```bash
python -c "from openai import OpenAI; print('✓ OpenAI SDK ready')"
python -c "from langgraph.graph import StateGraph; print('✓ LangGraph ready')"
python -c "from crewai import Agent; print('✓ CrewAI ready')"
```

## First Agent in 10 Minutes

### Step 1: Create Your First Agent
```bash
# Create week1 directory
mkdir -p week1
cd week1
```

### Step 2: Copy & Run This Code
Create `simple_agent.py`:

```python
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define a simple tool
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Add a task to the TODO list",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"}
                },
                "required": ["title"]
            }
        }
    }
]

# Simple task storage
tasks = []

def process_tool(tool_name, tool_input):
    if tool_name == "add_task":
        tasks.append(tool_input["title"])
        return f"Added: {tool_input['title']}"
    return "Unknown tool"

# Run agent
messages = [{"role": "user", "content": "Add a task: Buy milk"}]

response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=TOOLS,
    tool_choice="auto"
)

# Check if tool was called
if response.choice[0].message.tool_calls:
    for tool_call in response.choice[0].message.tool_calls:
        result = process_tool(
            tool_call.function.name,
            __import__('json').loads(tool_call.function.arguments)
        )
        print(f"✓ {result}")
        print(f"Tasks: {tasks}")
else:
    print(response.choice[0].message.content)
```

### Step 3: Run It
```bash
python simple_agent.py
```

**Expected Output:**
```
✓ Added: Buy milk
Tasks: ['Buy milk']
```

**Congratulations! You just built your first AI agent.** 🎉

## What's Next?

### Full 12-Week Path
1. **Follow the main training document** (`agentic_ai_training_program.md`)
2. **Use the weekly code templates** provided in the `week1/`, `week2/`, etc. directories
3. **Check off items** in the Master Checklist as you complete them
4. **Troubleshoot** using the fail recovery sections

### 4-Week Accelerated Path
If you're time-constrained:
1. Use `ACCELERATED_4_WEEK.md` instead
2. Skip foundation weeks (1-3) if you're comfortable with basic agent concepts
3. Focus on Weeks 6-9 (LangGraph + Voting)
4. Compress Weeks 10-12 into 1 week

### Learn by Doing
Best approach:
1. Read a week's learning section
2. Type out the code templates (don't copy-paste initially)
3. Modify the code to test your understanding
4. Compare your version with the template
5. Move to next week

## Common Issues & Fixes

### "ModuleNotFoundError: No module named 'openai'"
```bash
pip install openai
```

### "Invalid API key"
- Check `.env` file has correct key
- Regenerate key at https://platform.openai.com/api-keys
- Verify no extra spaces/quotes

### "Graph doesn't compile"
- Check StateGraph imports: `from langgraph.graph import StateGraph, START, END`
- Verify node names match edge definitions
- Check for circular dependencies

### Agent doesn't call tools
- Verify TOOLS list is properly formatted (valid JSON)
- Check function names are in lowercase/snake_case
- Ensure tool_choice="auto" is set

## Recommended Learning Schedule

### Week 1-2: Fundamentals
- **Time**: 4 hours per week
- **Focus**: Understand tool calling, agent loops, memory
- **Deliverable**: Working TODO agent

### Week 3-5: Frameworks
- **Time**: 5 hours per week
- **Focus**: CrewAI basics, task dependencies
- **Deliverable**: Multi-agent TODO system

### Week 6-8: Advanced
- **Time**: 6 hours per week
- **Focus**: LangGraph, voting, conflict resolution
- **Deliverable**: Integrated system with voting

### Week 9-12: Production
- **Time**: 8 hours per week
- **Focus**: Architecture design, implementation, testing
- **Deliverable**: Software dev agent system

## Key Concepts at a Glance

### Tool Calling
Agent tells you to execute a function. You run it and tell the agent the result.

```python
# Agent decides to call this tool
{
    "tool_name": "add_task",
    "arguments": {"title": "Buy milk"}
}

# You execute and return result
"Added: Buy milk"

# Agent gets result and continues
```

### Task Dependencies
Task B can't start until Task A completes.

```python
Task 1: Design Database
   ↓
Task 2: Write Backend (waits for Task 1)
   ↓
Task 3: Write Frontend (waits for Task 2)
```

### Voting
When agents disagree, they vote. Majority + human review = final decision.

```python
Agent A: "APPROVE" (confidence: 0.9)
Agent B: "REJECT" (confidence: 0.8)
         → Aggregate votes
         → Decision: Depends on weights
         → If tie: Human review required
```

### State Graphs
Nodes represent tasks. Edges represent flow. Conditional edges = branching logic.

```python
graph:
  [Parse Input] → [Validate] → [Execute]
                      ↓
                  [Error Handler] (if invalid)
```

## Resources

### Documentation
- **OpenAI Function Calling**: https://platform.openai.com/docs/guides/function-calling
- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **CrewAI**: https://docs.crewai.com/
- **LangChain**: https://python.langchain.com/docs/

### Tools
- **LangSmith** (debugging): https://smith.langchain.com
- **VS Code + Pylance** (IDE): https://code.visualstudio.com
- **Cursor** (AI-assisted coding): https://cursor.sh

### Community
- **LangChain Discord**: https://discord.gg/cU2adEyC7w
- **CrewAI GitHub**: https://github.com/joaomdmoura/crewai
- **OpenAI Community**: https://community.openai.com

## Success Metrics

By the end of Week 1, you should be able to:
- [ ] Explain what tool calling is
- [ ] Create a working agent with 4+ tools
- [ ] Maintain conversation context across 5+ turns
- [ ] Understand agent loops (reasoning → tool call → result → response)

By Week 6, you should:
- [ ] Understand state graphs (nodes, edges, conditional routing)
- [ ] Build workflows with dependencies
- [ ] Visualize agent workflows

By Week 12, you should:
- [ ] Design multi-agent systems with complex workflows
- [ ] Implement conflict resolution via voting
- [ ] Build production-ready agent systems
- [ ] Explain architecture to a technical audience

## Questions?

If you get stuck:
1. **Check the fail recovery sections** in the main training document
2. **Review the code templates** for that week
3. **Run the test files** to see expected behavior
4. **Check logs** (agent_trace.json, logs/)
5. **Ask Claude** - use the prompt templates in `CLAUDE_PROMPTS.md`

---

**Ready?** Start with Week 1 code in `week1/single_agent_todo.py`

**Estimated total time:** 130-150 hours over 12 weeks (~10-12 hours/week)
