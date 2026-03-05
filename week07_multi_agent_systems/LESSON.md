# Week 7 Lesson: Multi-Agent Systems

## What You Are Building

This week you build a code review system with 3 specialist agents (Analyzer, Security Auditor, Improver) that independently review the same code, then a Synthesizer agent combines their findings, identifies contradictions, and produces a unified report. The agents run in parallel using LangGraph.

Multi-agent systems are the architecture behind the most capable AI applications in production. A single agent with many tools hits a quality ceiling -- as you add more tools, the LLM becomes less reliable at choosing the right one, and the prompt grows too large. Splitting responsibilities across specialized agents produces better results because each agent has a focused role, a smaller tool set, and a targeted system prompt.

The cost tradeoff is real: multi-agent systems use roughly 15x more tokens than single-agent chat. This means they only make economic sense for high-value tasks where accuracy matters more than cost -- code review, compliance checking, financial analysis, medical record processing. Understanding when to use multi-agent (and when not to) is a key design skill.

## Core Concepts

### Parallel Execution in LangGraph

LangGraph runs nodes in parallel when multiple edges leave the same source. If three agents all have edges from START, they execute concurrently:

```python
builder.add_edge(START, "analyzer")
builder.add_edge(START, "security")
builder.add_edge(START, "improver")

# All three run in parallel, then feed into synthesizer
builder.add_edge("analyzer", "synthesizer")
builder.add_edge("security", "synthesizer")
builder.add_edge("improver", "synthesizer")

builder.add_edge("synthesizer", END)
```

LangGraph waits for all three agents to complete before starting the synthesizer. This is fan-out (parallel) followed by fan-in (join).

### Shared State for Agent Communication

Agents do not message each other directly. They communicate through shared state. Each agent writes to its own field in the state, and the synthesizer reads all fields.

```python
class ReviewState(TypedDict):
    code: str                        # Input: read by all agents
    filename: str                    # Input: read by all agents
    analyzer_findings: list[dict]    # Written by analyzer only
    security_findings: list[dict]    # Written by security only
    improvement_suggestions: list[dict]  # Written by improver only
    synthesized_report: dict         # Written by synthesizer only
    token_usage: Annotated[dict, merge_reducer]  # Written by all, merged
```

Watch for: when multiple agents write to the same field in the same step (like `token_usage`), you need an `Annotated` reducer. Without it, LangGraph raises `InvalidUpdateError` because its default channel only accepts one write per step. The reducer function defines how concurrent writes are merged:

```python
def _merge_token_usage(left: dict, right: dict) -> dict:
    return {
        "total_input": left.get("total_input", 0) + right.get("total_input", 0),
        "total_output": left.get("total_output", 0) + right.get("total_output", 0),
        "calls": left.get("calls", 0) + right.get("calls", 0),
    }

token_usage: Annotated[dict, _merge_token_usage]
```

### Role Separation

Each agent gets a focused system prompt that constrains its perspective:

- **Analyzer**: "Find bugs, code smells, and logic errors. Do NOT comment on security."
- **Security Auditor**: "Find security vulnerabilities. Check for SQL injection, path traversal, hardcoded secrets, unsafe deserialization."
- **Improver**: "Suggest improvements for readability, performance, error handling. Do NOT duplicate bug reports."

Without explicit boundaries, agents overlap heavily -- all three report the same SQL injection, and you get redundant findings instead of diverse perspectives. The "Do NOT" constraints are as important as the "Do" instructions.

### Synthesizer Pattern

The synthesizer is the most complex agent. It receives all findings from the specialists, identifies contradictions (Analyzer says "low severity" but Security says "critical"), deduplicates, prioritizes, and produces a final report.

```python
def synthesize(state: ReviewState) -> dict:
    client = LLMClient(provider="anthropic")
    response = client.chat(
        messages=[{"role": "user", "content": f"""
            Synthesize these code review findings:
            Analyzer: {json.dumps(state['analyzer_findings'])}
            Security: {json.dumps(state['security_findings'])}
            Improver: {json.dumps(state['improvement_suggestions'])}

            Identify contradictions. Prioritize by severity.
            Return: summary, critical_issues, recommendations, contradictions, overall_rating
        """}],
        system="You are a lead reviewer synthesizing multiple reviews.",
    )
```

Watch for: the synthesizer prompt must explicitly ask for contradictions. Without that instruction, the LLM tends to combine everything harmoniously, hiding disagreements that are actually the most valuable signal.

### Parsing LLM JSON Output

Every agent returns structured JSON, but LLMs are not reliable JSON generators. Always wrap parsing in error handling:

```python
def _parse_findings(text: str) -> list[dict]:
    try:
        start = text.index("[")
        end = text.rindex("]") + 1
        return json.loads(text[start:end])
    except (ValueError, json.JSONDecodeError):
        return [{"description": text, "severity": "info", "parse_error": True}]
```

The fallback wraps the raw text in a finding object so the pipeline never crashes on malformed output. The `parse_error` flag lets downstream code know the parsing failed.

## How the Pieces Connect

This is the first week where multiple concepts from earlier weeks converge: the agent loop (Week 1), structured output (Week 2), LangGraph orchestration (Week 6). Week 8 adds voting and conflict resolution on top of this system. Week 9 adds evaluation. By Week 10, the system gets a web UI. The multi-agent code review system built this week evolves through the next three weeks into a production-ready application.

## Now Build It

Open `README.md` for the exercise specification. Copy `code_review_agents_starter.py` to `code_review_agents.py` and implement the TODOs. Start with the state schema and one agent, verify it works in isolation, then add the other agents and the synthesizer. Run `pytest test_review.py -v` for unit tests, then `python code_review_agents.py` for the full multi-agent review. This exercise requires an Anthropic API key -- it makes 4 LLM calls per review.
