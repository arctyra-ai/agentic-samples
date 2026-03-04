#!/usr/bin/env python3
"""
Week 7: Human Review Interface
CLI interface for human review of voting outcomes.
Allows approve, reject, modify weights, and view details.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from voting_system import VotingSystem, VotePosition, Vote


class HumanReviewPanel:
    """CLI interface for human review of agent voting decisions"""

    def __init__(self, voting_system: VotingSystem):
        self.voting_system = voting_system

    def present_decision(self, action_description: str) -> str:
        """
        Show voting outcome and ask human for override.

        Returns: "proceed", "reject", or "modify"
        """
        result = self.voting_system.tally_votes()

        print("\n" + "=" * 60)
        print("HUMAN REVIEW REQUIRED")
        print("=" * 60)
        print(f"\nAction: {action_description}")
        print(f"\nVoting Result: {result['result']}")

        if "approve_percent" in result:
            print(f"Approval: {result['approve_percent'] * 100:.1f}%")

        if "vote_breakdown" in result:
            print("\nVote Breakdown:")
            for vote in result["vote_breakdown"]:
                print(f"  {vote['agent']:12} {vote['position']:10} ({vote['weight']}x weight)")
                print(f"    Reasoning: {vote['reasoning']}")

        print("\nYour Options:")
        print("  [A] Approve (accept agent vote)")
        print("  [R] Reject (override agents)")
        print("  [M] Modify (change agent weights)")
        print("  [S] Show full details")

        while True:
            choice = input("\nYour decision [A/R/M/S]: ").upper().strip()

            if choice == "A":
                return "proceed" if result.get("result") == "APPROVED" else "reject"
            elif choice == "R":
                return "reject" if result.get("result") == "APPROVED" else "proceed"
            elif choice == "M":
                self._modify_weights()
                # Recalculate with new weights
                return self.present_decision(action_description)
            elif choice == "S":
                print(f"\nFull result:\n{json.dumps(result, indent=2, default=str)}")
            else:
                print("Invalid choice. Enter A, R, M, or S.")

    def _modify_weights(self):
        """Allow human to adjust agent weights"""
        print("\nCurrent weights:")
        for agent, weight in self.voting_system.agent_weights.items():
            print(f"  {agent}: {weight}x")

        agent = input("Agent to modify (or 'done'): ").strip()
        if agent.lower() == "done":
            return

        if agent not in self.voting_system.agent_weights:
            print(f"Unknown agent: {agent}")
            return

        try:
            new_weight = float(input(f"New weight for {agent}: "))
            if new_weight < 0:
                print("Weight must be non-negative.")
                return
            self.voting_system.agent_weights[agent] = new_weight
            print(f"Updated {agent} weight to {new_weight}x")
        except ValueError:
            print("Invalid number.")

    def auto_review(self, action_description: str) -> str:
        """
        Non-interactive review for testing.
        Auto-approves if APPROVED, auto-rejects if REJECTED, escalates TIE.
        """
        result = self.voting_system.tally_votes()
        outcome = result.get("result", "NO_VOTES")

        if outcome == "APPROVED":
            return "proceed"
        elif outcome == "REJECTED":
            return "reject"
        elif outcome == "TIE":
            return "escalate"
        else:
            return "reject"


# ============================================================================
# Example usage
# ============================================================================

if __name__ == "__main__":
    voting_system = VotingSystem(agent_weights={
        "Security": 2.0,
        "QA": 1.5,
        "Backend": 1.0
    })

    voting_system.cast_vote(Vote(
        agent_name="Security",
        position=VotePosition.REJECT,
        reasoning="Missing authentication on endpoint",
        confidence=0.95
    ))

    voting_system.cast_vote(Vote(
        agent_name="Backend",
        position=VotePosition.APPROVE,
        reasoning="Implementation is straightforward",
        confidence=0.8
    ))

    voting_system.cast_vote(Vote(
        agent_name="QA",
        position=VotePosition.REJECT,
        reasoning="Performance concern on large datasets",
        confidence=0.7
    ))

    panel = HumanReviewPanel(voting_system)
    decision = panel.present_decision("Add public API endpoint without auth")
    print(f"\nFinal decision: {decision}")
