# Agentic AI Training: 4-Week Accelerated Path

**For:** Developers with intermediate+ architecture experience  
**Duration:** 40-50 hours (~10-12 hours/week)  
**Focus:** Skip foundations, deep dive into multi-agent architecture  
**Final Project:** Software dev agent system with voting-based conflict resolution

---

## Accelerated Path Overview

| Week | Focus | Hours | Deliverable |
|------|-------|-------|-------------|
| **1** | Foundations Compressed + LangGraph Basics | 12 | Multi-agent state graph TODO system |
| **2** | Voting System & Conflict Resolution | 12 | Integrated voting mechanism |
| **3** | Architecture Design & Planning | 10 | Software dev agent specification |
| **4** | Implementation & Testing | 16 | Production-ready multi-agent system |

---

## Week 1: Foundations Compressed + LangGraph Basics

### Day 1: Agent Fundamentals (3 hours)

**Learning Objectives:**
- Understand tool calling / function calling
- Know agent loop (input → reason → tool → output)
- Understand state management basics

**Resources:**
- OpenAI Function Calling docs (1 hr): https://platform.openai.com/docs/guides/function-calling
- Build simple agent (2 hrs)

**Quick Concept Refresher:**

```python
# Agent loop in 30 seconds:
1. User: "Add a task"
2. Agent reasons: "I should call add_task tool"
3. Agent calls: add_task(title="Buy milk")
4. You execute tool and return: "Task added"
5. Agent: "Done! I added 'Buy milk'"
```

### Days 2-4: LangGraph Fundamentals (6 hours)

**Learn LangGraph in 1 day:**

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

# 1. Define State
class AgentState(TypedDict):
    user_input: str
    agent_thoughts: str
    action: str
    result: str

# 2. Create Nodes (functions)
def think(state):
    return {"agent_thoughts": "I need to add a task"}

def act(state):
    return {"action": "add_task", "result": "Task added"}

# 3. Build Graph
builder = StateGraph(AgentState)
builder.add_node("think", think)
builder.add_node("act", act)
builder.add_edge(START, "think")
builder.add_edge("think", "act")
builder.add_edge("act", END)

# 4. Compile & Run
graph = builder.compile()
result = graph.invoke({"user_input": "Add milk"})
```

**Key Concepts:**
- **State**: Data structure flowing through graph
- **Nodes**: Functions that process state
- **Edges**: Connections between nodes
- **Conditional Edges**: Route based on state

### Days 5-7: Multi-Agent TODO (3 hours)

Build 3-agent TODO system:

```python
# Week 1 Final Project: 3-Agent TODO System

from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class TodoState(TypedDict):
    user_request: str
    parsed_intent: str
    validation_result: dict
    execution_result: dict

# Agent 1: Parser
def parser_node(state):
    intent = "add" if "add" in state["user_request"].lower() else "list"
    return {"parsed_intent": intent}

# Agent 2: Validator
def validator_node(state):
    is_valid = state["parsed_intent"] in ["add", "list", "delete"]
    return {"validation_result": {"valid": is_valid}}

# Agent 3: Executor
def executor_node(state):
    if state["validation_result"]["valid"]:
        result = "Operation executed"
    else:
        result = "Operation rejected"
    return {"execution_result": result}

# Build graph
builder = StateGraph(TodoState)
builder.add_node("parse", parser_node)
builder.add_node("validate", validator_node)
builder.add_node("execute", executor_node)

builder.add_edge(START, "parse")
builder.add_edge("parse", "validate")
builder.add_edge("validate", "execute")
builder.add_edge("execute", END)

# Test
graph = builder.compile()
result = graph.invoke({"user_request": "Add a task"})
print(result["execution_result"])  # "Operation executed"
```

### Week 1 Success Criteria
- [ ] Can explain agent loop
- [ ] Understand StateGraph structure (nodes, edges)
- [ ] 3-agent TODO system runs without errors
- [ ] All agents execute in correct order
- [ ] State flows correctly through agents

---

## Week 2: Voting System & Conflict Resolution

### Days 1-3: Voting Mechanism (5 hours)

**Learn to aggregate agent opinions:**

```python
from dataclasses import dataclass
from enum import Enum

