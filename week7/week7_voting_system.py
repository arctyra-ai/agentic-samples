#!/usr/bin/env python3
"""
Week 7-9: Integrated Voting System with Conflict Resolution
Complete system with agents, voting, and human review interface
"""

import json
from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Dict
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

# ============================================================================
# PART 1: Voting System Classes
# ============================================================================

class VotePosition(Enum):
    """Vote positions"""
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"

@dataclass
class Vote:
    """Single agent vote"""
    agent_name: str
    position: VotePosition
    weight: float = 1.0
    reasoning: str = ""
    confidence: float = 1.0
    
    def to_dict(self):
        return {
            "agent_name": self.agent_name,
            "position": self.position.value,
            "weight": self.weight,
            "reasoning": self.reasoning,
            "confidence": self.confidence
        }

class VotingSystem:
    """Aggregate and tally votes"""
    
    def __init__(self, agent_weights: Dict[str, float] = None):
        """
        Initialize voting system
        
        Args:
            agent_weights: Dict mapping agent names to vote weights
            Example: {"Security": 2.0, "QA": 1.5, "Backend": 1.0}
        """
        self.agent_weights = agent_weights or {}
        self.votes: List[Vote] = []
        self.history = []
    
    def cast_vote(self, vote: Vote):
        """Record a vote with applied weight"""
        if vote.agent_name in self.agent_weights:
            vote.weight *= self.agent_weights[vote.agent_name]
        self.votes.append(vote)
    
    def tally_votes(self) -> Dict:
        """Calculate voting outcome"""
        if not self.votes:
            return {
                "result": "NO_VOTES",
                "approve_weight": 0,
                "reject_weight": 0,
                "approve_percent": 0,
                "total_weight": 0,
                "vote_breakdown": []
            }
        
        # Calculate weights
        approve_weight = sum(
            v.weight for v in self.votes 
            if v.position == VotePosition.APPROVE
        )
        reject_weight = sum(
            v.weight for v in self.votes 
            if v.position == VotePosition.REJECT
        )
        total_weight = approve_weight + reject_weight
        
        if total_weight == 0:
            result = "ABSTAIN"
            approve_percent = 0
        else:
            approve_percent = approve_weight / total_weight
            
            if approve_percent > 0.5:
                result = "APPROVED"
            elif approve_percent < 0.5:
                result = "REJECTED"
            else:
                result = "TIE"
        
        return {
            "result": result,
            "approve_weight": approve_weight,
            "reject_weight": reject_weight,
            "approve_percent": approve_percent,
            "total_weight": total_weight,
            "vote_breakdown": [v.to_dict() for v in self.votes]
        }
    
    def reset(self):
        """Clear votes for next decision"""
        self.history.append([v.to_dict() for v in self.votes])
        self.votes = []
    
    def get_history(self) -> List:
        """Get all past voting rounds"""
        return self.history

# ============================================================================
# PART 2: State Schema
# ============================================================================

class VotingTodoState(TypedDict):
    """State for voting TODO system"""
    user_input: str
    proposed_action: str
    agent_votes: List[Dict]          # List of vote dicts
    voting_result: Dict              # Tally result
    human_decision: str              # Human's final decision
    execution_result: Dict           # Result of execution
    decision_log: List[Dict]         # Full trace

# ============================================================================
# PART 3: Agent Nodes (Voting)
# ============================================================================

def agent_1_validator(state: VotingTodoState) -> VotingTodoState:
    """Validator agent votes"""
    proposed_action = state.get("proposed_action", "")
    
    # Validation logic
    if "delete_all" in proposed_action.lower():
        vote = Vote(
            agent_name="Validator",
            position=VotePosition.REJECT,
            weight=1.5,
            reasoning="Dangerous operation - could lose all data",
            confidence=0.95
        )
    else:
        vote = Vote(
            agent_name="Validator",
            position=VotePosition.APPROVE,
            weight=1.5,
            reasoning="Standard validation passed",
            confidence=0.9
        )
    
    return {
        **state,
        "agent_votes": [vote.to_dict()]
    }

