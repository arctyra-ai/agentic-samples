"""Week 9: Evaluation and Observability

Builds an evaluation suite and cost tracking system for the code review agents.

Demonstrates: LangSmith integration, cost tracking, regression testing, metrics dashboards.
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
    """Track and enforce API cost budgets."""
    budget_usd: float
    spent_usd: float = 0.0
    calls: int = 0
    history: list = field(default_factory=list)

    def record(self, model: str, input_tokens: int, output_tokens: int, cost_usd: float):
        self.spent_usd += cost_usd
        self.calls += 1
        self.history.append({
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": cost_usd,
            "cumulative_usd": round(self.spent_usd, 4),
            "timestamp": datetime.now().isoformat(),
        })

    def check_budget(self) -> bool:
        """Returns True if within budget."""
        return self.spent_usd < self.budget_usd

    def remaining(self) -> float:
        return max(0, self.budget_usd - self.spent_usd)

    def summary(self) -> dict:
        return {
            "budget_usd": self.budget_usd,
            "spent_usd": round(self.spent_usd, 4),
            "remaining_usd": round(self.remaining(), 4),
            "total_calls": self.calls,
            "utilization_pct": round((self.spent_usd / self.budget_usd) * 100, 1) if self.budget_usd > 0 else 0,
        }

    def cost_per_call(self) -> float:
        if self.calls == 0:
            return 0
        return round(self.spent_usd / self.calls, 4)


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
            {"type": "quality", "description": "No input validation on filepath"},
        ],
    },
    {
        "id": "gt_003",
        "code": "def process(items):\n    result = []\n    for i in range(len(items)):\n        result.append(items[i] * 2)\n    return result",
        "filename": "process.py",
        "known_issues": [
            {"type": "quality", "description": "Non-Pythonic loop pattern"},
        ],
    },
    {
        "id": "gt_004",
        "code": "API_KEY = 'sk-abc123secret'\ndef call_api():\n    headers = {'Authorization': f'Bearer {API_KEY}'}\n    return requests.get('https://api.example.com', headers=headers)",
        "filename": "client.py",
        "known_issues": [
            {"type": "security", "description": "Hardcoded API key"},
        ],
    },
    {
        "id": "gt_005",
        "code": "def divide(a, b):\n    return a / b\n\ndef read_config(path):\n    return json.loads(open(path).read())",
        "filename": "utils.py",
        "known_issues": [
            {"type": "quality", "description": "No ZeroDivisionError handling"},
            {"type": "quality", "description": "File handle not closed properly"},
        ],
    },
]


def evaluate_code_review_system(review_fn, ground_truth: list[dict] = None) -> EvalReport:
    """Run evaluation against ground truth dataset.

    Args:
        review_fn: Function(code, filename) -> dict with keys like
                   'analyzer_findings', 'security_findings', 'synthesized_report'
        ground_truth: List of ground truth cases

    Returns:
        EvalReport with results
    """
    ground_truth = ground_truth or GROUND_TRUTH

    def agent_fn(input_data):
        code = input_data["code"]
        filename = input_data["filename"]
        result = review_fn(code, filename)
        # Flatten all findings into a single string for keyword matching
        all_findings = json.dumps(result, default=str)
        return all_findings

    def issue_evaluator(actual: str, expected: list[dict]) -> tuple[bool, float, dict]:
        actual_lower = actual.lower()
        found = []
        missing = []
        for issue in expected:
            keywords = issue["description"].lower().split()[:3]  # first 3 words
            if any(kw in actual_lower for kw in keywords):
                found.append(issue["description"])
            else:
                missing.append(issue["description"])
        score = len(found) / len(expected) if expected else 1.0
        return score >= 0.5, score, {"found": found, "missing": missing}

    test_cases = [
        {
            "id": case["id"],
            "input": {"code": case["code"], "filename": case["filename"]},
            "expected": case["known_issues"],
        }
        for case in ground_truth
    ]

    return run_evaluation(agent_fn, test_cases, issue_evaluator, metadata={"type": "code_review"})


# --- Metrics Report ---

def generate_metrics_report(eval_report: EvalReport, cost_tracker: CostTracker = None) -> dict:
    """Generate a comprehensive metrics report."""
    report = eval_report.summary()

    if cost_tracker:
        report["cost"] = cost_tracker.summary()
        report["cost_per_review"] = cost_tracker.cost_per_call()

    report["per_case"] = [
        {
            "id": r.case_id,
            "passed": r.passed,
            "score": round(r.score, 2),
            "latency_ms": round(r.latency_ms, 1),
            "details": r.details,
        }
        for r in eval_report.results
    ]

    return report


if __name__ == "__main__":
    # Demo with mock review function
    def mock_review(code: str, filename: str) -> dict:
        """Simulated review for testing the evaluation framework."""
        findings = []
        code_lower = code.lower()
        if "f'" in code and "select" in code_lower:
            findings.append({"type": "security", "description": "SQL injection via f-string"})
        if "pickle" in code_lower:
            findings.append({"type": "security", "description": "unsafe pickle deserialization"})
        if "api_key" in code_lower and "=" in code:
            findings.append({"type": "security", "description": "hardcoded API key"})
        if "range(len(" in code:
            findings.append({"type": "quality", "description": "non-Pythonic loop pattern"})
        return {"findings": findings}

    tracker = CostTracker(budget_usd=5.00)
    report = evaluate_code_review_system(mock_review)

    # Simulate some costs
    tracker.record("claude-sonnet", 1000, 500, 0.02)
    tracker.record("claude-sonnet", 1200, 600, 0.025)

    metrics = generate_metrics_report(report, tracker)
    print(json.dumps(metrics, indent=2))
