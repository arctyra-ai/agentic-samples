# Week 8 Lesson: Voting and Conflict Resolution

## What You Are Building

This week you add a decision layer to the multi-agent code review system. Instead of the synthesizer simply combining findings, agents now cast votes (approve, request changes, or block), and a voting system determines the outcome. When agents disagree, the system detects the conflict and routes it to a human reviewer.

This addresses a fundamental problem in multi-agent systems: what happens when agents disagree? In Week 7, the synthesizer resolved conflicts by summarizing them. That works for advisory reports but not for decisions. When the system must decide whether to approve or reject code, you need a formal resolution mechanism with clear rules, weights, and escalation paths.

Voting systems, human-in-the-loop review, and escalation policies are standard patterns in production multi-agent deployments for code review, content moderation, compliance checking, and any domain where the cost of a wrong decision is high.

## Core Concepts

### Weighted Voting

Not all agents are equal. A security auditor's opinion on a SQL injection should carry more weight than a style improver's opinion. Weights encode this.

```python
system = VotingSystem(weights={
    "security": 2.0,   # Security issues are critical
    "analyzer": 1.5,   # Quality bugs matter
    "improver": 1.0,   # Style suggestions matter less
})
```

The weighted tally computes approval and rejection ratios:

```python
total_weight = sum(v.weight for v in active_votes)
approve_weight = sum(v.weight for v in votes if v.position == APPROVE)
approve_ratio = approve_weight / total_weight  # 0.0 to 1.0
```

A threshold (e.g., 75%) determines whether the weighted majority is strong enough to auto-decide.

### Resolution Rules

The voting system applies rules in priority order. Each rule maps a condition to an outcome:

1. **Veto**: Any BLOCK from an agent with weight >= 2.0 triggers human review. This gives the security agent effective veto power.
2. **Low confidence**: If average confidence across agents is below 50%, escalate to human review. Uncertain agents should not make decisions.
3. **Strong majority**: If weighted approve ratio >= 75%, auto-approve. If weighted reject ratio >= 75%, auto-reject.
4. **Tie**: Everything else goes to human review.

```python
# Veto check
for v in active_votes:
    if v.position == BLOCK and v.weight >= 2.0:
        return VotingResult(outcome="human_review", trigger_reason="veto")

# Confidence check
avg_confidence = sum(v.confidence for v in active_votes) / len(active_votes)
if avg_confidence < 0.5:
    return VotingResult(outcome="human_review", trigger_reason="low_confidence")

# Majority check
if approve_ratio >= 0.75:
    return VotingResult(outcome="approved", trigger_reason="majority")
```

Watch for: the order of these checks matters. Veto must be checked before majority, otherwise a security BLOCK could be overridden by two approvals. Design your rules so higher-severity conditions are checked first.

### Vote Data Model

Each vote captures who voted, their position, confidence level, and reasoning. This creates an audit trail for every decision.

```python
@dataclass
class Vote:
    agent_name: str
    position: VotePosition  # APPROVE, REQUEST_CHANGES, BLOCK, ABSTAIN
    confidence: float       # 0.0 to 1.0
    reasoning: str          # Why the agent voted this way
    weight: float = 1.0     # Applied by the voting system
```

The confidence score is important. An agent that says APPROVE with 0.3 confidence is fundamentally different from one that says APPROVE with 0.95 confidence. Low-confidence approvals should not count the same as high-confidence ones.

Watch for: ABSTAIN votes are filtered out before tallying. An agent that cannot evaluate the code (e.g., the security auditor reviewing a pure documentation change) should abstain rather than guess.

### Human-in-the-Loop

When the system cannot auto-decide (veto, tie, low confidence), it presents the decision to a human reviewer with full context: all agent votes, their reasoning, confidence levels, and the specific trigger that caused escalation.

```python
class HumanReviewPanel:
    def review(self, voting_result: VotingResult) -> str:
        self._display(voting_result)  # Show votes, reasoning, trigger
        return self._get_input()      # approve, reject, or modify
```

In production, this is a web interface (Slack notification, dashboard queue, email). For this exercise, it is a CLI prompt. The auto_mode flag lets tests run without waiting for human input.

### Audit Trail

Every decision -- whether auto-decided or human-reviewed -- is logged with its full context. This is a compliance requirement in regulated industries and a debugging necessity everywhere else.

```python
system.get_history()
# [
#   {"outcome": "approved", "trigger": "unanimous", "vote_count": 3},
#   {"outcome": "human_review", "trigger": "veto_by_security", "vote_count": 3},
# ]
```

## How the Pieces Connect

This week's voting system integrates with Week 7's multi-agent review to create a complete decision pipeline: agents analyze code, cast votes, and the system determines the outcome. Week 9 adds evaluation -- measuring how often the voting system agrees with human reviewers and tracking the cost of each decision. The capstone requires voting/conflict resolution as a core component.

The human-in-the-loop pattern appears in production agent systems wherever the cost of a wrong autonomous decision exceeds the cost of human review time. Learning where to place these gates is a design skill that distinguishes senior agent engineers.

## Now Build It

Open `README.md` for the exercise specification. Copy `voting_starter.py` to `voting.py` and implement the TODOs. This exercise is pure Python -- no LLM calls, no external dependencies. Focus on getting the resolution rules right. Run `pytest test_voting.py -v` to validate all 12 voting scenarios (unanimous, veto, tie, low confidence, abstain, weighted majority, etc.).
