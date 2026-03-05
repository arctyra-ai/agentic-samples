# Architecture Diagrams

All diagrams are in Mermaid format. Render with:
- GitHub markdown (automatic)
- https://mermaid.live
- VS Code Mermaid extension

---

## Curriculum Progression (Weeks 1-12)

```mermaid
graph LR
    W1["Week 1 Agent Loop & Tool Calling"]
    W2["Week 2 Tool Chaining & Structured Output"]
    W3["Week 3 MCP Client & Dynamic Discovery"]
    W4["Week 4 RAG Pipeline & Vector Search"]
    W5["Week 5 Custom MCP Server\SQLite"]
    W6["Week 6 LangGraph & State Graphs"]
    W7["Week 7 Multi-Agent & Parallel Execution"]
    W8["Week 8 Voting & Conflict Resolution"]
    W9["Week 9 Evaluation & Observability"]
    W10["Week 10 Deploy Streamlit + FastAPI"]
    W11["Week 11 Capstone Build"]
    W12["Week 12 Capstone Polish"]

    W1 --> W2 --> W3
    W3 --> W4 --> W5 --> W6
    W6 --> W7 --> W8 --> W9
    W9 --> W10 --> W11 --> W12

    style W1 fill:#e3f2fd
    style W2 fill:#e3f2fd
    style W3 fill:#e3f2fd
    style W4 fill:#e8f5e9
    style W5 fill:#e8f5e9
    style W6 fill:#e8f5e9
    style W7 fill:#fff3e0
    style W8 fill:#fff3e0
    style W9 fill:#fff3e0
    style W10 fill:#fce4ec
    style W11 fill:#fce4ec
    style W12 fill:#fce4ec
```

---

## Week 1: Agent Loop

```mermaid
graph TD
    User["User Request"]
    LLM["LLM (Claude)"]
    Tools["Tool Executor"]
    Done["Final Response"]

    User -->|Natural language| LLM
    LLM -->|tool_use block| Tools
    Tools -->|tool_result| LLM
    LLM -->|text only = done| Done
    LLM -->|tool_use again| Tools

    style User fill:#e3f2fd
    style LLM fill:#fff3e0
    style Tools fill:#e8f5e9
    style Done fill:#c8e6c9
```

---

## Week 3: MCP Architecture

```mermaid
graph TB
    Agent["Agent"]
    Router["MCP Tool Router"]
    FS["MCP Server:Filesystem"]
    DB["MCP Server:SQLite"]
    Future["MCP Server:(any new server)"]

    Agent -->|discover tools| Router
    Agent -->|call tool| Router
    Router -->|filesystem__read_file| FS
    Router -->|sqlite__query| DB
    Router -->|newserver__tool| Future

    style Agent fill:#fff3e0
    style Router fill:#e3f2fd
    style FS fill:#e8f5e9
    style DB fill:#e8f5e9
    style Future fill:#f3e5f5,stroke-dasharray: 5 5
```

---

## Week 4: RAG Pipeline

```mermaid
graph LR
    Docs["Markdown Documents"]
    Chunk["Chunker 512 tokens 50 overlap"]
    Embed["Embedding Model"]
    Store["ChromaDB Vector Store"]
    Query["User Question"]
    Retrieve["Top-K Retrieval"]
    Generate["LLM Generate Answer"]
    Answer["Answer + Citations"]

    Docs --> Chunk --> Embed --> Store
    Query --> Retrieve
    Store --> Retrieve
    Retrieve --> Generate --> Answer

    style Docs fill:#e3f2fd
    style Store fill:#e8f5e9
    style Generate fill:#fff3e0
    style Answer fill:#c8e6c9
```

---

## Week 6: Document Processing Pipeline

```mermaid
graph TD
    Start["START"]
    Classify["classify_document (LLM call)"]
    Extract["extract_entities (LLM call)"]
    Validate["validate_data"]
    Transform["transform_format"]
    Store["store_result"]
    Error["error_handler"]
    End["END"]

    Start --> Classify
    Classify -->|"invoice/email/report"| Extract
    Classify -->|"unknown"| Error
    Extract --> Validate
    Validate -->|"no errors"| Transform
    Validate -->|"has errors"| Error
    Transform --> Store
    Store --> End
    Error --> End

    style Start fill:#e3f2fd
    style Classify fill:#fff3e0
    style Extract fill:#fff3e0
    style Validate fill:#e8f5e9
    style Transform fill:#e8f5e9
    style Store fill:#c8e6c9
    style Error fill:#ffcdd2
    style End fill:#e3f2fd
```