class Vote(Enum):
    APPROVE = "approve"
    REJECT = "reject"

@dataclass
class AgentVote:
    agent_name: str
    vote: Vote
    weight: float = 1.0
    reasoning: str = ""

class VotingSystem:
    def __init__(self):
        self.votes = []
    
    def cast_vote(self, agent_name: str, vote: Vote, weight: float = 1.0, reasoning: str = ""):
        self.votes.append(AgentVote(agent_name, vote, weight, reasoning))
    
    def tally(self):
        approve_weight = sum(v.weight for v in self.votes if v.vote == Vote.APPROVE)
        reject_weight = sum(v.weight for v in self.votes if v.vote == Vote.REJECT)
        total = approve_weight + reject_weight
        
        if total == 0:
            return "NO_VOTES"
        
        if approve_weight / total > 0.5:
            return "APPROVED"
        elif reject_weight / total > 0.5:
            return "REJECTED"
        else:
            return "TIE"

# Example
voting = VotingSystem()
voting.cast_vote("Security", Vote.REJECT, weight=2.0, reasoning="Missing auth")
voting.cast_vote("Backend", Vote.APPROVE, weight=1.0, reasoning="Works fine")
voting.cast_vote("QA", Vote.REJECT, weight=1.5, reasoning="Slow")

result = voting.tally()
print(result)  # REJECTED (because QA + Security = 3.5 vs Backend = 1.0)
```

### Days 4-5: Conflict Detection (3 hours)

**Detect & log conflicts:**

```python
# Integrate voting into LangGraph

class VotingState(TypedDict):
    proposed_action: str
    agent_votes: list  # List of AgentVote dicts
    voting_result: str
    requires_human_review: bool

def voting_aggregator_node(state):
    voting_system = VotingSystem()
    
    # Process each agent's vote
    for vote_data in state["agent_votes"]:
        voting_system.cast_vote(
            agent_name=vote_data["agent"],
            vote=Vote[vote_data["position"].upper()],
            weight=vote_data["weight"],
            reasoning=vote_data["reasoning"]
        )
    
    result = voting_system.tally()
    
    return {
        "voting_result": result,
        "requires_human_review": result == "TIE"
    }

# Route based on voting result
def route_on_voting(state):
    if state["requires_human_review"]:
        return "human_review"
    elif state["voting_result"] == "APPROVED":
        return "execute"
    else:
        return "reject"
```

### Days 6-7: Human Review Interface (2 hours)

**Simple CLI for human decision:**

```python
def human_review_node(state):
    print("\n" + "="*50)
    print(f"CONFLICT DETECTED: {state['voting_result']}")
    print(f"Action: {state['proposed_action']}")
    print("\nVotes:")
    for vote in state["agent_votes"]:
        print(f"  {vote['agent']}: {vote['position']} ({vote['reasoning']})")
    
    decision = input("\nApprove? (y/n): ").lower() == "y"
    
    return {
        "human_decision": "approved" if decision else "rejected"
    }

def route_on_human_decision(state):
    return "execute" if state["human_decision"] == "approved" else "reject"
```

### Week 2 Project: Integrated TODO with Voting

```python
# Week 2 Final: TODO System with Voting

from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from enum import Enum

class TodoVotingState(TypedDict):
    user_request: str
    proposed_action: str
    agent_votes: list
    voting_result: str
    final_decision: str

def agent_1_votes(state):
    # Validator agent votes
    votes = [AgentVote(
        agent_name="Validator",
        vote=Vote.APPROVE if state["proposed_action"] != "delete_all" else Vote.REJECT,
        weight=1.5,
        reasoning="Safe operation" if Vote.APPROVE else "Risky operation"
    ).__dict__]
    return {"agent_votes": votes}

