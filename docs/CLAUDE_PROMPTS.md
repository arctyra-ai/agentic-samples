# Claude Prompts for Training Program Expansion

Use these prompts with Claude Opus 4.5 to generate additional learning materials, examples, and customizations.

---

## Prompt 1: Video Lesson Recaps

**Use When:** You've watched course videos and want Claude to summarize them

**Prompt:**

```
I'm taking the "The Complete Agentic AI Engineering Course" on Udemy (Week 4: CrewAI Module).
The module covers:
- Agent definition with roles and backstory
- Task definition with dependencies
- Crew orchestration
- Agent communication patterns

Create a comprehensive summary including:
1. Key concepts (5-7 main ideas)
2. Code examples showing each concept
3. Common mistakes beginners make
4. 3 practice exercises to test understanding
5. Prerequisites from prior weeks
6. How this connects to LangGraph (Week 6)

Format as: Markdown file ready to study from
```

---

## Prompt 2: Additional Coding Exercises

**Use When:** You want more practice beyond the weekly templates

**Prompt:**

```
Create 3 additional coding exercises for Week {X} of the Agentic AI Training Program:

**Context:**
- Week {X} focus: {describe the week's focus}
- Difficulty: {Beginner/Intermediate/Advanced}
- Time per exercise: 30-60 minutes
- Prior weeks completed: {list them}

**Requirements:**
1. Exercise 1: {specific skill to practice}
   - Provide skeleton code
   - Include hints
   - Show expected output
   - Solution with explanation

2. Exercise 2: {different skill}
   - Slightly harder than Exercise 1
   - Builds on Week {X} concepts
   - Includes edge cases

3. Exercise 3: {challenging variation}
   - Combines multiple concepts
   - Real-world scenario
   - Optional: difficulty mode

Format: Python code files with detailed comments
```

---

## Prompt 3: Error Troubleshooting Guide

**Use When:** You encounter an error not covered in the main document

**Prompt:**

```
Create a comprehensive troubleshooting guide for common errors in Week {X} (Topic: {topic}).

Include:
1. "ModuleNotFoundError: No module named '{module}'"
   - Root cause
   - Step-by-step fix
   - Prevention tips

2. "{Specific API Error}" (e.g., "Invalid API key")
   - What causes this
   - How to diagnose
   - Multiple solutions
   - Verification steps

3. "{Logic Error}" (e.g., "Graph doesn't compile")
   - Common misconceptions
   - How to debug
   - Print statements to add
   - When to use LangSmith

4. "{Runtime Error}" (e.g., "Agent doesn't call tools")
   - Symptoms
   - Investigation steps
   - Code snippets to check
   - Solution variations

5. "{Integration Error}" (e.g., "Voting doesn't aggregate correctly")
   - Dependency checks
   - State validation
   - Unit test for diagnosis

Format: Markdown with code examples, not plain text
```

---

## Prompt 4: Alternative Implementation Approaches

**Use When:** You want to understand different ways to build the same thing

**Prompt:**

```
For Week {X} (Topic: {topic}), show 3 alternative implementations:

**Current Approach** (from training program):
{paste relevant code snippet}

**Alternative 1: {Name}**
- Pros vs current approach
- Cons vs current approach
- When to use this instead
- Complete code example
- Migration path if switching

**Alternative 2: {Name}**
- Different architecture pattern
- Trade-offs
- Performance implications
- Full implementation
- Comparison table

**Alternative 3: {Name}**
- Third-party library approach
- Setup/config required
- Advantages/disadvantages
- Code example
- When this is better

For each alternative:
- Provide production-ready code
- Include error handling
- Add comments explaining why this way
- Show how to test it
- Link to official docs
```

---

## Prompt 5: Weekly Quiz & Assessment

**Use When:** You want to test your understanding

**Prompt:**

```
Create a comprehensive quiz for Week {X} of the Agentic AI Training Program.

**Quiz Structure:**

Part 1: Conceptual (5 questions)
- Multiple choice
- Focus on understanding, not memorization
- Include common misconceptions as wrong answers
- Difficulty: Basic

Part 2: Application (4 questions)
- Given a scenario, what code would you write?
- "What's wrong with this code?" style
- Focus on practical skills
- Difficulty: Intermediate

Part 3: Deep Dive (3 questions)
- Design/architecture questions
- "How would you extend this?"
- Difficulty: Advanced

**Format:**
- Questions with clear answers
- Explanations for each answer (why correct, why others wrong)
- Links to relevant training materials
- Score: 0-12 points (80% = pass)
- Bonus challenge question worth 2 points

Include answer key with detailed explanations.
```

---

## Prompt 6: Real-World Project Ideas

**Use When:** You want to apply skills to your own project

