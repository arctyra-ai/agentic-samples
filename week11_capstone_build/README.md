# Week 11: Capstone Build

## Objective
Design and build a complete multi-agent system from scratch using all patterns from Weeks 1-10.

## What You Will Learn
- System architecture from requirements to implementation
- Tradeoff analysis for architectural decisions
- Integrating all curriculum components into one system

## Files
- `architecture_template.md` -- Fill this in BEFORE writing any code
- `capstone_scaffold.py` -- Starting point with state schema, agent stubs, graph builder

## Choose a Capstone Project

**Option A: DevOps Incident Response** -- Agents triage production incidents using log analysis, metrics, runbooks.

**Option B: Research Synthesis** -- Multi-agent RAG system that synthesizes findings from multiple document collections.

**Option C: Code Generation Pipeline** -- Agents generate database schema, API endpoints, frontend components, with security review.

## How to Start

1. Pick a project option
2. Fill in `architecture_template.md` completely
3. Review the architecture (with Claude Code or a peer)
4. Customize `capstone_scaffold.py` with your agents
5. Build incrementally: get one agent working before adding the next

## Requirements (all options)
- 4+ agents with distinct roles
- MCP integration for at least one external service
- LangGraph orchestration with conditional routing
- Voting/conflict resolution
- RAG component
- Evaluation pipeline with ground truth
- Cost tracking
- Streamlit UI or CLI

## Prerequisites
- All of Weeks 1-10 completed
