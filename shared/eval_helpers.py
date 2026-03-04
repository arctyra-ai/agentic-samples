"""Evaluation helpers for agent systems.

Provides utilities for running evaluations, comparing runs,
and generating metrics reports.
"""

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime


@dataclass
class EvalResult:
    """Result of a single evaluation case."""
    case_id: str
    passed: bool
    score: float  # 0.0 to 1.0
    expected: str
    actual: str
    latency_ms: float
    details: dict = field(default_factory=dict)


@dataclass
class EvalReport:
    """Aggregated evaluation report."""
    run_id: str
    timestamp: str
    results: list[EvalResult]
    metadata: dict = field(default_factory=dict)

    @property
    def accuracy(self) -> float:
        if not self.results:
            return 0.0
        return sum(1 for r in self.results if r.passed) / len(self.results)

    @property
    def avg_score(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.score for r in self.results) / len(self.results)

    @property
    def avg_latency_ms(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.latency_ms for r in self.results) / len(self.results)

    def summary(self) -> dict:
        return {
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "total_cases": len(self.results),
            "passed": sum(1 for r in self.results if r.passed),
            "failed": sum(1 for r in self.results if not r.passed),
            "accuracy": round(self.accuracy, 3),
            "avg_score": round(self.avg_score, 3),
            "avg_latency_ms": round(self.avg_latency_ms, 1),
            "metadata": self.metadata,
        }

    def save(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        data = {
            "summary": self.summary(),
            "results": [
                {
                    "case_id": r.case_id,
                    "passed": r.passed,
                    "score": r.score,
                    "expected": r.expected,
                    "actual": r.actual,
                    "latency_ms": r.latency_ms,
                    "details": r.details,
                }
                for r in self.results
            ],
        }
        Path(path).write_text(json.dumps(data, indent=2))


def run_evaluation(
    agent_fn,
    test_cases: list[dict],
    evaluator_fn,
    run_id: str = None,
    metadata: dict = None,
) -> EvalReport:
    """Run an evaluation suite against an agent function.

    Args:
        agent_fn: Function that takes a test case input and returns output.
        test_cases: List of dicts with 'id', 'input', and 'expected' keys.
        evaluator_fn: Function(actual, expected) -> (passed: bool, score: float, details: dict)
        run_id: Optional identifier for this run.
        metadata: Optional metadata to attach to the report.

    Returns:
        EvalReport with all results.
    """
    run_id = run_id or datetime.now().strftime("%Y%m%d_%H%M%S")
    results = []

    for case in test_cases:
        start = time.time()
        try:
            actual = agent_fn(case["input"])
        except Exception as e:
            actual = f"ERROR: {e}"
        latency_ms = (time.time() - start) * 1000

        passed, score, details = evaluator_fn(actual, case["expected"])
        results.append(EvalResult(
            case_id=case["id"],
            passed=passed,
            score=score,
            expected=str(case["expected"]),
            actual=str(actual),
            latency_ms=latency_ms,
            details=details,
        ))

    return EvalReport(
        run_id=run_id,
        timestamp=datetime.now().isoformat(),
        results=results,
        metadata=metadata or {},
    )


def keyword_evaluator(actual: str, expected: list[str]) -> tuple[bool, float, dict]:
    """Simple evaluator: check if expected keywords appear in actual output."""
    actual_lower = actual.lower()
    found = [kw for kw in expected if kw.lower() in actual_lower]
    missing = [kw for kw in expected if kw.lower() not in actual_lower]
    score = len(found) / len(expected) if expected else 1.0
    passed = score >= 0.8
    return passed, score, {"found": found, "missing": missing}


def compare_runs(report_a: EvalReport, report_b: EvalReport) -> dict:
    """Compare two evaluation runs and identify regressions."""
    a_scores = {r.case_id: r.score for r in report_a.results}
    b_scores = {r.case_id: r.score for r in report_b.results}

    regressions = []
    improvements = []
    for case_id in a_scores:
        if case_id in b_scores:
            diff = b_scores[case_id] - a_scores[case_id]
            if diff < -0.1:
                regressions.append({"case_id": case_id, "delta": round(diff, 3)})
            elif diff > 0.1:
                improvements.append({"case_id": case_id, "delta": round(diff, 3)})

    return {
        "run_a": report_a.run_id,
        "run_b": report_b.run_id,
        "accuracy_a": round(report_a.accuracy, 3),
        "accuracy_b": round(report_b.accuracy, 3),
        "regressions": regressions,
        "improvements": improvements,
        "net_change": round(report_b.accuracy - report_a.accuracy, 3),
    }
