# Agentic AI Engineering Curriculum
## Production-Ready Multi-Agent Systems for the 2026 Market

**Program Level:** Intermediate (assumes Python proficiency, basic API experience)
**Total Time:** ~120 hours (10 hrs/week x 12 weeks)
**Primary Tools:** Claude Code CLI, LangGraph, MCP, Anthropic/OpenAI APIs
**Development Workflow:** Claude Code as primary development environment
**Final Outcome:** Deployed multi-agent system with MCP integrations, evaluation pipeline, and production monitoring

---

## Program Philosophy

This curriculum is designed around three principles derived from what employers are hiring for in 2026:

1. **Real integrations from day one.** Every exercise makes real LLM API calls and connects to real services. MCP (Model Context Protocol) is the industry standard for connecting agents to tools, databases, and APIs -- it is a core thread from Week 3 through the capstone.

2. **Orchestration over syntax.** The primary skill is problem decomposition, agent design, evaluation, and deployment -- not writing boilerplate. Claude Code is the recommended development companion throughout, mirroring how production teams work.

3. **Production readiness is the bar.** Working demos are commodity. This program requires monitoring, evaluation, cost tracking, error handling at scale, and deployment as a service. The capstone is portfolio-ready and interview-presentable.

---

## Program Structure

| Phase | Weeks | Focus | Key Skills |
|-------|-------|-------|------------|
| **Foundations** | 1-3 | Agent loops, tool use, MCP basics | Tool calling, ReAct pattern, MCP client/server |
| **Real Integrations** | 4-6 | RAG, MCP servers, LangGraph | Vector search, custom MCP servers, state graphs |
| **Multi-Agent Systems** | 7-9 | Orchestration, voting, evaluation | Multi-agent coordination, conflict resolution, evals |
| **Production** | 10-12 | Deploy, monitor, capstone | Streamlit, LangSmith, cost tracking, full system |

---

## Pre-Course Setup

### Required Accounts and API Keys

- **Anthropic API** (https://console.anthropic.com): Primary LLM provider. Budget ~$15-30 for the full program.
- **OpenAI API** (https://platform.openai.com): Secondary provider for comparison exercises. Budget ~$10.
- **LangSmith** (https://smith.langchain.com): Free tier. Used from Week 6 onward for tracing and evaluation.
- **GitHub account**: All code version-controlled. Portfolio-ready by Week 12.

### Required Software

```bash
# Python 3.11+
python --version

# Claude Code CLI
npm install -g @anthropic-ai/claude-code

# Core Python dependencies
pip install anthropic openai langchain langgraph langchain-anthropic langchain-openai
pip install chromadb python-dotenv pydantic fastapi uvicorn streamlit
pip install mcp pytest langsmith

# Optional but recommended
pip install rich typer  # CLI formatting
```

### Environment Configuration

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
LANGCHAIN_API_KEY=ls-...          # LangSmith
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=agentic-training
```

### Directory Structure

```
agentic_ai/
├── .env
├── .gitignore
├── requirements.txt
├── README.md
├── week01_agent_fundamentals/
├── week02_tool_use_deep_dive/
├── week03_mcp_foundations/
├── week04_rag_agents/
├── week05_custom_mcp_servers/
├── week06_langgraph_orchestration/
├── week07_multi_agent_systems/
├── week08_voting_and_conflicts/
├── week09_evaluation_and_observability/
├── week10_production_deployment/
├── week11_capstone_build/
├── week12_capstone_polish/
└── shared/
    ├── llm_client.py        # Unified Anthropic/OpenAI wrapper
    ├── mcp_utils.py         # MCP client helpers
    └── eval_helpers.py      # Evaluation framework
```

### Development Workflow

Every exercise follows this pattern:

1. **Define the problem** in plain language
2. **Decompose** into agent tasks using Claude Code
3. **Implement** with real LLM calls and real integrations
4. **Test** with pytest (unit) and LangSmith (trace)
5. **Evaluate** with defined metrics
6. **Commit** to git with clear messages

Claude Code is the primary development companion throughout. You will use it to scaffold code, debug errors, explain concepts, and review your implementations. This mirrors the actual workflow at companies hiring for these roles.

---

# Phase 1: Foundations (Weeks 1-3)

---

## Week 1: Agent Fundamentals

### Learning Objectives
- Understand the agent loop: perceive, reason, act, observe
- Implement tool calling with the Anthropic API
- Handle multi-turn conversations with tool results
- Understand when agents add value vs. when deterministic code is sufficient

### Key Concepts
- **Agent loop**: User input -> LLM reasoning -> tool selection -> tool execution -> observation -> next step
- **Tool definitions**: JSON schema for function signatures the LLM can call
- **ReAct pattern**: Reason + Act in a loop until task complete
- **Stop conditions**: How the agent knows when to stop (max iterations, explicit completion, no tool calls)

### Exercise: Build a File Operations Agent

**Requirements:**
- Agent receives natural language requests ("Find all Python files with TODO comments", "Summarize the README", "List files larger than 1MB")
- Agent has 5 tools: list_files, read_file, search_in_files, get_file_info, write_summary
- Agent makes real Anthropic API calls
- Agent handles multi-turn: if it needs more info, it asks
- Agent stops when task is complete (no infinite loops)

**Success criteria:**
- Agent correctly selects tools based on user intent
- Agent handles errors (file not found, permission denied)
- Agent produces useful output for at least 5 different request types
- Cost per interaction stays under $0.05
- All tool calls are logged with input/output

**Starter structure:**
```python
# week01/agent.py
import json
from anthropic import Anthropic

TOOLS = [
    {
        "name": "list_files",
        "description": "List files in a directory with optional filtering",
        "input_schema": {
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "Path to directory"},
                "pattern": {"type": "string", "description": "Glob pattern filter"}
            },
            "required": ["directory"]
        }
    },
    # ... define remaining tools
]

def execute_tool(name: str, input: dict) -> str:
    """Execute a tool and return result as string."""
    # Real implementation -- actually reads files, searches, etc.
    pass

def run_agent(user_request: str, target_dir: str) -> str:
    """Run the agent loop until task completion."""
    client = Anthropic()
    messages = [{"role": "user", "content": user_request}]
    
    for iteration in range(10):  # Max iterations as safety net
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=f"You are a file operations assistant. Working directory: {target_dir}",
            tools=TOOLS,
            messages=messages
        )
        
        # Process response: check for tool_use blocks, execute tools, append results
        # If response has only text (no tool calls), agent is done
        pass
    
    return final_response
