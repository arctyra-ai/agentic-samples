# Week 10 Lesson: Production Deployment

## What You Are Building

This week you deploy the code review system as two production interfaces: a Streamlit web application where users upload files and see review results, and a FastAPI REST endpoint where other systems can submit code for review programmatically. You also add structured logging, error handling, and configuration management.

This is the week where your multi-agent system becomes a usable product instead of a script you run from the terminal. Every production AI role requires deployment skills -- the ability to wrap an agent system in an interface that non-technical users can use and that other services can call. Streamlit and FastAPI are the two most common deployment targets for Python AI systems.

## Core Concepts

### Streamlit for Agent UIs

Streamlit turns Python scripts into web applications with zero frontend code. Each Streamlit function call creates a UI element.

```python
import streamlit as st

st.title("Code Review Agent")
uploaded = st.file_uploader("Upload a Python file", type=["py"])
if uploaded:
    code = uploaded.read().decode("utf-8")
    st.code(code, language="python")

    if st.button("Run Review", type="primary"):
        with st.spinner("Reviewing..."):
            result = review_code(code, uploaded.name)
        st.metric("Issues Found", len(result["security_findings"]))
```

The key pattern: Streamlit re-runs the entire script on every interaction. State does not persist between reruns unless you use `st.session_state`. For agent systems, this means you trigger the review inside a button click handler, not at the top level.

Watch for: long-running agent calls (10-30 seconds) need a spinner or progress indicator. Without visual feedback, users think the app crashed.

### FastAPI for Programmatic Access

FastAPI creates REST endpoints with automatic request validation, documentation, and async support.

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ReviewRequest(BaseModel):
    code: str
    filename: str = "unknown.py"

class ReviewResponse(BaseModel):
    request_id: str
    findings: list[dict]
    overall_rating: str

@app.post("/review", response_model=ReviewResponse)
async def review(request: ReviewRequest):
    result = review_code(request.code, request.filename)
    return ReviewResponse(request_id="...", findings=..., overall_rating=...)
```

FastAPI generates API documentation automatically at `/docs`. The Pydantic models you defined in Week 2 for structured output work directly as request/response models here.

### Structured Logging

Production systems log every request with a unique ID, timing, and outcome. JSON-formatted logs are searchable and parseable by monitoring systems.

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
            "latency_ms": getattr(record, "latency_ms", None),
        })
```

Every request gets a UUID. Every log line includes that UUID. When something goes wrong, you filter logs by request_id and see the complete execution trace. Without this, debugging production issues is nearly impossible.

### Error Handling and Graceful Degradation

In production, individual agents can fail (API timeout, rate limit, malformed response). The system should degrade gracefully rather than crash.

```python
try:
    result = review_code(request.code, request.filename)
except Exception as e:
    logger.error(f"Review failed: {e}", extra={"request_id": request_id})
    raise HTTPException(status_code=500, detail="Review failed. Please retry.")
```

Better yet, design the agent system so that if one specialist agent fails, the others still contribute. A review with 2 of 3 agents is more useful than a 500 error.

### Configuration via Environment Variables

Hard-coding model names, budget limits, and feature flags in source code means every change requires a code deployment. Use environment variables for anything that might change between environments.

```python
import os
MODEL = os.getenv("REVIEW_MODEL", "claude-sonnet-4-20250514")
BUDGET = float(os.getenv("REVIEW_BUDGET_USD", "0.50"))
```

This lets you switch models, adjust budgets, or enable features without touching code. The `.env` file provides defaults for development; production environments set variables through their deployment platform.

## How the Pieces Connect

This week integrates everything from Weeks 7-9: the multi-agent review system (Week 7), the voting system (Week 8), and the evaluation/cost tracking (Week 9) are all wrapped in a deployable interface. The Streamlit UI shows review results including agent findings, voting outcomes, and cost per review. The FastAPI endpoint returns the same data as JSON for automation.

The capstone (Weeks 11-12) requires either a Streamlit UI or a CLI. The deployment patterns from this week transfer directly.

## Now Build It

Open `README.md` for the exercise specification. This week does not have a starter file -- the `app.py` (Streamlit) and `api.py` (FastAPI) are provided as working implementations with mock review functions. Your task is to connect them to the real multi-agent system from Weeks 7-8. Start with Streamlit (`streamlit run app.py`), verify the UI works with mock data, then replace the mock review function with the real one. Do the same for FastAPI (`uvicorn api:app --reload`).
