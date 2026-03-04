#!/usr/bin/env python3
"""
Weeks 8-9: Integrated TODO System
Full integration of LangGraph state graphs, voting system, and human review.
Agents vote in parallel, votes are aggregated, conflicts trigger human review.
"""

import json
import os
import sys
from typing import TypedDict, List

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "week7"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "week2"))

from langgraph.graph import StateGraph, START, END
from voting_system import VotingSystem, Vote, VotePosition
from human_review import HumanReviewPanel


# ============================================================================
# State Schema (extended with voting)
# ============================================================================

class IntegratedTodoState(TypedDict):
    user_input: str
    parsed_intent: str
    action_type: str
    task_data: dict
    validation_result: dict
    execution_result: dict
    conflict_detected: bool
    votes: list
    voting_result: dict
    human_decision: str
    error: str
    decision_log: list


# ============================================================================
# Parse Node
# ============================================================================

def parse_node(state: IntegratedTodoState) -> IntegratedTodoState:
    """Parse user input into action type"""
    user_input = state["user_input"].lower()

    if "add" in user_input or "create" in user_input:
        action_type = "add"
        parsed_intent = "Adding new task"
    elif "list" in user_input or "show" in user_input:
        action_type = "list"
        parsed_intent = "Listing tasks"
    elif "delete" in user_input or "remove" in user_input:
        action_type = "delete"
        parsed_intent = "Deleting task"
    elif "complete" in user_input or "done" in user_input:
        action_type = "mark_complete"
        parsed_intent = "Marking task complete"
    else:
        action_type = "unknown"
        parsed_intent = "Unknown action"

    state["parsed_intent"] = parsed_intent
    state["action_type"] = action_type
    state["decision_log"].append({
        "agent": "Parser",
        "action": f"Classified as: {action_type}",
        "intent": parsed_intent
    })
    return state


# ============================================================================
# Voting Agent Nodes
# ============================================================================

def validator_node(state: IntegratedTodoState) -> IntegratedTodoState:
    """Validator agent casts vote"""
    action_type = state.get("action_type", "")

    if action_type == "delete":
        position = VotePosition.REJECT.value
        reasoning = "Destructive operation - requires confirmation"
    elif action_type == "unknown":
        position = VotePosition.REJECT.value
        reasoning = "Cannot validate unknown action"
    else:
        position = VotePosition.APPROVE.value
        reasoning = "Standard validation passed"

    state["votes"].append({
        "agent_name": "Validator",
        "position": position,
        "weight": 1.5,
        "reasoning": reasoning
    })
    return state


def storage_node(state: IntegratedTodoState) -> IntegratedTodoState:
    """Storage agent casts vote"""
    action_type = state.get("action_type", "")

    if action_type == "unknown":
        position = VotePosition.ABSTAIN.value
        reasoning = "No storage operation to perform"
    else:
        position = VotePosition.APPROVE.value
        reasoning = "Ready to execute operation"

    state["votes"].append({
        "agent_name": "Storage",
        "position": position,
        "weight": 1.0,
        "reasoning": reasoning
    })
    return state


def security_node(state: IntegratedTodoState) -> IntegratedTodoState:
    """Security agent casts vote"""
    action_type = state.get("action_type", "")

    if action_type == "delete":
        position = VotePosition.REJECT.value
        reasoning = "Destructive operations require human approval"
    else:
        position = VotePosition.APPROVE.value
        reasoning = "No security concerns"

    state["votes"].append({
        "agent_name": "Security",
        "position": position,
        "weight": 2.0,
        "reasoning": reasoning
    })
    return state


# ============================================================================
# Voting Aggregator
# ============================================================================

def voting_aggregator_node(state: IntegratedTodoState) -> IntegratedTodoState:
    """Aggregate all votes and determine outcome"""
    voting_system = VotingSystem(agent_weights={
        "Security": 2.0,
        "Validator": 1.5,
        "Storage": 1.0
    })

    for vote_dict in state["votes"]:
        vote = Vote(
            agent_name=vote_dict["agent_name"],
            position=VotePosition(vote_dict["position"]),
            weight=vote_dict.get("weight", 1.0),
            reasoning=vote_dict.get("reasoning", "")
        )
        voting_system.cast_vote(vote)

    result = voting_system.tally_votes()
    state["voting_result"] = result
    state["conflict_detected"] = result.get("result") in ("TIE", "REJECTED")

    state["decision_log"].append({
        "agent": "VotingAggregator",
        "action": f"Tally result: {result.get('result')}",
        "details": result
    })

    return state


# ============================================================================
# Human Review Node
# ============================================================================

