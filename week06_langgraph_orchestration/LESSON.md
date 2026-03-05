# Week 6 Lesson: LangGraph Orchestration

## What You Are Building

This week you build a document processing pipeline using LangGraph's StateGraph. Documents enter the pipeline, get classified by type (invoice, email, report), have entities extracted, pass through validation, get transformed into a standard format, and are stored. The pipeline uses conditional routing -- different document types follow different paths, and validation failures redirect to an error handler.

LangGraph is the orchestration framework in the LangChain ecosystem. It turns the informal agent loops from Weeks 1-3 into explicit, inspectable, checkpointable graphs. Instead of a while loop with if statements, you declare nodes (functions) and edges (transitions) as a graph that LangGraph executes. This makes complex workflows debuggable, resumable, and observable.

This is the transition from "scripting agents" to "engineering agent systems." Production agent deployments overwhelmingly use graph-based orchestration because it provides the control, visibility, and reliability that ad-hoc loops cannot.

## Core Concepts

### StateGraph and TypedDict

A StateGraph defines a workflow as nodes connected by edges, with a typed state that flows through the graph. The state is defined as a TypedDict -- a Python dictionary with declared key types.

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class PipelineState(TypedDict):
    document: str
    doc_type: str          # Written by classifier
    entities: dict         # Written by extractor
    validation_errors: list[str]  # Written by validator
    stored: bool           # Written by store node

builder = StateGraph(PipelineState)
```

Each node function receives the full state and returns a partial update -- just the keys it wants to change. LangGraph merges the update into the existing state.

```python
def classify_document(state: PipelineState) -> dict:
    # Only return the fields this node updates
    return {"doc_type": "invoice"}
```

Watch for: returning the entire state from a node causes no harm but is unnecessary. Returning only the changed fields makes it clear what each node is responsible for.

### Nodes and Edges

Nodes are functions. Edges connect nodes. The graph executes nodes in the order defined by edges, starting from START and ending at END.

```python
builder.add_node("classify", classify_document)
builder.add_node("extract", extract_entities)
builder.add_node("validate", validate_data)
builder.add_node("store", store_result)

builder.add_edge(START, "classify")
builder.add_edge("classify", "extract")
builder.add_edge("extract", "validate")
builder.add_edge("validate", "store")
builder.add_edge("store", END)

graph = builder.compile()
```

This creates a linear pipeline: classify → extract → validate → store. Every document follows the same path.

### Conditional Routing

Real pipelines need branching. A document that fails validation should not be stored. An unknown document type should go to an error handler. Conditional edges use a routing function to decide the next node.

```python
def route_after_validate(state: PipelineState) -> str:
    if state["validation_errors"]:
        return "error_handler"  # Has errors → handle them
    return "transform"          # Clean → continue

builder.add_conditional_edges("validate", route_after_validate)
```

The routing function examines the state and returns the name of the next node. LangGraph calls the routing function after the source node completes and follows the returned path.

Watch for: the routing function must return a valid node name that has been added to the graph. Returning a name that does not exist causes a runtime error.

### Checkpointing

Checkpointing saves the graph's state after each node, allowing resumption from any point. If a 5-node pipeline fails at node 4, you can resume from node 3's state instead of restarting.

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "invoice-001"}}
result = graph.invoke(initial_state, config)
```

The `thread_id` identifies this execution. Calling invoke again with the same thread_id resumes from the saved state. Production systems use persistent checkpointers (SQLite, Postgres) that survive process restarts.

### LangSmith Tracing

LangSmith records every node execution, LLM call, and state transition for debugging and monitoring. Enable it with environment variables:

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls-your-key
LANGCHAIN_PROJECT=agentic-training
```

Once enabled, every graph execution appears in the LangSmith dashboard with timing, token usage, and the full state at each step. This is optional for this week but becomes essential in Week 9 (evaluation) and beyond.

## How the Pieces Connect

The StateGraph pattern from this week is the orchestration layer for everything that follows. Week 7 uses a StateGraph to run 3 agents in parallel and synthesize their results. Week 8 adds voting logic as a node in the graph. The capstone project (Weeks 11-12) requires LangGraph orchestration with conditional routing as a core requirement.

The conditional routing pattern you build here is a formalization of the ad-hoc if/else decisions from the Week 1-2 agent loops. Instead of burying routing logic inside a while loop, it becomes an explicit, testable function that LangGraph calls at the right time.

## Now Build It

Open `README.md` for the exercise specification. Copy `document_pipeline_starter.py` to `document_pipeline.py` and implement the TODOs. The classify and extract nodes make real LLM calls. The validate, transform, and store nodes are pure Python. Test routing logic independently with `pytest test_pipeline.py -v` before running the full pipeline with `python document_pipeline.py --type invoice`.
