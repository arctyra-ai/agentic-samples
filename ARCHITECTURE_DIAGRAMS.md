# Architecture Diagrams

All diagrams are in Mermaid format. Render with:
- GitHub markdown (automatic)
- https://mermaid.live
- VS Code Mermaid extension

---

## Curriculum Progression (Weeks 1-12)

```mermaid
graph LR
    W1["Week 1\nAgent Loop\nTool Calling"]
    W2["Week 2\nTool Chaining\nStructured Output"]
    W3["Week 3\nMCP Client\nDynamic Discovery"]
    W4["Week 4\nRAG Pipeline\nVector Search"]
    W5["Week 5\nCustom MCP Server\nSQLite"]
    W6["Week 6\nLangGraph\nState Graphs"]
    W7["Week 7\nMulti-Agent\nParallel Execution"]
    W8["Week 8\nVoting\nConflict Resolution"]
    W9["Week 9\nEvaluation\nObservability"]
    W10["Week 10\nDeploy\nStreamlit + FastAPI"]
    W11["Week 11\nCapstone\nBuild"]
    W12["Week 12\nCapstone\nPolish"]

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
    FS["MCP Server:\nFilesystem"]
    DB["MCP Server:\nSQLite"]
    Future["MCP Server:\n(any new server)"]

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
    Docs["Markdown\nDocuments"]
    Chunk["Chunker\n512 tokens\n50 overlap"]
    Embed["Embedding\nModel"]
    Store["ChromaDB\nVector Store"]
    Query["User\nQuestion"]
    Retrieve["Top-K\nRetrieval"]
    Generate["LLM\nGenerate Answer"]
    Answer["Answer\n+ Citations"]

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
    Classify["classify_document\n(LLM call)"]
    Extract["extract_entities\n(LLM call)"]
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
    Start["START\n(code input)"]
    Analyzer["Analyzer Agent\nBugs, smells, logic"]
    Security["Security Agent\nVulnerabilities"]
    Improver["Improver Agent\nEnhancements"]
    Synth["Synthesizer\nCombine + resolve"]
    End["END\n(unified report)"]

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
    Veto{"Security\nBLOCK?"}
    Unanimous{"All\nAgree?"}
    Majority{"Clear\nMajority?"}
    Confidence{"High\nConfidence?"}
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
    UI["Streamlit UI\n(file upload)"]
    API["FastAPI\n(/review endpoint)"]
    Graph["LangGraph\nOrchestration"]
    A1["Analyzer"]
    A2["Security"]
    A3["Improver"]
    Synth["Synthesizer"]
    Vote["Voting System"]
    Log["Structured\nLogging"]
    Trace["LangSmith\nTracing"]
    Cost["Cost\nTracker"]

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
    User["User\nFeature Spec"]
    Orch["Orchestrator\nDecompose Tasks"]
    DB["DB Agent\nSchema Design"]
    BE["Backend Agent\nAPI Endpoints"]
    FE["Frontend Agent\nComponents"]
    SEC["Security Agent\nAudit (weight: 2.0)"]
    QA["QA Agent\nTest Generation"]
    Vote["Voting\nSystem"]
    Human["Human Review\n(ties/vetoes)"]
    Output["Final Output\nCode + Reports"]
    MCP["MCP Server\nProject DB"]
    RAG["RAG\nDocs Retrieval"]
    Eval["Evaluation\nPipeline"]

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
