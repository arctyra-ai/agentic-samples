# System Architecture Diagrams

All diagrams below are in Mermaid format. They can be visualized with:
- GitHub markdown (automatic rendering)
- Mermaid live editor: https://mermaid.live
- VS Code Mermaid extension

---

## Diagram 1: TODO Agent Evolution (Weeks 1-9)

Shows how the system evolves from simple to complex.

```mermaid
graph TD
    A["Week 1: Single Agent<br/>4 Tools"]
    B["Week 2: Multi-Tool<br/>6+ Tools + Memory"]
    C["Week 3: Error Handling<br/>Logging + Self-Correction"]
    D["Week 4: CrewAI<br/>3 Agents with Roles"]
    E["Week 5: Dependencies<br/>Task Sequencing"]
    F["Week 6: LangGraph<br/>State Graphs"]
    G["Week 7: Voting<br/>Conflict Resolution"]
    H["Week 8-9: Integration<br/>Full System"]
    
    A -->|Week 1-2| B
    B -->|Week 2-3| C
    C -->|Week 3-4| D
    D -->|Week 4-5| E
    E -->|Week 5-6| F
    F -->|Week 6-7| G
    G -->|Week 7-9| H
    
    style A fill:#e1f5ff
    style H fill:#4caf50
```

---

## Diagram 2: Agent Architecture Overview

High-level view of how agents interact.

```mermaid
graph TB
    User["👤 User<br/>Natural Language<br/>Request"]
    
    Orch["🎯 Orchestrator Agent<br/>Decompose Tasks<br/>Assign Agents"]
    
    DB["💾 Database Agent<br/>Schema Design<br/>Optimization"]
    
    BE["🔧 Backend Agent<br/>API Design<br/>Business Logic"]
    
    FE["🎨 Frontend Agent<br/>Components<br/>UI Layout"]
    
    SEC["🔒 Security Agent<br/>Audit<br/>Vulnerability Check"]
    
    QA["✅ QA Agent<br/>Testing<br/>Performance"]
    
    Vote["🗳️ Voting System<br/>Aggregate Votes<br/>Resolve Conflicts"]
    
    Human["👨‍⚖️ Human Reviewer<br/>Break Ties<br/>Override Decisions"]
    
    Output["📄 Final Code<br/>Database Schema<br/>Audits"]
    
    User -->|Requirements| Orch
    
    Orch -->|Task: Design DB| DB
    DB -->|Votes| Vote
    
    Orch -->|Task: Write Backend| BE
    BE -->|Votes| Vote
    
    Orch -->|Task: Build Frontend| FE
    FE -->|Votes| Vote
    
    Orch -->|Task: Security Review| SEC
    SEC -->|Votes| Vote
    
    Orch -->|Task: QA Testing| QA
    QA -->|Votes| Vote
    
    Vote -->|Conflict?| Human
    Vote -->|Clear Decision| Output
    Human -->|Decision| Output
    
    style Orch fill:#ff9800
    style DB fill:#2196f3
    style BE fill:#2196f3
    style FE fill:#2196f3
    style SEC fill:#f44336
    style QA fill:#4caf50
    style Vote fill:#9c27b0
    style Human fill:#ffc107
    style Output fill:#4caf50
```

---

## Diagram 3: Task Dependency Graph

Shows how tasks depend on each other.

```mermaid
graph LR
    Start["📥 User Requirement"]
    
    Task1["1️⃣ Parse & Decompose<br/>Orchestrator"]
    Task2["2️⃣ Database Design<br/>Database Agent"]
    Task3["3️⃣ Backend Code<br/>Backend Agent"]
    Task4["4️⃣ Frontend Code<br/>Frontend Agent"]
    Task5["🔒 Security Review<br/>Security Agent"]
    Task6["✅ QA Testing<br/>QA Agent"]
    Task7["🗳️ Vote & Aggregate<br/>Voting System"]
    Task8["👨‍⚖️ Human Review?<br/>Only if Conflict"]
    Task9["📄 Final Output<br/>Code + Audits"]
    
    Start -->|Requires parsing| Task1
    Task1 -->|Broken into| Task2
    Task2 -->|Schema provided to| Task3
    Task3 -->|API contract to| Task4
    
    Task3 -->|Code to review| Task5
    Task4 -->|Code to review| Task5
    Task5 -->|Review result| Task7
    
    Task3 -->|Test code| Task6
    Task4 -->|Test code| Task6
    Task6 -->|Test result| Task7
    
    Task7 -->|Tie or veto?| Task8
    Task7 -->|Clear decision| Task9
    Task8 -->|Human approves| Task9
    
    style Start fill:#e1f5ff
    style Task1 fill:#ff9800
    style Task2 fill:#2196f3
    style Task3 fill:#2196f3
    style Task4 fill:#2196f3
    style Task5 fill:#f44336
    style Task6 fill:#4caf50
    style Task7 fill:#9c27b0
    style Task8 fill:#ffc107
    style Task9 fill:#4caf50
```

