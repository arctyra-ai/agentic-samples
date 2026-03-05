"""Week 7: Multi-Agent Code Review System

Three specialist agents (Analyzer, Security, Improver) independently review code,
then a Synthesizer combines their findings.

Demonstrates: multi-agent coordination, parallel execution, shared state, role separation.
"""

import sys
import json
import operator
from typing import TypedDict, Annotated
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.llm_client import LLMClient

load_dotenv()

try:
    from langgraph.graph import StateGraph, START, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False


# --- State Schema ---

def _merge_token_usage(left: dict, right: dict) -> dict:
    """Reducer: merge token usage dicts by summing values."""
    if not left:
        return right
    if not right:
        return left
    return {
        "total_input": left.get("total_input", 0) + right.get("total_input", 0),
        "total_output": left.get("total_output", 0) + right.get("total_output", 0),
        "calls": left.get("calls", 0) + right.get("calls", 0),
    }


class ReviewState(TypedDict):
    code: str
    filename: str
    analyzer_findings: list[dict]
    security_findings: list[dict]
    improvement_suggestions: list[dict]
    synthesized_report: dict
    token_usage: Annotated[dict, _merge_token_usage]


def create_review_state(code: str, filename: str = "unknown.py") -> ReviewState:
    return ReviewState(
        code=code,
        filename=filename,
        analyzer_findings=[],
        security_findings=[],
        improvement_suggestions=[],
        synthesized_report={},
        token_usage={"total_input": 0, "total_output": 0, "calls": 0},
    )


# --- Agent Nodes ---

def _parse_findings(text: str) -> list[dict]:
    """Try to parse JSON findings from LLM response."""
    try:
        start = text.index("[")
        end = text.rindex("]") + 1
        return json.loads(text[start:end])
    except (ValueError, json.JSONDecodeError):
        return [{"description": text, "severity": "info", "parse_error": True}]


def run_analyzer(state: ReviewState) -> dict:
    """Code quality analyzer: finds bugs, code smells, logic errors."""
    client = LLMClient(provider="anthropic")
    response = client.chat(
        messages=[{"role": "user", "content": (
            f"Review this code for quality issues.\n\n"
            f"File: {state['filename']}\n```python\n{state['code']}\n```\n\n"
            "Return a JSON array of findings. Each finding:\n"
            '{"line": N, "severity": "high|medium|low", "type": "bug|smell|logic", "description": "..."}\n'
            "Return [] if no issues found."
        )}],
        system="You are a code quality analyzer. Find bugs, code smells, and logic errors. Respond with JSON array only.",
    )
    findings = _parse_findings(client.get_text(response))
    usage = client.usage.summary()
    return {
        "analyzer_findings": findings,
        "token_usage": {"total_input": usage["total_input_tokens"], "total_output": usage["total_output_tokens"], "calls": usage["total_calls"]},
    }


def run_security_auditor(state: ReviewState) -> dict:
    """Security auditor: finds vulnerabilities and unsafe patterns."""
    client = LLMClient(provider="anthropic")
    response = client.chat(
        messages=[{"role": "user", "content": (
            f"Audit this code for security vulnerabilities.\n\n"
            f"File: {state['filename']}\n```python\n{state['code']}\n```\n\n"
            "Check for: SQL injection, path traversal, hardcoded secrets, unsafe deserialization, "
            "command injection, insecure crypto, SSRF, missing input validation.\n\n"
            "Return a JSON array of findings:\n"
            '{"line": N, "severity": "critical|high|medium|low", "vulnerability": "...", "description": "...", "remediation": "..."}\n'
            "Return [] if no issues found."
        )}],
        system="You are a security auditor. Find vulnerabilities. Respond with JSON array only.",
    )
    findings = _parse_findings(client.get_text(response))
    usage = client.usage.summary()
    return {
        "security_findings": findings,
        "token_usage": {"total_input": usage["total_input_tokens"], "total_output": usage["total_output_tokens"], "calls": usage["total_calls"]},
    }