**Prompt:**

```
Suggest 5 real-world project ideas where I can apply Week {X} concepts:

**Context:**
- My background: {your background}
- My industry: {your industry}
- Available tools: {tools you have access to}
- Time constraint: {how much time you have}
- Learning goal: {what you want to get out of it}

For each project:
1. **Project name & description**
   - What problem it solves
   - How it uses Week {X} concepts

2. **Implementation roadmap**
   - Step 1: Set up (time)
   - Step 2: Build core feature (time)
   - Step 3: Add complexity (time)
   - Step 4: Deploy/test (time)

3. **Learning outcomes**
   - What you'll learn
   - Skills practiced
   - Challenges you'll face

4. **Code skeleton**
   - File structure
   - Key functions needed
   - Integration points

5. **Extension ideas**
   - How to make it more advanced
   - Scalability considerations
   - Production readiness steps

Rank projects by difficulty (Easy → Hard)
```

---

## Prompt 7: Custom Domain Adaptation

**Use When:** You want to apply training to your specific industry

**Prompt:**

```
Adapt the Agentic AI training program to the {your domain} domain.

**Your Domain Specifics:**
- Industry: {industry}
- Typical workflows: {describe 2-3}
- Key challenges: {what makes this domain hard}
- Constraints: {limitations unique to your domain}
- Tools/systems in use: {what you work with}

**Adaptation Needed:**

1. **Domain-specific agents** (replace generic task/storage/validator)
   - Agent 1: {role specific to your domain}
   - Agent 2: {role specific to your domain}
   - Agent 3: {role specific to your domain}
   - Define responsibilities for each

2. **Custom state schema**
   - What data flows through your agents?
   - What fields are domain-specific?
   - Show TypedDict definition

3. **Realistic project example**
   - Real problem from your domain
   - How agents would solve it
   - Step-by-step workflow
   - Expected challenges

4. **Conflict scenarios for your domain**
   - What would agents disagree on?
   - How would voting work?
   - Real examples from your industry

5. **Integration points**
   - Existing systems to connect
   - Data sources to tap
   - Outputs needed

Provide complete code examples using your domain's terminology and workflows.
```

---

## Prompt 8: Performance Optimization

**Use When:** Your system is too slow or using too many tokens

**Prompt:**

```
Optimize my agentic AI system for performance and cost.

**Current State:**
```python
{paste your system code}
```

**Current Performance:**
- API calls per request: {X}
- Average tokens per request: {X}
- Latency: {X}ms
- Cost per 100 requests: ${X}

**Bottlenecks:**
- Agent 1 is slow because: {reason}
- Agent 2 uses too many tokens because: {reason}
- Overall issue: {describe the problem}

**Constraints:**
- Must maintain quality/accuracy
- Can't remove agents
- Need to stay under {X} ms latency
- Must reduce costs by {X}%

**Provide:**
1. Root cause analysis (which agents are expensive?)
2. 3 optimization strategies ranked by impact
3. Complete optimized code for bottleneck agents
4. Caching strategy (where and how)
5. Batch processing opportunities
6. Token reduction techniques
7. Performance benchmarks before/after
8. Trade-offs of each optimization
```

---

## Prompt 9: Production Deployment Guide

**Use When:** You're ready to deploy to production

**Prompt:**

```
Create a production deployment guide for the software dev agent system.

**Deployment Target:** {Where will it run?}
- Cloud platform: {AWS/GCP/Azure/other}
- Container: {Docker/Kubernetes/serverless}
- Scale: {Expected requests/day}

**Production Requirements:**
1. **Monitoring & Observability**
   - What metrics to track?
   - Logging strategy
   - Error alerting
   - Performance dashboards

2. **Reliability & Fault Tolerance**
   - Agent failure handling
   - Retry strategies
   - Circuit breakers
   - Fallback agents

3. **Security**
   - API key management
   - Rate limiting
   - Input validation
   - Output sanitization

4. **Scalability**
   - Horizontal scaling approach
   - Load balancing
   - Database considerations
   - Caching strategy

5. **Cost Optimization**
   - Token budgets per agent
   - API provider comparison
   - Cost monitoring

**Provide:**
- Architecture diagram (text-based)
- Deployment checklist
- Configuration files (docker-compose.yml, etc.)
- Monitoring/alerting setup
- Cost calculator
- Runbooks for common issues
```

---

## Prompt 10: Testing & Quality Assurance

**Use When:** You want comprehensive test coverage

**Prompt:**

