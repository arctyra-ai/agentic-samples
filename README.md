# Agentic AI Training Program

A 12-week curriculum for building multi-agent AI systems with dependency management and conflict resolution.

## Quick Start

```bash
# Clone and setup
git clone <your-repo-url>
cd agentic_ai_training
python -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your API keys

# Run Week 1
python week1/single_agent_todo.py          # OpenAI version
python week1/claude_code_todo.py           # Anthropic version
```

## Structure

```
agentic_ai_training/
├── requirements.txt
├── .gitignore
├── .env                        # Your API keys (not committed)
├── week1/                      # Single Agent TODO
│   ├── single_agent_todo.py    # OpenAI version
│   ├── claude_code_todo.py     # Anthropic version
│   ├── tools.py                # Tool definitions
│   └── test_week1.py
├── week2/                      # Multi-Tool Agent + Memory
│   ├── memory.py               # TaskMemory & ConversationMemory
│   ├── multi_tool_agent.py     # OpenAI version
│   ├── claude_code_multi_tool_agent.py  # Anthropic version
│   └── test_week2.py
├── week3/                      # Error Handling & Logging
│   ├── logging_config.py       # StructuredLogger
│   ├── agent_with_errors.py    # OpenAI version
│   ├── claude_code_agent_with_errors.py  # Anthropic version
│   └── test_week3.py
├── week4/                      # CrewAI Multi-Agent
│   ├── crewai_orchestrator.py
│   ├── agents_config.yaml
│   ├── claude_code_config.py   # Anthropic config for CrewAI
│   └── test_week4.py
├── week5/                      # Conflict Detection
│   ├── conflict_detection.py
│   ├── crewai_with_conflicts.py
│   └── test_week5.py
├── week6/                      # LangGraph State Graphs
│   ├── state_schemas.py
│   ├── langgraph_system.py
│   ├── visualize_graph.py
│   └── test_week6.py
├── week7/                      # Voting System
│   ├── voting_system.py
│   ├── human_review.py
│   └── test_week7.py
├── week8_9/                    # Full Integration
│   ├── integrated_todo_system.py
│   └── test_week8_9.py
└── week10_12/                  # Software Dev Agents
    ├── software_dev_agents.py
    ├── architecture_spec.md
    ├── integration_tests.py
    ├── test_scenarios.py
    └── README.md
```

## Two Tracks

Every week that involves direct LLM API calls has two versions:

| Track | Files | API Key |
|-------|-------|---------|
| OpenAI | `single_agent_todo.py`, `multi_tool_agent.py`, etc. | `OPENAI_API_KEY` |
| Anthropic | `claude_code_*.py` files | `ANTHROPIC_API_KEY` |

Weeks 5-12 use LangGraph and voting logic that is LLM-agnostic.

## Running Tests

```bash
# Run all tests
python -m pytest --tb=short

# Run tests for a specific week
python -m pytest week1/test_week1.py -v
python -m pytest week7/test_week7.py -v

# Run with coverage
python -m pytest --cov=. --cov-report=term-missing
```

## Curriculum Overview

| Week | Focus | Key Deliverable |
|------|-------|-----------------|
| 1 | Single Agent | Working TODO agent with tool calling |
| 2 | Multi-Tool + Memory | Agent with persistent state |
| 3 | Error Handling | Robust agent with logging |
| 4 | CrewAI | 3-agent crew with roles |
| 5 | Conflict Detection | Agents detecting disagreements |
| 6 | LangGraph | State graph with conditional routing |
| 7 | Voting System | Weighted voting + human review |
| 8-9 | Integration | Full system with voting + graph |
| 10 | Architecture | System specification document |
| 11 | Implementation | 6-agent software dev system |
| 12 | Testing | 5 scenarios, documentation |