```

**Tests (week01/test_agent.py):**
- test_list_files_tool_selected: Agent calls list_files for "show me what's in this directory"
- test_search_tool_selected: Agent calls search_in_files for "find files containing X"
- test_error_handling: Agent handles nonexistent directory gracefully
- test_max_iterations: Agent does not loop forever
- test_cost_tracking: Total tokens used is logged

### Deliverable
Working file operations agent. Run with `python week01/agent.py`. Committed to git.

### What This Teaches (mapped to job requirements)
- Tool calling API mechanics (every agentic AI job posting)
- Agent loop design (core pattern in all frameworks)
- Cost awareness (token tracking from day 1)
- Error handling in LLM interactions (production requirement)

---

## Week 2: Tool Use Deep Dive

### Learning Objectives
- Design effective tool schemas (descriptions that guide LLM selection)
- Implement tool composition (agent uses output of one tool as input to another)
- Add persistent memory across sessions
- Handle structured output from LLMs

### Key Concepts
- **Tool description quality**: The LLM selects tools based on descriptions. Vague descriptions = wrong tool selection.
- **Tool chaining**: Agent calls tool A, uses result to decide whether/how to call tool B
- **Structured output**: Getting the LLM to return JSON, not free text, when you need it
- **Persistent state**: Saving conversation history and task state between sessions

### Exercise: Research Assistant Agent

Build an agent that takes a research question, searches multiple sources, synthesizes findings, and produces a structured report. This introduces tool chaining and structured output.

**Requirements:**
- Agent has 6 tools: web_search (simulated or real), read_url, extract_key_points, compare_sources, generate_outline, write_section
- Agent chains tools: search -> read -> extract -> compare -> outline -> write
- Agent produces structured JSON output (not free text) for the report
- Agent maintains session state (can continue research across calls)
- Agent tracks which sources it used and can cite them

**Success criteria:**
- Agent produces a 3-section report for any research question
- Sources are tracked and cited in output
- Session state persists to disk (can resume after restart)
- Structured output validates against a Pydantic schema
- Tool descriptions are specific enough that the LLM never selects the wrong tool

**New concepts introduced:**
```python
# Structured output with Pydantic
from pydantic import BaseModel

class ResearchReport(BaseModel):
    question: str
    sources: list[dict]
    sections: list[dict]
    confidence: float
    follow_up_questions: list[str]

# Session persistence
import json
from pathlib import Path

class SessionMemory:
    def __init__(self, session_id: str):
        self.path = Path(f"sessions/{session_id}.json")
        self.state = self._load()
    
    def _load(self) -> dict:
        if self.path.exists():
            return json.loads(self.path.read_text())
        return {"messages": [], "sources": [], "findings": []}
    
    def save(self):
        self.path.parent.mkdir(exist_ok=True)
        self.path.write_text(json.dumps(self.state, indent=2))