```
Create a complete testing strategy for the agentic AI system.

**Current System:**
```python
{paste your system code}
```

**Provide:**

1. **Unit Tests** (test individual agents)
   - Test agent 1: {agent name}
   - Test agent 2: {agent name}
   - etc.
   - Each test file with 3-5 test cases
   - Mock external dependencies

2. **Integration Tests** (test agent interactions)
   - Agent coordination tests
   - Dependency enforcement tests
   - State propagation tests
   - Edge case tests

3. **Scenario Tests** (real-world workflows)
   - Scenario 1: Simple case (no conflicts)
   - Scenario 2: Complex case (multi-dependency)
   - Scenario 3: Conflict scenario
   - Scenario 4: Agent failure
   - Scenario 5: Edge case

4. **Load Tests** (performance under stress)
   - How many requests/second?
   - Token usage at scale?
   - Latency distribution?

5. **Quality Metrics**
   - Code coverage target: 80%+
   - Agent accuracy metrics
   - Voting correctness validation
   - Human review quality checks

**Format:**
- pytest-based test files
- Test fixtures and mocks
- CI/CD integration instructions
- Coverage reports
- Performance baselines
```

---

## Prompt 11: Cost Analysis & Token Budgeting

**Use When:** You want to control API spending

**Prompt:**

```
Analyze costs and create token budgets for my agentic system.

**System Architecture:**
- Number of agents: {X}
- Average request complexity: {simple/medium/complex}
- Expected monthly requests: {X}
- LLM provider: {OpenAI/Anthropic/other}
- Model used: {GPT-4/Claude-3/other}

**Provide:**

1. **Cost Breakdown**
   - Cost per agent per request
   - Overhead costs (routing, voting, etc.)
   - Cost per conflict resolution
   - Human review costs

2. **Token Budget Plan**
   - System prompt tokens per agent
   - Average response tokens per agent
   - Optional: streaming to reduce latency
   - Caching opportunities

3. **Cost Optimization**
   - Which agents use most tokens?
   - Can we use cheaper models for some agents?
   - Batch processing opportunities?
   - Rate limiting strategy?

4. **Price Comparison**
   - GPT-4 vs Claude-3 vs open-source
   - Cost per 1000 requests
   - ROI analysis

5. **Monitoring Dashboard**
   - Metrics to track daily
   - Alerts if budget exceeded
   - Monthly cost forecasting

**Output:**
- Cost spreadsheet (CSV)
- Token budget per agent
- Recommendations for cost reduction
- Break-even analysis if this is paid service
```

---

## Prompt 12: Custom Conflict Resolution Rules

**Use When:** Your domain has specific conflict rules

**Prompt:**

```
Design custom conflict resolution rules for {your domain}.

**Your Domain:** {domain}
**Agents in your system:** {list agents}

**Conflict Rules to Design:**

1. **Weighted Voting**
   - Agent 1 weight: X.Xx
   - Agent 2 weight: X.Xx
   - etc.
   - Justification for each weight

2. **Veto Authority**
   - Which agents can veto? {agents}
   - Under what conditions? {conditions}
   - How to escalate after veto?

3. **Tie Resolution**
   - What counts as tie? (e.g., 50/50 split)
   - Who decides in case of tie? (human/orchestrator/majority)
   - Escalation path?

4. **Special Scenarios**
   - Critical decisions (always human review?)
   - Risky decisions (veto by safety agent?)
   - Time-sensitive decisions (auto-approve if time-limited?)

5. **Appeals Process**
   - Can human change decision?
   - How to re-vote with new information?
   - Learning for future similar decisions?

**Provide:**
- Decision tree (ASCII or text-based)
- Pseudocode for voting logic
- Example scenarios with resolution
- Testing matrix (all vote combinations)
- Documentation for stakeholders
```

---

## Prompt 13: Feature Requests & Extensions

**Use When:** You want to add features to the basic system

**Prompt:**

```
Design and implement {feature name} for the agentic system.

**Feature Description:** {What you want to add}

**Integration Requirements:**
- Which agents does this affect? {list}
- New state fields needed? {describe}
- New nodes required? {describe}
- Changes to voting logic? {describe}

**Provide:**

1. **Architecture Design**
   - How does feature fit into current system?
   - Dependencies and interactions
   - Data flow diagram (text)

2. **Implementation**
   - Code to add to existing agents
   - New nodes/functions needed
   - Configuration changes
   - Database schema changes (if any)

3. **Testing**
   - Unit tests for new logic
   - Integration tests with existing agents
   - Edge case tests
   - Performance impact

4. **Documentation**
   - User guide for feature
   - Admin configuration guide
   - Troubleshooting section

5. **Deployment**
   - Migration plan from v1 to v2
   - Backward compatibility
   - Rollback procedure

**Examples of features:**
- Persistent decision logging
- Agent performance metrics
- Historical decision learning
- Multi-round voting
- Budget constraints
- Real-time monitoring dashboard
```

