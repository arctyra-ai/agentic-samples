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
        {"title": "Overview Article", "url": "https://example.com/overview", "snippet": "A comprehensive overview of the topic covering key aspects and recent developments."},
        {"title": "Research Paper", "url": "https://example.com/paper", "snippet": "Recent research findings suggest significant progress in this area."},
        {"title": "Industry Report", "url": "https://example.com/report", "snippet": "Market analysis shows growing adoption across enterprise sectors."},
    ]
}


def execute_tool(name: str, tool_input: dict) -> str:
    """Execute a research tool."""
    try:
        if name == "web_search":
            results = _SIMULATED_RESULTS.get(tool_input["query"], _SIMULATED_RESULTS["default"])
            return json.dumps({"query": tool_input["query"], "results": results})

        elif name == "read_url":
            return json.dumps({
                "url": tool_input["url"],
                "content": f"Detailed content from {tool_input['url']}. This covers the main aspects of the topic with supporting evidence and analysis. Key data points and conclusions are presented.",
                "word_count": 500,
            })

        elif name == "extract_key_points":
            return json.dumps({
                "key_points": [
                    "Primary finding related to the topic",
                    "Supporting evidence from multiple sources",
                    "Emerging trend worth monitoring",
                ],
                "focus": tool_input.get("focus", "general"),
            })

        elif name == "compare_sources":
            findings = tool_input.get("findings", [])
            return json.dumps({
                "agreements": ["Sources agree on core premise"],
                "contradictions": [],
                "gaps": ["Limited data on long-term outcomes"],
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
        "You are a research assistant. Given a question, use the available tools to:\n"
        "1. Search for relevant information\n"
        "2. Read and extract key points from sources\n"
        "3. Compare findings across sources\n"
        "4. Generate a report outline\n"
        "5. Write each section\n\n"
        "Chain tools logically: search first, then read, extract, compare, outline, write.\n"
        "When done, provide your final answer as a JSON object matching this schema:\n"
        '{"question": "...", "sources": [...], "sections": [...], "confidence": 0.0-1.0, "follow_up_questions": [...]}\n'
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
