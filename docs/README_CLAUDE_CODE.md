# Agentic AI Training Program - Claude Code Edition

**Use Claude models instead of OpenAI for the entire training program**

This edition is optimized for Claude Code, Anthropic's native tool for agentic AI development.

---

## 📋 What's Different

| Aspect | OpenAI Edition | Claude Code Edition |
|--------|---|---|
| **Primary SDK** | `openai` | `anthropic` |
| **IDE Support** | LangChain tools | Cursor native |
| **Tool Protocol** | Function calling | Native + MCP |
| **Context Window** | 128K | 200K |
| **Best For** | Chat | Task automation |
| **Cost** | Higher | Lower |

---

## 🚀 Quick Start (5 minutes)

### Step 1: Install
```bash
# Python 3.10+
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install Claude Code dependencies
pip install anthropic python-dotenv

# Optional: Install Claude Code CLI
pip install claude-code
```

### Step 2: Configure
```bash
# Create .env file
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# Get key from: https://console.anthropic.com/api-keys
```

### Step 3: Run Week 1 (Claude Code Version)
```bash
python week1_claude_code_todo.py
```

**You'll see:**
```
===============================================================
  TODO Agent - Multi-Turn Conversation (Claude Code Edition)
===============================================================

Try these commands:
  'Add a task: Buy milk'
  'List all my tasks'
  'Mark task 1 complete'
  'Delete task 2'

You: Add a task: Buy milk
  → Calling add_task
  ✓ add_task executed
Agent: I've added "Buy milk" to your TODO list!
```

---

## 📁 Files in This Edition

### Main Documents
- **agentic_ai_training_program.md** - Full 12-week curriculum (works with both)
- **CLAUDE_CODE_SETUP.md** ⭐ **START HERE** - Migration guide from OpenAI to Claude
- **QUICKSTART.md** - 30-minute setup
- **ACCELERATED_4_WEEK.md** - Fast-track version

### Code Examples (Claude Code Versions)
- **week1_claude_code_todo.py** ⭐ **Run this first** - Single agent with Claude
- week1_single_agent_todo.py - OpenAI version (for comparison)
- week6_langgraph_todo.py - Works with both OpenAI and Claude
- week7_voting_system.py - Works with both

### Reference Materials
- **CLAUDE_PROMPTS.md** - Reusable prompts for Claude Opus
- **ARCHITECTURE_DIAGRAMS.md** - System visualizations
- **README.md** - This file

---

## 🎯 Why Claude Code?

### ✅ Better for Multi-Agent Systems
- Designed for task automation workflows
- Natural reasoning about conflicts
- Superior task decomposition

### ✅ Higher Context Window
- 200K tokens vs 128K (GPT-4)
- Keeps full conversation history
- Better state management

### ✅ Lower Cost
- ~5x cheaper for input tokens
- Competitive output pricing
- Volume discounts available

### ✅ Better IDE Integration
- Native support in Cursor
- `claude-code` CLI for automation
- MCP for tool integration

---

## 📚 Reading Order

1. **CLAUDE_CODE_SETUP.md** (20 min)
   - Understand OpenAI vs Claude differences
   - See migration examples
   - Cost comparison

2. **week1_claude_code_todo.py** (10 min)
   - Read the annotated code
   - Understand Claude's response structure
   - Note the key differences

3. **Run the example** (5 min)
   ```bash
   python week1_claude_code_todo.py
   ```

4. **Follow main training** (130-150 hours)
   - Use agentic_ai_training_program.md
   - Adapt code examples using patterns from week1_claude_code_todo.py
   - All major frameworks support Claude

---

## 🔄 Key Differences from OpenAI

### 1. Client Initialization
```python
# OpenAI
from openai import OpenAI
client = OpenAI()

# Claude Code
from anthropic import Anthropic
client = Anthropic()
```

### 2. API Call
```python
# OpenAI
response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=TOOLS,
    tool_choice="auto"
)

# Claude Code
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    system="Your instructions here",
    tools=TOOLS,
    messages=messages
)
```

### 3. Response Handling
```python
# OpenAI
if response.choice[0].message.tool_calls:
    for tool_call in response.choice[0].message.tool_calls:
        tool_name = tool_call.function.name
        tool_input = json.loads(tool_call.function.arguments)

# Claude Code
for content_block in response.content:
    if content_block.type == "tool_use":
        tool_name = content_block.name
        tool_input = content_block.input
```

### 4. Tool Format
```python
# OpenAI
{
    "type": "function",
    "function": {
        "name": "add_task",
        "parameters": {...}
    }
}

# Claude Code
{
    "name": "add_task",
    "description": "...",
    "input_schema": {...}
}
```

---

## ✅ Implementation Checklist

### Pre-Course
- [ ] Python 3.10+ installed
- [ ] Virtual environment created
- [ ] `anthropic` package installed
- [ ] API key set in `.env`
- [ ] Verified: `python -c "from anthropic import Anthropic; print('✓')"`

### Week 1
- [ ] Read CLAUDE_CODE_SETUP.md
- [ ] Understand Claude response structure
- [ ] Run week1_claude_code_todo.py
- [ ] Test with 3+ commands
- [ ] Can explain differences from OpenAI

### Week 2-5
- [ ] Adapt code examples using Claude patterns
- [ ] Test with Claude models instead of OpenAI
- [ ] Monitor API costs (should be lower)

### Week 6+
- [ ] Use LangChain with ChatAnthropic
- [ ] Voting system works with Claude
- [ ] Full integration test passes