def human_review_node(state: IntegratedTodoState) -> IntegratedTodoState:
    """Get human decision on conflicts (auto-review for testing)"""
    voting_result = state.get("voting_result", {})
    result_str = voting_result.get("result", "NO_VOTES")

    if result_str in ("TIE", "REJECTED"):
        # In production, this would prompt the human interactively
        # For automated testing, use auto_review logic
        vs = VotingSystem()
        panel = HumanReviewPanel(vs)
        # Simulate: approve if there are more approve votes by count
        approve_count = sum(1 for v in state["votes"] if v["position"] == "approve")
        reject_count = sum(1 for v in state["votes"] if v["position"] == "reject")
        if approve_count > reject_count:
            state["human_decision"] = "proceed"
        else:
            state["human_decision"] = "reject"
    else:
        state["human_decision"] = "AUTO_APPROVED" if result_str == "APPROVED" else "AUTO_REJECTED"

    state["decision_log"].append({
        "agent": "HumanReview",
        "action": f"Decision: {state['human_decision']}"
    })

    return state


# ============================================================================
# Execution Nodes
# ============================================================================

def execute_node(state: IntegratedTodoState) -> IntegratedTodoState:
    """Execute the approved action"""
    state["execution_result"] = {
        "status": "executed",
        "action": state["action_type"],
        "intent": state["parsed_intent"]
    }
    state["decision_log"].append({"agent": "Executor", "action": "Executed operation"})
    return state


def reject_node(state: IntegratedTodoState) -> IntegratedTodoState:
    """Handle rejected action"""
    state["execution_result"] = {
        "status": "rejected",
        "action": state["action_type"],
        "reason": "Action rejected by voting or human review"
    }
    state["decision_log"].append({"agent": "Executor", "action": "Operation rejected"})
    return state


# ============================================================================
# Routing
# ============================================================================

def route_on_decision(state: IntegratedTodoState) -> str:
    """Route based on human decision"""
    decision = state.get("human_decision", "")
    if decision in ("proceed", "AUTO_APPROVED"):
        return "execute"
    else:
        return "reject"


# ============================================================================
# Build Graph
# ============================================================================

graph_builder = StateGraph(IntegratedTodoState)

graph_builder.add_node("parse", parse_node)
graph_builder.add_node("validator", validator_node)
graph_builder.add_node("storage", storage_node)
graph_builder.add_node("security", security_node)
graph_builder.add_node("voting_aggregator", voting_aggregator_node)
graph_builder.add_node("human_review", human_review_node)
graph_builder.add_node("execute", execute_node)
graph_builder.add_node("reject", reject_node)

# Flow: parse -> parallel voting -> aggregate -> human review -> execute/reject
graph_builder.add_edge(START, "parse")
graph_builder.add_edge("parse", "validator")
graph_builder.add_edge("parse", "storage")
graph_builder.add_edge("parse", "security")

graph_builder.add_edge("validator", "voting_aggregator")
graph_builder.add_edge("storage", "voting_aggregator")
graph_builder.add_edge("security", "voting_aggregator")

graph_builder.add_edge("voting_aggregator", "human_review")
graph_builder.add_conditional_edges(
    "human_review",
    route_on_decision,
    {"execute": "execute", "reject": "reject"}
)

graph_builder.add_edge("execute", END)
graph_builder.add_edge("reject", END)

integrated_graph = graph_builder.compile()


# ============================================================================
# Public API
# ============================================================================

def run_integrated_system(user_input: str) -> dict:
    """Run full integrated system"""
    initial_state = {
        "user_input": user_input,
        "parsed_intent": "",
        "action_type": "",
        "task_data": {},
        "validation_result": {},
        "execution_result": {},
        "conflict_detected": False,
        "votes": [],
        "voting_result": {},
        "human_decision": "",
        "error": "",
        "decision_log": []
    }

    result = integrated_graph.invoke(initial_state)
    return result


if __name__ == "__main__":
    print("=" * 60)
    print("  Integrated TODO System - Weeks 8-9")
    print("=" * 60)

    test_cases = [
        "Add task: Buy milk",
        "List all tasks",
        "Delete task 1",
        "What is the meaning of life?",
    ]

    for user_input in test_cases:
        print(f"\n{'='*60}")
        print(f"Input: {user_input}")
        result = run_integrated_system(user_input)
        print(f"Decision: {result['human_decision']}")
        print(f"Execution: {result['execution_result']}")
        print(f"Votes: {len(result['votes'])}")
        print(f"Decision log entries: {len(result['decision_log'])}")
