"""Week 8: Voting and Conflict Resolution

Adds a weighted voting layer to the multi-agent code review system.
Each agent votes on the code, and conflicts trigger human review.

Demonstrates: weighted voting, conflict detection, human-in-the-loop, audit trails.
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
    """Weighted voting system for multi-agent decisions."""

    def __init__(self, weights: dict[str, float] = None):
        self.weights = weights or {}
        self.vote_history: list[VotingResult] = []

    def tally(self, votes: list[Vote]) -> VotingResult:
        """Tally votes and determine outcome.

        Resolution rules:
        - Any BLOCK from agent with weight >= 2.0 -> human_review (veto)
        - Unanimous APPROVE -> approved
        - Unanimous REQUEST_CHANGES/BLOCK -> rejected
        - Weighted approve > 0.75 of total -> approved
        - Tie or close margin -> human_review
        """
        # Apply weights
        for vote in votes:
            if vote.agent_name in self.weights:
                vote.weight = self.weights[vote.agent_name]

        # Filter out abstains
        active_votes = [v for v in votes if v.position != VotePosition.ABSTAIN]

        if not active_votes:
            result = VotingResult(
                outcome="human_review", weighted_approve=0, weighted_reject=0,
                votes=votes, requires_human=True, trigger_reason="no_active_votes",
            )
            self.vote_history.append(result)
            return result

        # Check for veto
        for v in active_votes:
            if v.position == VotePosition.BLOCK and v.weight >= 2.0:
                result = VotingResult(
                    outcome="human_review", weighted_approve=0, weighted_reject=0,
                    votes=votes, requires_human=True,
                    trigger_reason=f"veto_by_{v.agent_name}",
                )
                self.vote_history.append(result)
                return result

        # Calculate weighted scores
        total_weight = sum(v.weight for v in active_votes)
        approve_weight = sum(v.weight for v in active_votes if v.position == VotePosition.APPROVE)
        reject_weight = sum(
            v.weight for v in active_votes
            if v.position in (VotePosition.REQUEST_CHANGES, VotePosition.BLOCK)
        )

        approve_ratio = approve_weight / total_weight if total_weight > 0 else 0
        reject_ratio = reject_weight / total_weight if total_weight > 0 else 0

        # Check for low confidence
        avg_confidence = sum(v.confidence for v in active_votes) / len(active_votes)
        if avg_confidence < 0.5:
            result = VotingResult(
                outcome="human_review", weighted_approve=approve_weight,
                weighted_reject=reject_weight, votes=votes,
                requires_human=True, trigger_reason="low_confidence",
            )
            self.vote_history.append(result)
            return result

        # Determine outcome
        if approve_ratio >= 0.75:
            outcome = "approved"
            trigger = "majority" if approve_ratio < 1.0 else "unanimous"
            requires_human = False
        elif reject_ratio >= 0.75:
            outcome = "rejected"
            trigger = "majority" if reject_ratio < 1.0 else "unanimous"
            requires_human = False
        else:
            outcome = "human_review"
            trigger = "tie"
            requires_human = True

        result = VotingResult(
            outcome=outcome, weighted_approve=approve_weight,
            weighted_reject=reject_weight, votes=votes,
            requires_human=requires_human, trigger_reason=trigger,
        )
        self.vote_history.append(result)
        return result

    def get_history(self) -> list[dict]:
        """Get vote history as serializable dicts."""
        return [
            {
                "outcome": r.outcome,
                "trigger": r.trigger_reason,
                "requires_human": r.requires_human,
                "approve_weight": r.weighted_approve,
                "reject_weight": r.weighted_reject,
                "vote_count": len(r.votes),
            }
            for r in self.vote_history
        ]


# --- Human Review Interface ---

class HumanReviewPanel:
    """CLI interface for human review of agent decisions."""

    def __init__(self, auto_mode: bool = False, auto_decision: str = "approve"):
        self.auto_mode = auto_mode
        self.auto_decision = auto_decision
        self.decisions: list[dict] = []

    def review(self, voting_result: VotingResult, context: dict = None) -> str:
        """Present decision to human and get their input.

        Returns: "approve", "reject", or "modify"
        """
        if self.auto_mode:
            decision = self.auto_decision
        else:
            self._display(voting_result, context)
            decision = self._get_input()

        self.decisions.append({
            "trigger": voting_result.trigger_reason,
            "decision": decision,
            "timestamp": datetime.now().isoformat(),
        })
        return decision

    def _display(self, result: VotingResult, context: dict = None):
        print("\n" + "=" * 60)
        print("  HUMAN REVIEW REQUIRED")
        print("=" * 60)
        print(f"  Trigger: {result.trigger_reason}")
        print(f"  Approve weight: {result.weighted_approve:.1f}")
        print(f"  Reject weight: {result.weighted_reject:.1f}")
        print()
        for vote in result.votes:
            pos = vote.position.value.upper()
            print(f"  [{vote.agent_name}] {pos} (confidence: {vote.confidence:.0%}, weight: {vote.weight}x)")
            print(f"    Reason: {vote.reasoning}")
        print()
        if context:
            print(f"  Context: {json.dumps(context, indent=4)[:500]}")
        print("=" * 60)

    def _get_input(self) -> str:
        while True:
            choice = input("  Decision [approve/reject/modify]: ").strip().lower()
            if choice in ("approve", "reject", "modify"):
                return choice
            print("  Invalid choice. Enter: approve, reject, or modify")


if __name__ == "__main__":
    # Demo
    system = VotingSystem(weights={
        "security": 2.0,
        "analyzer": 1.5,
        "improver": 1.0,
    })

    # Scenario 1: Unanimous approve
    votes = [
        Vote("analyzer", VotePosition.APPROVE, 0.9, "Code looks clean"),
        Vote("security", VotePosition.APPROVE, 0.85, "No vulnerabilities found"),
        Vote("improver", VotePosition.APPROVE, 0.7, "Minor style suggestions only"),
    ]
    result = system.tally(votes)
    print(f"Scenario 1 (unanimous): {result.outcome} ({result.trigger_reason})")

    # Scenario 2: Security veto
    votes = [
        Vote("analyzer", VotePosition.APPROVE, 0.8, "Looks fine"),
        Vote("security", VotePosition.BLOCK, 0.95, "SQL injection vulnerability"),
        Vote("improver", VotePosition.APPROVE, 0.7, "Some improvements possible"),
    ]
    result = system.tally(votes)
    print(f"Scenario 2 (veto): {result.outcome} ({result.trigger_reason})")

    # Scenario 3: Tie
    votes = [
        Vote("analyzer", VotePosition.REQUEST_CHANGES, 0.7, "Has bugs"),
        Vote("security", VotePosition.APPROVE, 0.6, "Secure enough"),
        Vote("improver", VotePosition.REQUEST_CHANGES, 0.65, "Needs refactoring"),
    ]
    result = system.tally(votes)
    print(f"Scenario 3 (mixed): {result.outcome} ({result.trigger_reason})")

    print(f"\nVote history: {json.dumps(system.get_history(), indent=2)}")
