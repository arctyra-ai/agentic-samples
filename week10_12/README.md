# Software Development Multi-Agent System

## Overview

A multi-agent system that generates code from natural language requirements using 6 specialized agents with voting-based conflict resolution.

## Architecture

```
User Requirement
  -> Orchestrator (decompose into tasks)
    -> Database Agent (schema design)
      -> Backend Agent (API code)
        -> Frontend Agent (React components)
          -> Security Agent (audit + vote)
            -> QA Agent (test review + vote)
              -> Voting Aggregator
                -> Human Review (if conflict)
                  -> Final Output
```

## Agents

| Agent | Weight | Role |
|-------|--------|------|
| Orchestrator | N/A | Decomposes requirements |
| Database | 1.5x | Schema design |
| Backend | 1.0x | API and business logic |
| Frontend | 1.0x | UI components |
| Security | 2.0x | Vulnerability review (can veto) |
| QA | 1.5x | Testing and performance |

## Usage

```bash
# Install dependencies
pip install langgraph langchain-core

# Run the system
python software_dev_agents.py

# Run integration tests
python -m pytest integration_tests.py -v

# Run test scenarios
python test_scenarios.py
```

## Files

- `software_dev_agents.py` - Main system implementation
- `architecture_spec.md` - Architecture specification document
- `integration_tests.py` - Unit tests
- `test_scenarios.py` - 5 real-world test scenarios
- `README.md` - This file

## Voting Rules

1. All APPROVE -> auto-proceed
2. All REJECT -> auto-reject
3. Weighted majority determines outcome
4. TIE -> human review required
5. Security REJECT -> always triggers human review

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ImportError: langgraph` | Run `pip install langgraph` |
| Voting always rejects | Check agent weights in voting_aggregator_node |
| Human review not triggered | Verify route_on_conflict logic |
| Empty final output | Check that all agent nodes return state |