```

**Tests:**
- test_tool_chaining: Agent calls search before extract (correct order)
- test_structured_output: Report validates against Pydantic schema
- test_session_persistence: State survives restart
- test_source_tracking: Every claim maps to a source
- test_wrong_tool_never_selected: Run 10 varied queries, verify 100% correct tool selection

### Deliverable
Research assistant that produces structured reports. Committed to git.

---

## Week 3: MCP Foundations

### Learning Objectives
- Understand MCP architecture (client, server, transport)
- Connect to existing MCP servers (filesystem, database)
- Understand how MCP replaces custom tool integrations
- Build a simple MCP client that an agent can use

### Key Concepts
- **MCP architecture**: Client (your agent) connects to Server (tool provider) over Transport (stdio, SSE, HTTP)
- **Why MCP matters**: Write integration once, use with any LLM. Like USB-C for AI.
- **Resources vs. Tools vs. Prompts**: Three MCP primitives. Resources = data access, Tools = actions, Prompts = reusable templates.
- **Server discovery**: How agents find and connect to available MCP servers

### Exercise: Agent with MCP File Server

Refactor the Week 1 file agent to use MCP instead of hardcoded tool functions. Then connect it to a second MCP server (SQLite) so the agent can work with both files and databases.

**Requirements:**
- Start the MCP filesystem server locally
- Build an MCP client that discovers available tools from the server
- Refactor the agent to call tools via MCP instead of direct function calls
- Add a second MCP server (SQLite) and have the agent use both
- Agent dynamically discovers what tools are available (no hardcoding)

**Success criteria:**
- Agent works identically to Week 1 but tools are provided via MCP
- Agent can answer questions that require both file and database access
- Adding a new MCP server requires zero changes to agent code
- Tool discovery is dynamic (agent reads tool list from server at startup)

**Key implementation:**
```python
# week03/mcp_agent.py
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def connect_to_server(command: str, args: list[str]) -> ClientSession:
    """Connect to an MCP server and return session."""
    server_params = StdioServerParameters(command=command, args=args)
    read, write = await stdio_client(server_params)
    session = ClientSession(read, write)
    await session.initialize()
    return session

async def discover_tools(session: ClientSession) -> list[dict]:
    """Get available tools from MCP server in Anthropic API format."""
    tools = await session.list_tools()
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        }
        for tool in tools.tools
    ]

async def call_tool(session: ClientSession, name: str, arguments: dict) -> str:
    """Call a tool on the MCP server."""
    result = await session.call_tool(name, arguments)
    return result.content[0].text
```

**Tests:**
- test_server_connection: MCP server starts and responds
- test_tool_discovery: Agent discovers correct tool count from server
- test_tool_execution_via_mcp: File listing works through MCP
- test_multi_server: Agent uses tools from both filesystem and SQLite servers
- test_no_hardcoded_tools: Removing a server removes those tools from agent

### Deliverable
MCP-connected agent with dynamic tool discovery. Committed to git.

### What Phase 1 Teaches (cumulative)
By end of Week 3, you can build an agent that connects to any MCP server, discovers tools dynamically, chains tool calls, persists state, tracks costs, and handles errors. This is the foundation for everything in Phases 2-4.

---

# Phase 2: Real Integrations (Weeks 4-6)

---

## Week 4: RAG Agents

### Learning Objectives
- Understand retrieval-augmented generation (RAG) architecture
- Build a vector store with ChromaDB
- Implement a RAG agent that answers questions from a document corpus
- Evaluate retrieval quality (precision, recall, relevance)

### Key Concepts
- **RAG pipeline**: Ingest documents -> chunk -> embed -> store -> query -> retrieve -> generate
- **Chunking strategies**: Fixed size, semantic, recursive. Tradeoffs between context and precision.
- **Embedding models**: Convert text to vectors for similarity search
- **Retrieval evaluation**: Is the agent finding the right documents? Is the answer grounded?

### Exercise: Documentation Q&A Agent

Build an agent that ingests a set of markdown documentation files (use the LangGraph docs or any public docs), builds a vector index, and answers questions with citations.

**Requirements:**
- Ingest 20+ markdown files into ChromaDB
- Chunk with overlap (512 tokens, 50 token overlap)
- Agent retrieves top-k relevant chunks before answering
- Every answer includes source citations (file + section)
- Agent says "I don't know" when retrieved context is insufficient
- Evaluate with 10 pre-written question/answer pairs

**Success criteria:**
- Agent answers 8/10 evaluation questions correctly
- Zero hallucinated citations (every citation maps to real content)
- Retrieval returns relevant chunks for 9/10 queries
- Ingestion pipeline processes 20 files in under 30 seconds
- Agent distinguishes between "found answer" and "insufficient context"

**Key implementation:**
```python
# week04/rag_agent.py
import chromadb
from chromadb.utils import embedding_functions