---

## Diagram 4: Voting System Flow

How voting works when conflicts arise.

```mermaid
graph TD
    A["Agents Express Opinions<br/>on Proposed Action"]
    
    B["Collect Votes"]
    B -->|Backend votes APPROVE| C1["Backend Vote<br/>weight: 1.0x<br/>✓ APPROVE"]
    B -->|Security votes REJECT| C2["Security Vote<br/>weight: 2.0x<br/>✗ REJECT"]
    B -->|QA votes REJECT| C3["QA Vote<br/>weight: 1.5x<br/>✗ REJECT"]
    
    C1 -->|Apply weights| D["Weighted Tally<br/>Approve: 1.0<br/>Reject: 3.5"]
    C2 -->|Apply weights| D
    C3 -->|Apply weights| D
    
    D -->|Calculate percentages| E["Outcome Determination<br/>Approve: 22%<br/>Reject: 78%"]
    
    E -->|Check result type| F{Decision Type}
    
    F -->|Unanimous| G["⚪ AUTO APPROVED<br/>or<br/>⚪ AUTO REJECTED<br/>(No human needed)"]
    
    F -->|Clear Winner| H["🟡 APPROVED/REJECTED<br/>with high confidence<br/>(Human can override)"]
    
    F -->|Tie Vote| I["🔴 CONFLICT<br/>50/50 split<br/>REQUIRES HUMAN"]
    
    F -->|Security Veto| J["🔴 SECURITY VETO<br/>REQUIRES HUMAN<br/>Override=Accept risk"]
    
    G -->|Execute| K["✅ EXECUTED"]
    H -->|Likely OK| K
    I -->|Need input| L["👨‍⚖️ Human Review"]
    J -->|Need input| L
    L -->|Approve/Reject| K
    
    style A fill:#e3f2fd
    style C1 fill:#4caf50
    style C2 fill:#f44336
    style C3 fill:#f44336
    style D fill:#9c27b0
    style E fill:#9c27b0
    style F fill:#ff9800
    style G fill:#4caf50
    style H fill:#ffc107
    style I fill:#f44336
    style J fill:#f44336
    style L fill:#ffc107
    style K fill:#4caf50
```

---

## Diagram 5: LangGraph State Flow

How state moves through the graph nodes.

```mermaid
graph LR
    User["👤 User Input"]
    
    User -->|Request: 'Add a task'| State1["📦 State<br/>user_input: 'Add...'<br/>parsed_intent: null"]
    
    State1 -->|→ Parse Node| State2["📦 State<br/>user_input: 'Add...'<br/>parsed_intent: 'add_task'"]
    
    State2 -->|→ Validate Node| State3["📦 State<br/>parsed_intent: 'add_task'<br/>is_valid: true"]
    
    State3 -->|Valid?| Condition{Decision}
    
    Condition -->|Yes| State4["📦 State<br/>is_valid: true<br/>result: 'Task added'"]
    Condition -->|No| State5["📦 State<br/>is_valid: false<br/>error: 'Invalid input'"]
    
    State4 -->|→ Execute Node| Output1["✅ Task Added"]
    State5 -->|→ Error Handler| Output2["❌ Error Handled"]
    
    Output1 -->|Return to User| User2["👤 User"]
    Output2 -->|Return to User| User2
    
    style User fill:#e1f5ff
    style State1 fill:#f3e5f5
    style State2 fill:#f3e5f5
    style State3 fill:#f3e5f5
    style State4 fill:#f3e5f5
    style State5 fill:#f3e5f5
    style Condition fill:#ff9800
    style Output1 fill:#4caf50
    style Output2 fill:#f44336
    style User2 fill:#c8e6c9
```

---

## Diagram 6: Conflict Resolution Decision Tree

What happens when agents disagree.

