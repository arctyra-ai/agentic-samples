# Progress Tracker

Check off items as you complete them. Use this to track your progress through the curriculum.

---

## Phase 1: Foundations (Weeks 1-3)

### Week 1: Agent Fundamentals
- [ ] Read `week01_agent_fundamentals/README.md`
- [ ] Understand the agent loop pattern (perceive, reason, act, observe)
- [ ] Copy `agent_starter.py` to `agent.py` and implement all TODOs
- [ ] All 5 tools implemented and returning correct JSON
- [ ] Agent loop handles multi-turn conversations
- [ ] Max iterations safety limit working
- [ ] `pytest test_agent.py -v -k "not Integration"` -- all tests pass
- [ ] Run agent interactively with 5+ different requests
- [ ] Cost per interaction under $0.05
- [ ] Code committed to git

### Week 2: Tool Use Deep Dive
- [ ] Read `week02_tool_use_deep_dive/README.md`
- [ ] Copy `research_agent_starter.py` to `research_agent.py` and implement all TODOs
- [ ] 6 tools defined with descriptions specific enough for correct selection
- [ ] Tool chaining works (search -> read -> extract -> compare -> outline -> write)
- [ ] Pydantic ResearchReport validates correctly
- [ ] Session persistence works (state survives restart)
- [ ] `pytest test_research.py -v` -- all tests pass
- [ ] Code committed to git

### Week 3: MCP Foundations
- [ ] Read `week03_mcp_foundations/README.md`
- [ ] Understand MCP architecture (client, server, transport)
- [ ] Copy `mcp_agent_starter.py` to `mcp_agent.py` and implement all TODOs
- [ ] Mock router provides tools from 2 servers
- [ ] Agent discovers tools dynamically (no hardcoded tool names)
- [ ] Adding/removing a server changes available tools with zero code changes
- [ ] `pytest test_mcp.py -v` -- all tests pass
- [ ] Code committed to git

**Phase 1 checkpoint:** Can you explain the agent loop, tool calling, and MCP architecture to someone unfamiliar? If yes, proceed to Phase 2.

---

## Phase 2: Real Integrations (Weeks 4-6)

### Week 4: RAG Agents
- [ ] Read `week04_rag_agents/README.md`
- [ ] Copy `rag_agent_starter.py` to `rag_agent.py` and implement all TODOs
- [ ] Chunking works with configurable size and overlap
- [ ] ChromaDB index built from `docs/` directory (5 sample files)
- [ ] RAG query returns answers with source citations
- [ ] Agent says "insufficient context" when appropriate
- [ ] Evaluation pipeline runs against EVAL_CASES
- [ ] Accuracy target: 80%+ on eval cases
- [ ] `pytest test_rag.py -v` -- all tests pass
- [ ] Code committed to git

### Week 5: Custom MCP Servers
- [ ] Read `week05_custom_mcp_servers/README.md`
- [ ] Copy `project_mcp_server_starter.py` to `project_mcp_server.py` and implement all TODOs
- [ ] SQLite tables created correctly
- [ ] All 6 tools implemented with input validation
- [ ] Errors return structured JSON (not crashes)
- [ ] Data persists across server restarts
- [ ] `pytest test_mcp_server.py -v` -- all tests pass
- [ ] Code committed to git

### Week 6: LangGraph Orchestration
- [ ] Read `week06_langgraph_orchestration/README.md`
- [ ] Copy `document_pipeline_starter.py` to `document_pipeline.py` and implement all TODOs
- [ ] StateGraph with 6 nodes compiles successfully
- [ ] Conditional routing works (unknown -> error, valid -> extract)
- [ ] classify and extract nodes make real LLM calls
- [ ] Checkpointing enabled with MemorySaver
- [ ] Pipeline processes all 3 sample document types correctly
- [ ] `pytest test_pipeline.py -v` -- all tests pass
- [ ] Optional: LangSmith tracing configured and showing traces
- [ ] Code committed to git