def build_index(docs_dir: str) -> chromadb.Collection:
    """Ingest documents into vector store."""
    client = chromadb.PersistentClient(path="./chroma_db")
    ef = embedding_functions.DefaultEmbeddingFunction()
    collection = client.get_or_create_collection("docs", embedding_function=ef)
    
    for file in Path(docs_dir).glob("**/*.md"):
        chunks = chunk_document(file.read_text(), chunk_size=512, overlap=50)
        for i, chunk in enumerate(chunks):
            collection.add(
                ids=[f"{file.stem}_{i}"],
                documents=[chunk],
                metadatas=[{"source": str(file), "chunk_index": i}]
            )
    return collection

def query_with_rag(question: str, collection, client: Anthropic) -> dict:
    """RAG query: retrieve then generate."""
    results = collection.query(query_texts=[question], n_results=5)
    context = "\n---\n".join(results["documents"][0])
    sources = results["metadatas"][0]
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system="Answer based only on the provided context. Cite sources. Say 'insufficient context' if unsure.",
        messages=[{
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}"
        }]
    )
    return {"answer": response.content[0].text, "sources": sources}
```

**Evaluation framework:**
```python
# week04/eval_rag.py
EVAL_PAIRS = [
    {"question": "How do you define state in LangGraph?", "expected_keywords": ["TypedDict", "StateGraph"]},
    {"question": "What is a conditional edge?", "expected_keywords": ["routing", "function", "condition"]},
    # ... 8 more
]

def evaluate(agent_fn, eval_pairs: list[dict]) -> dict:
    """Run evaluation and return metrics."""
    results = {"correct": 0, "total": len(eval_pairs), "details": []}
    for pair in eval_pairs:
        answer = agent_fn(pair["question"])
        has_keywords = all(kw.lower() in answer["answer"].lower() for kw in pair["expected_keywords"])
        results["correct"] += int(has_keywords)
        results["details"].append({"question": pair["question"], "pass": has_keywords})
    results["accuracy"] = results["correct"] / results["total"]
    return results
```

### Deliverable
RAG agent with evaluation pipeline scoring 80%+ accuracy. Committed to git.

---

## Week 5: Custom MCP Servers

### Learning Objectives
- Build a custom MCP server from scratch
- Expose a real service (database, API, file system) via MCP
- Handle authentication and error cases in MCP servers
- Test MCP servers independently of agents

### Key Concepts
- **MCP server lifecycle**: Initialize -> handle requests -> cleanup
- **Tool registration**: Defining tools with schemas that agents can discover
- **Resource exposure**: Making data queryable via MCP resources
- **Error handling**: Returning structured errors that agents can interpret

### Exercise: Build a Project Management MCP Server

Build a custom MCP server that wraps a SQLite database for project/task management. Then connect your agent to it.

**Requirements:**
- MCP server exposes 6 tools: create_project, list_projects, add_task, update_task, get_project_status, search_tasks
- Server uses SQLite for persistence
- Server validates inputs and returns structured errors
- Server exposes 2 resources: project list, task statistics
- Agent connects to this server and can manage projects via natural language

**Success criteria:**
- Server passes MCP protocol compliance tests
- Agent can create a project, add 5 tasks, mark 3 complete, and report status -- all via natural language
- Server handles concurrent requests without data corruption
- Error messages are specific enough for the agent to self-correct
- Server can be restarted without losing data

**Key implementation:**
```python
# week05/project_mcp_server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import sqlite3

app = Server("project-manager")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="create_project",
            description="Create a new project with a name and description",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["name"]
            }
        ),
        # ... remaining tools
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    db = get_db()
    if name == "create_project":
        # Real SQLite insert
        pass
    # ... handle other tools