```mermaid
graph TD
    A["⚙️ Voting Complete"]
    
    A --> B{All agents<br/>agree?}
    
    B -->|YES| C["✅ AUTO EXECUTE<br/>No human needed"]
    B -->|NO| D{Security Veto?}
    
    D -->|YES| E["🔴 ESCALATE<br/>Human MUST review<br/>Risk acceptance needed"]
    D -->|NO| F{Result is TIE?<br/>50-50 split}
    
    F -->|YES| G["🟡 ESCALATE<br/>Human breaks tie<br/>Review both options"]
    F -->|NO| H["🟢 CLEAR WINNER<br/>Vote: 70% vs 30%"]
    
    H --> I{Confidence<br/>high?}
    I -->|YES - 75%+ | J["✅ AUTO EXECUTE<br/>Human can override"]
    I -->|NO - < 75%| G
    
    C --> K["📋 Log Decision<br/>Reasoning: All unanimous<br/>Agents: X,Y,Z"]
    E --> L["📋 Log Decision<br/>Reasoning: Security veto<br/>Risk: Acknowledged"]
    G --> L
    J --> M["📋 Log Decision<br/>Reasoning: High confidence<br/>Agents: X,Y vs Z"]
    
    K --> N["Execute or return result"]
    L --> N
    M --> N
    
    style A fill:#e3f2fd
    style B fill:#ff9800
    style C fill:#4caf50
    style D fill:#ff9800
    style E fill:#f44336
    style F fill:#ff9800
    style G fill:#ffc107
    style H fill:#4caf50
    style I fill:#ff9800
    style J fill:#8bc34a
    style K fill:#e8f5e9
    style L fill:#ffebee
    style M fill:#e8f5e9
    style N fill:#4caf50
```

---

## Diagram 7: Agent Communication Pattern

How agents coordinate without direct messaging.

```mermaid
graph TB
    User["👤 User Request"]
    
    Orch["🎯 Orchestrator<br/>Receives request<br/>Creates state"]
    
    Orch -->|Creates State| State["📦 Shared State<br/>requirement: '....'<br/>agent_votes: []"]
    
    State -->|Read state| DB["💾 Database Agent<br/>Reads requirement<br/>Generates design<br/>Casts vote"]
    State -->|Read state| BE["🔧 Backend Agent<br/>Reads req + DB design<br/>Generates code<br/>Casts vote"]
    State -->|Read state| FE["🎨 Frontend Agent<br/>Reads req + APIs<br/>Generates components<br/>Casts vote"]
    State -->|Read state| SEC["🔒 Security Agent<br/>Reads all code<br/>Audits<br/>Casts vote"]
    
    DB -->|Write vote| State
    BE -->|Write vote| State
    FE -->|Write vote| State
    SEC -->|Write vote| State
    
    State -->|All votes in| Vote["🗳️ Voting System<br/>Tally votes<br/>Determine outcome"]
    
    Vote -->|Decision result| Final["📄 Final Output<br/>Code + Votes<br/>Log + Decision"]
    
    Final -->|Return to user| User
    
    style User fill:#e1f5ff
    style Orch fill:#ff9800
    style State fill:#f3e5f5
    style DB fill:#2196f3
    style BE fill:#2196f3
    style FE fill:#2196f3
    style SEC fill:#f44336
    style Vote fill:#9c27b0
    style Final fill:#4caf50
```

---

## Diagram 8: Week 1-3 Progression

Simple agent evolution.

```mermaid
graph LR
    W1["⏰ Week 1<br/>Single Agent<br/>Tool Calling<br/>4 Tools"]
    
    W2["⏰ Week 2<br/>Multi-Tool Agent<br/>Persistent Memory<br/>6+ Tools"]
    
    W3["⏰ Week 3<br/>Error Handling<br/>Self-Correction<br/>Logging"]
    
    W1 -->|Add memory| W2
    W2 -->|Add robustness| W3
    
    W1 -.->|Concepts| C1["✓ Tool Calling<br/>✓ Agent Loop<br/>✓ Conversation Memory"]
    W2 -.->|Concepts| C2["✓ Persistent Storage<br/>✓ Validation<br/>✓ Search/Filter"]
    W3 -.->|Concepts| C3["✓ Error Recovery<br/>✓ Self-Correction<br/>✓ Decision Tracing"]
    
    style W1 fill:#2196f3
    style W2 fill:#2196f3
    style W3 fill:#2196f3
    style C1 fill:#e3f2fd
    style C2 fill:#e3f2fd
    style C3 fill:#e3f2fd
```

---

## Diagram 9: Week 4-9 Framework Comparison

CrewAI vs LangGraph comparison.

