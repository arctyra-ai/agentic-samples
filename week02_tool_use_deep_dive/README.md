# Week 2: Tool Use Deep Dive

## Objective
Build a research assistant that chains tools, produces structured output, and persists sessions.

## What You Will Learn
- Tool description quality and its effect on LLM tool selection
- Tool chaining: output of one tool feeds into the next
- Structured output with Pydantic validation
- Session persistence across restarts

## Files
- `research_agent.py` -- Research assistant with 6 tools, session memory, structured reports
- `test_research.py` -- Tests for tools, sessions, structured output

## How to Run
```bash
# Default research question
python research_agent.py

# Custom question
python research_agent.py "What is the current state of MCP adoption?"
```

## How to Test
```bash
pytest test_research.py -v
```

## Success Criteria
- [ ] Agent chains tools in logical order (search -> read -> extract -> compare -> outline -> write)
- [ ] Report validates against Pydantic schema
- [ ] Session state persists to disk and survives restart
- [ ] Source tracking: every claim maps to a source
- [ ] Tool descriptions are specific enough for 100% correct selection