async def main():
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())
```

**Tests:**
- test_server_starts: Server initializes and responds to list_tools
- test_create_and_retrieve: Full CRUD cycle through MCP
- test_validation_errors: Invalid input returns structured error
- test_agent_integration: Agent manages a project end-to-end via natural language
- test_persistence: Data survives server restart

### Deliverable
Custom MCP server + agent integration. Server is reusable. Committed to git.

---

## Week 6: LangGraph Orchestration

### Learning Objectives
- Build stateful workflows with LangGraph StateGraph
- Implement conditional routing based on agent decisions
- Use checkpointing for long-running workflows
- Integrate LangSmith for tracing and debugging

### Key Concepts
- **StateGraph**: Define nodes (functions), edges (flow), and state (TypedDict)
- **Conditional edges**: Route to different nodes based on state
- **Checkpointing**: Save and resume graph execution (critical for production)
- **LangSmith tracing**: Visualize every step of graph execution

### Exercise: Document Processing Pipeline

Build a LangGraph workflow that processes documents through multiple stages: classify, extract, validate, transform, and store. Each stage is a node. Routing depends on document type.

**Requirements:**
- State schema tracks document through entire pipeline
- 5 nodes: classify_document, extract_entities, validate_data, transform_format, store_result
- Conditional routing: classification determines which extraction strategy to use
- Checkpointing enabled: can resume from any node after failure
- LangSmith tracing active: every node execution is visible in dashboard
- At least 2 nodes make real LLM calls (classify and extract)

**Success criteria:**
- Pipeline correctly routes 3 document types (invoice, email, report)
- Checkpoint allows resume after simulated failure at any node
- LangSmith shows full trace for every execution
- Pipeline processes 10 documents with zero routing errors
- Each node has clear input/output contract via state schema

**Key implementation:**
```python
# week06/document_pipeline.py
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

class PipelineState(TypedDict):
    document: str
    doc_type: Literal["invoice", "email", "report", "unknown"]
    entities: dict
    validation_errors: list[str]
    transformed: dict
    stored: bool
    trace: list[str]

def classify_document(state: PipelineState) -> dict:
    """LLM call to classify document type."""
    # Real Anthropic API call
    pass

def route_by_type(state: PipelineState) -> str:
    """Conditional routing based on classification."""
    if state["doc_type"] == "unknown":
        return "error_handler"
    return "extract_entities"

# Build graph
builder = StateGraph(PipelineState)
builder.add_node("classify", classify_document)
builder.add_node("extract", extract_entities)
builder.add_node("validate", validate_data)
builder.add_node("transform", transform_format)
builder.add_node("store", store_result)
builder.add_node("error_handler", handle_error)

builder.add_edge(START, "classify")
builder.add_conditional_edges("classify", route_by_type)
builder.add_edge("extract", "validate")
builder.add_conditional_edges("validate", route_on_validation)
builder.add_edge("transform", "store")
builder.add_edge("store", END)

checkpointer = MemorySaver()
pipeline = builder.compile(checkpointer=checkpointer)
```

### Deliverable
LangGraph document pipeline with checkpointing and LangSmith tracing. Committed to git.

### What Phase 2 Teaches (cumulative)
By end of Week 6, you can build RAG systems, create custom MCP servers, and orchestrate multi-step workflows with LangGraph. You have evaluation frameworks, observability via LangSmith, and real integrations with databases and vector stores.

---

# Phase 3: Multi-Agent Systems (Weeks 7-9)

---

## Week 7: Multi-Agent Coordination

### Learning Objectives
- Design multi-agent systems with clear role separation
- Implement agent-to-agent communication via shared state
- Handle task dependencies between agents
- Understand when multi-agent adds value vs. single agent with more tools

### Key Concepts
- **Role-based agents**: Each agent has a specific expertise and responsibility boundary
- **Shared state**: Agents communicate by reading/writing to a shared state object (not direct messaging)
- **Task dependencies**: Agent B cannot start until Agent A completes (DAG execution)
- **Agent economics**: Multi-agent uses 15x more tokens than chat. Only use when justified.

### Exercise: Code Review Multi-Agent System

Build a 3-agent system that reviews code: Analyzer (finds issues), Security Auditor (checks vulnerabilities), Improver (suggests fixes). All three read the same code, produce independent assessments, then a synthesizer combines them.

**Requirements:**
- 3 specialist agents + 1 synthesizer, each with distinct system prompts
- Each agent makes independent LLM calls (no agent sees another's output until synthesis)
- Shared state tracks all agent outputs
- Synthesizer resolves contradictions between agents
- System processes a real Python file and produces actionable report

**Success criteria:**
- Each agent produces distinct findings (not repeating each other)
- Synthesizer correctly identifies when agents disagree
- Total cost per review is under $0.50
- System handles files up to 500 lines
- Report includes severity ratings and specific line references

**Key implementation:**
```python
# week07/code_review_agents.py
from langgraph.graph import StateGraph, START, END