def agent_2_votes(state):
    # Storage agent votes
    votes = state["agent_votes"] + [AgentVote(
        agent_name="Storage",
        vote=Vote.APPROVE,
        weight=1.0,
        reasoning="Ready to execute"
    ).__dict__]
    return {"agent_votes": votes}

def agent_3_votes(state):
    # Safety agent votes
    votes = state["agent_votes"] + [AgentVote(
        agent_name="Safety",
        vote=Vote.APPROVE if not "delete" in state["proposed_action"] else Vote.REJECT,
        weight=2.0,
        reasoning="Safety check passed"
    ).__dict__]
    return {"agent_votes": votes}

# Build graph
builder = StateGraph(TodoVotingState)

# Parallel voting
builder.add_node("validator", agent_1_votes)
builder.add_node("storage", agent_2_votes)
builder.add_node("safety", agent_3_votes)

# Sequential: gather votes then aggregate
builder.add_edge(START, "validator")
builder.add_edge(START, "storage")
builder.add_edge(START, "safety")

builder.add_node("aggregate_votes", voting_aggregator_node)
builder.add_edge("validator", "aggregate_votes")
builder.add_edge("storage", "aggregate_votes")
builder.add_edge("safety", "aggregate_votes")

# Conditional routing
builder.add_node("human_review", human_review_node)
builder.add_node("execute", lambda s: {**s, "final_decision": "executed"})
builder.add_node("reject", lambda s: {**s, "final_decision": "rejected"})

builder.add_conditional_edges(
    "aggregate_votes",
    route_on_voting,
    {"human_review": "human_review", "execute": "execute", "reject": "reject"}
)

builder.add_edge("human_review", "execute")
builder.add_edge("execute", END)
builder.add_edge("reject", END)

voting_graph = builder.compile()

# Test
result = voting_graph.invoke({
    "user_request": "Delete all tasks",
    "proposed_action": "delete_all",
    "agent_votes": []
})

print(f"Result: {result['final_decision']}")
```

### Week 2 Success Criteria
- [ ] VotingSystem class implemented
- [ ] Vote tallying correct
- [ ] Weighted voting works (2x, 1.5x, 1.0x)
- [ ] Conflicts detected (TIE outcome)
- [ ] Human review triggered on conflicts
- [ ] Final decision logged
- [ ] Integrated TODO system runs end-to-end

---

## Week 3: Architecture Design & Planning

### Days 1-3: Software Dev Agent Architecture (5 hours)

**Design the system before building:**

```markdown
## Software Development Multi-Agent System

### 6 Specialized Agents

1. **Database Agent** (weight: 1.5x)
   - Design schema
   - Optimize queries
   - Validate constraints

2. **Backend Agent** (weight: 1.0x)
   - API design
   - Business logic
   - Error handling
   - Dependencies: Wait for Database

3. **Frontend Agent** (weight: 1.0x)
   - Component design
   - State management
   - UI flow
   - Dependencies: Wait for Backend

4. **Security Agent** (weight: 2.0x) ← Can veto
   - Vulnerability scan
   - Auth check
   - Data sanitization

5. **QA Agent** (weight: 1.5x)
   - Test coverage
   - Performance
   - Edge cases

6. **Orchestrator Agent** (weight: 1.0x)
   - Parse requirements
   - Task assignment
   - Progress monitoring

### Execution Flow

```
User Requirement
    ↓
[Orchestrator: Parse & Decompose]
    ↓
Parallel:
  [Database Design] →
  [Backend] → [Frontend] →
    ↓
  [Security Review] (blocks if issues)
    ↓
  [QA Testing]
    ↓
[Voting & Aggregation]
    ↓
[Human Review if conflict]
    ↓
[Final Code Output]
```

### Conflict Scenarios

1. Security says "Add auth", Backend says "Not needed"
   → Security weight 2.0x → Security wins

