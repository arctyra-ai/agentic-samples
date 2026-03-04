"""Tests for Week 4: RAG Agent."""

import pytest
from rag_agent import chunk_document, EVAL_CASES


class TestChunking:
    def test_basic_chunking(self):
        text = " ".join(["word"] * 1000)
        chunks = chunk_document(text, chunk_size=100, overlap=10)
        assert len(chunks) > 1
        assert all(len(c.split()) <= 100 for c in chunks)

    def test_overlap_exists(self):
        text = " ".join([f"w{i}" for i in range(200)])
        chunks = chunk_document(text, chunk_size=50, overlap=10)
        # Last words of chunk N should appear at start of chunk N+1
        if len(chunks) >= 2:
            words_end = chunks[0].split()[-10:]
            words_start = chunks[1].split()[:10]
            assert any(w in words_start for w in words_end)

    def test_single_chunk_for_short_text(self):
        chunks = chunk_document("Short text", chunk_size=100)
        assert len(chunks) == 1

    def test_empty_text(self):
        chunks = chunk_document("", chunk_size=100)
        assert len(chunks) == 0

    def test_respects_chunk_size(self):
        text = " ".join(["word"] * 500)
        chunks = chunk_document(text, chunk_size=50, overlap=5)
        for chunk in chunks:
            assert len(chunk.split()) <= 50


class TestEvalCases:
    def test_eval_cases_have_required_fields(self):
        for case in EVAL_CASES:
            assert "id" in case
            assert "input" in case
            assert "expected" in case
            assert isinstance(case["expected"], list)
            assert len(case["expected"]) > 0

    def test_eval_case_ids_unique(self):
        ids = [c["id"] for c in EVAL_CASES]
        assert len(ids) == len(set(ids))
