# Conditional Edges in LangGraph

## What are Conditional Edges?

Conditional edges allow a graph to take different paths based on the current state. Instead of a fixed edge from node A to node B, a conditional edge calls a routing function that examines the state and returns the name of the next node.

## Defining a Routing Function

A routing function takes the state and returns a string -- the name of the next node to execute.

```python
def should_continue(state: MyState) -> str:
    if state.get("errors"):
        return "error_handler"
    if state["parsed_data"].get("needs_review"):
        return "review"
    return "execute"
```

## Adding Conditional Edges

Use `add_conditional_edges` on the graph builder:

```python
builder.add_conditional_edges(
    "parse",           # source node
    should_continue,   # routing function
    {                  # mapping of return values to node names
        "error_handler": "error_handler",
        "review": "review",
        "execute": "execute",
    }
)
```

The mapping dict is optional. If omitted, the routing function's return value is used directly as the node name.

## Common Patterns

### Binary routing (if/else)
```python
def route_validation(state) -> str:
    if state["is_valid"]:
        return "process"
    return "reject"
```

### Multi-way routing
```python
def route_by_type(state) -> str:
    doc_type = state["doc_type"]
    if doc_type == "invoice":
        return "process_invoice"
    elif doc_type == "email":
        return "process_email"
    return "unknown_handler"
```

### Routing based on agent decisions
When an LLM agent decides the next step, the routing function reads the agent's output from state and maps it to a node.

## Important Notes

- The routing function must return a valid node name or the graph will raise an error.
- Conditional edges replace fixed edges from the source node. You cannot have both a fixed edge and conditional edges from the same node.
- The routing function should be deterministic given the same state. Side effects in routing functions make debugging difficult.
