"""Week 6 STARTER: LangGraph Document Processing Pipeline

TODO: Build a multi-stage pipeline with conditional routing and checkpointing.
Copy this file to document_pipeline.py and fill in the TODO sections.
"""

import sys
import json
from typing import TypedDict, Literal
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.llm_client import LLMClient

load_dotenv()

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver


# --- State Schema ---

class PipelineState(TypedDict):
    """TODO: This is provided. Understand what each field does."""
    document: str
    doc_type: Literal["invoice", "email", "report", "unknown"]
    entities: dict
    validation_errors: list[str]
    transformed: dict
    stored: bool
    trace: list[str]


def create_initial_state(document: str) -> PipelineState:
    return PipelineState(
        document=document, doc_type="unknown", entities={},
        validation_errors=[], transformed={}, stored=False, trace=[],
    )


# --- Pipeline Nodes ---

def classify_document(state: PipelineState) -> dict:
    """Classify the document type using an LLM call.

    TODO:
    1. Create an LLMClient
    2. Send the document to the LLM with a system prompt asking it to classify
       as one of: invoice, email, report
    3. Parse the response (should be a single word)
    4. Return {"doc_type": ..., "trace": ...}
    """
    pass


def extract_entities(state: PipelineState) -> dict:
    """Extract entities based on document type using an LLM call.

    TODO:
    1. Based on state["doc_type"], choose what to extract:
       - invoice: vendor, amount, date, invoice_number
       - email: sender, recipient, subject, date, key_points
       - report: title, author, date, summary, key_findings
    2. Call LLM asking for JSON extraction
    3. Parse the JSON response
    4. Return {"entities": ..., "trace": ...}
    """
    pass


def validate_data(state: PipelineState) -> dict:
    """Validate extracted entities for completeness.

    TODO: Check that required fields exist for each doc type.
    Return {"validation_errors": [...], "trace": ...}
    """
    pass


def transform_format(state: PipelineState) -> dict:
    """Transform into standardized output format.

    TODO: Create a standardized dict with type, entities, timestamp, validation_status.
    Return {"transformed": ..., "trace": ...}
    """
    pass


def store_result(state: PipelineState) -> dict:
    """Store the processed document (simulated).

    TODO: Return {"stored": True, "trace": ...}
    """
    pass


def handle_error(state: PipelineState) -> dict:
    """Handle documents that fail classification or validation.

    TODO: Return error information and stored=False.
    """
    pass


# --- Routing Logic ---

def route_after_classify(state: PipelineState) -> str:
    """TODO: Return "error_handler" if unknown, "extract_entities" otherwise."""
    pass


def route_after_validate(state: PipelineState) -> str:
    """TODO: Return "error_handler" if errors exist, "transform" otherwise."""
    pass


# --- Build Graph ---

def build_pipeline():
    """Build the LangGraph document processing pipeline.

    TODO:
    1. Create StateGraph(PipelineState)
    2. Add all 6 nodes
    3. Add edges: START -> classify
    4. Add conditional edges: classify -> (extract or error)
    5. Add edge: extract -> validate
    6. Add conditional edges: validate -> (transform or error)
    7. Add edges: transform -> store -> END, error -> END
    8. Compile with MemorySaver checkpointer
    """
    pass


# --- Sample Documents ---

SAMPLE_DOCUMENTS = {
    "invoice": "INVOICE #2024-001\nFrom: Acme Corp\nDate: 2024-03-15\nAmount: $5,250.00",
    "email": "From: alice@company.com\nTo: bob@company.com\nSubject: Q3 Planning\n\nLet's schedule the Q3 meeting.",
    "report": "Quarterly Report\nAuthor: Analytics Team\nDate: March 2024\n\nSummary: Revenue grew 15% YoY.",
}

if __name__ == "__main__":
    doc = SAMPLE_DOCUMENTS["invoice"]
    pipeline = build_pipeline()
    result = pipeline.invoke(create_initial_state(doc), {"configurable": {"thread_id": "demo"}})
    print(f"Type: {result['doc_type']}")
    print(f"Entities: {json.dumps(result['entities'], indent=2)}")
    print(f"Trace: {result['trace']}")
