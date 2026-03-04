"""Week 9 STARTER: Evaluation and Observability

TODO: Build evaluation pipeline, cost tracking, and metrics reporting.
Copy this file to evaluation.py and fill in the TODO sections.
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.eval_helpers import run_evaluation, keyword_evaluator, EvalReport


# --- Cost Tracker ---

@dataclass
class CostTracker:
    """Track and enforce API cost budgets.

    TODO: Implement these methods:
    - record(): Add a call's cost to the tracker
    - check_budget(): Return True if within budget
    - remaining(): Return remaining budget
    - summary(): Return dict with budget, spent, remaining, calls, utilization_pct
    - cost_per_call(): Return average cost per call
    """
    budget_usd: float
    spent_usd: float = 0.0
    calls: int = 0
    history: list = field(default_factory=list)

    def record(self, model: str, input_tokens: int, output_tokens: int, cost_usd: float):
        # TODO: Track the cost and append to history
        pass

    def check_budget(self) -> bool:
        # TODO: Return True if spent < budget
        pass

    def remaining(self) -> float:
        # TODO: Return max(0, budget - spent)
        pass

    def summary(self) -> dict:
        # TODO: Return comprehensive summary dict
        pass

    def cost_per_call(self) -> float:
        # TODO: Return average cost per call
        pass


# --- Ground Truth Dataset ---

GROUND_TRUTH = [
    {
        "id": "gt_001",
        "code": "def login(user, pwd):\n    query = f'SELECT * FROM users WHERE name={user}'\n    return db.execute(query)",
        "filename": "auth.py",
        "known_issues": [
            {"type": "security", "description": "SQL injection via f-string"},
            {"type": "security", "description": "No password hashing"},
        ],
    },
    {
        "id": "gt_002",
        "code": "import pickle\ndef load_data(filepath):\n    with open(filepath, 'rb') as f:\n        return pickle.load(f)",
        "filename": "loader.py",
        "known_issues": [
            {"type": "security", "description": "Unsafe pickle deserialization"},
        ],
    },
    # TODO: Add 3+ more ground truth cases with known issues
]


def evaluate_code_review_system(review_fn, ground_truth: list[dict] = None) -> EvalReport:
    """Run evaluation against ground truth dataset.

    TODO:
    1. For each ground truth case, run review_fn(code, filename)
    2. Check if the review found the known issues (keyword matching)
    3. Use run_evaluation() from shared/eval_helpers.py
    4. Return the EvalReport
    """
    pass


def generate_metrics_report(eval_report: EvalReport, cost_tracker: CostTracker = None) -> dict:
    """Generate comprehensive metrics report.

    TODO: Combine evaluation results with cost tracking data.
    Include: accuracy, avg_score, avg_latency, cost summary, per-case details.
    """
    pass


if __name__ == "__main__":
    # Demo with a simple mock reviewer
    def mock_review(code, filename):
        findings = []
        if "f'" in code and "select" in code.lower():
            findings.append({"type": "security", "description": "SQL injection"})
        if "pickle" in code.lower():
            findings.append({"type": "security", "description": "unsafe pickle"})
        return {"findings": findings}

    tracker = CostTracker(budget_usd=5.00)
    report = evaluate_code_review_system(mock_review)
    metrics = generate_metrics_report(report, tracker)
    print(json.dumps(metrics, indent=2))
