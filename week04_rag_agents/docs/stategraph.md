# LangGraph StateGraph

## What is a StateGraph?

A StateGraph is the core primitive in LangGraph for building stateful workflows. You define a state schema using TypedDict, then add nodes (functions) and edges (transitions) to create a directed graph that processes data step by step.

## Defining State

State is defined as a TypedDict. Each key represents a piece of data that flows through the graph. Nodes read from and write to this shared state.

```python
from typing import TypedDict

class MyState(TypedDict):
    user_input: str
    parsed_data: dict
    result: str
    errors: list[str]
```

Every node function receives the current state and returns a partial update. LangGraph merges the update into the existing state automatically.

## Creating a StateGraph

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(MyState)
builder.add_node("parse", parse_function)
builder.add_node("process", process_function)
builder.add_edge(START, "parse")
builder.add_edge("parse", "process")
builder.add_edge("process", END)

graph = builder.compile()
```

## Node Functions

A node function takes the state and returns a dict with the fields it wants to update. It does not need to return the entire state.

```python
def parse_function(state: MyState) -> dict:
    return {"parsed_data": {"action": "add", "item": state["user_input"]}}
```

## Running the Graph

Invoke the compiled graph with an initial state:

```python
result = graph.invoke({"user_input": "hello", "parsed_data": {}, "result": "", "errors": []})
```

The graph executes nodes in order, following edges, until it reaches END.
