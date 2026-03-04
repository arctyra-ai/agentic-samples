# Week 7: Multi-Agent Systems

## Objective
Build a 3-agent code review system where specialists independently analyze code, then a synthesizer combines their findings.

## What You Will Learn
- Multi-agent coordination with clear role separation
- Parallel agent execution in LangGraph
- Agent-to-agent communication via shared state
- Contradiction detection across agent outputs

## Files
- `code_review_agents.py` -- 3 specialists (Analyzer, Security, Improver) + Synthesizer
- `test_review.py` -- Tests for state, finding parsing, usage tracking

## How to Run
```bash
# Review a Python file
python code_review_agents.py path/to/your_file.py

# Review built-in example (has intentional SQL injection)
python code_review_agents.py
```

## How to Test
```bash
pytest test_review.py -v
```

## Success Criteria
- [ ] Each agent produces distinct findings (not repeating each other)
- [ ] Synthesizer identifies when agents disagree
- [ ] Total cost per review under $0.50
- [ ] Report includes severity ratings and specific line references

## Prerequisites
- Weeks 1-6 completed
- ANTHROPIC_API_KEY set (real LLM calls required)
