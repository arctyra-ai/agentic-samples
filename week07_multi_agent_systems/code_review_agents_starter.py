"""Week 7 STARTER: Multi-Agent Code Review

TODO: Build 3 specialist agents + synthesizer using LangGraph.
Copy this file to code_review_agents.py and fill in the TODO sections.
"""

import sys
import json
from typing import TypedDict
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.llm_client import LLMClient

load_dotenv()

from langgraph.graph import StateGraph, START, END


# --- State Schema ---

class ReviewState(TypedDict):
    code: str
    filename: str
    analyzer_findings: list[dict]
    security_findings: list[dict]
    improvement_suggestions: list[dict]
    synthesized_report: dict
    token_usage: dict


def create_review_state(code: str, filename: str = "unknown.py") -> ReviewState:
    return ReviewState(
        code=code, filename=filename, analyzer_findings=[], security_findings=[],
        improvement_suggestions=[], synthesized_report={},
        token_usage={"total_input": 0, "total_output": 0, "calls": 0},
    )


# --- Agent Nodes ---

def run_analyzer(state: ReviewState) -> dict:
    """Code quality analyzer: finds bugs, code smells, logic errors.

    TODO:
    1. Create LLMClient
    2. Send code to LLM with system prompt for quality analysis
    3. Ask for JSON array of findings: [{line, severity, type, description}]
    4. Parse the response
    5. Return {"analyzer_findings": [...], "token_usage": ...}
    """
    pass


def run_security_auditor(state: ReviewState) -> dict:
    """Security auditor: finds vulnerabilities.

    TODO: Similar to analyzer but focused on security:
    SQL injection, path traversal, hardcoded secrets, etc.
    Return {"security_findings": [...], "token_usage": ...}
    """
    pass


def run_improver(state: ReviewState) -> dict:
    """Code improver: suggests enhancements.

    TODO: Focus on readability, performance, error handling, Pythonic patterns.
    Return {"improvement_suggestions": [...], "token_usage": ...}
    """
    pass


def synthesize(state: ReviewState) -> dict:
    """Combine all agent findings into a unified report.

    TODO:
    1. Send all three agents' findings to LLM
    2. Ask it to identify contradictions and prioritize by severity
    3. Return unified report with: summary, critical_issues, recommendations, overall_rating
    """
    pass


# --- Build Graph ---

def build_review_graph():
    """Build multi-agent review graph with parallel execution.

    TODO:
    1. Create StateGraph(ReviewState)
    2. Add 4 nodes: analyzer, security, improver, synthesizer
    3. All 3 specialists run from START (parallel)
    4. All 3 feed into synthesizer
    5. Synthesizer -> END
    6. Compile and return
    """
    pass


def review_code(code: str, filename: str = "unknown.py") -> dict:
    graph = build_review_graph()
    return graph.invoke(create_review_state(code, filename))


if __name__ == "__main__":
    code = '''
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)
'''
    result = review_code(code, "example.py")
    print(json.dumps(result["synthesized_report"], indent=2))