```mermaid
graph TB
    W4["⏰ Week 4: CrewAI<br/>Role-based agents<br/>Task dependencies<br/>Agent collaboration"]
    
    W5["⏰ Week 5: CrewAI Conflicts<br/>Task depends_on<br/>Conflict detection<br/>Agent opinions"]
    
    W6["⏰ Week 6: LangGraph<br/>State graphs<br/>Node/edge model<br/>Conditional routing"]
    
    W7["⏰ Week 7: Voting<br/>Vote aggregation<br/>Weighted votes<br/>Human override"]
    
    W8_9["⏰ Week 8-9: Integration<br/>Full voting + graph<br/>Parallel execution<br/>Conflict resolution"]
    
    W4 -->|Simple start| W5
    W5 -->|More control needed| W6
    W6 -->|Add voting| W7
    W7 -->|Full integration| W8_9
    
    W4 -->|CrewAI pros| P1["✓ Easier to learn<br/>✓ Role clarity<br/>✓ Task management"]
    W6 -->|LangGraph pros| P2["✓ Fine-grained control<br/>✓ Flexible routing<br/>✓ State management"]
    W8_9 -->|Combined| P3["✓ Best of both<br/>✓ Production-ready<br/>✓ Conflict handling"]
    
    style W4 fill:#4caf50
    style W5 fill:#4caf50
    style W6 fill:#2196f3
    style W7 fill:#9c27b0
    style W8_9 fill:#ff9800
    style P1 fill:#e8f5e9
    style P2 fill:#e3f2fd
    style P3 fill:#fff3e0
```

---

## Diagram 10: Complete System End-to-End

Full workflow from requirement to output.

```mermaid
graph TD
    A["👤 Developer Request<br/>'Build a task<br/>management system'"]
    
    B["🎯 Orchestrator parses<br/>requirement"]
    
    C["📋 Decomposes into<br/>5 subtasks"]
    
    D["💾 Database Agent<br/>→ Schema"]
    E["🔧 Backend Agent<br/>→ API Code<br/>(waits for D)"]
    F["🎨 Frontend Agent<br/>→ Components<br/>(waits for E)"]
    
    G["🔒 Security Audit<br/>→ Vulnerabilities"]
    H["✅ QA Testing<br/>→ Test Suite"]
    
    I["Collect votes<br/>D: ✓ APPROVE<br/>E: ✓ APPROVE<br/>F: ✓ APPROVE<br/>G: ✗ REJECT (auth missing)<br/>H: ✓ APPROVE"]
    
    J["Tally votes<br/>Approve: 4.0x<br/>Reject: 2.0x"]
    
    K["Outcome: TIE"]
    
    L["🟡 Escalate to human"]
    
    M["👨‍⚖️ Human reviews"]
    
    N["Decision: Add<br/>authentication"]
    
    O["📄 Final Output<br/>✓ Database schema<br/>✓ Backend code<br/>✓ Frontend code<br/>✓ Security audit<br/>✓ Test suite<br/>✓ Decision log"]
    
    A --> B --> C
    C --> D
    C --> E
    C --> F
    C --> G
    C --> H
    
    D --> I
    E --> I
    F --> I
    G --> I
    H --> I
    
    I --> J --> K --> L --> M --> N --> O
    
    style A fill:#e1f5ff
    style B fill:#ff9800
    style C fill:#ff9800
    style D fill:#2196f3
    style E fill:#2196f3
    style F fill:#2196f3
    style G fill:#f44336
    style H fill:#4caf50
    style I fill:#9c27b0
    style J fill:#9c27b0
    style K fill:#ffc107
    style L fill:#f44336
    style M fill:#ffc107
    style N fill:#8bc34a
    style O fill:#4caf50
```

---

## Diagram 11: Human Review Decision Panel

What the human sees when making a decision.

```mermaid
graph TD
    A["🔴 CONFLICT DETECTED"]
    
    B["Show Agent Votes:<br/>━━━━━━━━━━━━━━━━"]
    B1["✓ Database: APPROVE<br/>reasoning: 'Schema normalized'<br/>weight: 1.5x"]
    B2["✗ Backend: REJECT<br/>reasoning: 'Performance issue'<br/>weight: 1.0x"]
    B3["✗ QA: REJECT<br/>reasoning: 'No tests'<br/>weight: 1.5x"]
    
    C["Weighted Tally:<br/>━━━━━━━━━━━━━━━━<br/>Approve: 1.5x (25%)<br/>Reject: 2.5x (75%)"]
    
    D["Recommendation:<br/>REJECT"]
    
    E["Human Options:<br/>━━━━━━━━━━━━━━━━<br/>[A] Accept REJECT<br/>[B] Override to APPROVE<br/>[M] Modify weights<br/>[S] Show details"]
    
    B --> B1
    B --> B2
    B --> B3
    B1 --> C
    B2 --> C
    B3 --> C
    C --> D --> E
    
    E -->|[A]| F["✅ Proceed with<br/>system recommendation"]
    E -->|[B]| G["⚠️ Override system<br/>Accept risk?"]
    E -->|[M]| H["Adjust weights<br/>Re-tally votes"]
    
    F --> I["📋 Log decision<br/>who: human<br/>action: accept<br/>reasoning: logged"]
    G --> I
    H --> I
    
    I --> J["Execute Final<br/>Decision"]
    
    style A fill:#f44336
    style B fill:#fff3e0
    style B1 fill:#e8f5e9
    style B2 fill:#ffebee
    style B3 fill:#ffebee
    style C fill:#e3f2fd
    style D fill:#ffebee
    style E fill:#fff3e0
    style F fill:#e8f5e9
    style G fill:#ffe0b2
    style H fill:#f3e5f5
    style I fill:#e3f2fd
    style J fill:#4caf50
```

