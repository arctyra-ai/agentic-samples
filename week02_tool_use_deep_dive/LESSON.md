# Week 2 Lesson: Tool Use Deep Dive

## What You Are Building

This week you build a research assistant that chains multiple tools in sequence -- search for information, read the results, extract key points, compare findings across sources, and produce a structured report with citations. Unlike Week 1 where the agent called one or two tools to answer a question, this agent orchestrates 4-6 tool calls in a logical pipeline.

This matters because real agent tasks are never single-step. A production agent that processes insurance claims might call tools to retrieve the policy, check coverage rules, extract claim details, cross-reference against fraud patterns, and generate a decision. The ability to design tool chains -- choosing what tools to build, what each returns, and how their outputs feed into each other -- is the core agent engineering skill.

You will also implement structured output (the agent produces JSON that validates against a schema) and session persistence (the agent remembers what it found across restarts). These are standard requirements in any production agent.

## Core Concepts

### Tool Chaining

Tool chaining means the output of one tool becomes the input to another. The LLM reads each tool's result and decides what to call next. Your job is to design tools whose outputs naturally feed into each other.

```
web_search("MCP adoption") → 3 URLs
    ↓
read_url(url_1) → article text
    ↓
extract_key_points(article_text) → ["point 1", "point 2"]
    ↓
compare_sources(all_points) → agreements, contradictions
    ↓
Final report (text, no tool call)
```

The LLM manages this flow, not your code. You provide the tools. The system prompt tells the LLM the expected workflow and when to stop. Without a stop condition, the agent will keep calling tools indefinitely (this is the most common agent bug -- you will fix it if you encounter it).

Watch for: if the agent skips steps (jumps from search to final report) or loops (keeps searching instead of reading), the problem is usually in the system prompt. Be explicit about the workflow order and the stopping condition.

### Tool Description Quality

The LLM chooses tools based entirely on descriptions. Compare these two descriptions for the same tool:

Bad: `"Extract key points from text"`

Good: `"Extract the 3-5 most important findings from a block of text. Returns a JSON list of key takeaways. Use this AFTER reading a URL to distill the content before comparing sources."`

The good description tells the LLM what the tool returns (JSON list), when to use it (after reading), and why (to distill before comparing). Specific descriptions lead to correct tool selection. Vague descriptions lead to trial-and-error.

### Structured Output with Pydantic

Instead of letting the agent return freeform text, you define a schema for the output and validate it. This guarantees downstream systems can parse the agent's response.

```python
from pydantic import BaseModel, Field

class Source(BaseModel):
    title: str
    url: str
    snippet: str
    relevance: float = Field(ge=0.0, le=1.0)

class ResearchReport(BaseModel):
    question: str
    sources: list[Source]
    confidence: float = Field(ge=0.0, le=1.0)
```

To get the LLM to produce this, include the schema in the system prompt and ask for JSON output. Then parse and validate:

```python
text = response.content[0].text
report_data = json.loads(text)
report = ResearchReport(**report_data)  # Validates against schema
```

Watch for: the LLM sometimes wraps JSON in markdown code fences (\`\`\`json ... \`\`\`). Strip those before parsing. Also, the LLM may produce JSON that is structurally valid but semantically wrong (e.g., confidence of 0.99 when it only found one vague source). Validation catches type errors, not reasoning errors.

### Session Persistence

A session stores the agent's state (sources found, findings extracted, reports generated) to disk so it can resume after a restart. This is essential for long research tasks.

```python
class SessionMemory:
    def __init__(self, session_id: str):
        self.path = Path(f"sessions/{session_id}.json")
        self.state = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            return json.loads(self.path.read_text())
        return {"sources": [], "findings": [], "reports": []}

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.state, indent=2))
```

The pattern is simple: load from disk on init, write to disk after every mutation. Production systems use databases instead of JSON files, but the principle is identical.

### When to Stop Calling Tools

This is the single most important lesson from this week. An agent without a clear stop condition will exhaust its iteration limit every time. The system prompt must include explicit instructions:

```
IMPORTANT: After 4-6 tool calls, you have enough information.
STOP calling tools and write your final report directly as text.
```

The number depends on the task. For research: 4-6 calls. For file operations: 1-3 calls. For multi-step data processing: 6-10 calls. Always set an explicit budget in the prompt, not just the max_iterations safety limit.

## How the Pieces Connect

Week 1 gave you the agent loop. This week you learn that the loop's power comes from the tools you design and the prompts that orchestrate them. The tool chaining pattern scales directly: Week 6 uses LangGraph to formalize multi-step chains as state graphs with conditional routing. The structured output pattern carries through every subsequent week -- Weeks 7-9 require agents to produce JSON that other agents consume. Session persistence evolves into checkpointing in Week 6.

## Now Build It

Open `README.md` for the exercise specification. Copy `research_agent_starter.py` to `research_agent.py` and implement the TODOs. The tools use simulated data (no real web access needed), so focus on the chaining logic, structured output validation, and session persistence. Run `pytest test_research.py -v` to validate.
