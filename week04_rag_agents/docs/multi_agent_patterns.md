# Multi-Agent Design Patterns

## When to Use Multiple Agents

Multi-agent systems use 15x more tokens than single-agent chat interactions. Only use them when:
- The task requires genuinely different expertise areas
- Agents need to provide independent assessments (to catch errors)
- The workflow has natural parallelism (agents can run concurrently)
- You need voting or consensus mechanisms for high-stakes decisions

Do not use multi-agent when a single agent with more tools would suffice.

## Pattern 1: Parallel Specialists

Multiple agents analyze the same input independently, then a synthesizer combines their findings.

```
Input -> [Agent A] --\
Input -> [Agent B] ----> [Synthesizer] -> Output
Input -> [Agent C] --/
```

Use when: You need diverse perspectives on the same data (e.g., code review with quality, security, and performance specialists).

## Pattern 2: Sequential Pipeline

Each agent handles one stage, passing output to the next.

```
Input -> [Agent A] -> [Agent B] -> [Agent C] -> Output
```

Use when: Tasks have natural ordering (e.g., classify document, extract entities, validate, store).

## Pattern 3: Orchestrator with Workers

A central orchestrator decomposes the task and delegates to specialist workers.

```
Input -> [Orchestrator] -> [Worker 1] -> [Orchestrator]
                        -> [Worker 2] -> [Orchestrator] -> Output
                        -> [Worker 3] -> [Orchestrator]
```

Use when: The task decomposition itself requires intelligence (e.g., breaking a feature request into database, backend, and frontend subtasks).

## Communication via Shared State

Agents in LangGraph do not message each other directly. Instead, they read from and write to a shared state object. This is simpler to debug and reason about than direct messaging.

```python
class ReviewState(TypedDict):
    code: str                        # Input (read by all agents)
    analyzer_findings: list[dict]    # Written by analyzer
    security_findings: list[dict]    # Written by security auditor
    synthesized_report: dict         # Written by synthesizer
```

## Voting and Conflict Resolution

When agents disagree, you need a resolution mechanism:
- **Weighted voting**: Security agent's opinion counts more than style suggestions
- **Veto power**: A security BLOCK overrides all other approvals
- **Human-in-the-loop**: Ties and vetoes escalate to a human reviewer
- **Confidence thresholds**: Low-confidence decisions automatically escalate

## Cost Management

Track token usage per agent, per request. Set budgets. Multi-agent systems can become expensive quickly if agents generate verbose outputs or make unnecessary tool calls.
