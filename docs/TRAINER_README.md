# Claude Agentic Trainer System

A multi-agent AI training system that helps you learn agentic AI while building a sophisticated trainer system in parallel.

Uses Claude Opus 4.6 with extended thinking, LangGraph for orchestration, and the Anthropic API.

## 🎯 What This Does

The trainer system consists of **5 specialized agents** that work together:

1. **Curriculum Analyzer** - Reads your training curriculum and extracts learning objectives
2. **Exercise Generator** - Creates 5 progressive exercises for each week
3. **Code Reviewer** - Reviews your solutions and provides technical feedback
4. **Feedback Provider** - Explains concepts and provides personalized guidance
5. **Progress Tracker** - Monitors your learning journey and provides insights

All agents coordinate through **LangGraph** for intelligent task orchestration.

## 📋 What's Included

```
claude-agentic-trainer/
├── agents/
│   ├── curriculum_analyzer.py      # Reads curriculum
│   ├── exercise_generator.py        # Creates exercises
│   ├── code_reviewer.py             # Reviews code
│   ├── feedback_provider.py         # Explains concepts
│   └── progress_tracker.py          # Tracks progress
│
├── orchestrator/
│   ├── graph.py                    # LangGraph orchestration
│   └── state.py                    # State schema
│
├── scripts/
│   ├── run.py                      # Main CLI
│   └── evaluate.py                 # Code evaluation
│
├── requirements.txt
└── README.md (this file)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Key

```bash
echo "ANTHROPIC_API_KEY=your_key_here" > .env
```

Get your key from: https://console.anthropic.com/api-keys

### 3. Run the System

```bash
# Analyze Week 1
python scripts/run.py --week 1 --action analyze

# Generate exercises
python scripts/run.py --week 1 --action generate

# See your progress
python scripts/run.py --action progress

# Review your code
python scripts/evaluate.py --exercise week1_exercise_1 --code ./solution.py
```

## 💡 How It Works

### The Workflow

```
1. ANALYZE WEEK
   └─ CurriculumAnalyzer reads training materials
   └─ Extracts learning objectives and concepts

2. GENERATE EXERCISES
   └─ ExerciseGenerator creates 5 progressive exercises
   └─ Each builds on previous, easy → hard

3. YOU WRITE CODE
   └─ You complete exercises with guidance

4. REVIEW CODE
   └─ CodeReviewer tests and analyzes
   └─ Provides quality assessment

5. GET FEEDBACK
   └─ FeedbackProvider explains concepts
   └─ Provides next steps

6. TRACK PROGRESS
   └─ ProgressTracker monitors journey
   └─ Shows insights and motivation
```

### Running a Full Workflow

```bash
# Complete workflow for Week 1
python scripts/run.py --week 1 --action full
```

This:
1. Analyzes the curriculum
2. Generates 5 exercises
3. Shows your progress

## 📊 Architecture

### State Schema

All agents work with a shared `TrainerState` that flows through the system:

```python
TrainerState {
    # Input
    week: int
    exercise_id: str
    user_code: str
    
    # Curriculum Analysis
    learning_objectives: List[LearningObjective]
    key_concepts: List[str]
    
    # Generated Exercises
    exercises: List[Exercise]
    
    # Review Results
    code_review_result: CodeReviewResult
    
    # Feedback
    feedback_message: FeedbackMessage
    
    # Progress
    progress: ProgressSnapshot
    
    # Logging
    decision_log: List[Dict]
}
```

### LangGraph Orchestration

```
START
  ↓
[Analyze Curriculum] ← Curriculum Analyzer
  ↓
[Generate Exercises] ← Exercise Generator
  ↓
[Review Code] ← Code Reviewer
  ↓
[Provide Feedback] ← Feedback Provider
  ↓
[Track Progress] ← Progress Tracker
  ↓
END
```

## 🎓 Usage Examples

### Example 1: Start Week 1

```bash
python scripts/run.py --week 1 --action analyze
```

**Output:**
```
🎓 Analyzing Week 1 of the curriculum...

✅ Analysis complete!

Learning Objectives:
  • Understand AI agent loops
  • Implement tool calling with Claude
  • Maintain conversation history

Key Concepts (5):
  • Agent loops
  • Tool calling
  • Conversation memory
  • Function definitions
  • Error handling

Estimated Time: 8 hours

Success Criteria:
  ✓ Build working TODO agent
  ✓ Multi-turn conversations work
  ✓ All tools callable correctly
```

### Example 2: Generate Exercises

```bash
python scripts/run.py --week 1 --action generate
```

**Output:**
```
📝 Generating exercises for Week 1...

✅ Generated 5 exercises!

  1. Create a Simple TODO Agent
     Difficulty: BEGINNER | Time: 30 mins
  
  2. Add Multiple Tools to Your Agent
     Difficulty: BEGINNER | Time: 45 mins
  
  3. Implement Conversation Memory
     Difficulty: INTERMEDIATE | Time: 1 hour
  
  4. Error Handling and Recovery
     Difficulty: INTERMEDIATE | Time: 1 hour
  
  5. Challenge: Multi-Turn Conversations
     Difficulty: ADVANCED | Time: 90 mins
```

### Example 3: Review Your Code

```bash
python scripts/evaluate.py --exercise week1_exercise_1 --code ./solution.py
```

**Output:**
```
============================================================
CODE REVIEW: week1_exercise_1
============================================================

✅ Tests: PASS
📊 Quality Score: 8.5/10

