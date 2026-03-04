# Week 6: LangGraph Orchestration

## Objective
Build a multi-stage document processing pipeline using LangGraph StateGraph with conditional routing and checkpointing.

## What You Will Learn
- StateGraph: nodes, edges, and state schema
- Conditional routing based on agent decisions
- Checkpointing for long-running workflow recovery
- LangSmith tracing for observability

## Files
- `document_pipeline.py` -- 5-node pipeline (classify, extract, validate, transform, store) with LLM calls
- `test_pipeline.py` -- Tests for state, routing, validation, error handling

## How to Run
```bash
# Process a sample invoice
python document_pipeline.py --type invoice

# Process a sample email
python document_pipeline.py --type email

# Process custom text
python document_pipeline.py --document "Your document text here"
```

## How to Test
```bash
pytest test_pipeline.py -v
```

## Success Criteria
- [ ] Pipeline correctly routes 3 document types (invoice, email, report)
- [ ] Checkpoint allows resume after simulated failure
- [ ] LangSmith shows full trace for every execution
- [ ] Each node has clear input/output contract via state schema

## Prerequisites
- Weeks 1-5 completed
- `pip install langgraph` (included in requirements.txt)
- Optional: LangSmith account configured in .env
