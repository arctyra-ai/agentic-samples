# Week 1: Agent Fundamentals

## Objective
Build a file operations agent that uses tool calling to read, search, and summarize files.

## What You Will Learn
- The agent loop: perceive, reason, act, observe
- Tool calling with the Anthropic API
- Multi-turn conversations with tool results
- Cost tracking from day one

## Files
- `agent.py` -- Complete file operations agent (starter + reference)
- `test_agent.py` -- Unit tests (run without API key) and integration tests (require API key)

## How to Run
```bash
# Interactive mode (operates on current directory)
python agent.py

# Operate on a specific directory
python agent.py /path/to/directory
```

## How to Test
```bash
# Local tests only (no API key needed)
pytest test_agent.py -v -k "not TestAgentIntegration"

# Full tests (requires ANTHROPIC_API_KEY)
pytest test_agent.py -v
```

## Success Criteria
- [ ] Agent correctly selects tools based on user intent
- [ ] Agent handles errors (file not found, permission denied)
- [ ] Agent produces useful output for 5+ request types
- [ ] Cost per interaction stays under $0.05
- [ ] All tool calls are logged with input/output

## Key Concepts to Understand Before Moving On
- How does the agent decide which tool to call?
- What happens when no tool calls are returned? (The agent is done.)
- Why is there a max_iterations safety limit?
- How does the LLMClient track token usage?