**Phase 2 checkpoint:** Can you build a RAG pipeline, create a custom MCP server, and orchestrate a multi-step workflow with LangGraph? If yes, proceed to Phase 3.

---

## Phase 3: Multi-Agent Systems (Weeks 7-9)

### Week 7: Multi-Agent Coordination
- [ ] Read `week07_multi_agent_systems/README.md`
- [ ] Copy `code_review_agents_starter.py` to `code_review_agents.py` and implement all TODOs
- [ ] 3 specialist agents produce independent findings
- [ ] Agents run in parallel via LangGraph
- [ ] Synthesizer combines findings and identifies contradictions
- [ ] Token usage tracked across all agents
- [ ] Total cost per review under $0.50
- [ ] `pytest test_review.py -v` -- all tests pass
- [ ] Code committed to git

### Week 8: Voting and Conflict Resolution
- [ ] Read `week08_voting_and_conflicts/README.md`
- [ ] Copy `voting_starter.py` to `voting.py` and implement all TODOs
- [ ] Weighted voting tallies correctly
- [ ] Security BLOCK (weight >= 2.0) always triggers human review
- [ ] Ties trigger human review
- [ ] Low confidence triggers human review
- [ ] HumanReviewPanel works in both auto and interactive modes
- [ ] Decision log is complete JSON
- [ ] `pytest test_voting.py -v` -- all tests pass
- [ ] Code committed to git

### Week 9: Evaluation and Observability
- [ ] Read `week09_evaluation_and_observability/README.md`
- [ ] Copy `evaluation_starter.py` to `evaluation.py` and implement all TODOs
- [ ] CostTracker records costs and enforces budget
- [ ] Ground truth dataset has 5+ cases
- [ ] Evaluation pipeline runs and produces accuracy metrics
- [ ] Budget enforcement stops execution before overspend
- [ ] Metrics report combines eval results + cost data
- [ ] `pytest test_evaluation.py -v` -- all tests pass
- [ ] Code committed to git

**Phase 3 checkpoint:** Can you design a multi-agent system with voting, evaluate it against ground truth, and track costs? If yes, proceed to Phase 4.

---

## Phase 4: Production (Weeks 10-12)

### Week 10: Production Deployment
- [ ] Read `week10_production_deployment/README.md`
- [ ] Streamlit UI runs and accepts file uploads
- [ ] FastAPI endpoint returns valid JSON for all inputs
- [ ] Structured logging with request IDs
- [ ] Graceful degradation if one agent fails
- [ ] Configuration via environment variables
- [ ] Code committed to git

### Week 11: Capstone Build
- [ ] Read `week11_capstone_build/README.md`
- [ ] Capstone project option chosen (A, B, or C)
- [ ] `architecture_template.md` filled in completely
- [ ] Architecture reviewed (by Claude or peer)
- [ ] 4+ agents implemented with distinct roles
- [ ] MCP integration working
- [ ] LangGraph orchestration with conditional routing
- [ ] Voting/conflict resolution integrated
- [ ] RAG component functional
- [ ] Evaluation pipeline with ground truth
- [ ] Cost tracking active
- [ ] UI or CLI working end-to-end
- [ ] Code committed to git

### Week 12: Capstone Polish
- [ ] Read `week12_capstone_polish/README.md`
- [ ] All tests pass (minimum 20)
- [ ] Evaluation shows measurable results
- [ ] README with architecture diagram, setup, usage, design decisions
- [ ] Cost report: development spend + estimated production costs
- [ ] 5-minute demo script written and practiced
- [ ] Clean git history with meaningful commits
- [ ] Can explain every design decision

**Curriculum complete.** Your capstone project is portfolio-ready.

---

## Summary

| Phase | Weeks | Status |
|-------|-------|--------|
| Foundations | 1-3 | [ ] Complete |
| Real Integrations | 4-6 | [ ] Complete |
| Multi-Agent Systems | 7-9 | [ ] Complete |
| Production | 10-12 | [ ] Complete |

**Total API spend:** $_______ (budget: $50)
**Completion date:** ___________
