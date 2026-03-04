"""Week 6: LangGraph Document Processing Pipeline

A multi-stage pipeline that classifies, extracts, validates, transforms,
and stores documents using LangGraph StateGraph.

Demonstrates: StateGraph, conditional routing, checkpointing, LangSmith tracing.
"""

import sys
import json
from typing import TypedDict, Literal
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.llm_client import LLMClient

load_dotenv()

try:
    from langgraph.graph import StateGraph, START, END
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("Warning: langgraph not installed. Run: pip install langgraph")


# --- State Schema ---

class PipelineState(TypedDict):
    """State that flows through the document processing pipeline."""
    document: str
    doc_type: Literal["invoice", "email", "report", "unknown"]
    entities: dict
    validation_errors: list[str]
    transformed: dict
    stored: bool
    trace: list[str]


def create_initial_state(document: str) -> PipelineState:
    return PipelineState(
        document=document,
        doc_type="unknown",
        entities={},
        validation_errors=[],
        transformed={},
        stored=False,
        trace=[],
    )


# --- Pipeline Nodes ---

def classify_document(state: PipelineState) -> dict:
    """Classify the document type using an LLM call."""
    client = LLMClient(provider="anthropic")
    response = client.chat(
        messages=[{
            "role": "user",
            "content": (
                "Classify this document as one of: invoice, email, report\n"
                "Respond with ONLY the type, nothing else.\n\n"
                f"Document:\n{state['document'][:2000]}"
            ),
        }],
        system="You are a document classifier. Respond with exactly one word: invoice, email, or report.",
    )
    text = client.get_text(response).strip().lower()
    doc_type = text if text in ("invoice", "email", "report") else "unknown"
    return {
        "doc_type": doc_type,
        "trace": state["trace"] + [f"Classified as: {doc_type}"],
    }


def extract_entities(state: PipelineState) -> dict:
    """Extract entities based on document type using an LLM call."""
    client = LLMClient(provider="anthropic")

    extraction_prompts = {
        "invoice": "Extract: vendor, amount, date, invoice_number, line_items",
        "email": "Extract: sender, recipient, subject, date, key_points",
        "report": "Extract: title, author, date, summary, key_findings",
    }
    prompt = extraction_prompts.get(state["doc_type"], "Extract all key entities")

    response = client.chat(
        messages=[{
            "role": "user",
            "content": f"{prompt}\n\nRespond as JSON.\n\nDocument:\n{state['document'][:3000]}",
        }],
        system="Extract entities from the document. Respond with valid JSON only.",
    )
    text = client.get_text(response)
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        entities = json.loads(text[start:end])
    except (ValueError, json.JSONDecodeError):
        entities = {"raw": text, "parse_error": True}

    return {
        "entities": entities,
        "trace": state["trace"] + [f"Extracted {len(entities)} entity fields"],
    }


def validate_data(state: PipelineState) -> dict:
    """Validate extracted entities for completeness and consistency."""
    errors = []

    if not state["entities"]:
        errors.append("No entities extracted")
    if state["entities"].get("parse_error"):
        errors.append("Entity extraction produced unparseable output")

    required_fields = {
        "invoice": ["amount", "date"],
        "email": ["sender", "subject"],
        "report": ["title", "summary"],
    }

    for field in required_fields.get(state["doc_type"], []):
        if field not in state["entities"]:
            errors.append(f"Missing required field: {field}")

    return {
        "validation_errors": errors,
        "trace": state["trace"] + [f"Validation: {len(errors)} errors found"],
    }


def transform_format(state: PipelineState) -> dict:
    """Transform extracted data into standardized output format."""
    transformed = {
        "type": state["doc_type"],
        "entities": state["entities"],
        "processed_at": datetime.now().isoformat(),
        "validation_status": "clean" if not state["validation_errors"] else "has_errors",
    }
    return {
        "transformed": transformed,
        "trace": state["trace"] + ["Transformed to standard format"],
    }


