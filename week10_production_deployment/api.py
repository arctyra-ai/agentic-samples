"""Week 10: Production Deployment - FastAPI API

REST API for the code review multi-agent system.
Run with: uvicorn api:app --reload

Demonstrates: FastAPI deployment, structured logging, error handling, request tracking.
"""

import sys
import json
import uuid
import logging
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel, Field
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


# --- Structured Logging ---

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "latency_ms"):
            log_data["latency_ms"] = record.latency_ms
        return json.dumps(log_data)


logger = logging.getLogger("code-review-api")
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)


# --- Request/Response Models ---

if FASTAPI_AVAILABLE:
    class ReviewRequest(BaseModel):
        code: str = Field(..., min_length=1, max_length=50000)
        filename: str = Field(default="unknown.py")
        model: str = Field(default="claude-sonnet-4-20250514")
        budget_usd: float = Field(default=0.50, ge=0.01, le=5.0)

    class ReviewResponse(BaseModel):
        request_id: str
        filename: str
        analyzer_findings: list[dict]
        security_findings: list[dict]
        improvement_suggestions: list[dict]
        synthesized_report: dict
        token_usage: dict
        latency_ms: float

    app = FastAPI(title="Code Review API", version="1.0.0")

    @app.post("/review", response_model=ReviewResponse)
    async def review_code(request: ReviewRequest):
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()

        logger.info("Review started", extra={"request_id": request_id})

        try:
            # In production, replace with actual review
            # from week07_multi_agent_systems.code_review_agents import review_code
            result = _mock_review(request.code, request.filename)

            latency_ms = (time.time() - start_time) * 1000
            logger.info("Review complete", extra={
                "request_id": request_id, "latency_ms": round(latency_ms, 1)
            })

            return ReviewResponse(
                request_id=request_id,
                filename=request.filename,
                analyzer_findings=result.get("analyzer_findings", []),
                security_findings=result.get("security_findings", []),
                improvement_suggestions=result.get("improvement_suggestions", []),
                synthesized_report=result.get("synthesized_report", {}),
                token_usage=result.get("token_usage", {}),
                latency_ms=round(latency_ms, 1),
            )
        except Exception as e:
            logger.error(f"Review failed: {e}", extra={"request_id": request_id})
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/health")
    async def health():
        return {"status": "ok", "timestamp": datetime.now().isoformat()}


def _mock_review(code: str, filename: str) -> dict:
    """Mock review for testing."""
    return {
        "analyzer_findings": [],
        "security_findings": [],
        "improvement_suggestions": [],
        "synthesized_report": {"summary": "Mock review", "overall_rating": "pass"},
        "token_usage": {"total_input": 0, "total_output": 0, "calls": 0},
    }


if __name__ == "__main__":
    if FASTAPI_AVAILABLE:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        print("FastAPI not installed. Run: pip install fastapi uvicorn")
