"""Tests for Week 6: LangGraph Document Processing Pipeline."""

import pytest
from document_pipeline import (
    create_initial_state, validate_data, handle_error,
    route_after_classify, route_after_validate, SAMPLE_DOCUMENTS,
)


class TestState:
    def test_initial_state_has_all_fields(self):
        state = create_initial_state("test doc")
        assert state["document"] == "test doc"
        assert state["doc_type"] == "unknown"
        assert state["entities"] == {}
        assert state["validation_errors"] == []
        assert state["stored"] is False
        assert state["trace"] == []


class TestValidation:
    def test_empty_entities_fails(self):
        state = create_initial_state("test")
        state["doc_type"] = "invoice"
        state["entities"] = {}
        result = validate_data(state)
        assert len(result["validation_errors"]) > 0

    def test_valid_invoice_passes(self):
        state = create_initial_state("test")
        state["doc_type"] = "invoice"
        state["entities"] = {"amount": "100", "date": "2024-01-01"}
        result = validate_data(state)
        assert len(result["validation_errors"]) == 0

    def test_missing_required_field(self):
        state = create_initial_state("test")
        state["doc_type"] = "email"
        state["entities"] = {"sender": "alice"}  # missing subject
        result = validate_data(state)
        assert any("subject" in e for e in result["validation_errors"])


class TestRouting:
    def test_unknown_routes_to_error(self):
        state = create_initial_state("test")
        state["doc_type"] = "unknown"
        assert route_after_classify(state) == "error_handler"

    def test_known_type_routes_to_extract(self):
        state = create_initial_state("test")
        state["doc_type"] = "invoice"
        assert route_after_classify(state) == "extract_entities"

    def test_validation_errors_route_to_error(self):
        state = create_initial_state("test")
        state["validation_errors"] = ["Missing field"]
        assert route_after_validate(state) == "error_handler"

    def test_clean_validation_routes_to_transform(self):
        state = create_initial_state("test")
        state["validation_errors"] = []
        assert route_after_validate(state) == "transform"


class TestErrorHandler:
    def test_error_handler_marks_not_stored(self):
        state = create_initial_state("test")
        state["doc_type"] = "unknown"
        state["validation_errors"] = ["Unknown type"]
        result = handle_error(state)
        assert result["stored"] is False
        assert result["transformed"]["type"] == "error"


class TestSampleDocuments:
    def test_samples_exist(self):
        assert "invoice" in SAMPLE_DOCUMENTS
        assert "email" in SAMPLE_DOCUMENTS
        assert "report" in SAMPLE_DOCUMENTS

    def test_samples_non_empty(self):
        for doc_type, text in SAMPLE_DOCUMENTS.items():
            assert len(text) > 50, f"{doc_type} sample too short"
