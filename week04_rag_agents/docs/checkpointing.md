# Checkpointing in LangGraph

## What is Checkpointing?

Checkpointing allows a LangGraph workflow to save its state at each step and resume from any point. This is critical for production systems where long-running workflows may be interrupted by failures, timeouts, or deliberate pauses for human review.

## Why Checkpointing Matters

Without checkpointing, if a 5-node pipeline fails at node 4, you must restart from the beginning. With checkpointing, you resume from the last successful checkpoint -- node 3's output -- and only re-run node 4.

Use cases:
- Error recovery: resume after transient failures (API timeouts, rate limits)
- Human-in-the-loop: pause the graph, wait for human input, then resume
- Long-running workflows: save progress for multi-hour pipelines
- Debugging: inspect state at any point in the execution

## Using MemorySaver

The simplest checkpointer stores state in memory. Suitable for development and testing.

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)
```

## Thread IDs

Each execution needs a unique thread ID. The checkpointer uses this to store and retrieve state.

```python
config = {"configurable": {"thread_id": "my-workflow-001"}}
result = graph.invoke(initial_state, config)
```

Calling invoke again with the same thread ID resumes from the saved state rather than starting over.

## Persistent Checkpointers

For production, use a persistent backend:

```python
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver.from_conn_string("checkpoints.db")
graph = builder.compile(checkpointer=checkpointer)
```

This survives process restarts. The state is stored in SQLite and can be queried for debugging.

## Inspecting Checkpoints

You can retrieve the state at any checkpoint:

```python
state = graph.get_state(config)
print(state.values)  # current state dict
print(state.next)    # which node would execute next
```

This is useful for debugging failed workflows -- you can see exactly what the state looked like when it failed.

## Best Practices

- Always use checkpointing in production workflows
- Use meaningful thread IDs (e.g., include request ID or user ID)
- Clean up old checkpoints periodically to manage storage
- Test resume behavior explicitly: simulate a failure, then verify the graph resumes correctly
