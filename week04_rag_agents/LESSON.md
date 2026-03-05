# Week 4 Lesson: RAG Agents

## What You Are Building

This week you build a documentation Q&A agent that answers questions by searching a vector database of documents, retrieving relevant chunks, and generating answers with source citations. This is RAG -- Retrieval-Augmented Generation.

RAG appears in nearly every AI engineer job posting. It solves the fundamental problem that LLMs only know what was in their training data. When a user asks about your company's internal documentation, last week's meeting notes, or a specific technical spec, the LLM has no idea. RAG gives it the relevant context at query time by searching a document store and injecting the results into the prompt.

By the end of this week you will have a working RAG pipeline: ingest markdown files into ChromaDB, chunk them with overlap, query with semantic search, generate grounded answers with citations, and evaluate retrieval quality against a ground truth dataset.

## Core Concepts

### The RAG Pipeline

RAG has two phases: indexing (done once) and querying (done per question).

```
INDEXING (offline):
Documents → Chunk → Embed → Store in vector database

QUERYING (per question):
Question → Embed → Search vector DB → Top-K chunks → LLM generates answer
```

Each step has design decisions that affect quality. The curriculum focuses on the ones that matter most in practice.

### Chunking

Documents must be split into chunks small enough for the LLM's context window but large enough to contain meaningful information. Chunks that are too small lose context. Chunks that are too large dilute relevance.

```python
def chunk_document(text: str, chunk_size: int = 512, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end - overlap  # Overlap prevents cutting concepts in half
    return chunks
```

The overlap is critical. Without it, a sentence that spans two chunks gets split and neither chunk contains the complete thought. With 50-word overlap, the end of chunk N appears at the start of chunk N+1, preserving continuity.

Watch for: chunk size is measured in words here as an approximation. Production systems use token-based chunking (different models have different tokenizers). For this exercise, word-based is sufficient and avoids tokenizer dependencies.

### Vector Search with ChromaDB

ChromaDB stores document chunks as vectors (high-dimensional number arrays that represent meaning). When you query, ChromaDB converts your question to a vector and finds the chunks whose vectors are closest -- meaning they are semantically similar, not just keyword matches.

```python
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.create_collection("docs")

# Add chunks with metadata
collection.add(
    ids=["doc1_chunk0", "doc1_chunk1"],
    documents=["StateGraph is the core primitive...", "Nodes read from shared state..."],
    metadatas=[{"source": "stategraph.md", "chunk_index": 0},
               {"source": "stategraph.md", "chunk_index": 1}],
)

# Query
results = collection.query(query_texts=["What is a StateGraph?"], n_results=3)
# Returns the 3 most semantically similar chunks
```

The default embedding function in ChromaDB handles vectorization automatically. Production systems use dedicated embedding models (OpenAI `text-embedding-3-small`, Cohere `embed-v4`, etc.) for better quality.

### Grounded Generation

After retrieval, you send the chunks to the LLM as context and ask it to answer based only on that context. The system prompt enforces grounding:

```python
system_prompt = """Answer questions based ONLY on the provided context.
Rules:
- Cite sources using [Source N] format
- If the context doesn't contain enough information, say 'Insufficient context'
- Do not make up information not in the context"""

user_message = f"""Context:
[Source 1: stategraph.md]
StateGraph is the core primitive in LangGraph for building stateful workflows...

[Source 2: conditional_edges.md]
Conditional edges allow a graph to take different paths based on state...

Question: What is a StateGraph?"""
```

Watch for: LLMs are trained to be helpful, which means they will try to answer even when the context is insufficient. The "say insufficient context" instruction must be explicit and firm, or the LLM will hallucinate. Test this by asking questions your documents do not cover.

### Retrieval Evaluation

A RAG system is only as good as its retrieval. If the wrong chunks are retrieved, the LLM generates wrong answers no matter how good the model is. Evaluation measures whether the right chunks come back.

```python
EVAL_CASES = [
    {
        "id": "eval_001",
        "input": "What is a StateGraph?",
        "expected": ["TypedDict", "node", "edge"],  # Keywords that should appear in the answer
    },
]
```

For each case, you query the system and check if the expected keywords appear in the answer. This is a coarse metric (keyword matching), but it catches the most common failure: retrieval returning irrelevant chunks. Production systems use LLM-as-judge evaluation for nuance, but keyword matching establishes the baseline.

## How the Pieces Connect

RAG is a required component of the capstone project (Weeks 11-12). At least one agent in your multi-agent system must use retrieval to ground its responses. The evaluation pattern you build this week (ground truth dataset, keyword matching, accuracy metrics) is extended in Week 9 into a full evaluation pipeline with cost tracking and regression testing.

The sample documents in `docs/` cover LangGraph, MCP, and multi-agent patterns -- topics from other weeks. This is intentional: the RAG agent can answer questions about the curriculum itself, which makes testing intuitive.

## Now Build It

Open `README.md` for the exercise specification. Copy `rag_agent_starter.py` to `rag_agent.py` and implement the TODOs. Start with chunking (pure Python, no dependencies), then indexing (requires ChromaDB), then querying (requires Anthropic API key), then evaluation. Run `pytest test_rag.py -v` for the chunking tests, and use `python rag_agent.py eval` for the full evaluation.