class ReviewState(TypedDict):
    code: str
    filename: str
    analyzer_findings: list[dict]
    security_findings: list[dict]
    improvement_suggestions: list[dict]
    synthesized_report: dict
    token_usage: dict

def run_analyzer(state: ReviewState) -> dict:
    """Analyzer agent: find code quality issues."""
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        system="You are a code quality analyzer. Find bugs, code smells, and logic errors.",
        messages=[{"role": "user", "content": f"Review this code:\n```\n{state['code']}\n```"}]
    )
    # Parse structured findings
    pass

def run_security_auditor(state: ReviewState) -> dict:
    """Security agent: find vulnerabilities."""
    pass

def run_improver(state: ReviewState) -> dict:
    """Improvement agent: suggest enhancements."""
    pass

def synthesize(state: ReviewState) -> dict:
    """Combine all findings, resolve contradictions."""
    pass

# Agents run in parallel, then synthesize
builder = StateGraph(ReviewState)
builder.add_node("analyzer", run_analyzer)
builder.add_node("security", run_security_auditor)
builder.add_node("improver", run_improver)
builder.add_node("synthesizer", synthesize)

builder.add_edge(START, "analyzer")
builder.add_edge(START, "security")
builder.add_edge(START, "improver")
builder.add_edge("analyzer", "synthesizer")
builder.add_edge("security", "synthesizer")
builder.add_edge("improver", "synthesizer")
builder.add_edge("synthesizer", END)
```

### Deliverable
Multi-agent code review system with synthesized reports. Committed to git.

---

## Week 8: Voting and Conflict Resolution

### Learning Objectives
- Implement weighted voting for multi-agent decisions
- Build conflict detection and resolution logic
- Design human-in-the-loop review for edge cases
- Handle agent disagreement productively

### Key Concepts
- **Weighted voting**: Not all agents are equal. Security agent's veto carries more weight than style suggestions.
- **Conflict types**: Unanimous agreement, clear majority, tie, veto (single agent overrides)
- **Resolution strategies**: Auto-approve (unanimous), majority wins (clear), human review (tie/veto)
- **Audit trail**: Every decision must be traceable -- who voted what and why

### Exercise: Extend Week 7 with Voting

Add a voting layer to the code review system. Each agent votes APPROVE, REQUEST_CHANGES, or BLOCK on the code. Weighted voting determines the outcome. Ties and BLOCK votes trigger human review.

**Requirements:**
- Each agent casts a structured vote with position, confidence score, and reasoning
- Voting weights: Security (2.0x), Analyzer (1.5x), Improver (1.0x)
- Resolution rules: unanimous approve = auto-approve, any BLOCK = human review, tie = human review, clear majority = auto-decide
- Human review interface (CLI) shows all votes, reasoning, and code context
- Decision log records every vote and final decision with timestamps

**Success criteria:**
- Voting correctly tallies weighted scores
- BLOCK from security always triggers human review regardless of other votes
- Human can approve, reject, or override individual agent weights
- Decision log is complete and machine-parseable (JSON)
- System handles edge cases: all abstain, single agent timeout, conflicting confidence scores

**Key implementation:**
```python
# week08/voting.py
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

class VotePosition(Enum):
    APPROVE = "approve"
    REQUEST_CHANGES = "request_changes"
    BLOCK = "block"
    ABSTAIN = "abstain"

@dataclass
class Vote:
    agent_name: str
    position: VotePosition
    confidence: float          # 0.0 to 1.0
    reasoning: str
    weight: float = 1.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class VotingResult:
    outcome: str               # "approved", "rejected", "human_review"
    weighted_score: float
    votes: list[Vote]
    requires_human: bool
    trigger_reason: str        # "unanimous", "majority", "tie", "veto"

class VotingSystem:
    def __init__(self, weights: dict[str, float]):
        self.weights = weights
    
    def tally(self, votes: list[Vote]) -> VotingResult:
        # Check for veto (any BLOCK from high-weight agent)
        # Calculate weighted scores
        # Determine outcome based on resolution rules
        pass
