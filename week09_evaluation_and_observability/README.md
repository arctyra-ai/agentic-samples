# Week 9: Evaluation and Observability

## Objective
Build an evaluation pipeline, cost tracking system, and metrics dashboard for the code review agents.

## What You Will Learn
- Agent evaluation with ground truth datasets
- Cost tracking and budget enforcement
- Regression testing for non-deterministic systems
- LangSmith integration for production tracing

## Files
- `evaluation.py` -- CostTracker, ground truth dataset (5 cases), evaluation runner, metrics report
- `test_evaluation.py` -- Tests for cost tracking, ground truth structure, evaluation pipeline

## How to Run
```bash
# Run evaluation with mock reviewer
python evaluation.py
```

## How to Test
```bash
pytest test_evaluation.py -v
```

## Success Criteria
- [ ] Evaluation pipeline runs all ground truth cases and produces metrics
- [ ] Cost tracking is accurate within 5% of actual API charges
- [ ] Budget enforcement stops execution before overspend
- [ ] Metrics are stored and comparable across runs

## Prerequisites
- Weeks 7-8 completed
- Recommended: LangSmith account for full tracing