def agent_2_storage(state: VotingTodoState) -> VotingTodoState:
    """Storage agent votes"""
    proposed_action = state.get("proposed_action", "")
    existing_votes = state.get("agent_votes", [])
    
    # Storage always approves (ready to execute)
    vote = Vote(
        agent_name="Storage",
        position=VotePosition.APPROVE,
        weight=1.0,
        reasoning="Database ready to execute operation",
        confidence=0.95
    )
    
    return {
        **state,
        "agent_votes": existing_votes + [vote.to_dict()]
    }

def agent_3_security(state: VotingTodoState) -> VotingTodoState:
    """Security agent votes (high weight)"""
    proposed_action = state.get("proposed_action", "")
    existing_votes = state.get("agent_votes", [])
    
    # Security concerns about certain operations
    if "delete" in proposed_action.lower():
        vote = Vote(
            agent_name="Security",
            position=VotePosition.REJECT,
            weight=2.0,  # High weight - can veto
            reasoning="Destructive operations require explicit confirmation",
            confidence=0.99
        )
    else:
        vote = Vote(
            agent_name="Security",
            position=VotePosition.APPROVE,
            weight=2.0,
            reasoning="Security checks passed",
            confidence=0.9
        )
    
    return {
        **state,
        "agent_votes": existing_votes + [vote.to_dict()]
    }

def voting_aggregator(state: VotingTodoState) -> VotingTodoState:
    """Aggregate all votes and determine outcome"""
    
    # Create voting system with weighted votes
    voting_system = VotingSystem(agent_weights={
        "Security": 2.0,
        "Validator": 1.5,
        "Storage": 1.0
    })
    
    # Process each vote
    for vote_dict in state.get("agent_votes", []):
        vote = Vote(
            agent_name=vote_dict["agent_name"],
            position=VotePosition(vote_dict["position"]),
            weight=vote_dict.get("weight", 1.0),
            reasoning=vote_dict.get("reasoning", ""),
            confidence=vote_dict.get("confidence", 1.0)
        )
        voting_system.cast_vote(vote)
    
    # Tally
    result = voting_system.tally_votes()
    
    # Determine if human review needed
    requires_human = result["result"] in ["TIE", "REJECTED"]
    
    new_state = {
        **state,
        "voting_result": result,
        "requires_human_review": requires_human
    }
    
    new_state["decision_log"].append({
        "stage": "voting_aggregation",
        "result": result["result"],
        "approve_percent": result["approve_percent"],
        "requires_human": requires_human
    })
    
    return new_state

# ============================================================================
# PART 4: Conditional Routing
# ============================================================================

def route_on_voting(state: VotingTodoState) -> str:
    """Route based on voting outcome"""
    voting_result = state.get("voting_result", {})
    outcome = voting_result.get("result", "")
    
    if outcome in ["TIE", "REJECTED"]:
        return "human_review"
    elif outcome == "APPROVED":
        return "execute"
    else:
        return "execute"

# ============================================================================
# PART 5: Human Review
# ============================================================================

def human_review_node(state: VotingTodoState) -> VotingTodoState:
    """Get human decision on conflicts"""
    
    voting_result = state.get("voting_result", {})
    
    print("\n" + "="*70)
    print("🔴 HUMAN REVIEW REQUIRED - VOTING CONFLICT")
    print("="*70)
    
    print(f"\nProposed Action: {state['proposed_action']}")
    print(f"\nVoting Result: {voting_result['result']}")
    print(f"Approval Percentage: {voting_result['approve_percent']*100:.1f}%")
    
    print("\nAgent Votes:")
    print("-"*70)
    for vote in voting_result["vote_breakdown"]:
        print(f"  {vote['agent_name']:15} {vote['position']:10} (weight: {vote['weight']}x)")
        print(f"    └─ {vote['reasoning']}")
    
    print("\n" + "-"*70)
    print("Your Options:")
    print("  [A] Approve  - Execute the action")
    print("  [R] Reject   - Don't execute the action")
    print("  [M] Modify   - Adjust agent weights and re-vote")
    print("  [S] Show     - Show detailed voting breakdown")
    
    while True:
        choice = input("\nYour decision [A/R/M/S]: ").upper().strip()
        
        if choice == "A":
            decision = "HUMAN_APPROVED"
            print("✅ You approved the action")
            break
        elif choice == "R":
            decision = "HUMAN_REJECTED"
            print("❌ You rejected the action")
            break
        elif choice == "M":
            print("Not implemented in demo - using default weights")
            decision = "HUMAN_APPROVED"
            break
        elif choice == "S":
            print(json.dumps(voting_result, indent=2))
        else:
            print("Invalid choice. Try again.")
    
    print("="*70 + "\n")
    
    return {
        **state,
        "human_decision": decision
    }