2. QA says "Too slow", Backend says "Works fine"
   → Equal weight → Tie → Human review

3. All agree → Auto-execute
```

### Days 4-5: Create Specification Document (5 hours)

**Create detailed spec:**

```markdown
# Software Development Agent System Specification

## Agents

### Agent 1: Database Designer
- **Role**: Database schema and query optimization
- **Inputs**: Requirements, tables needed
- **Outputs**: SQL schema, indexes, constraints
- **Voting Weight**: 1.5x
- **Can Influence**: Backend agent

### Agent 2: Backend Developer
- **Role**: REST API and business logic
- **Inputs**: Database schema, API contracts
- **Outputs**: Python/Node.js code
- **Voting Weight**: 1.0x
- **Dependencies**: Must await Database
- **Can Block**: Security concerns

### Agent 3: Frontend Developer
- **Role**: React components and UI
- **Inputs**: API contracts, design requirements
- **Outputs**: React component code
- **Voting Weight**: 1.0x
- **Dependencies**: Must await Backend
- **Can Block**: UX/accessibility issues

### Agent 4: Security Auditor
- **Role**: Vulnerability and compliance review
- **Inputs**: Backend code, API design
- **Outputs**: Security audit report
- **Voting Weight**: 2.0x ← Can veto
- **Veto Conditions**: 
  - Missing authentication
  - SQL injection vulnerability
  - Unencrypted sensitive data
  - CORS misconfiguration

### Agent 5: QA Engineer
- **Role**: Testing and performance
- **Inputs**: Code, database design
- **Outputs**: Test suite, performance analysis
- **Voting Weight**: 1.5x
- **Veto Conditions**:
  - Query performance < 100ms
  - Test coverage < 80%
  - Memory leak detected

### Agent 6: Orchestrator
- **Role**: Central coordination
- **Inputs**: User requirements
- **Outputs**: Task decomposition, progress
- **Voting Weight**: 1.0x
- **Responsibilities**:
  - Parse requirements
  - Assign tasks
  - Monitor dependencies
  - Escalate conflicts

## Voting Rules

### Automatic Decisions
- **All APPROVE** → Execute immediately
- **All REJECT** → Reject immediately
- **Security VETO** → Human review mandatory
- **TIE vote** → Human review mandatory

### Weighted Voting
```
Security (2.0x) + QA (1.5x) + Backend (1.0x) + Frontend (1.0x) + DB (1.5x)
```

Example:
- Security APPROVE (2.0)
- QA REJECT (1.5)
- Backend APPROVE (1.0)
- Total: 3.0 approve, 1.5 reject → APPROVED

### Human Review
Show:
1. All agent votes with reasoning
2. Weighted tallies
3. Conflict summary
4. Recommendations

Allow human to:
1. Accept majority
2. Override majority
3. Adjust weights
4. Request agent re-vote

## Implementation Phases

### Phase 1: Core Agents (Days 1-2)
- Implement 6 agent nodes
- Define state schema
- Add edges with dependencies

### Phase 2: Voting (Day 3)
- Integrate voting system
- Add vote aggregation
- Implement conflict detection

### Phase 3: Human Review (Day 4)
- Build review interface
- Add decision logging
- Implement overrides

### Phase 4: Testing (Day 5)
- Test all agents
- Test conflicts
- Test human overrides
```

### Week 3 Success Criteria
- [ ] Architecture specification document complete (3+ pages)
- [ ] 6 agents clearly defined
- [ ] Dependencies documented (acyclic)
- [ ] Voting rules explicit
- [ ] 3+ conflict scenarios described with resolution
- [ ] Human review process documented
- [ ] Can draw the system architecture
- [ ] No overlapping agent responsibilities

---

## Week 4: Implementation & Testing

### Days 1-2: Build Core System (8 hours)

**Implementation:**

```python
# Week 4: Software Dev Agents Implementation

