"""Week 11: Capstone Scaffold

Starting point for your capstone project. Fill in the agent implementations,
state schema, and graph construction based on your architecture document.
"""

import sys
import json
from typing import TypedDict
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.llm_client import LLMClient
from shared.eval_helpers import run_evaluation, EvalReport

load_dotenv()

try:
    from langgraph.graph import StateGraph, START, END
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False


# --- State Schema (customize for your project) ---

class CapstoneState(TypedDict):
    """Define the state that flows through your system.

    Add fields for each agent's input and output.
    Include voting, trace, and error fields.
    """
    user_request: str

    # Agent outputs -- add one per agent
    agent_a_output: dict
    agent_b_output: dict
    agent_c_output: dict
    agent_d_output: dict

    # Voting
    votes: list[dict]
    voting_result: dict
    requires_human_review: bool

    # Pipeline metadata
    trace: list[str]
    errors: list[str]
    final_output: dict
    cost_usd: float


# --- Agent Implementations (fill in) ---

def agent_a(state: CapstoneState) -> dict:
    """Agent A: [Describe role]

    TODO: Implement with real LLM call.
    """
    client = LLMClient(provider="anthropic")
    # response = client.chat(...)
    return {
        "agent_a_output": {"placeholder": True},
        "trace": state["trace"] + ["Agent A completed"],
    }


def agent_b(state: CapstoneState) -> dict:
    """Agent B: [Describe role]

    TODO: Implement with real LLM call.
    """
    return {
        "agent_b_output": {"placeholder": True},
        "trace": state["trace"] + ["Agent B completed"],
    }


def agent_c(state: CapstoneState) -> dict:
    """Agent C: [Describe role]

    TODO: Implement with real LLM call.
    """
    return {
        "agent_c_output": {"placeholder": True},
        "trace": state["trace"] + ["Agent C completed"],
    }


def agent_d(state: CapstoneState) -> dict:
    """Agent D: [Synthesizer / Coordinator]

    TODO: Combine outputs from other agents, run voting, produce final output.
    """
    return {
        "agent_d_output": {"placeholder": True},
        "final_output": {"status": "placeholder"},
        "trace": state["trace"] + ["Agent D (synthesizer) completed"],
    }


# --- Routing Logic ---

def route_after_initial(state: CapstoneState) -> str:
    """Route based on initial analysis. Customize for your project."""
    if state.get("errors"):
        return "error_handler"
    return "agent_b"


def handle_error(state: CapstoneState) -> dict:
    return {
        "final_output": {"status": "error", "errors": state["errors"]},
        "trace": state["trace"] + ["Error handler invoked"],
    }


# --- Build Graph ---

def build_capstone_graph():
    """Build the capstone LangGraph pipeline.

    TODO: Customize edges and routing for your architecture.
    """
    if not LANGGRAPH_AVAILABLE:
        raise ImportError("langgraph required: pip install langgraph")

    builder = StateGraph(CapstoneState)

    # Add nodes
    builder.add_node("agent_a", agent_a)
    builder.add_node("agent_b", agent_b)
    builder.add_node("agent_c", agent_c)
    builder.add_node("agent_d", agent_d)
    builder.add_node("error_handler", handle_error)

    # Define flow -- customize for your dependency graph
    builder.add_edge(START, "agent_a")
    builder.add_conditional_edges("agent_a", route_after_initial)
    builder.add_edge("agent_b", "agent_c")
    builder.add_edge("agent_c", "agent_d")
    builder.add_edge("agent_d", END)
    builder.add_edge("error_handler", END)

    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)


def run_capstone(user_request: str) -> dict:
    """Run the full capstone system."""
    graph = build_capstone_graph()
    initial_state = CapstoneState(
        user_request=user_request,
        agent_a_output={},
        agent_b_output={},
        agent_c_output={},
        agent_d_output={},
        votes=[],
        voting_result={},
        requires_human_review=False,
        trace=[],
        errors=[],
        final_output={},
        cost_usd=0.0,
    )
    config = {"configurable": {"thread_id": datetime.now().strftime("%Y%m%d_%H%M%S")}}
    return graph.invoke(initial_state, config)


# --- Evaluation ---

def run_capstone_eval(ground_truth_path: str = None) -> EvalReport:
    """Run evaluation against your ground truth dataset.

    TODO: Create ground_truth.json with your test cases.
    """
    # Load ground truth
    if ground_truth_path and Path(ground_truth_path).exists():
        cases = json.loads(Path(ground_truth_path).read_text())
    else:
        # Placeholder -- replace with your actual test cases
        cases = [
            {"id": "test_001", "input": "Test request 1", "expected": ["expected_keyword"]},
            {"id": "test_002", "input": "Test request 2", "expected": ["expected_keyword"]},
        ]

    from shared.eval_helpers import keyword_evaluator

    def agent_fn(input_str):
        result = run_capstone(input_str)
        return json.dumps(result.get("final_output", {}))

    test_cases = [{"id": c["id"], "input": c["input"], "expected": c["expected"]} for c in cases]
    return run_evaluation(agent_fn, test_cases, keyword_evaluator)


if __name__ == "__main__":
    result = run_capstone("Sample request for capstone project")
    print(json.dumps(result.get("final_output", {}), indent=2))
    print(f"\nTrace: {result.get('trace', [])}")
