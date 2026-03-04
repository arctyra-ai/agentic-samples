#!/usr/bin/env python3
"""
Week 5: Conflict Detection System
Detects and logs disagreements between agents.
"""

from dataclasses import dataclass, asdict
from enum import Enum
from typing import List
from datetime import datetime
import json


class ConflictType(Enum):
    VALIDATION_REJECTED = "validation_rejected"
    DATA_CONFLICT = "data_conflict"
    PERFORMANCE_CONCERN = "performance_concern"
    SECURITY_ISSUE = "security_issue"


@dataclass
class AgentOpinion:
    agent_name: str
    position: str  # "approve", "reject", "concern"
    reasoning: str
    confidence: float  # 0.0 to 1.0


@dataclass
class ConflictResolution:
    action: str
    requires_human_review: bool
    reasoning: str


class ConflictDetector:
    """Detect and log disagreements between agents"""

    def __init__(self):
        self.conflicts = []

    def detect_conflict(self, opinions: List[AgentOpinion]) -> bool:
        """Check if agents disagree. Returns True if positions are not unanimous."""
        positions = [op.position for op in opinions]
        return len(set(positions)) > 1

    def log_conflict(self, conflict_type: ConflictType, opinions: List[AgentOpinion]):
        """Record conflict with full details"""
        self.conflicts.append({
            "type": conflict_type.value,
            "opinions": [asdict(op) for op in opinions],
            "timestamp": datetime.now().isoformat()
        })

    def get_conflicts(self) -> list:
        """Return all recorded conflicts"""
        return self.conflicts

    def resolve_simple(self, opinions: List[AgentOpinion]) -> ConflictResolution:
        """
        Simple resolution: majority wins, high-confidence concerns escalate.
        Returns a ConflictResolution with recommended action.
        """
        approve_count = sum(1 for op in opinions if op.position == "approve")
        reject_count = sum(1 for op in opinions if op.position == "reject")
        concern_count = sum(1 for op in opinions if op.position == "concern")

        # Any high-confidence concern or rejection triggers human review
        high_confidence_issues = [
            op for op in opinions
            if op.position in ("reject", "concern") and op.confidence >= 0.9
        ]

        if high_confidence_issues:
            return ConflictResolution(
                action="escalate",
                requires_human_review=True,
                reasoning=f"High-confidence concern from: {', '.join(op.agent_name for op in high_confidence_issues)}"
            )

        if approve_count > reject_count + concern_count:
            return ConflictResolution(
                action="proceed",
                requires_human_review=False,
                reasoning="Majority approved"
            )

        return ConflictResolution(
            action="escalate",
            requires_human_review=True,
            reasoning=f"No clear majority: {approve_count} approve, {reject_count} reject, {concern_count} concern"
        )


# ============================================================================
# Example: Storage vs Validator conflict
# ============================================================================

if __name__ == "__main__":
    detector = ConflictDetector()

    storage_opinion = AgentOpinion(
        agent_name="Storage Agent",
        position="approve",
        reasoning="User explicitly requested delete all tasks",
        confidence=0.9
    )

    validator_opinion = AgentOpinion(
        agent_name="Validator Agent",
        position="concern",
        reasoning="This is a destructive operation. Should confirm first.",
        confidence=0.95
    )

    opinions = [storage_opinion, validator_opinion]

    if detector.detect_conflict(opinions):
        print("CONFLICT DETECTED:")
        detector.log_conflict(ConflictType.DATA_CONFLICT, opinions)
        for op in opinions:
            print(f"  {op.agent_name}: {op.position} (confidence: {op.confidence})")
            print(f"    Reasoning: {op.reasoning}")

        resolution = detector.resolve_simple(opinions)
        print(f"\nResolution: {resolution.action}")
        print(f"Human review required: {resolution.requires_human_review}")
        print(f"Reasoning: {resolution.reasoning}")
    else:
        print("No conflict - all agents agree.")
