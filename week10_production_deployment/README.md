# Week 10: Production Deployment

## Objective
Deploy the code review system as a Streamlit web app and FastAPI REST endpoint.

## What You Will Learn
- Streamlit UI for agent interaction
- FastAPI for programmatic agent access
- Production error handling (retries, graceful degradation)
- Structured logging with request tracking

## Files
- `app.py` -- Streamlit web interface (file upload, review results, voting display)
- `api.py` -- FastAPI REST endpoint with structured logging

## How to Run
```bash
# Streamlit UI
streamlit run app.py

# FastAPI
uvicorn api:app --reload

# Test the API
curl -X POST http://localhost:8000/review \
  -H "Content-Type: application/json" \
  -d '{"code": "def hello():\n    print(\"hi\")", "filename": "hello.py"}'
```

## Success Criteria
- [ ] Streamlit UI works end-to-end (upload -> review -> results)
- [ ] API returns valid JSON for all inputs including malformed code
- [ ] Structured JSON logs with request IDs
- [ ] Configuration via environment variables (no code changes)

## Prerequisites
- Weeks 7-9 completed
- `pip install streamlit fastapi uvicorn`
