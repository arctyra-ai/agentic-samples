"""Tests for Week 9: Evaluation and Observability."""

import pytest
from evaluation import CostTracker, GROUND_TRUTH, evaluate_code_review_system, generate_metrics_report


class TestCostTracker:
    def test_starts_empty(self):
        tracker = CostTracker(budget_usd=10.0)
        assert tracker.spent_usd == 0
        assert tracker.calls == 0
        assert tracker.check_budget() is True

    def test_records_costs(self):
        tracker = CostTracker(budget_usd=1.0)
        tracker.record("model", 100, 50, 0.01)
        assert tracker.spent_usd == 0.01
        assert tracker.calls == 1

    def test_budget_exceeded(self):
        tracker = CostTracker(budget_usd=0.05)
        tracker.record("model", 100, 50, 0.03)
        tracker.record("model", 100, 50, 0.03)
        assert tracker.check_budget() is False

    def test_remaining(self):
        tracker = CostTracker(budget_usd=1.0)
        tracker.record("model", 100, 50, 0.25)
        assert tracker.remaining() == 0.75

    def test_cost_per_call(self):
        tracker = CostTracker(budget_usd=10.0)
        tracker.record("model", 100, 50, 0.10)
        tracker.record("model", 100, 50, 0.20)
        assert tracker.cost_per_call() == 0.15

    def test_summary(self):
        tracker = CostTracker(budget_usd=5.0)
        tracker.record("model", 100, 50, 1.0)
        s = tracker.summary()
        assert s["budget_usd"] == 5.0
        assert s["spent_usd"] == 1.0
        assert s["utilization_pct"] == 20.0


class TestGroundTruth:
    def test_has_cases(self):
        assert len(GROUND_TRUTH) >= 5

    def test_cases_have_required_fields(self):
        for case in GROUND_TRUTH:
            assert "id" in case
            assert "code" in case
            assert "filename" in case
            assert "known_issues" in case
            assert len(case["known_issues"]) > 0

    def test_ids_unique(self):
        ids = [c["id"] for c in GROUND_TRUTH]
        assert len(ids) == len(set(ids))


class TestEvaluation:
    def test_mock_review_detects_sql_injection(self):
        def mock_review(code, filename):
            if "f'" in code and "select" in code.lower():
                return {"findings": [{"type": "security", "description": "SQL injection"}]}
            return {"findings": []}

        report = evaluate_code_review_system(mock_review)
        assert report.summary()["total_cases"] == len(GROUND_TRUTH)

    def test_generates_metrics_report(self):
        def noop_review(code, filename):
            return {"findings": []}

        report = evaluate_code_review_system(noop_review)
        tracker = CostTracker(budget_usd=1.0)
        tracker.record("model", 100, 50, 0.01)

        metrics = generate_metrics_report(report, tracker)
        assert "accuracy" in metrics
        assert "cost" in metrics
        assert "per_case" in metrics