```

### Deliverable
Voting system integrated with code review agents. Full audit trail. Committed to git.

---

## Week 9: Evaluation and Observability

### Learning Objectives
- Build evaluation pipelines for agent systems
- Use LangSmith for production-grade tracing
- Implement cost tracking and budget enforcement
- Create regression tests for agent behavior

### Key Concepts
- **Agent evaluation**: Unlike traditional software, agent outputs are non-deterministic. Need statistical evaluation over many runs.
- **LangSmith datasets**: Create test sets, run evaluations, track metrics over time
- **Cost tracking**: Token usage per agent, per workflow, per user request. Set budgets.
- **Regression testing**: Ensure new changes don't break existing behavior. Golden test sets.

### Exercise: Evaluation Suite for the Code Review System

Build a comprehensive evaluation and monitoring layer for the Week 7-8 system.

**Requirements:**
- Create a dataset of 15 code samples with known issues (ground truth)
- Build an evaluation pipeline that runs the full system against the dataset
- Track: accuracy (did agents find known issues?), cost per review, latency per agent, agreement rate between agents
- Implement cost budget: system refuses to run if projected cost exceeds limit
- Create a LangSmith dataset and run evaluations through it
- Build a simple dashboard (CLI or Streamlit) showing metrics

**Success criteria:**
- Evaluation pipeline runs all 15 samples and produces metrics report
- Accuracy is measured against ground truth (target: 70%+ issue detection)
- Cost tracking is accurate within 5% of actual API charges
- Budget enforcement stops execution before overspend
- Metrics are stored and can be compared across runs (regression detection)

**Key implementation:**
```python
# week09/evaluation.py
from langsmith import Client
from langsmith.evaluation import evaluate

ls_client = Client()

# Create dataset
dataset = ls_client.create_dataset("code-review-eval")
for sample in ground_truth_samples:
    ls_client.create_example(
        inputs={"code": sample["code"], "filename": sample["filename"]},
        outputs={"known_issues": sample["issues"]},
        dataset_id=dataset.id
    )

# Define evaluator
def issue_detection_evaluator(run, example):
    """Check if agents found the known issues."""
    predicted = run.outputs["synthesized_report"]["issues"]
    expected = example.outputs["known_issues"]
    found = sum(1 for e in expected if any(e["type"] in p.get("type", "") for p in predicted))
    return {"score": found / len(expected) if expected else 1.0}

# Run evaluation
results = evaluate(
    run_code_review_system,
    data=dataset.name,
    evaluators=[issue_detection_evaluator],
    experiment_prefix="v1.0"
)
```

### Deliverable
Evaluation suite with LangSmith integration, cost tracking, and metrics dashboard. Committed to git.

### What Phase 3 Teaches (cumulative)
By end of Week 9, you can build multi-agent systems with voting, conflict resolution, and human oversight. You have evaluation pipelines, cost tracking, and observability. This is the skill set described in D.E. Shaw, Deloitte, and EY job postings.

---

# Phase 4: Production (Weeks 10-12)

---

## Week 10: Production Deployment

### Learning Objectives
- Deploy an agent system as a web service
- Build a Streamlit UI for human interaction
- Implement proper error handling and retry logic for production
- Set up logging, monitoring, and alerting

### Key Concepts
- **Streamlit for agent UIs**: Fast way to build interactive frontends for agent systems
- **FastAPI for agent APIs**: Expose agents as REST endpoints for programmatic access
- **Production error handling**: Retries with exponential backoff, circuit breakers, graceful degradation
- **Structured logging**: JSON logs with request IDs, latency, cost, and error details

### Exercise: Deploy the Code Review System

Take the Week 7-9 code review system and make it production-ready.

**Requirements:**
- Streamlit UI: upload a Python file, see review results with voting details
- FastAPI endpoint: POST /review with file content, returns JSON report
- Error handling: API timeouts retry 3x with exponential backoff, graceful degradation if one agent fails
- Logging: every request gets a UUID, all agent calls logged with latency and tokens
- Configuration: model, weights, budget all configurable via environment variables

**Success criteria:**
- Streamlit UI works end-to-end (upload -> review -> results displayed)
- API returns valid JSON for all inputs (including malformed code)
- System degrades gracefully: if security agent fails, other two still produce results
- Logs are structured JSON, queryable by request ID
- Configuration changes require no code changes (env vars only)

### Deliverable
Deployed code review service (Streamlit + FastAPI). Committed to git.

---

## Week 11: Capstone Build

### Learning Objectives
- Design and build a complete multi-agent system from scratch
- Apply all patterns from Weeks 1-10
- Make architectural decisions with tradeoff analysis
- Build something portfolio-worthy

### Capstone Project: Choose One

**Option A: DevOps Incident Response System**
Multi-agent system that triages production incidents. Agents: Log Analyzer, Metric Checker, Runbook Executor, Communication Drafter, Escalation Manager. Connected via MCP to (simulated) monitoring tools.

**Option B: Research Synthesis Agent**
Multi-agent RAG system that takes a research question, searches multiple document collections, synthesizes findings from different perspectives, identifies contradictions, and produces a structured report with confidence scores.

**Option C: Code Generation Pipeline**
Multi-agent system that takes a feature spec and produces: database schema (DB Agent), API endpoints (Backend Agent), and frontend components (Frontend Agent). Security Agent reviews all output. QA Agent writes tests. Voting resolves conflicts.

**Requirements (all options):**
- Minimum 4 agents with distinct roles
- MCP integration for at least one external service
- LangGraph orchestration with conditional routing
- Voting/conflict resolution for multi-agent decisions
- RAG component (at least one agent uses retrieval)
- Evaluation pipeline with ground truth dataset
- Cost tracking and budget enforcement
- Streamlit UI or CLI interface
- LangSmith tracing enabled

**Architecture document required before coding:**
```markdown
# Capstone Architecture

