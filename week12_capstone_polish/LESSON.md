# Week 12 Lesson: Capstone Polish

## What You Are Building

This week you complete, test, document, and prepare your capstone project for presentation. The deliverable is a portfolio-ready system that you can demonstrate in a job interview, link from a resume, or use as a reference implementation for future projects.

The difference between a capstone that demonstrates competence and one that does not is in the details: does it handle edge cases? Are the tests meaningful? Does the documentation explain the design decisions, not just the setup steps? Can you walk someone through the architecture in 5 minutes and answer questions about tradeoffs?

## Core Concepts

### Testing Strategy for Agent Systems

Agent systems are non-deterministic. The same input can produce different outputs on different runs. Your testing strategy must account for this.

**Deterministic tests (always pass or fail consistently):**
- State schema validation
- Routing logic (given this state, which node runs next?)
- Voting tallies (given these votes, what is the outcome?)
- Cost tracking arithmetic
- Input validation

These are the tests from Weeks 1-9. They test your code, not the LLM's behavior.

**Statistical tests (pass rate over multiple runs):**
- Does the RAG agent find the right documents?
- Do the review agents detect known vulnerabilities?
- Does the synthesizer identify contradictions?

These use the evaluation pipeline from Week 9. The target is not 100% -- it is a specific accuracy threshold (e.g., 80%) that you measure and report. State the threshold in your documentation and explain why you chose it.

**You need at least 20 tests total.** A reasonable split: 15 deterministic + 5 evaluation cases.

### Documentation That Demonstrates Understanding

The README is not just setup instructions. It is evidence that you understand what you built and why. Interviewers read READMEs.

Structure:
1. **What the system does** (2-3 sentences, no jargon)
2. **Architecture diagram** (Mermaid or image)
3. **Design decisions** (why 4 agents and not 2? Why this voting weight? Why this RAG chunking strategy?)
4. **Setup and usage** (step-by-step, tested on a clean checkout)
5. **Evaluation results** (accuracy, cost per request, latency)
6. **Known limitations** (what does the system not handle well?)

The design decisions section is the most important. It shows that you made intentional choices and can articulate tradeoffs. "I gave the security agent 2x voting weight because false negatives on security are more costly than false positives on style" demonstrates engineering judgment.

### The 5-Minute Demo

Prepare a demo script that walks through:

**Minute 1: Problem and solution.** "This system solves [problem] by coordinating [N] agents. A user provides [input] and gets [output]."

**Minute 2: Architecture.** Walk through the LangGraph flow. Name the agents and their roles. Show the graph structure.

**Minute 3: Live run.** Execute the system on a prepared input. Show the output. Point out: which agents contributed what, how voting resolved a conflict, and what the RAG component retrieved.

**Minute 4: Design decisions.** Pick 2-3 decisions and explain the tradeoff. "I chose X over Y because Z."

**Minute 5: Evaluation and production readiness.** State the accuracy score, cost per request, and what you would add for production (monitoring, auth, rate limiting).

Practice this. A 5-minute demo that is clear and confident leaves a stronger impression than 30 minutes of rambling exploration.

### Cost Report

Document your total API spend for development and testing, then estimate production costs:

```
Development: $X.XX over Y API calls
Evaluation: $X.XX over Z test cases
Estimated production: $X.XX per request × N requests/month = $X.XX/month
```

Include which model you used and why. "I used Claude Sonnet for all agents ($0.15/review) instead of Opus ($1.20/review) because the accuracy difference was less than 3% on my evaluation set" is the kind of cost-conscious reasoning employers look for.

### Git History

Clean your commit history before calling the project done. Meaningful commits like "Add security agent with SQL injection detection" tell a story. Commits like "fix" or "wip" or "asdf" do not.

If your history is messy, use interactive rebase to squash and rename:
```bash
git rebase -i HEAD~20  # Review last 20 commits
```

This is not cosmetic. Interviewers look at commit history to understand how you work.

## Final Checklist

Open `final_checklist.md` for the complete list. The critical items:

- System runs end-to-end without errors
- 4+ agents with distinct roles
- MCP integration working
- LangGraph orchestration with conditional routing
- Voting/conflict resolution implemented
- RAG component functional
- Evaluation pipeline with metrics
- Cost tracking accurate
- 20+ tests passing
- README complete with architecture diagram
- Can explain every design decision

## Now Finish It

This week is execution, not learning. You have all the skills. Use `final_checklist.md` as your task list. Work through it top to bottom. When every item is checked, you have a portfolio-ready project.
