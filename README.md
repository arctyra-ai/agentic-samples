# Agentic AI Engineering Curriculum

Production-ready multi-agent systems with MCP, LangGraph, evaluation, and deployment.

## Quick Start

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
python week01_agent_fundamentals/agent.py
```

## Structure

| Phase | Weeks | Focus |
|-------|-------|-------|
| Foundations | 1-3 | Agent loops, tool use, MCP basics |
| Real Integrations | 4-6 | RAG, custom MCP servers, LangGraph |
| Multi-Agent Systems | 7-9 | Orchestration, voting, evaluation |
| Production | 10-12 | Deploy, monitor, capstone |

## Running Tests

```bash
# All tests
pytest

# Specific week
pytest week01_agent_fundamentals/test_agent.py -v

# Tests that don't require API keys
pytest -m "not requires_api" -v
```

## API Keys Required

- `ANTHROPIC_API_KEY` -- primary LLM provider
- `OPENAI_API_KEY` -- secondary provider (optional, for comparison)
- `LANGCHAIN_API_KEY` -- LangSmith tracing (free tier, used from Week 6)

See `agentic_ai_curriculum.md` for the full 12-week curriculum.