def store_result(state: PipelineState) -> dict:
    """Store the processed document (simulated)."""
    # In production: write to database, S3, etc.
    return {
        "stored": True,
        "trace": state["trace"] + ["Stored result"],
    }


def handle_error(state: PipelineState) -> dict:
    """Handle documents that fail classification or validation."""
    return {
        "transformed": {
            "type": "error",
            "doc_type": state["doc_type"],
            "errors": state["validation_errors"],
            "original_length": len(state["document"]),
        },
        "stored": False,
        "trace": state["trace"] + [f"Error handler: {state['validation_errors']}"],
    }


# --- Routing Logic ---

def route_after_classify(state: PipelineState) -> str:
    """Route based on classification result."""
    if state["doc_type"] == "unknown":
        return "error_handler"
    return "extract_entities"


def route_after_validate(state: PipelineState) -> str:
    """Route based on validation result."""
    if state["validation_errors"]:
        return "error_handler"
    return "transform"


# --- Build Graph ---

def build_pipeline():
    """Build the LangGraph document processing pipeline."""
    if not LANGGRAPH_AVAILABLE:
        raise ImportError("langgraph required")

    builder = StateGraph(PipelineState)

    # Add nodes
    builder.add_node("classify", classify_document)
    builder.add_node("extract_entities", extract_entities)
    builder.add_node("validate", validate_data)
    builder.add_node("transform", transform_format)
    builder.add_node("store", store_result)
    builder.add_node("error_handler", handle_error)

    # Add edges
    builder.add_edge(START, "classify")
    builder.add_conditional_edges("classify", route_after_classify)
    builder.add_edge("extract_entities", "validate")
    builder.add_conditional_edges("validate", route_after_validate)
    builder.add_edge("transform", "store")
    builder.add_edge("store", END)
    builder.add_edge("error_handler", END)

    # Compile with checkpointing
    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)


def process_document(document: str, thread_id: str = "default") -> dict:
    """Process a document through the pipeline."""
    pipeline = build_pipeline()
    initial_state = create_initial_state(document)
    config = {"configurable": {"thread_id": thread_id}}
    result = pipeline.invoke(initial_state, config)
    return result


# --- CLI ---

SAMPLE_DOCUMENTS = {
    "invoice": "INVOICE #2024-001\nFrom: Acme Corp\nTo: Client Inc\nDate: 2024-03-15\nAmount: $5,250.00\nServices: Consulting (40 hrs @ $125/hr), Travel expenses ($250)",
    "email": "From: alice@company.com\nTo: bob@company.com\nSubject: Q3 Planning Meeting\nDate: March 10, 2024\n\nHi Bob,\n\nLet's schedule the Q3 planning meeting for next week. Key topics: budget review, hiring plan, product roadmap.\n\nBest,\nAlice",
    "report": "Quarterly Performance Report\nAuthor: Analytics Team\nDate: March 2024\n\nSummary: Revenue grew 15% YoY. Key findings: 1) Customer acquisition cost decreased by 8%. 2) Retention improved to 94%. 3) New product line exceeded targets by 20%.",
}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Document Processing Pipeline")
    parser.add_argument("--type", choices=["invoice", "email", "report"], default="invoice")
    parser.add_argument("--document", help="Document text (or use --type for samples)")
    args = parser.parse_args()

    doc = args.document or SAMPLE_DOCUMENTS.get(args.type, SAMPLE_DOCUMENTS["invoice"])
    print(f"Processing document ({args.type})...\n")

    result = process_document(doc, thread_id=f"demo_{args.type}")
    print(f"Classification: {result['doc_type']}")
    print(f"Entities: {json.dumps(result['entities'], indent=2)}")
    print(f"Validation errors: {result['validation_errors']}")
    print(f"Stored: {result['stored']}")
    print(f"\nTrace:")
    for step in result["trace"]:
        print(f"  -> {step}")