---

## Diagram 12: Voting Result Outcomes

All possible voting outcomes and what they mean.

```mermaid
graph TD
    A["Voting Results<br/>(After tallying)"]
    
    A --> B{Result Type}
    
    B -->|All Approve<br/>or<br/>All Reject| C["⚪ UNANIMOUS<br/>AUTO-EXECUTE<br/>No human needed<br/>High confidence"]
    
    B -->|Clear Winner<br/>70%+ majority| D["🟢 STRONG<br/>EXECUTE<br/>Human can override<br/>Low escalation risk"]
    
    B -->|Close Vote<br/>60-40| E["🟡 WEAK<br/>MARGINAL<br/>Human review<br/>Consider override"]
    
    B -->|50-50 Split| F["🔴 TIE<br/>CONFLICT<br/>MUST escalate<br/>Human decides"]
    
    B -->|Any Veto<br/>Security blocks| G["🔴 VETO<br/>BLOCKED<br/>MUST escalate<br/>Risk acknowledgment"]
    
    C -->|Log| L1["📋 Unanimous decision<br/>Agents: X,Y,Z"]
    D -->|Log| L2["📋 Majority decision<br/>Agents: X,Y beat Z"]
    E -->|Log| L3["📋 Marginal decision<br/>Needs review<br/>Agents: X vs Y"]
    F -->|Log| L4["📋 Tie decision<br/>Human chose: X<br/>Agents: Y vs Z"]
    G -->|Log| L5["📋 Veto decision<br/>Risk: acknowledged<br/>Agent: Security"]
    
    L1 --> K["✅ EXECUTE"]
    L2 --> K
    L3 --> K
    L4 --> K
    L5 --> K
    
    style A fill:#e1f5ff
    style B fill:#ff9800
    style C fill:#4caf50
    style D fill:#8bc34a
    style E fill:#ffc107
    style F fill:#f44336
    style G fill:#d32f2f
    style K fill:#1b5e20
```

---

## How to Use These Diagrams

### Option 1: View in GitHub
If these files are on GitHub, the diagrams render automatically.

### Option 2: Mermaid Live Editor
1. Visit: https://mermaid.live
2. Copy a diagram (the code block)
3. Paste into the editor
4. Edit/modify as needed

### Option 3: VS Code
1. Install "Mermaid" extension
2. Open `.md` file with diagram
3. Preview renders automatically

### Option 4: Generate Images
```bash
# Using mmdc (Mermaid CLI)
npm install -g @mermaid-js/mermaid-cli

# Convert to PNG
mmdc -i architecture.md -o architecture.png

# Or use online: https://kroki.io (accepts Mermaid)
```

---

## Customizing Diagrams

### Change colors
Find the `style` lines and modify:
```
style NodeName fill:#ff9800  ← Orange
style NodeName fill:#2196f3  ← Blue
style NodeName fill:#4caf50  ← Green
style NodeName fill:#f44336  ← Red
style NodeName fill:#9c27b0  ← Purple
style NodeName fill:#ffc107  ← Yellow
```

### Add/remove nodes
1. Find the node in the diagram code
2. Modify the label or add new nodes
3. Adjust arrows (→) to connect new nodes

### Change flow direction
```
graph LR   ← Left to Right (current)
graph TD   ← Top to Down
graph BT   ← Bottom to Top
graph RL   ← Right to Left
```

---

## References

- **Mermaid Documentation**: https://mermaid.js.org/
- **Flowchart Syntax**: https://mermaid.js.org/syntax/flowchart.html
- **Graph Styling**: https://mermaid.js.org/syntax/flowchart.html#styling-and-classes

---

**Tip:** Copy these diagrams into your documentation, presentations, and study materials. Modify them to match your implementation!