⚠️ Issues Found (1):
  [MEDIUM] Line 42: Unhandled exception if tool fails

💡 Improvements:
  • Add docstrings to functions
  • Consider using TypedDict for state
  • Add error handling for failed tools

============================================================
✅ READY FOR NEXT EXERCISE
============================================================
```

### Example 4: Get Detailed Feedback

```bash
python scripts/evaluate.py --exercise week1_exercise_1 --code ./solution.py --show-feedback
```

Adds personalized explanations of concepts and learning resources.

## 🔧 Configuration

### Environment Variables

```
ANTHROPIC_API_KEY=your_key_here
```

### Model Selection

Edit `agents/` files to change model:

```python
self.model = "claude-opus-4-20250805"  # Latest Opus
```

Available models:
- `claude-opus-4-20250805` - Latest Opus (recommended)
- `claude-opus-4-20250514` - Previous Opus
- `claude-sonnet-4-20250514` - Faster, cheaper

### Extended Thinking

Extended thinking is enabled by default for deep reasoning:

```python
thinking={
    "type": "enabled",
    "budget_tokens": 1000  # Reasoning budget
}
```

Adjust `budget_tokens` based on complexity and cost concerns.

## 📈 Understanding Your Progress

### Weekly Progress

```
Week 1:  ████████████████░░ 80% (4/5 exercises)
Week 2:  ██████░░░░░░░░░░░░ 30% (1/5 exercises)

Overall: ████████░░░░░░░░░░ 23% (5/25 exercises)
```

### Metrics

- **Completion Percentage**: How many exercises you've finished
- **Quality Score**: Average code quality (0-10)
- **Average Score**: Mean score across exercises
- **Estimated Completion**: When you'll finish all 12 weeks

Run:
```bash
python scripts/run.py --action progress
```

## 🤝 How to Use with Claude Project

This system integrates with your Claude Project:

1. **Upload training materials** to Claude Project knowledge base
2. **Use agents directly** in Claude for additional exercises
3. **Track progress** across both Claude Project and local system
4. **Reference curriculum** whenever you need clarification

The agents in this repo augment the Claude Project system.

## 🧠 Extended Thinking

The system uses Claude's extended thinking for:

- **Architecture decisions** - Designing agents and workflows
- **Code analysis** - Deep review of your solutions
- **Concept explanations** - Understanding complex patterns
- **Progress analysis** - Identifying learning patterns

Extended thinking budget defaults to 1000 tokens per request. Adjust based on:

```python
thinking={
    "type": "enabled",
    "budget_tokens": 500   # Less thinking = faster/cheaper
    # or
    "budget_tokens": 2000  # More thinking = deeper analysis
}
```

## 📚 Connecting to Your Training

This system works alongside your main training materials in GitHub:

- **agentic-samples repo** - Your learning and solutions
- **claude-agentic-trainer repo** - This agent system
- **Claude Project** - Interactive learning and exercises

All three are coordinated:
- Claude Project hosts curriculum materials
- Trainer agents generate exercises
- You solve exercises and commit to GitHub
- Trainer reviews and provides feedback

## 🔗 Key Files

| File | Purpose |
|------|---------|
| `agents/curriculum_analyzer.py` | Analyzes curriculum |
| `agents/exercise_generator.py` | Generates exercises |
| `agents/code_reviewer.py` | Reviews solutions |
| `agents/feedback_provider.py` | Explains concepts |
| `agents/progress_tracker.py` | Tracks progress |
| `orchestrator/graph.py` | Coordinates agents |
| `orchestrator/state.py` | Defines state schema |
| `scripts/run.py` | Main CLI interface |
| `scripts/evaluate.py` | Code evaluation CLI |

## 🚀 Next Steps

1. **Set up** - Install dependencies and configure API key
2. **Start Week 1** - Run `python scripts/run.py --week 1 --action full`
3. **Do exercises** - Use generated exercises as starting point
4. **Get feedback** - Review your solutions with `evaluate.py`
5. **Progress** - Track your journey with `--action progress`
6. **Advance** - Move to Week 2, repeat process

## 📖 Learning Path

- **Week 1-3**: Foundations (single agents, tool calling, memory)
- **Week 4-6**: Frameworks (CrewAI, LangGraph, orchestration)
- **Week 7-9**: Advanced (voting, conflict resolution)
- **Week 10-12**: Production (building software dev agents)

Each week:
1. Analyze what you should learn
2. Get 5 progressive exercises
3. Build your solutions
4. Get code review and feedback
5. Track progress to next week

## 🆘 Troubleshooting

### "Invalid API key"
```bash
# Check your key is set
echo $ANTHROPIC_API_KEY

# Or check .env file
cat .env
```

### "Module not found"
```bash
# Make sure you're in project root
pwd  # Should end in /claude-agentic-trainer

# Install dependencies
pip install -r requirements.txt
```

### "LangGraph not recognized"
```bash
# LangGraph might need specific version
pip install --upgrade langgraph
```

## 📄 License

MIT License - See LICENSE file

## 🎯 Success Metrics

After 12 weeks you'll have:

✅ Completed all 12 weeks of training  
✅ Built 5 fully functional agents  
✅ Created LangGraph orchestration  
✅ Implemented voting and conflict resolution  
✅ Produced production-ready code  
✅ Generated 60+ exercises  
✅ Demonstrated mastery of agentic AI  

---

**Ready to learn agentic AI by building a trainer system?**

```bash
python scripts/run.py --week 1 --action full
```

Let's go! 🚀