def route_on_human_decision(state: VotingTodoState) -> str:
    """Route based on human decision"""
    decision = state.get("human_decision", "")
    if "APPROVED" in decision:
        return "execute"
    else:
        return "reject"

# ============================================================================
# PART 6: Execution
# ============================================================================

def execute_node(state: VotingTodoState) -> VotingTodoState:
    """Execute the action"""
    return {
        **state,
        "execution_result": {
            "status": "executed",
            "message": f"Action '{state['proposed_action']}' executed successfully"
        }
    }

def reject_node(state: VotingTodoState) -> VotingTodoState:
    """Reject the action"""
    return {
        **state,
        "execution_result": {
            "status": "rejected",
            "message": f"Action '{state['proposed_action']}' was rejected"
        }
    }

# ============================================================================
# PART 7: Build Integrated Graph
# ============================================================================

def build_voting_graph():
    """Build complete voting system graph"""
    
    builder = StateGraph(VotingTodoState)
    
    # Add nodes
    builder.add_node("validator", agent_1_validator)
    builder.add_node("storage", agent_2_storage)
    builder.add_node("security", agent_3_security)
    builder.add_node("aggregate", voting_aggregator)
    builder.add_node("human_review", human_review_node)
    builder.add_node("execute", execute_node)
    builder.add_node("reject", reject_node)
    
    # Parallel voting (all agents vote simultaneously)
    builder.add_edge(START, "validator")
    builder.add_edge(START, "storage")
    builder.add_edge(START, "security")
    
    # Sequential: gather votes then aggregate
    builder.add_edge("validator", "aggregate")
    builder.add_edge("storage", "aggregate")
    builder.add_edge("security", "aggregate")
    
    # Conditional routing based on voting outcome
    builder.add_conditional_edges(
        "aggregate",
        route_on_voting,
        {
            "human_review": "human_review",
            "execute": "execute",
            "reject": "reject"
        }
    )
    
    # Human review routes to execute/reject
    builder.add_conditional_edges(
        "human_review",
        route_on_human_decision,
        {
            "execute": "execute",
            "reject": "reject"
        }
    )
    
    # End
    builder.add_edge("execute", END)
    builder.add_edge("reject", END)
    
    return builder.compile()

# ============================================================================
# PART 8: Demo
# ============================================================================

def run_voting_demo():
    """Run voting system demo"""
    
    graph = build_voting_graph()
    
    # Test scenarios
    scenarios = [
        {
            "name": "Simple Add Task",
            "action": "Add a new task: Buy milk",
            "expects_human_review": False
        },
        {
            "name": "Delete Single Task",
            "action": "Delete task 1",
            "expects_human_review": True
        },
        {
            "name": "Delete All Tasks",
            "action": "Delete all tasks",
            "expects_human_review": True
        }
    ]
    
    print("\n" + "="*70)
    print("VOTING SYSTEM DEMO")
    print("="*70)
    
    for scenario in scenarios:
        print(f"\n\n📋 Scenario: {scenario['name']}")
        print(f"   Action: {scenario['action']}")
        print("-"*70)
        
        initial_state = {
            "user_input": scenario['action'],
            "proposed_action": scenario['action'],
            "agent_votes": [],
            "voting_result": {},
            "human_decision": "",
            "execution_result": {},
            "decision_log": []
        }
        
        # Run graph
        result = graph.invoke(initial_state)
        
        # Show results
        print(f"\n✅ Execution Result: {result['execution_result']['status']}")
        print(f"   Message: {result['execution_result']['message']}")

# ============================================================================
# PART 9: Main
# ============================================================================

if __name__ == "__main__":
    run_voting_demo()
