# Week 8: Voting and Conflict Resolution

## Objective
Add weighted voting and human-in-the-loop review to the multi-agent code review system.

## What You Will Learn
- Weighted voting mechanics (not all agents are equal)
- Conflict detection: unanimous, majority, tie, veto
- Human-in-the-loop review for edge cases
- Audit trails for every decision

## Files
- `voting.py` -- VotingSystem, HumanReviewPanel, Vote/VotingResult dataclasses
- `test_voting.py` -- Tests for all voting scenarios (unanimous, veto, tie, low confidence, abstain)

## How to Run
```bash
# Run demo with 3 scenarios
python voting.py
```

## How to Test
```bash
pytest test_voting.py -v
```

## Success Criteria
- [ ] Weighted voting correctly tallies scores
- [ ] Security BLOCK always triggers human review (veto)
- [ ] Ties trigger human review
- [ ] Low-confidence votes trigger human review
- [ ] Decision log is complete and machine-parseable (JSON)
- [ ] Human reviewer can approve, reject, or modify

## Prerequisites
- Week 7 completed (this extends the code review system)