## System Overview
[What does this system do? Who is the user? What problem does it solve?]

## Agent Definitions
[For each agent: role, tools, MCP servers, voting weight, failure mode]

## State Schema
[TypedDict with all fields, which agent writes which field]

## Dependency Graph
[Which agents depend on which? DAG visualization]

## Conflict Scenarios
[3 scenarios where agents disagree, and how they resolve]

## Evaluation Plan
[Ground truth dataset, metrics, target scores]

## Cost Budget
[Estimated tokens per request, monthly budget at expected volume]
```

### Deliverable
Architecture document reviewed (by Claude Code or peer). Initial implementation committed.

---

## Week 12: Capstone Polish and Presentation

### Learning Objectives
- Complete and test the capstone system end-to-end
- Write documentation that demonstrates understanding
- Prepare the project for portfolio/interview presentation
- Reflect on the full learning journey

### Requirements
- All tests pass (minimum 20 tests)
- Evaluation pipeline shows measurable results
- README includes: architecture diagram, setup instructions, usage examples, design decisions
- Cost report: total API spend for development, estimated production costs
- 5-minute demo script: what the system does, how it works, key design decisions

### Final Checklist
- [ ] System runs end-to-end without errors
- [ ] 4+ agents with distinct roles
- [ ] MCP integration working
- [ ] LangGraph orchestration with conditional routing
- [ ] Voting/conflict resolution implemented
- [ ] RAG component functional
- [ ] Evaluation pipeline with metrics
- [ ] Cost tracking accurate
- [ ] Streamlit UI or CLI working
- [ ] LangSmith tracing active
- [ ] 20+ tests passing
- [ ] README complete with architecture diagram
- [ ] Git history clean with meaningful commits
- [ ] Can explain every design decision in an interview

### Deliverable
Complete, tested, documented capstone project. Portfolio-ready.

---

## Appendix A: Skills Mapped to Job Requirements

| Skill | Where Learned | Job Postings Requiring It |
|-------|--------------|--------------------------|
| Tool calling / function calling | Week 1 | All agentic AI roles |
| MCP integration | Weeks 3, 5 | Growing rapidly -- Deloitte, Google Cloud, startups |
| RAG / vector search | Week 4 | Nearly all AI engineer postings |
| LangGraph / state graphs | Week 6 | LangChain ecosystem roles, growing |
| Multi-agent orchestration | Weeks 7-8 | D.E. Shaw, EY, senior AI roles |
| Evaluation and observability | Week 9 | All production AI roles |
| Production deployment | Week 10 | All roles beyond research/prototyping |
| Voting / conflict resolution | Week 8 | Multi-agent system roles |
| Cost management | Weeks 1-12 | All production roles (token economics) |
| Claude Code / AI-assisted dev | Throughout | Increasingly expected, not always stated |

## Appendix B: Estimated API Costs

| Phase | Weeks | Estimated Cost |
|-------|-------|---------------|
| Foundations | 1-3 | $3-5 |
| Real Integrations | 4-6 | $5-8 |
| Multi-Agent | 7-9 | $5-10 |
| Production + Capstone | 10-12 | $5-10 |
| **Total** | **1-12** | **$18-33** |

Costs assume Claude Sonnet for most calls. Using Opus for evaluation or synthesis will increase costs. Budget $50 to be safe.

## Appendix C: Resources

- **MCP Specification**: https://modelcontextprotocol.io
- **LangGraph Documentation**: https://langchain-ai.github.io/langgraph/
- **LangSmith Documentation**: https://docs.smith.langchain.com/
- **Anthropic API Docs**: https://docs.anthropic.com/
- **ChromaDB Documentation**: https://docs.trychroma.com/
- **Streamlit Documentation**: https://docs.streamlit.io/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **OpenAI Agents Guide**: https://platform.openai.com/docs/guides/agents

---

**Last Updated:** March 2026
**Aligned To:** 2026 job market requirements -- MCP, production deployment, evaluation, multi-agent orchestration