from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from dataclasses import dataclass

class SoftwareDevState(TypedDict):
    user_requirement: str
    database_design: str
    backend_code: str
    frontend_code: str
    security_audit: dict
    qa_report: dict
    agent_votes: list
    voting_result: str
    human_decision: str
    final_output: dict

# Nodes
def orchestrator(state):
    return {"database_design": "Schema designed"}

def database_agent(state):
    return {"database_design": "CREATE TABLE users..."}

def backend_agent(state):
    code = """
@app.post("/tasks")
def create_task(user_id: int, title: str):
    return {"id": 1, "title": title}
"""
    return {"backend_code": code}

def frontend_agent(state):
    code = "export function TaskApp() { ... }"
    return {"frontend_code": code}

def security_agent(state):
    vote = AgentVote("Security", Vote.REJECT, 2.0, "Missing authentication")
    return {"agent_votes": [vote.__dict__]}

def qa_agent(state):
    votes = state["agent_votes"] + [AgentVote("QA", Vote.APPROVE, 1.5, "Test coverage OK").__dict__]
    return {"agent_votes": votes}

def voting_node(state):
    voting = VotingSystem()
    for vote_data in state["agent_votes"]:
        # Tally votes
        pass
    return {"voting_result": "TIE"}

def human_review_node(state):
    decision = input("Approve? (y/n): ")
    return {"human_decision": "approved" if decision == "y" else "rejected"}

def finalize_node(state):
    return {
        "final_output": {
            "database": state["database_design"],
            "backend": state["backend_code"],
            "frontend": state["frontend_code"],
            "audit": state["security_audit"],
            "qa": state["qa_report"]
        }
    }

# Build graph
builder = StateGraph(SoftwareDevState)

# Add nodes
for name, func in [
    ("orch", orchestrator),
    ("db", database_agent),
    ("backend", backend_agent),
    ("frontend", frontend_agent),
    ("security", security_agent),
    ("qa", qa_agent),
    ("voting", voting_node),
    ("human", human_review_node),
    ("finalize", finalize_node)
]:
    builder.add_node(name, func)

# Add edges with dependencies
builder.add_edge(START, "orch")
builder.add_edge("orch", "db")
builder.add_edge("db", "backend")
builder.add_edge("backend", "frontend")
builder.add_edge("frontend", "security")
builder.add_edge("security", "qa")
builder.add_edge("qa", "voting")
builder.add_conditional_edges(
    "voting",
    lambda s: "human" if s["voting_result"] == "TIE" else "finalize",
    {"human": "human", "finalize": "finalize"}
)
builder.add_edge("human", "finalize")
builder.add_edge("finalize", END)

# Compile & test
graph = builder.compile()
result = graph.invoke({"user_requirement": "Build a task app"})
```

### Days 3-4: Testing (6 hours)

**Test scenarios:**

```python
# test_scenarios.py

def test_simple_requirement():
    """No conflicts expected"""
    result = graph.invoke({"user_requirement": "Add status field to tasks"})
    assert result["voting_result"] in ["APPROVED", "REJECTED"]

def test_complex_requirement():
    """Multiple dependencies"""
    result = graph.invoke({
        "user_requirement": "Implement OAuth2, user roles, and data encryption"
    })
    assert "database_design" in result
    assert "backend_code" in result
    assert "frontend_code" in result

def test_security_conflict():
    """Security vs Backend"""
    # Modify agents to disagree
    result = graph.invoke({"user_requirement": "Public API endpoint"})
    assert result["voting_result"] == "TIE"  # Conflict

def test_human_override():
    """Human can override voting"""
    result = graph.invoke({"user_requirement": "Add feature"})
    # Simulate human input
    result = human_review_node(result)
    assert result["human_decision"] in ["approved", "rejected"]

