"""Week 4: RAG Agent - Documentation Q&A with Vector Search

Ingests markdown docs into ChromaDB, retrieves relevant chunks,
and generates answers with citations.

Demonstrates: RAG pipeline, chunking, vector search, citation tracking, evaluation.
"""

import sys
import json
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.llm_client import LLMClient

load_dotenv()


# --- Document Chunking ---

def chunk_document(text: str, chunk_size: int = 512, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks by approximate token count.

    Uses word-based splitting as a simple tokenizer approximation.
    """
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start = end - overlap
    return chunks


# --- Vector Store ---

def build_index(docs_dir: str, collection_name: str = "docs", db_path: str = "./chroma_db"):
    """Ingest markdown files into ChromaDB.

    Args:
        docs_dir: Path to directory containing .md files
        collection_name: Name of the ChromaDB collection
        db_path: Path for persistent ChromaDB storage

    Returns:
        ChromaDB collection
    """
    import chromadb
    from chromadb.utils import embedding_functions

    client = chromadb.PersistentClient(path=db_path)
    ef = embedding_functions.DefaultEmbeddingFunction()

    # Delete existing collection if present
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass

    collection = client.create_collection(collection_name, embedding_function=ef)

    docs_path = Path(docs_dir)
    file_count = 0
    chunk_count = 0

    for filepath in sorted(docs_path.glob("**/*.md")):
        text = filepath.read_text(encoding="utf-8")
        chunks = chunk_document(text, chunk_size=512, overlap=50)
        file_count += 1

        for i, chunk in enumerate(chunks):
            doc_id = f"{filepath.stem}_{i:04d}"
            collection.add(
                ids=[doc_id],
                documents=[chunk],
                metadatas=[{
                    "source": str(filepath.relative_to(docs_path)),
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                }],
            )
            chunk_count += 1

    print(f"Indexed {file_count} files, {chunk_count} chunks into '{collection_name}'")
    return collection


def get_collection(collection_name: str = "docs", db_path: str = "./chroma_db"):
    """Get an existing ChromaDB collection."""
    import chromadb
    from chromadb.utils import embedding_functions

    client = chromadb.PersistentClient(path=db_path)
    ef = embedding_functions.DefaultEmbeddingFunction()
    return client.get_collection(collection_name, embedding_function=ef)


# --- RAG Query ---

def query_with_rag(
    question: str,
    collection,
    llm_client: LLMClient = None,
    n_results: int = 5,
) -> dict:
    """RAG query: retrieve relevant chunks then generate answer.

    Args:
        question: User question
        collection: ChromaDB collection to search
        llm_client: LLMClient instance (creates one if not provided)
        n_results: Number of chunks to retrieve

    Returns:
        dict with: answer, sources, chunks_used, usage
    """
    llm_client = llm_client or LLMClient(provider="anthropic")

    # Retrieve
    results = collection.query(query_texts=[question], n_results=n_results)
    chunks = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0] if results.get("distances") else [0] * len(chunks)

    # Format context with source references
    context_parts = []
    for i, (chunk, meta) in enumerate(zip(chunks, metadatas)):
        context_parts.append(f"[Source {i+1}: {meta['source']}]\n{chunk}")
    context = "\n\n---\n\n".join(context_parts)

    # Generate
    system_prompt = (
        "You are a documentation assistant. Answer questions based ONLY on the provided context.\n"
        "Rules:\n"
        "- Cite sources using [Source N] format\n"
        "- If the context doesn't contain enough information, say 'Insufficient context'\n"
        "- Do not make up information not in the context\n"
        "- Be specific and reference exact details from the sources\n"
    )

    response = llm_client.chat(
        messages=[{
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}"
        }],
        system=system_prompt,
    )

    answer = llm_client.get_text(response)

    sources = [
        {
            "source": meta["source"],
            "chunk_index": meta["chunk_index"],
            "distance": dist,
            "preview": chunk[:100],
        }
        for chunk, meta, dist in zip(chunks, metadatas, distances)
    ]

    return {
        "answer": answer,
        "sources": sources,
        "chunks_used": len(chunks),
        "usage": llm_client.usage.summary(),
    }


# --- Evaluation ---

EVAL_CASES = [
    # Populate these with questions specific to your document corpus
    {
        "id": "eval_001",
        "input": "What is a StateGraph?",
        "expected": ["TypedDict", "node", "edge"],
    },
    {
        "id": "eval_002",
        "input": "How do you add conditional routing?",
        "expected": ["conditional", "edge", "routing"],
    },
    {
        "id": "eval_003",
        "input": "What is checkpointing used for?",
        "expected": ["save", "resume", "state"],
    },
]


def evaluate_rag(collection, eval_cases: list[dict] = None) -> dict:
    """Run evaluation against the RAG system."""
    from shared.eval_helpers import run_evaluation, keyword_evaluator

    eval_cases = eval_cases or EVAL_CASES
    llm_client = LLMClient(provider="anthropic", budget_usd=1.00)

    def agent_fn(question):
        result = query_with_rag(question, collection, llm_client)
        return result["answer"]

    test_cases = [
        {"id": case["id"], "input": case["input"], "expected": case["expected"]}
        for case in eval_cases
    ]

    report = run_evaluation(agent_fn, test_cases, keyword_evaluator)
    return report.summary()


# --- CLI ---

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="RAG Agent")
    parser.add_argument("command", choices=["index", "query", "eval"], help="Command to run")
    parser.add_argument("--docs-dir", default="./docs", help="Directory with markdown files")
    parser.add_argument("--question", "-q", help="Question to ask")
    parser.add_argument("--db-path", default="./chroma_db", help="ChromaDB storage path")
    args = parser.parse_args()

    if args.command == "index":
        build_index(args.docs_dir, db_path=args.db_path)

    elif args.command == "query":
        if not args.question:
            print("Error: --question required for query command")
            sys.exit(1)
        collection = get_collection(db_path=args.db_path)
        result = query_with_rag(args.question, collection)
        print(f"\nAnswer: {result['answer']}")
        print(f"\nSources ({result['chunks_used']} chunks):")
        for s in result["sources"]:
            print(f"  - {s['source']} (chunk {s['chunk_index']})")
        print(f"\nCost: ${result['usage']['estimated_cost_usd']:.4f}")

    elif args.command == "eval":
        collection = get_collection(db_path=args.db_path)
        results = evaluate_rag(collection)
        print(json.dumps(results, indent=2))
