#!/usr/bin/env python3
"""
Weeks 10-12: Software Development Multi-Agent System
6 specialized agents with voting-based conflict resolution.
Agents: Orchestrator, Database, Backend, Frontend, Security, QA
"""

import json
import os
import sys
from typing import TypedDict, List

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "week7"))

from langgraph.graph import StateGraph, START, END
from voting_system import VotingSystem, Vote, VotePosition
from human_review import HumanReviewPanel


# ============================================================================
# State Schema
# ============================================================================

class SoftwareDevState(TypedDict):
    user_requirement: str
    orchestrator_tasks: List[dict]
    database_design: dict
    backend_code: str
    frontend_code: str
    security_audit: dict
    qa_report: dict
    votes: List[dict]
    voting_result: dict
    human_decision: str
    final_output: dict
    error: str
    decision_log: List[dict]


# ============================================================================
# Agent Nodes
# ============================================================================

def orchestrator_node(state: SoftwareDevState) -> SoftwareDevState:
    """Decompose requirements into subtasks"""
    requirement = state["user_requirement"]

    tasks = [
        {"id": 1, "name": "database_design", "depends_on": []},
        {"id": 2, "name": "backend_code", "depends_on": [1]},
        {"id": 3, "name": "frontend_code", "depends_on": [2]},
        {"id": 4, "name": "security_audit", "depends_on": [2, 3]},
        {"id": 5, "name": "qa_testing", "depends_on": [2, 3, 4]}
    ]

    state["orchestrator_tasks"] = tasks
    state["decision_log"].append({
        "agent": "Orchestrator",
        "action": "Decomposed requirements into 5 tasks",
        "tasks": tasks
    })

    return state


def database_agent_node(state: SoftwareDevState) -> SoftwareDevState:
    """Design database schema"""
    design = {
        "tables": [
            {"name": "users", "fields": ["id", "email", "created_at"]},
            {"name": "tasks", "fields": ["id", "user_id", "title", "completed"]}
        ],
        "indexes": ["users.email", "tasks.user_id"],
        "constraints": ["FK tasks.user_id -> users.id"]
    }

    state["database_design"] = design
    state["decision_log"].append({
        "agent": "Database",
        "action": f"Designed schema with {len(design['tables'])} tables"
    })
    return state


def backend_agent_node(state: SoftwareDevState) -> SoftwareDevState:
    """Generate backend code"""
    code = '''
# Backend API
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel

app = FastAPI()

class TaskCreate(BaseModel):
    title: str
    user_id: int

@app.post("/tasks")
def create_task(task: TaskCreate):
    return {"id": 1, "user_id": task.user_id, "title": task.title}

@app.get("/tasks/{user_id}")
def list_tasks(user_id: int):
    return [{"id": 1, "title": "Task 1"}]

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    return {"deleted": task_id}
'''
    state["backend_code"] = code
    state["decision_log"].append({
        "agent": "Backend",
        "action": "Generated FastAPI backend with 3 endpoints"
    })
    return state


def frontend_agent_node(state: SoftwareDevState) -> SoftwareDevState:
    """Generate frontend code"""
    code = '''
import React, { useState, useEffect } from 'react';

export function TaskApp() {
    const [tasks, setTasks] = useState([]);

    useEffect(() => {
        fetch('/tasks/1').then(r => r.json()).then(setTasks);
    }, []);

    return (
        <div>
            <h1>Tasks</h1>
            {tasks.map(t => <div key={t.id}>{t.title}</div>)}
        </div>
    );
}
'''
    state["frontend_code"] = code
    state["decision_log"].append({
        "agent": "Frontend",
        "action": "Generated React component with API integration"
    })
    return state


def security_agent_node(state: SoftwareDevState) -> SoftwareDevState:
    """Review security and cast vote"""
    backend = state.get("backend_code", "")

    audit = {
        "vulnerabilities": [],
        "warnings": ["Missing authentication check on endpoints"],
        "recommendations": ["Add OAuth2", "Validate user_id ownership", "Add rate limiting"]
    }

    vote = {
        "agent_name": "Security",
        "position": VotePosition.REJECT.value,
        "weight": 2.0,
        "reasoning": "Missing authentication on create_task and delete_task endpoints"
    }

    state["votes"].append(vote)
    state["security_audit"] = audit
    state["decision_log"].append({
        "agent": "Security",
        "action": f"Found {len(audit['warnings'])} warnings, voted REJECT"
    })
    return state


