"""Week 2 STARTER: Research Assistant Agent

TODO: Implement tool chaining, structured output, and session persistence.
Copy this file to research_agent.py and fill in the TODO sections.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel, Field
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.llm_client import LLMClient

load_dotenv()


# --- Structured Output Schema ---
# TODO: Define Pydantic models for the research report.
# Need: Source, ReportSection, ResearchReport
# ResearchReport should have: question, sources, sections, confidence (0-1), follow_up_questions

class Source(BaseModel):
    title: str
    url: str = ""
    snippet: str
    relevance: float = Field(ge=0.0, le=1.0)

class ReportSection(BaseModel):
    # TODO: Define fields (heading, content, source_indices)
    pass

class ResearchReport(BaseModel):
    # TODO: Define fields (question, sources, sections, confidence, follow_up_questions)
    pass


# --- Session Memory ---

class SessionMemory:
    """Persist research sessions to disk.

    TODO: Implement _load(), save(), add_finding(), add_source(), add_report().
    Store as JSON in sessions/{session_id}.json
    """

    def __init__(self, session_id: str, sessions_dir: str = "sessions"):
        self.path = Path(sessions_dir) / f"{session_id}.json"
        self.state = self._load()

    def _load(self) -> dict:
        # TODO: Load from disk if exists, otherwise return empty state
        pass

    def save(self):
        # TODO: Write self.state to self.path as JSON
        pass

    def add_finding(self, finding: dict):
        # TODO: Append to findings list and save
        pass

    def add_source(self, source: dict):
        # TODO: Append to sources list and save
        pass


# --- Tool Definitions ---
# TODO: Define 6 tools: web_search, read_url, extract_key_points,
# compare_sources, generate_outline, write_section
# Focus on making descriptions specific enough that the LLM chains them correctly.

TOOLS = [
    # TODO: Define tools here
]


# --- Tool Implementations ---

def execute_tool(name: str, tool_input: dict) -> str:
    """Execute a research tool.

    TODO: Implement each tool. For this exercise, tools can return
    simulated data (you don't need real web access).
    The key learning is the chaining pattern, not real HTTP calls.
    """
    pass


# --- Agent Loop ---

def run_research_agent(question: str, session_id: str = None, max_iterations: int = 15) -> dict:
    """Run the research agent.

    TODO: Implement the agent loop (similar to Week 1 but with):
    - Session memory tracking
    - Structured output parsing (try to parse JSON from final response)
    - ResearchReport validation with Pydantic

    Return: dict with report (ResearchReport dict or raw), tool_calls, usage, session_id
    """
    pass


if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else "What is the current state of MCP adoption?"
    print(f"Researching: {question}\n")
    result = run_research_agent(question)
    print(json.dumps(result.get("report", {}), indent=2, default=str))
