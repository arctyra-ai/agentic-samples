"""Week 4 STARTER: RAG Agent

TODO: Build a RAG pipeline with document ingestion, vector search, and evaluation.
Copy this file to rag_agent.py and fill in the TODO sections.
"""

import sys
import json
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.llm_client import LLMClient

load_dotenv()


# --- Document Chunking ---

def chunk_document(text: str, chunk_size: int = 512, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks.

    TODO: Implement word-based chunking with overlap.
    - Split text into words
    - Create chunks of chunk_size words
    - Each chunk overlaps with the previous by overlap words
    - Return list of chunk strings
    """
    pass


# --- Vector Store ---

def build_index(docs_dir: str, collection_name: str = "docs", db_path: str = "./chroma_db"):
    """Ingest markdown files into ChromaDB.

    TODO:
    1. Create a ChromaDB PersistentClient
    2. Create a collection with default embedding function
    3. For each .md file in docs_dir:
       a. Read the file
       b. Chunk it with chunk_document()
       c. Add chunks to collection with metadata (source file, chunk index)
    4. Return the collection
    """
    import chromadb
    from chromadb.utils import embedding_functions
    pass


def get_collection(collection_name: str = "docs", db_path: str = "./chroma_db"):
    """Get an existing ChromaDB collection."""
    import chromadb
    from chromadb.utils import embedding_functions
    pass


# --- RAG Query ---

def query_with_rag(question: str, collection, llm_client=None, n_results: int = 5) -> dict:
    """RAG query: retrieve relevant chunks then generate answer.

    TODO:
    1. Query the collection for top-k relevant chunks
    2. Format chunks as numbered context with source references
    3. Send context + question to LLM with system prompt that requires:
       - Answer based ONLY on provided context
       - Cite sources using [Source N] format
       - Say "Insufficient context" when unsure
    4. Return dict with: answer, sources, chunks_used, usage
    """
    pass


# --- Evaluation ---

EVAL_CASES = [
    {"id": "eval_001", "input": "What is a StateGraph?", "expected": ["TypedDict", "node", "edge"]},
    {"id": "eval_002", "input": "How do you add conditional routing?", "expected": ["conditional", "edge", "routing"]},
    {"id": "eval_003", "input": "What is checkpointing used for?", "expected": ["save", "resume", "state"]},
]


def evaluate_rag(collection, eval_cases: list[dict] = None) -> dict:
    """Run evaluation against the RAG system.

    TODO:
    1. For each eval case, query the RAG system
    2. Check if expected keywords appear in the answer
    3. Calculate accuracy (target: 80%+)
    4. Return metrics dict
    """
    pass


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["index", "query", "eval"])
    parser.add_argument("--docs-dir", default="./docs")
    parser.add_argument("--question", "-q")
    args = parser.parse_args()

    if args.command == "index":
        build_index(args.docs_dir)
    elif args.command == "query":
        collection = get_collection()
        result = query_with_rag(args.question, collection)
        print(f"Answer: {result['answer']}")
    elif args.command == "eval":
        collection = get_collection()
        print(json.dumps(evaluate_rag(collection), indent=2))