# Run tests
if __name__ == "__main__":
    test_simple_requirement()
    print("✓ Simple requirement")
    
    test_complex_requirement()
    print("✓ Complex requirement")
    
    test_security_conflict()
    print("✓ Security conflict")
    
    test_human_override()
    print("✓ Human override")
    
    print("\nAll tests passed!")
```

### Days 5-7: Polish & Document (6 hours)

**Create final documentation:**

```markdown
# Software Dev Agent System - Final Documentation

## System Overview
Multi-agent system for autonomous code generation with:
- 6 specialized agents
- Dependency-aware task execution
- Weighted voting for conflict resolution
- Human review on tie/veto

## How to Use

### 1. Run the system
```bash
python software_dev_agents.py "Build a user authentication system"
```

### 2. System generates
- Database schema
- Backend API code
- Frontend components
- Security audit
- QA test suite

### 3. If conflicts arise
- Agents vote
- If tie: human reviews
- Human can approve/reject/modify weights

### 4. Output
JSON file with all generated code and audit reports

## Troubleshooting

**Agent doesn't run**: Check state schema matches node outputs
**Voting doesn't work**: Verify vote format and weights
**No human review**: Check if conflict detected (TIE outcome)

## Next Steps

1. Integrate with real LLMs (GPT-4, Claude)
2. Add persistent storage
3. Add progress monitoring
4. Deploy as service
```

### Week 4 Success Criteria
- [ ] All 6 agents implemented
- [ ] Dependencies enforced
- [ ] Voting system integrated
- [ ] All 4+ test scenarios pass
- [ ] System runs end-to-end without errors
- [ ] Decision log shows full trace
- [ ] Documentation complete
- [ ] Can explain architecture to someone unfamiliar with the code

---

## Accelerated Path Success Checklist

### Week 1
- [ ] LangGraph fundamentals understood
- [ ] StateGraph, nodes, edges, conditional edges working
- [ ] 3-agent TODO system built and tested
- [ ] Can explain agent loop and state flow

### Week 2
- [ ] VotingSystem class implemented
- [ ] Vote tallying correct with weights
- [ ] Conflict detection working
- [ ] Human review interface functional
- [ ] Integrated voting TODO system runs
- [ ] Can explain weighted voting and conflict resolution

### Week 3
- [ ] Architecture specification document written
- [ ] 6 agents clearly defined with no overlap
- [ ] Dependencies documented and acyclic
- [ ] Voting rules explicit
- [ ] Conflict scenarios detailed
- [ ] Human review process documented

### Week 4
- [ ] Software dev agent system implemented
- [ ] All nodes execute in correct order
- [ ] Voting integrated with graph
- [ ] All test scenarios pass
- [ ] Decision logs complete
- [ ] Final code generated correctly
- [ ] System is production-ready

---

## Comparison: Full vs Accelerated

| Aspect | Full (12 weeks) | Accelerated (4 weeks) |
|--------|-----------------|----------------------|
| **Foundations** | 3 weeks | Combined into Week 1 |
| **CrewAI** | 2 weeks | Skipped (use LangGraph directly) |
| **LangGraph** | 2 weeks | Integrated into Week 1 |
| **Voting** | 2 weeks | 1 week |
| **Implementation** | 3 weeks | 2 weeks |
| **Testing** | Ongoing | Focused in Week 4 |
| **Total Hours** | 130-150 | 40-50 |
| **Best For** | Thorough learning | Time-constrained developers |

---

## Resources for Accelerated Path

- **LangGraph Quick Start**: https://langchain-ai.github.io/langgraph/tutorials/getting-started/
- **StateGraph Guide**: https://langchain-ai.github.io/langgraph/concepts/high_level_plan/
- **OpenAI Function Calling**: https://platform.openai.com/docs/guides/function-calling
- **Example Projects**: https://github.com/langchain-ai/langgraph/tree/main/examples

---

**Ready to start?** Begin with Week 1, Day 1: LangGraph Fundamentals

**Questions?** Refer to main training program (`agentic_ai_training_program.md`) for detailed explanations