def qa_agent_node(state: SoftwareDevState) -> SoftwareDevState:
    """Review testing/performance and cast vote"""
    report = {
        "test_coverage": 45,
        "performance_issues": [],
        "edge_cases": ["Empty task list", "Invalid user_id", "Concurrent writes"],
        "missing_tests": ["Unit tests for endpoints", "Integration tests", "Load tests"]
    }

    vote = {
        "agent_name": "QA",
        "position": VotePosition.APPROVE.value,
        "weight": 1.5,
        "reasoning": "Code structure is sound, needs tests but can proceed"
    }

    state["votes"].append(vote)
    state["qa_report"] = report
    state["decision_log"].append({
        "agent": "QA",
        "action": f"Coverage at {report['test_coverage']}%, voted APPROVE"
    })
    return state


# ============================================================================
# Voting & Review
# ============================================================================

def voting_aggregator_node(state: SoftwareDevState) -> SoftwareDevState:
    """Aggregate votes from Security and QA"""
    voting_system = VotingSystem(agent_weights={
        "Security": 2.0,
        "QA": 1.5,
        "Backend": 1.0,
        "Frontend": 1.0,
        "Database": 1.5
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

    state["decision_log"].append({
        "agent": "VotingAggregator",
        "action": f"Result: {result.get('result')}"
    })

    return state


def route_on_conflict(state: SoftwareDevState) -> str:
    """Check if human review is needed"""
    result = state["voting_result"]
    if result.get("result") in ("TIE", "REJECTED"):
        return "human_review"
    else:
        return "finalize"


def human_review_node(state: SoftwareDevState) -> SoftwareDevState:
    """Get human decision (auto-approve for testing)"""
    state["human_decision"] = "proceed"
    state["decision_log"].append({
        "agent": "HumanReview",
        "action": "Auto-approved for testing"
    })
    return state


def finalize_node(state: SoftwareDevState) -> SoftwareDevState:
    """Generate final output"""
    state["final_output"] = {
        "database": state.get("database_design"),
        "backend": state.get("backend_code"),
        "frontend": state.get("frontend_code"),
        "security_audit": state.get("security_audit"),
        "qa_report": state.get("qa_report"),
        "approval": state["voting_result"].get("result"),
        "human_decision": state.get("human_decision", "N/A")
    }
    state["decision_log"].append({
        "agent": "Finalizer",
        "action": "Generated final output package"
    })
    return state


# ============================================================================
# Build Graph
# ============================================================================

graph_builder = StateGraph(SoftwareDevState)

graph_builder.add_node("orchestrator", orchestrator_node)
graph_builder.add_node("database", database_agent_node)
graph_builder.add_node("backend", backend_agent_node)
graph_builder.add_node("frontend", frontend_agent_node)
graph_builder.add_node("security", security_agent_node)
graph_builder.add_node("qa", qa_agent_node)
graph_builder.add_node("voting", voting_aggregator_node)
graph_builder.add_node("human_review", human_review_node)
graph_builder.add_node("finalize", finalize_node)

# Edges with dependencies
graph_builder.add_edge(START, "orchestrator")
graph_builder.add_edge("orchestrator", "database")
graph_builder.add_edge("database", "backend")
graph_builder.add_edge("backend", "frontend")
graph_builder.add_edge("frontend", "security")
graph_builder.add_edge("security", "qa")
graph_builder.add_edge("qa", "voting")
graph_builder.add_conditional_edges(
    "voting",
    route_on_conflict,
    {"human_review": "human_review", "finalize": "finalize"}
)
graph_builder.add_edge("human_review", "finalize")
graph_builder.add_edge("finalize", END)

software_dev_graph = graph_builder.compile()


# ============================================================================
# Public API
# ============================================================================

def run_software_dev_system(requirement: str) -> dict:
    """Run full software development agent system"""
    initial_state = {
        "user_requirement": requirement,
        "orchestrator_tasks": [],
        "database_design": {},
        "backend_code": "",
        "frontend_code": "",
        "security_audit": {},
        "qa_report": {},
        "votes": [],
        "voting_result": {},
        "human_decision": "",
        "final_output": {},
        "error": "",
        "decision_log": []
    }

    result = software_dev_graph.invoke(initial_state)
    return result


if __name__ == "__main__":
    print("=" * 60)
    print("  Software Development Agent System - Weeks 10-12")
    print("=" * 60)

    result = run_software_dev_system("Build a task management application")

    print("\nFinal Output:")
    print(json.dumps(result["final_output"], indent=2, default=str)[:1000])

    print(f"\nDecision Log ({len(result['decision_log'])} entries):")
    for entry in result["decision_log"]:
        print(f"  [{entry['agent']}] {entry['action']}")