---

## Prompt 14: Hands-On Tutorial Generation

**Use When:** You want step-by-step tutorials for complex topics

**Prompt:**

```
Create a detailed, hands-on tutorial for {topic} in the context of agentic AI.

**Tutorial Specification:**

1. **Topic:** {What to teach}
   - Prerequisite knowledge: {what they should know first}
   - Time estimate: {X hours}
   - Difficulty: {Beginner/Intermediate/Advanced}

2. **Learning Format**
   - Interactive code-along tutorial
   - Run this command → See this result
   - Common mistakes & how to fix them
   - "Why" explanations for each step

3. **Tutorial Sections**
   - Part 1: {Concept introduction}
   - Part 2: {Build basic version}
   - Part 3: {Add complexity}
   - Part 4: {Edge cases & robustness}
   - Part 5: {Real-world application}

4. **For Each Section**
   - Clear learning objective
   - Code you should write (not copy-paste)
   - Expected output (with screenshots as text)
   - Common mistakes
   - Quick check: "Can you explain why this works?"

5. **Included Artifacts**
   - Complete runnable code files
   - test files to verify learning
   - Troubleshooting checklist
   - Further reading links

**Output format:** Markdown with code blocks, suitable for self-paced learning
```

---

## How to Use These Prompts

### Step 1: Copy the prompt
Select a prompt above that matches what you need.

### Step 2: Fill in the blanks
Replace `{placeholders}` with your specific context. Example:

```
Original:
"Create a comprehensive summary for Week {X}: {topic}"

Filled in:
"Create a comprehensive summary for Week 4: CrewAI Multi-Agent Architecture"
```

### Step 3: Submit to Claude
Paste the filled-in prompt into Claude Opus and run it.

### Step 4: Refine if needed
If the output isn't quite right, follow up with:
- "Add more code examples"
- "Make this more beginner-friendly"
- "Focus on the voting mechanism"
- "Include edge cases"

---

## Chaining Prompts for Maximum Effect

**Example workflow: Generate complete Week 4 materials**

```
Prompt 1: "Video Lesson Recap"
  → Read transcript of Udemy CrewAI module
  → Get key concepts summary

Prompt 2: "Additional Coding Exercises"
  → Get 3 new exercises on CrewAI

Prompt 3: "Error Troubleshooting Guide"
  → Get CrewAI-specific debugging help

Prompt 4: "Quiz & Assessment"
  → Test your understanding of Week 4

Prompt 7: "Custom Domain Adaptation"
  → Adapt CrewAI agents to your domain

Output: Complete Week 4 customized for your needs
```

---

## Tips for Best Results

1. **Be Specific**
   - Instead of: "Explain agents"
   - Use: "Explain how task dependencies work in CrewAI agents"

2. **Provide Context**
   - Tell Claude what you've already learned
   - Mention your experience level
   - Describe your use case

3. **Ask for Specifics**
   - "Include error messages and fixes"
   - "Show 3 complete code examples"
   - "Format as a reference card"

4. **Request Output Format**
   - "Format as Markdown file"
   - "Include Python code blocks"
   - "Add a comparison table"
   - "Make it printable"

5. **Iterate**
   - First prompt gets 80% there
   - Follow-ups refine to 100%
   - "Expand the X section"
   - "Make this more advanced"

---

## Templates for Common Follow-Up Requests

### "I don't understand X"
```
I'm stuck on {topic} from {section}.

Here's what I understand:
{describe what makes sense}

Here's what confuses me:
{describe the confusion}

Can you:
1. Explain {topic} in simpler terms
2. Show a concrete example
3. Explain why it works this way
4. Show what happens if I do it wrong
```

### "I want to modify X"
```
In Week {week}, the {agent/node/function} does {current behavior}.

I want to change it to {desired behavior}.

Current code:
```python
{paste relevant code}
```

Questions:
1. What changes are needed?
2. What could break?
3. How do I test the changes?
4. Full working code example?
```

### "Show me an alternative"
```
The training shows one way to implement {feature}.
Can you show me:
1. A simpler version (for beginners)
2. A more complex version (for production)
3. A version using {library}
4. Performance comparison of all three

Code examples for each, with pros/cons?
```

---

## Next Steps

1. **Pick one prompt** from above that matches your current need
2. **Fill in the blanks** with your specific context
3. **Run it with Claude** (Opus 4.5 recommended)
4. **Use the output** as a study material or reference
5. **Share back** useful outputs with study partners

---

**Last Updated:** February 2026
**Version:** 1.0

**Questions or want to add more prompts?** The prompt template is simple - you can create your own by following the pattern: [Context] + [Task] + [Output Format]
