"""Tests for Week 8: Voting and Conflict Resolution."""

import pytest
from voting import Vote, VotePosition, VotingSystem, VotingResult, HumanReviewPanel


@pytest.fixture
def weighted_system():
    return VotingSystem(weights={"security": 2.0, "analyzer": 1.5, "improver": 1.0})


class TestVotingSystem:
    def test_unanimous_approve(self, weighted_system):
        votes = [
            Vote("analyzer", VotePosition.APPROVE, 0.9, "Good"),
            Vote("security", VotePosition.APPROVE, 0.85, "Safe"),
            Vote("improver", VotePosition.APPROVE, 0.8, "Clean"),
        ]
        result = weighted_system.tally(votes)
        assert result.outcome == "approved"
        assert result.trigger_reason == "unanimous"
        assert not result.requires_human

    def test_unanimous_reject(self, weighted_system):
        votes = [
            Vote("analyzer", VotePosition.REQUEST_CHANGES, 0.9, "Bugs"),
            Vote("security", VotePosition.BLOCK, 0.95, "Vuln"),
            Vote("improver", VotePosition.REQUEST_CHANGES, 0.8, "Bad"),
        ]
        result = weighted_system.tally(votes)
        # Security BLOCK with weight 2.0 triggers veto before unanimous check
        assert result.requires_human
        assert "veto" in result.trigger_reason

    def test_security_veto(self, weighted_system):
        votes = [
            Vote("analyzer", VotePosition.APPROVE, 0.9, "Fine"),
            Vote("security", VotePosition.BLOCK, 0.95, "SQL injection"),
            Vote("improver", VotePosition.APPROVE, 0.8, "OK"),
        ]
        result = weighted_system.tally(votes)
        assert result.outcome == "human_review"
        assert "veto" in result.trigger_reason

    def test_weighted_majority_approve(self, weighted_system):
        votes = [
            Vote("analyzer", VotePosition.APPROVE, 0.9, "Clean"),      # 1.5
            Vote("security", VotePosition.APPROVE, 0.85, "Safe"),       # 2.0
            Vote("improver", VotePosition.REQUEST_CHANGES, 0.6, "Meh"), # 1.0
        ]
        result = weighted_system.tally(votes)
        # approve: 3.5, reject: 1.0, ratio: 3.5/4.5 = 0.78 > 0.75
        assert result.outcome == "approved"

    def test_tie_triggers_human_review(self, weighted_system):
        votes = [
            Vote("analyzer", VotePosition.APPROVE, 0.7, "OK"),          # 1.5
            Vote("security", VotePosition.REQUEST_CHANGES, 0.7, "Risk"),  # 2.0
            Vote("improver", VotePosition.APPROVE, 0.6, "Fine"),         # 1.0
        ]
        result = weighted_system.tally(votes)
        # approve: 2.5, reject: 2.0, neither >= 0.75
        assert result.outcome == "human_review"
        assert result.trigger_reason == "tie"

    def test_all_abstain(self, weighted_system):
        votes = [
            Vote("analyzer", VotePosition.ABSTAIN, 0.5, "N/A"),
            Vote("security", VotePosition.ABSTAIN, 0.5, "N/A"),
        ]
        result = weighted_system.tally(votes)
        assert result.requires_human
        assert result.trigger_reason == "no_active_votes"

    def test_low_confidence_triggers_human(self, weighted_system):
        votes = [
            Vote("analyzer", VotePosition.APPROVE, 0.3, "Maybe"),
            Vote("security", VotePosition.APPROVE, 0.2, "Unsure"),
            Vote("improver", VotePosition.APPROVE, 0.4, "Possibly"),
        ]
        result = weighted_system.tally(votes)
        assert result.outcome == "human_review"
        assert result.trigger_reason == "low_confidence"

    def test_vote_history_tracked(self, weighted_system):
        votes = [Vote("analyzer", VotePosition.APPROVE, 0.9, "OK")]
        weighted_system.tally(votes)
        weighted_system.tally(votes)
        assert len(weighted_system.get_history()) == 2

    def test_unweighted_system(self):
        system = VotingSystem()
        votes = [
            Vote("a", VotePosition.APPROVE, 0.9, "OK"),
            Vote("b", VotePosition.APPROVE, 0.9, "OK"),
        ]
        result = system.tally(votes)
        assert result.outcome == "approved"


class TestHumanReviewPanel:
    def test_auto_mode_approve(self):
        panel = HumanReviewPanel(auto_mode=True, auto_decision="approve")
        result = VotingResult("human_review", 1.0, 1.0, [], True, "tie")
        decision = panel.review(result)
        assert decision == "approve"

    def test_auto_mode_reject(self):
        panel = HumanReviewPanel(auto_mode=True, auto_decision="reject")
        result = VotingResult("human_review", 1.0, 1.0, [], True, "tie")
        decision = panel.review(result)
        assert decision == "reject"

    def test_decisions_logged(self):
        panel = HumanReviewPanel(auto_mode=True, auto_decision="approve")
        result = VotingResult("human_review", 1.0, 1.0, [], True, "tie")
        panel.review(result)
        panel.review(result)
        assert len(panel.decisions) == 2
        assert panel.decisions[0]["decision"] == "approve"
