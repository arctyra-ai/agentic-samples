# Week 4: RAG Agents

## Objective
Build a documentation Q&A agent with vector search, citation tracking, and retrieval evaluation.

## What You Will Learn
- RAG pipeline: ingest, chunk, embed, store, retrieve, generate
- Chunking strategies and tradeoffs
- Retrieval evaluation (are the right documents being found?)
- Grounded generation (agent cites sources, admits when context is insufficient)

## Files
- `rag_agent.py` -- Full RAG pipeline with ChromaDB, evaluation framework
- `test_rag.py` -- Tests for chunking, eval cases
- `docs/` -- Sample markdown files for ingestion (5 documents on LangGraph, MCP, multi-agent patterns)

## How to Run
```bash
# Step 1: Index the sample documents
python rag_agent.py index --docs-dir ./docs

# Step 2: Ask questions
python rag_agent.py query -q "What is a StateGraph?"

# Step 3: Run evaluation
python rag_agent.py eval
```

## How to Test
```bash
pytest test_rag.py -v
```

## Success Criteria
- [ ] Agent answers 8/10 evaluation questions correctly
- [ ] Zero hallucinated citations
- [ ] Agent says "insufficient context" when appropriate
- [ ] Ingestion processes all docs in under 30 seconds

## Prerequisites
- Weeks 1-3 completed
- `pip install chromadb` (included in requirements.txt)