---

## 💡 Tips for Success

### Use Claude's Strengths
Claude is better at:
- Task decomposition (Weeks 10-12)
- Conflict reasoning (Week 7-9)
- Complex decision trees (voting)
- Maintaining context (200K window)

### Leverage the Larger Context
- Send full conversation history
- Include system prompts
- Reference past decisions
- Maintain decision logs

### Cost Optimization
- Use smaller models for simple tasks
- Batch similar requests
- Leverage context window (fewer prompts)
- Monitor usage at https://console.anthropic.com

### IDE Integration
- Install Cursor for Claude Code support
- Use `claude-code` CLI for automation
- Let Claude Code help fix errors
- Use for code generation assistance

---

## 🐛 Troubleshooting

### "Invalid API key"
```bash
# Check your key
echo $ANTHROPIC_API_KEY

# Get new key from:
# https://console.anthropic.com/api-keys

# Update .env file
echo "ANTHROPIC_API_KEY=your_new_key" > .env
```

### "Tool not found"
- Check tool name in response (should match definition)
- Ensure input_schema is valid JSON
- Claude may not use tools if task is trivial - add more complex request

### "Rate limited"
- Account for rate limits on free tier
- Use paid API key for testing
- Batch requests when possible

### "Context exceeded"
- 200K limit is generous, but remember token counting
- Split very long conversations
- Summarize old messages

---

## 📊 Model Selection

### For This Training

| Week | Task | Recommended Model |
|------|------|-------------------|
| 1-3 | Single agent | claude-3-5-sonnet |
| 4-6 | Multi-agent | claude-3-5-sonnet |
| 7-9 | Voting/conflicts | claude-3-5-sonnet |
| 10-12 | Software dev system | claude-3-5-sonnet |

**Note:** claude-3-5-sonnet is the best balance of cost and performance for this training.

### Model Comparison
```
claude-3-5-sonnet (Recommended)
  - Best for most tasks
  - Good speed/cost tradeoff
  - Excellent reasoning
  - Use for entire training

claude-3-opus (Premium)
  - Best reasoning
  - Slowest
  - Most expensive
  - Use only if sonnet insufficient

claude-3-haiku (Budget)
  - Fastest
  - Cheapest
  - Limited reasoning
  - Not recommended for this training
```

---

## 🚀 Next Steps

1. **Right now:** Read CLAUDE_CODE_SETUP.md
2. **Next 10 min:** Run week1_claude_code_todo.py
3. **This week:** Complete Week 1 with Claude
4. **Next 12 weeks:** Follow agentic_ai_training_program.md using Claude models

---

## 📖 Full Learning Path

```
START
  ↓
CLAUDE_CODE_SETUP.md (20 min)
  ↓
week1_claude_code_todo.py (10 min read + 5 min run)
  ↓
QUICKSTART.md (30 min hands-on)
  ↓
Week 1-3: agentic_ai_training_program.md (Weeks 1-3)
  - Adapt code using Claude patterns
  - Test with claude-3-5-sonnet
  
Week 4-6: Frameworks (CrewAI/LangGraph with Claude)
  - Use ChatAnthropic instead of ChatOpenAI
  - langgraph works perfectly with Claude
  
Week 7-9: Voting System
  - Use Claude for agent reasoning
  - Leverage 200K context window
  
Week 10-12: Production System
  - Full software dev agent system
  - Multi-agent voting with Claude
  
COMPLETION
  ↓
Have production-ready multi-agent system
```

---

## 🤝 Support

### Get Help
- **Claude Code Docs:** https://docs.anthropic.com/
- **API Reference:** https://docs.anthropic.com/messages/getting-started-with-the-api
- **SDK Repo:** https://github.com/anthropics/anthropic-sdk-python
- **Cursor IDE:** https://cursor.sh

### Keep Learning
- Read CLAUDE_PROMPTS.md for expansion ideas
- Study ARCHITECTURE_DIAGRAMS.md for system design
- Join Anthropic community (https://discord.gg/anthropic)

---

## 📊 Training Statistics

**Claude Code Edition:**
- 12 weeks
- 130-150 hours total
- 3 runnable code examples
- 14 reusable Claude prompts
- 12 system architecture diagrams
- 100+ success checkpoints

**Cost Estimate:**
- API costs: ~$15-30 (vs $20-43 with OpenAI)
- Time: 130-150 hours
- ROI: Production-ready multi-agent system

---

## ✨ What You'll Build

By Week 12, you'll have:

✅ **Single Agent** (Week 1) - TODO app with tool calling
✅ **Multi-Tool Agent** (Week 2) - Persistent memory
✅ **Robust Agent** (Week 3) - Error handling
✅ **Multi-Agent Team** (Weeks 4-5) - With dependencies
✅ **State Graphs** (Week 6) - LangGraph system
✅ **Voting System** (Week 7) - Conflict resolution
✅ **Integrated System** (Weeks 8-9) - Full voting + graph
✅ **Architecture Design** (Week 10) - Specification
✅ **Software Dev Agents** (Week 11) - Multi-agent coding system
✅ **Production Ready** (Week 12) - Tested and documented

---

**Ready to start?**

```bash
# 1. Read this file (5 min)
# 2. Read CLAUDE_CODE_SETUP.md (20 min)
# 3. Run week1_claude_code_todo.py (10 min)
# 4. Start Week 1 of training (8-10 hrs)

python week1_claude_code_todo.py
```

---

**Last Updated:** March 4, 2026  
**Version:** Claude Code Edition 1.0
