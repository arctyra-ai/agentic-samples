"""Week 8 STARTER: Voting and Conflict Resolution

TODO: Build a weighted voting system with human-in-the-loop review.
Copy this file to voting.py and fill in the TODO sections.
"""

import json
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


class VotePosition(Enum):
    APPROVE = "approve"
    REQUEST_CHANGES = "request_changes"
    BLOCK = "block"
    ABSTAIN = "abstain"


@dataclass
class Vote:
    agent_name: str
    position: VotePosition
    confidence: float  # 0.0 to 1.0
    reasoning: str
    weight: float = 1.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class VotingResult:
    outcome: str  # "approved", "rejected", "human_review"
    weighted_approve: float
    weighted_reject: float
    votes: list[Vote]
    requires_human: bool
    trigger_reason: str  # "unanimous", "majority", "tie", "veto", "low_confidence"


class VotingSystem:
    """Weighted voting system for multi-agent decisions.

    TODO: Implement the tally() method with these resolution rules:
    1. Apply weights from self.weights to each vote
    2. Filter out ABSTAIN votes
    3. If no active votes -> human_review (no_active_votes)
    4. If any BLOCK with weight >= 2.0 -> human_review (veto)
    5. Calculate weighted approve and reject scores
    6. If avg confidence < 0.5 -> human_review (low_confidence)
    7. If approve ratio >= 0.75 -> approved
    8. If reject ratio >= 0.75 -> rejected
    9. Otherwise -> human_review (tie)
    """

    def __init__(self, weights: dict[str, float] = None):
        self.weights = weights or {}
        self.vote_history: list[VotingResult] = []

    def tally(self, votes: list[Vote]) -> VotingResult:
        """Tally votes and determine outcome.

        TODO: Implement the resolution rules described above.
        Remember to:
        - Apply weights to votes based on agent_name
        - Track vote history
        - Return a VotingResult with all fields populated
        """
        pass

    def get_history(self) -> list[dict]:
        """Get vote history as serializable dicts."""
        return [
            {
                "outcome": r.outcome,
                "trigger": r.trigger_reason,
                "requires_human": r.requires_human,
                "vote_count": len(r.votes),
            }
            for r in self.vote_history
        ]


class HumanReviewPanel:
    """CLI interface for human review of agent decisions.

    TODO: Implement review() method that:
    - In auto_mode: returns self.auto_decision immediately
    - Otherwise: displays vote details and prompts for approve/reject/modify
    - Logs every decision to self.decisions list
    """

    def __init__(self, auto_mode: bool = False, auto_decision: str = "approve"):
        self.auto_mode = auto_mode
        self.auto_decision = auto_decision
        self.decisions: list[dict] = []

    def review(self, voting_result: VotingResult, context: dict = None) -> str:
        """Present decision to human and get input. Returns: approve, reject, or modify."""
        pass


if __name__ == "__main__":
    system = VotingSystem(weights={"security": 2.0, "analyzer": 1.5, "improver": 1.0})

    # Test scenario: unanimous approve
    votes = [
        Vote("analyzer", VotePosition.APPROVE, 0.9, "Code looks clean"),
        Vote("security", VotePosition.APPROVE, 0.85, "No vulnerabilities"),
        Vote("improver", VotePosition.APPROVE, 0.7, "Minor suggestions only"),
    ]
    result = system.tally(votes)
    print(f"Unanimous: {result.outcome} ({result.trigger_reason})")

    # Test scenario: security veto
    votes = [
        Vote("analyzer", VotePosition.APPROVE, 0.8, "Looks fine"),
        Vote("security", VotePosition.BLOCK, 0.95, "SQL injection found"),
        Vote("improver", VotePosition.APPROVE, 0.7, "OK"),
    ]
    result = system.tally(votes)
    print(f"Veto: {result.outcome} ({result.trigger_reason})")
