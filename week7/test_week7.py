#!/usr/bin/env python3
"""
Week 7: Test Cases for Voting System & Human Review
Tests VotingSystem, weighted voting, tallying, and HumanReviewPanel auto_review.
No API calls required.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from voting_system import VotingSystem, Vote, VotePosition
from human_review import HumanReviewPanel


class TestVotePosition(unittest.TestCase):
    """Test VotePosition enum"""

    def test_all_positions(self):
        self.assertEqual(VotePosition.APPROVE.value, "approve")
        self.assertEqual(VotePosition.REJECT.value, "reject")
        self.assertEqual(VotePosition.ABSTAIN.value, "abstain")


class TestVote(unittest.TestCase):
    """Test Vote dataclass"""

    def test_default_values(self):
        vote = Vote(agent_name="Test", position=VotePosition.APPROVE)
        self.assertEqual(vote.weight, 1.0)
        self.assertEqual(vote.reasoning, "")
        self.assertEqual(vote.confidence, 1.0)

    def test_custom_values(self):
        vote = Vote(
            agent_name="Security",
            position=VotePosition.REJECT,
            weight=2.0,
            reasoning="Vulnerability found",
            confidence=0.95
        )
        self.assertEqual(vote.agent_name, "Security")
        self.assertEqual(vote.weight, 2.0)


class TestVotingSystem(unittest.TestCase):
    """Test VotingSystem core logic"""

    def setUp(self):
        self.vs = VotingSystem(agent_weights={
            "Security": 2.0,
            "QA": 1.5,
            "Backend": 1.0
        })

    def test_no_votes(self):
        result = self.vs.tally_votes()
        self.assertEqual(result["result"], "NO_VOTES")

    def test_unanimous_approve(self):
        self.vs.cast_vote(Vote("Security", VotePosition.APPROVE))
        self.vs.cast_vote(Vote("QA", VotePosition.APPROVE))
        self.vs.cast_vote(Vote("Backend", VotePosition.APPROVE))
        result = self.vs.tally_votes()
        self.assertEqual(result["result"], "APPROVED")
        self.assertEqual(result["approve_percent"], 1.0)

    def test_unanimous_reject(self):
        self.vs.cast_vote(Vote("Security", VotePosition.REJECT))
        self.vs.cast_vote(Vote("QA", VotePosition.REJECT))
        result = self.vs.tally_votes()
        self.assertEqual(result["result"], "REJECTED")

    def test_weighted_security_overrides(self):
        """Security (2.0x) reject should outweigh Backend (1.0x) approve"""
        self.vs.cast_vote(Vote("Security", VotePosition.REJECT, reasoning="Vulnerability"))
        self.vs.cast_vote(Vote("Backend", VotePosition.APPROVE, reasoning="Works fine"))
        result = self.vs.tally_votes()
        self.assertEqual(result["result"], "REJECTED")

    def test_weighted_majority(self):
        """QA (1.5x) + Backend (1.0x) approve = 2.5x vs Security (2.0x) reject"""
        self.vs.cast_vote(Vote("Security", VotePosition.REJECT))
        self.vs.cast_vote(Vote("QA", VotePosition.APPROVE))
        self.vs.cast_vote(Vote("Backend", VotePosition.APPROVE))
        result = self.vs.tally_votes()
        self.assertEqual(result["result"], "APPROVED")

    def test_tie(self):
        """Equal weighted votes should result in TIE"""
        vs = VotingSystem(agent_weights={"A": 1.0, "B": 1.0})
        vs.cast_vote(Vote("A", VotePosition.APPROVE))
        vs.cast_vote(Vote("B", VotePosition.REJECT))
        result = vs.tally_votes()
        self.assertEqual(result["result"], "TIE")

    def test_abstain_not_counted(self):
        """Abstain votes should not affect the outcome"""
        self.vs.cast_vote(Vote("Security", VotePosition.APPROVE))
        self.vs.cast_vote(Vote("QA", VotePosition.ABSTAIN))
        self.vs.cast_vote(Vote("Backend", VotePosition.ABSTAIN))
        result = self.vs.tally_votes()
        self.assertEqual(result["result"], "APPROVED")

    def test_all_abstain(self):
        self.vs.cast_vote(Vote("Security", VotePosition.ABSTAIN))
        self.vs.cast_vote(Vote("QA", VotePosition.ABSTAIN))
        result = self.vs.tally_votes()
        self.assertEqual(result["result"], "ABSTAIN")

    def test_vote_breakdown_included(self):
        self.vs.cast_vote(Vote("Security", VotePosition.APPROVE, reasoning="OK"))
        result = self.vs.tally_votes()
        self.assertIn("vote_breakdown", result)
        self.assertEqual(len(result["vote_breakdown"]), 1)
        self.assertEqual(result["vote_breakdown"][0]["agent"], "Security")

    def test_reset_clears_votes(self):
        self.vs.cast_vote(Vote("Security", VotePosition.APPROVE))
        self.vs.reset()
        result = self.vs.tally_votes()
        self.assertEqual(result["result"], "NO_VOTES")

    def test_history_tracked(self):
        self.vs.cast_vote(Vote("Security", VotePosition.APPROVE))
        self.vs.reset()
        self.vs.cast_vote(Vote("QA", VotePosition.REJECT))
        self.vs.reset()
        history = self.vs.get_history()
        self.assertEqual(len(history), 2)

    def test_weight_applied_from_agent_weights(self):
        """Weights from agent_weights dict should multiply vote weight"""
        self.vs.cast_vote(Vote("Security", VotePosition.APPROVE))
        # Security has 2.0x weight, default vote weight is 1.0
        result = self.vs.tally_votes()
        self.assertEqual(result["approve_weight"], 2.0)


class TestHumanReviewAutoReview(unittest.TestCase):
    """Test HumanReviewPanel non-interactive auto_review"""

    def test_auto_approve(self):
        vs = VotingSystem()
        vs.cast_vote(Vote("A", VotePosition.APPROVE))
        vs.cast_vote(Vote("B", VotePosition.APPROVE))
        panel = HumanReviewPanel(vs)
        self.assertEqual(panel.auto_review("Test action"), "proceed")

    def test_auto_reject(self):
        vs = VotingSystem(agent_weights={"A": 2.0, "B": 1.0})
        vs.cast_vote(Vote("A", VotePosition.REJECT))
        vs.cast_vote(Vote("B", VotePosition.APPROVE))
        panel = HumanReviewPanel(vs)
        self.assertEqual(panel.auto_review("Test action"), "reject")

    def test_auto_escalate_tie(self):
        vs = VotingSystem(agent_weights={"A": 1.0, "B": 1.0})
        vs.cast_vote(Vote("A", VotePosition.APPROVE))
        vs.cast_vote(Vote("B", VotePosition.REJECT))
        panel = HumanReviewPanel(vs)
        self.assertEqual(panel.auto_review("Test action"), "escalate")

    def test_auto_reject_no_votes(self):
        vs = VotingSystem()
        panel = HumanReviewPanel(vs)
        self.assertEqual(panel.auto_review("Test action"), "reject")


if __name__ == "__main__":
    unittest.main()
