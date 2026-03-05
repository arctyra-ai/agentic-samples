"""Week 2: Research Assistant Agent

An agent that researches a question using multiple tools, chains their outputs,
and produces a structured report with citations.

Demonstrates: tool chaining, structured output, session persistence, Pydantic validation.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel, Field
from anthropic import Anthropic
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.llm_client import LLMClient

load_dotenv()


# --- Structured Output Schema ---

class Source(BaseModel):
    title: str
    url: str = ""
    snippet: str
    relevance: float = Field(ge=0.0, le=1.0)

class ReportSection(BaseModel):
    heading: str
    content: str
    source_indices: list[int] = Field(default_factory=list)

class ResearchReport(BaseModel):
    question: str
    sources: list[Source]
    sections: list[ReportSection]
    confidence: float = Field(ge=0.0, le=1.0)
    follow_up_questions: list[str] = Field(default_factory=list)


# --- Session Memory ---

class SessionMemory:
    """Persist research sessions to disk."""

    def __init__(self, session_id: str, sessions_dir: str = "sessions"):
        self.path = Path(sessions_dir) / f"{session_id}.json"
        self.state = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            return json.loads(self.path.read_text())
        return {
            "session_id": self.path.stem,
            "created": datetime.now().isoformat(),
            "messages": [],
            "sources": [],
            "findings": [],
            "reports": [],
        }

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.state, indent=2))

    def add_finding(self, finding: dict):
        self.state["findings"].append(finding)
        self.save()

    def add_source(self, source: dict):
        self.state["sources"].append(source)
        self.save()

    def add_report(self, report: dict):
        self.state["reports"].append(report)
        self.save()


# --- Tool Definitions ---

TOOLS = [
    {
        "name": "web_search",
        "description": "Search the web for information on a topic. Returns a list of results with titles, URLs, and snippets.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "read_url",
        "description": "Read the text content of a web page. Returns the page text (truncated to 5000 chars).",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to read"},
            },
            "required": ["url"],
        },
    },
    {
        "name": "extract_key_points",
        "description": "Extract the main points from a block of text. Returns a list of key takeaways.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to extract key points from"},
                "focus": {"type": "string", "description": "What aspect to focus on"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "compare_sources",
        "description": "Compare findings from multiple sources to identify agreements, contradictions, and gaps.",
        "input_schema": {
            "type": "object",
            "properties": {
                "findings": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of findings from different sources",
                },
            },
            "required": ["findings"],
        },
    },
    {
        "name": "generate_outline",
        "description": "Generate a report outline based on research findings. Returns section headings and key points per section.",
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "Original research question"},
                "findings": {"type": "array", "items": {"type": "string"}, "description": "Key findings"},
            },
            "required": ["question", "findings"],
        },
    },
    {
        "name": "write_section",
        "description": "Write a single section of the report given a heading and key points to cover.",
        "input_schema": {
            "type": "object",
            "properties": {
                "heading": {"type": "string"},
                "key_points": {"type": "array", "items": {"type": "string"}},
                "source_refs": {"type": "array", "items": {"type": "string"}, "description": "Source references to cite"},
            },
            "required": ["heading", "key_points"],
        },
    },
]


# --- Simulated Tool Implementations ---
# In production, these would make real HTTP requests.
# For training purposes, they return plausible structured data.

_SIMULATED_RESULTS = {
    "default": [
        {"title": "Enterprise AI Adoption Report 2026", "url": "https://example.com/enterprise-ai-2026", "snippet": "Survey of 500 enterprises shows 62% are experimenting with AI agents, 23% have scaled to production. Key barriers: integration complexity, security concerns, cost management."},
        {"title": "MCP Protocol Overview and Adoption", "url": "https://example.com/mcp-adoption", "snippet": "Model Context Protocol adoption has grown rapidly since open-sourcing. 75% of API gateway vendors plan MCP support by end of 2026. OpenAI, Google, and Microsoft have all adopted the standard."},
        {"title": "Multi-Agent Systems in Production", "url": "https://example.com/multi-agent-prod", "snippet": "Production multi-agent deployments use 15x more tokens than chat interfaces. Economics only work for high-value tasks. Weighted voting and human-in-the-loop are standard conflict resolution patterns."},
    ]
}


def execute_tool(name: str, tool_input: dict) -> str:
    """Execute a research tool."""
    try:
        if name == "web_search":
            results = _SIMULATED_RESULTS.get(tool_input["query"], _SIMULATED_RESULTS["default"])
            return json.dumps({"query": tool_input["query"], "results": results})

        elif name == "read_url":
            url = tool_input["url"]
            content_map = {
                "https://example.com/enterprise-ai-2026": (
                    "A 2026 survey of 500 enterprises found that 62% are experimenting with AI agents "
                    "and 23% have scaled agentic AI to production. The primary barriers to adoption are "
                    "integration complexity with legacy systems, security and governance concerns, and "
                    "managing the cost of multi-agent token usage. High-performing organizations are "
                    "3x more likely to have scaled agents than their peers. The key differentiator is "
                    "willingness to redesign workflows rather than layering agents onto existing processes."
                ),
                "https://example.com/mcp-adoption": (
                    "The Model Context Protocol (MCP), created by Anthropic and donated to the Linux "
                    "Foundation, has become the de facto standard for connecting AI agents to external "
                    "tools and data sources. OpenAI, Google DeepMind, Microsoft, and AWS have all adopted "
                    "MCP. By end of 2026, 75% of API gateway vendors are expected to integrate MCP features. "
                    "MCP replaces custom point-to-point integrations with a universal protocol, similar to "
                    "how USB-C standardized hardware connectivity. Organizations implementing MCP report "
                    "significantly reduced integration maintenance costs."
                ),
                "https://example.com/multi-agent-prod": (
                    "Multi-agent systems in production use 15x more tokens than single-agent chat interfaces. "
                    "The economics only justify multi-agent approaches for high-value tasks requiring diverse "
                    "expertise. Standard patterns include parallel specialist agents with a synthesizer, "
                    "weighted voting for conflict resolution, and human-in-the-loop review for edge cases. "
                    "Evaluation frameworks with ground truth datasets are essential for measuring agent quality."
                ),
            }
            return json.dumps({
                "url": url,
                "content": content_map.get(url, f"Content from {url} covering the requested topic in detail."),
                "word_count": 150,
            })

        elif name == "extract_key_points":
            text = tool_input.get("text", "")
            # Generate points based on content keywords
            points = []
            if "enterprise" in text.lower() or "adoption" in text.lower():
                points = [
                    "62% of enterprises are experimenting with AI agents, 23% at production scale",
                    "High performers are 3x more likely to scale agents successfully",
                    "Workflow redesign is the key differentiator, not just adding agents to existing processes",
                ]
            elif "mcp" in text.lower() or "protocol" in text.lower():
                points = [
                    "MCP is now the industry standard, adopted by all major vendors",
                    "75% of gateway vendors will integrate MCP by end of 2026",
                    "MCP eliminates custom integration maintenance through standardization",
                ]
            elif "multi-agent" in text.lower() or "token" in text.lower():
                points = [
                    "Multi-agent systems use 15x more tokens than chat interfaces",
                    "Economics only work for high-value tasks",
                    "Voting, human-in-the-loop, and evaluation frameworks are standard patterns",
                ]
            else:
                points = [
                    "Key finding from the source material",
                    "Supporting data point with specific metrics",
                    "Actionable implication for practitioners",
                ]
            return json.dumps({
                "key_points": points,
                "focus": tool_input.get("focus", "general"),
            })

        elif name == "compare_sources":
            findings = tool_input.get("findings", [])
            return json.dumps({
                "agreements": [
                    "All sources confirm rapid growth in agentic AI adoption",
                    "MCP standardization is accelerating enterprise integration",
                ],
                "contradictions": [
                    "Adoption rates vary: 23% scaled vs. optimistic vendor claims of higher numbers"
                ],
                "gaps": [
                    "Limited data on long-term ROI of multi-agent systems",
                    "Security governance frameworks still maturing",
                ],
                "source_count": len(findings),
            })

        elif name == "generate_outline":
            return json.dumps({
                "sections": [
                    {"heading": "Background", "points": ["Context", "Current state"]},
                    {"heading": "Key Findings", "points": ["Finding 1", "Finding 2"]},
                    {"heading": "Implications", "points": ["Impact", "Next steps"]},
                ],
            })

        elif name == "write_section":
            heading = tool_input["heading"]
            points = tool_input.get("key_points", [])
            return json.dumps({
                "heading": heading,
                "content": f"## {heading}\n\n" + "\n".join(f"- {p}" for p in points),
            })

        else:
            return json.dumps({"error": f"Unknown tool: {name}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


# --- Agent Loop ---

def run_research_agent(question: str, session_id: str = None, max_iterations: int = 15) -> dict:
    """Run the research agent to answer a question.

    Returns dict with: report (ResearchReport as dict), tool_calls, usage
    """
    client = LLMClient(provider="anthropic", budget_usd=1.00)
    session = SessionMemory(session_id or datetime.now().strftime("%Y%m%d_%H%M%S"))

    system_prompt = (
        "You are a research assistant. Given a question, use the available tools to research it.\n\n"
        "WORKFLOW (use each tool at most once or twice):\n"
        "1. web_search - find relevant sources (call ONCE)\n"
        "2. read_url - read 1-2 of the top results\n"
        "3. extract_key_points - pull out the main findings\n"
        "4. compare_sources - compare if you have multiple sources\n"
        "5. generate_outline - plan your report structure\n\n"
        "IMPORTANT: After 4-6 tool calls, you have enough information.\n"
        "STOP calling tools and write your final report directly as text.\n"
        "Do NOT call write_section -- instead, produce the complete report yourself.\n\n"
        "Your final response (with NO tool calls) must be a JSON object:\n"
        '{"question": "...", "sources": [{"title": "...", "url": "...", "snippet": "...", "relevance": 0.0-1.0}], '
        '"sections": [{"heading": "...", "content": "...", "source_indices": [0]}], '
        '"confidence": 0.0-1.0, "follow_up_questions": [...]}\n'
    )

    messages = [{"role": "user", "content": f"Research this question: {question}"}]
    all_tool_calls = []

    for iteration in range(max_iterations):
        response = client.chat(messages=messages, system=system_prompt, tools=TOOLS)
        tool_calls = client.get_tool_calls(response)

        if not tool_calls:
            text = client.get_text(response)
            # Try to parse structured output
            report = None
            try:
                # Find JSON in response
                start = text.index("{")
                end = text.rindex("}") + 1
                report_data = json.loads(text[start:end])
                report = ResearchReport(**report_data)
                session.add_report(report.model_dump())
            except (ValueError, json.JSONDecodeError, Exception):
                report = None

            return {
                "report": report.model_dump() if report else {"raw_response": text},
                "tool_calls": all_tool_calls,
                "usage": client.usage.summary(),
                "session_id": session.path.stem,
            }

        # Build assistant message
        assistant_content = []
        for block in response["content"]:
            if block["type"] == "text" and block.get("text"):
                assistant_content.append({"type": "text", "text": block["text"]})
            elif block["type"] == "tool_use":
                assistant_content.append({
                    "type": "tool_use", "id": block["id"],
                    "name": block["name"], "input": block["input"],
                })
        messages.append({"role": "assistant", "content": assistant_content})

        # Execute tools
        tool_results = []
        for tc in tool_calls:
            result = execute_tool(tc["name"], tc["input"])
            all_tool_calls.append({"tool": tc["name"], "input": tc["input"]})
            tool_results.append({
                "type": "tool_result", "tool_use_id": tc["id"], "content": result,
            })
        messages.append({"role": "user", "content": tool_results})

    return {
        "report": {"error": "Max iterations reached"},
        "tool_calls": all_tool_calls,
        "usage": client.usage.summary(),
    }


if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else "What is the current state of MCP adoption in enterprise AI?"
    print(f"Researching: {question}\n")
    result = run_research_agent(question)
    print(json.dumps(result["report"], indent=2))
    print(f"\nTool calls: {len(result['tool_calls'])}")
    print(f"Cost: ${result['usage']['estimated_cost_usd']:.4f}")