def run_improver(state: ReviewState) -> dict:
    """Code improver: suggests enhancements and best practices."""
    client = LLMClient(provider="anthropic")
    response = client.chat(
        messages=[{"role": "user", "content": (
            f"Suggest improvements for this code.\n\n"
            f"File: {state['filename']}\n```python\n{state['code']}\n```\n\n"
            "Focus on: readability, performance, error handling, documentation, Pythonic patterns.\n\n"
            "Return a JSON array of suggestions:\n"
            '{"line": N, "category": "readability|performance|error_handling|documentation|pattern", "suggestion": "...", "priority": "high|medium|low"}\n'
            "Return [] if code is already excellent."
        )}],
        system="You are a code improvement advisor. Suggest enhancements. Respond with JSON array only.",
    )
    suggestions = _parse_findings(client.get_text(response))
    usage = client.usage.summary()
    return {
        "improvement_suggestions": suggestions,
        "token_usage": {"total_input": usage["total_input_tokens"], "total_output": usage["total_output_tokens"], "calls": usage["total_calls"]},
    }


def synthesize(state: ReviewState) -> dict:
    """Combine all agent findings into a unified report."""
    client = LLMClient(provider="anthropic")
    response = client.chat(
        messages=[{"role": "user", "content": (
            "Synthesize these code review findings into a unified report.\n\n"
            f"Analyzer findings: {json.dumps(state['analyzer_findings'])}\n\n"
            f"Security findings: {json.dumps(state['security_findings'])}\n\n"
            f"Improvement suggestions: {json.dumps(state['improvement_suggestions'])}\n\n"
            "Identify contradictions between agents. Prioritize by severity.\n"
            "Return JSON:\n"
            '{"summary": "...", "critical_issues": [...], "recommendations": [...], '
            '"contradictions": [...], "overall_rating": "pass|needs_work|fail"}'
        )}],
        system="You are a lead reviewer synthesizing multiple code reviews. Respond with JSON only.",
    )
    text = client.get_text(response)
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        report = json.loads(text[start:end])
    except (ValueError, json.JSONDecodeError):
        report = {"summary": text, "parse_error": True}

    report["timestamp"] = datetime.now().isoformat()
    report["agent_counts"] = {
        "analyzer": len(state["analyzer_findings"]),
        "security": len(state["security_findings"]),
        "improver": len(state["improvement_suggestions"]),
    }

    usage = client.usage.summary()
    return {
        "synthesized_report": report,
        "token_usage": {"total_input": usage["total_input_tokens"], "total_output": usage["total_output_tokens"], "calls": usage["total_calls"]},
    }


def _merge_usage(existing: dict, new: dict) -> dict:
    return {
        "total_input": existing.get("total_input", 0) + new.get("total_input_tokens", 0),
        "total_output": existing.get("total_output", 0) + new.get("total_output_tokens", 0),
        "calls": existing.get("calls", 0) + new.get("total_calls", 0),
    }


# --- Build Graph ---

def build_review_graph():
    """Build multi-agent review graph with parallel agent execution."""
    if not LANGGRAPH_AVAILABLE:
        raise ImportError("langgraph required")

    builder = StateGraph(ReviewState)

    builder.add_node("analyzer", run_analyzer)
    builder.add_node("security", run_security_auditor)
    builder.add_node("improver", run_improver)
    builder.add_node("synthesizer", synthesize)

    # All three agents run from START (parallel)
    builder.add_edge(START, "analyzer")
    builder.add_edge(START, "security")
    builder.add_edge(START, "improver")

    # All feed into synthesizer
    builder.add_edge("analyzer", "synthesizer")
    builder.add_edge("security", "synthesizer")
    builder.add_edge("improver", "synthesizer")

    builder.add_edge("synthesizer", END)

    return builder.compile()


def review_code(code: str, filename: str = "unknown.py") -> dict:
    """Run the full multi-agent code review."""
    graph = build_review_graph()
    initial_state = create_review_state(code, filename)
    return graph.invoke(initial_state)


# --- CLI ---

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Multi-Agent Code Review")
    parser.add_argument("file", nargs="?", help="Python file to review")
    args = parser.parse_args()

    if args.file:
        code = Path(args.file).read_text()
        filename = args.file
    else:
        code = '''
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = db.execute(query)
    return result

def process_data(data):
    for i in range(len(data)):
        data[i] = data[i] * 2
    return data
'''
        filename = "example.py"

    print(f"Reviewing: {filename} ({len(code)} chars)\n")
    result = review_code(code, filename)

    print(f"Analyzer found: {len(result['analyzer_findings'])} issues")
    print(f"Security found: {len(result['security_findings'])} issues")
    print(f"Improver suggested: {len(result['improvement_suggestions'])} improvements")
    print(f"\nSynthesized Report:")
    print(json.dumps(result["synthesized_report"], indent=2))
    print(f"\nToken usage: {result['token_usage']}")
