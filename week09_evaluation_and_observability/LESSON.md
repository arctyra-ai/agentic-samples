# Week 9 Lesson: Evaluation and Observability

## What You Are Building

This week you build the measurement layer for your multi-agent system: a ground truth evaluation pipeline, a cost tracking system with budget enforcement, and a metrics dashboard that combines both. You will measure whether the code review agents actually find the bugs they should, how much each review costs, and whether changes to the system improve or degrade quality.

Evaluation is what separates prototype agents from production agents. A demo that works on 3 cherry-picked examples is not evidence that a system works. A system that scores 80% on a 20-case ground truth dataset with tracked cost per request is evidence. Every production AI role requires evaluation skills -- it appears in job postings as "building eval pipelines," "measuring agent quality," or "LLM evaluation frameworks."

This week is also where you learn that non-determinism is a feature of LLM systems, not a bug. The same code review agent given the same input twice may produce slightly different findings. Your evaluation framework must account for this.

## Core Concepts

### Ground Truth Datasets

A ground truth dataset is a set of inputs with known correct outputs. For the code review system, each case is a code snippet with known issues:

```python
GROUND_TRUTH = [
    {
        "id": "gt_001",
        "code": "query = f'SELECT * FROM users WHERE name={user}'",
        "filename": "auth.py",
        "known_issues": [
            {"type": "security", "description": "SQL injection via f-string"},
            {"type": "security", "description": "No password hashing"},
        ],
    },
    # ... more cases
]
```

The evaluation runs the system against each case and checks whether the known issues were detected. This is not about perfect detection -- it is about establishing a measurable baseline that you can track over time.

Watch for: start with at least 5 cases. Fewer than 5 and individual results dominate the average. More than 20 is ideal for production but expensive to create by hand. The cases should cover different issue types (security, quality, performance) and difficulty levels (obvious bugs vs. subtle ones).

### Evaluation Metrics

The core metrics for agent evaluation:

```python
accuracy = cases_passed / total_cases      # Did the system find the issues?
avg_score = sum(scores) / total_cases      # How many issues per case were found?
avg_latency = sum(latencies) / total_cases # How long does each review take?
cost_per_review = total_cost / total_cases # How much does each review cost?
```

A case "passes" if the system detects at least 50% of the known issues (configurable threshold). The score is the fraction of issues detected. This allows partial credit -- finding 1 of 2 known issues is better than finding 0.

```python
def issue_evaluator(actual: str, expected: list[dict]) -> tuple[bool, float, dict]:
    found = [issue for issue in expected if keywords_match(actual, issue)]
    missing = [issue for issue in expected if not keywords_match(actual, issue)]
    score = len(found) / len(expected)
    passed = score >= 0.5
    return passed, score, {"found": found, "missing": missing}
```

### Cost Tracking and Budget Enforcement

Every LLM call has a cost. The `CostTracker` records each call and enforces a budget limit:

```python
tracker = CostTracker(budget_usd=5.00)
tracker.record(model="claude-sonnet", input_tokens=1000, output_tokens=500, cost_usd=0.02)

tracker.check_budget()    # True (within budget)
tracker.remaining()       # 4.98
tracker.cost_per_call()   # 0.02
tracker.summary()         # {"budget_usd": 5.0, "spent_usd": 0.02, "utilization_pct": 0.4}
```

Budget enforcement is a hard requirement for production agents. Without it, a loop bug or an unusually complex input can cause unbounded API spending. The tracker should stop execution before the budget is exceeded, not after.

Watch for: estimated costs from token counting are approximations. Actual charges from the API provider may differ slightly due to prompt caching, batch discounts, or pricing changes. Build in a 10-20% margin.

### Regression Testing

When you change the system (new prompt, different model, updated tool descriptions), you need to know if quality improved or degraded. Regression testing compares two evaluation runs:

```python
comparison = compare_runs(report_before, report_after)
# {
#   "accuracy_a": 0.80,
#   "accuracy_b": 0.85,
#   "regressions": [{"case_id": "gt_003", "delta": -0.5}],
#   "improvements": [{"case_id": "gt_005", "delta": 0.5}],
#   "net_change": 0.05
# }
```

A net improvement can hide regressions. If accuracy goes from 80% to 85% but case gt_003 went from passing to failing, you need to know about gt_003 specifically. Always report per-case results, not just aggregates.

### LangSmith Integration

LangSmith (free tier) provides production-grade tracing for LangGraph executions. It records every node execution, every LLM call, token usage, and latency -- automatically, with no code changes beyond setting environment variables.

For evaluation, LangSmith's dataset feature stores ground truth cases and tracks evaluation runs over time. This is optional for this exercise but is the standard approach in production LangChain/LangGraph applications.

## How the Pieces Connect

The evaluation framework built this week is used directly in the capstone (Weeks 11-12). Your capstone must include a ground truth dataset with at least 15 cases and a passing evaluation pipeline. The cost tracking integrates with the budget enforcement from `shared/llm_client.py` that you have been using since Week 1.

The regression testing pattern is how production teams validate changes to agent systems. Unlike traditional software where you test exact outputs, agent systems require statistical testing -- "is accuracy still above 80%?" instead of "does this function return exactly 42?"

## Now Build It

Open `README.md` for the exercise specification. Copy `evaluation_starter.py` to `evaluation.py` and implement the TODOs. Start with `CostTracker` (pure Python, no dependencies), then the evaluation pipeline (uses `shared/eval_helpers.py`), then the metrics report. Run `pytest test_evaluation.py -v` to validate. The included mock reviewer demonstrates the evaluation flow without API calls.
