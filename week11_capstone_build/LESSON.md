# Week 11 Lesson: Capstone Build

## What You Are Building

This week you design and begin building a complete multi-agent system from scratch. You choose one of three project options, write an architecture document before writing any code, then implement the system using every pattern from the curriculum: agent loops, MCP integration, RAG, LangGraph orchestration, multi-agent coordination, voting, evaluation, and cost tracking.

This is where the curriculum shifts from guided exercises to independent engineering. The previous 10 weeks taught individual skills. This week tests whether you can combine them into a coherent system and make the architectural decisions that hold it together.

## Core Concepts

### Architecture Before Code

The single most common mistake in capstone projects is starting to code before designing. Multi-agent systems have interacting components with dependencies, shared state, conflict scenarios, and cost implications. Discovering these during implementation leads to rewrites.

The `architecture_template.md` file has sections you must fill in before writing a line of code:

1. **Agent definitions**: What does each agent do? What tools does it use? What is its voting weight?
2. **State schema**: What data flows through the system? What does each agent read and write?
3. **Dependency graph**: Which agents depend on which? Are there circular dependencies?
4. **Conflict scenarios**: Where might agents disagree? What resolves the conflict?
5. **Evaluation plan**: What does "correct" mean for your system? What are the test cases?
6. **Cost budget**: How many tokens per request? What is the monthly cost at expected volume?

### Choosing a Project

The three options target different domains but require the same architectural components:

**Option A: DevOps Incident Response** -- Agents triage production incidents using log analysis, metrics retrieval, and runbook execution. Good if you have operations experience.

**Option B: Research Synthesis** -- Multi-agent RAG system that synthesizes findings across multiple document collections. Good if you want to deepen the RAG skills from Week 4.

**Option C: Code Generation Pipeline** -- Agents generate database schemas, API endpoints, and frontend components from a feature specification, with security review. Good if you want to extend the code review system from Weeks 7-8.

All three require: 4+ agents, MCP integration, LangGraph orchestration, voting, RAG, evaluation, cost tracking, and a UI or CLI.

### Designing Agent Roles

Each agent should have a single, clear responsibility. If you cannot describe what an agent does in one sentence, it is doing too much. Split it.

```
Good: "The Security Agent reviews generated code for vulnerabilities."
Bad: "The Security Agent reviews code, suggests fixes, and deploys patches."
```

Common mistake: creating a "coordinator" agent that does too much. The coordinator should only decompose the task and route sub-tasks. If it is also analyzing, generating, or evaluating, it will produce worse results than a focused specialist.

### State Schema Design

The state schema is the contract between agents. Design it so that:
- Each agent has clear read fields (inputs) and write fields (outputs)
- No two agents write to the same field without a reducer
- The schema captures everything needed for evaluation and debugging

```python
class CapstoneState(TypedDict):
    user_request: str                    # Input
    agent_a_output: dict                 # Written by agent A
    agent_b_output: dict                 # Written by agent B
    votes: list[dict]                    # Written by voting system
    voting_result: dict                  # Written by voting system
    requires_human_review: bool          # Written by voting system
    final_output: dict                   # Written by synthesizer
    trace: list[str]                     # Appended by every node
    errors: list[str]                    # Appended by error handlers
    cost_usd: Annotated[float, sum_reducer]  # Accumulated by all agents
```

### Incremental Build Strategy

Do not try to build all 4+ agents at once. Build incrementally:

1. Get one agent working end-to-end (input → agent → output)
2. Add the LangGraph orchestration (single-node graph)
3. Add a second agent (two-node graph, sequential)
4. Add parallel execution and the synthesizer
5. Add voting
6. Add MCP integration
7. Add RAG
8. Add evaluation
9. Add the UI

At each step, the system works. You are adding capabilities to a working system, not debugging a broken one.

## How the Pieces Connect

Every week of the curriculum feeds into this capstone:

| Week | Skill | Capstone Application |
|------|-------|---------------------|
| 1 | Agent loop, tool calling | Core of every agent |
| 2 | Tool chaining, structured output | Agent pipelines, report generation |
| 3 | MCP client | Connecting agents to external services |
| 4 | RAG | Grounding agent decisions in documents |
| 5 | MCP server | Custom service integration |
| 6 | LangGraph | Orchestration backbone |
| 7 | Multi-agent | Specialist agents with synthesizer |
| 8 | Voting | Decision resolution |
| 9 | Evaluation | Quality measurement |
| 10 | Deployment | User interface |

## Now Build It

Start with `architecture_template.md`. Fill in every section. Review the architecture (with a peer or Claude) before opening `capstone_scaffold.py`. The scaffold has the state schema, agent stubs, routing logic, and graph builder ready for customization. Rename agents, adjust the state, and implement one agent at a time.