---

## Week 7: Multi-Agent Code Review

```mermaid
graph TD
    Start["START (code input)"]
    Analyzer["Analyzer Agent Bugs, smells, logic"]
    Security["Security Agent Vulnerabilities"]
    Improver["Improver Agent Enhancements"]
    Synth["Synthesizer Combine + resolve"]
    End["END (unified report)"]

    Start --> Analyzer
    Start --> Security
    Start --> Improver
    Analyzer --> Synth
    Security --> Synth
    Improver --> Synth
    Synth --> End

    style Start fill:#e3f2fd
    style Analyzer fill:#fff3e0
    style Security fill:#ffcdd2
    style Improver fill:#e8f5e9
    style Synth fill:#f3e5f5
    style End fill:#c8e6c9
```

---

## Week 8: Voting and Conflict Resolution

```mermaid
graph TD
    Votes["All Votes In"]
    Veto{"Security BLOCK?"}
    Unanimous{"All Agree?"}
    Majority{"Clear Majority?"}
    Confidence{"High Confidence?"}
    Auto["AUTO-APPROVE"]
    Reject["AUTO-REJECT"]
    Human["HUMAN REVIEW"]

    Votes --> Veto
    Veto -->|"Yes (weight >= 2.0)"| Human
    Veto -->|No| Unanimous
    Unanimous -->|"All APPROVE"| Auto
    Unanimous -->|"All REJECT"| Reject
    Unanimous -->|Mixed| Majority
    Majority -->|">= 75%"| Confidence
    Majority -->|"< 75%"| Human
    Confidence -->|">= 50% avg"| Auto
    Confidence -->|"< 50% avg"| Human

    style Votes fill:#e3f2fd
    style Auto fill:#c8e6c9
    style Reject fill:#ffcdd2
    style Human fill:#fff3e0
```

---

## Week 10: Production Architecture

```mermaid
graph TB
    UI["Streamlit UI (file upload)"]
    API["FastAPI (/review endpoint)"]
    Graph["LangGraph Orchestration"]
    A1["Analyzer"]
    A2["Security"]
    A3["Improver"]
    Synth["Synthesizer"]
    Vote["Voting System"]
    Log["Structured Logging"]
    Trace["LangSmith Tracing"]
    Cost["Cost Tracker"]

    UI --> Graph
    API --> Graph
    Graph --> A1
    Graph --> A2
    Graph --> A3
    A1 --> Synth
    A2 --> Synth
    A3 --> Synth
    Synth --> Vote
    Graph --> Log
    Graph --> Trace
    Graph --> Cost

    style UI fill:#e3f2fd
    style API fill:#e3f2fd
    style Graph fill:#fff3e0
    style Vote fill:#f3e5f5
    style Log fill:#e8f5e9
    style Trace fill:#e8f5e9
    style Cost fill:#e8f5e9
```

---

## Capstone: Full System (Example: Code Generation Pipeline)

```mermaid
graph TB
    User["User Feature Spec"]
    Orch["Orchestrator Decompose Tasks"]
    DB["DB Agent Schema Design"]
    BE["Backend Agent API Endpoints"]
    FE["Frontend Agent Components"]
    SEC["Security Agent Audit (weight: 2.0)"]
    QA["QA Agent Test Generation"]
    Vote["Voting System"]
    Human["Human Review (ties/vetoes)"]
    Output["Final Output Code + Reports"]
    MCP["MCP Server Project DB"]
    RAG["RAG Docs Retrieval"]
    Eval["Evaluation Pipeline"]

    User --> Orch
    Orch --> DB
    DB --> BE
    BE --> FE
    DB --> SEC
    BE --> SEC
    FE --> SEC
    SEC --> QA
    QA --> Vote
    SEC --> Vote
    Vote -->|"Conflict"| Human
    Vote -->|"Clear"| Output
    Human --> Output

    Orch -.-> MCP
    BE -.-> RAG
    Output -.-> Eval

    style User fill:#e3f2fd
    style Orch fill:#fff3e0
    style DB fill:#e3f2fd
    style BE fill:#e3f2fd
    style FE fill:#e3f2fd
    style SEC fill:#ffcdd2
    style QA fill:#e8f5e9
    style Vote fill:#f3e5f5
    style Human fill:#fff3e0
    style Output fill:#c8e6c9
    style MCP fill:#e0e0e0
    style RAG fill:#e0e0e0
    style Eval fill:#e0e0e0
```
