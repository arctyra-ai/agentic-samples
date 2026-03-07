# Agentic AI Engineering Curriculum

Production-ready multi-agent systems with MCP, LangGraph, evaluation, and deployment.

## Prerequisites

- **Python 3.11+** (required -- run `python3 --version` to check)
  - macOS: `brew install python@3.12`
  - Ubuntu: `sudo apt install python3.12`
  - Windows: download from python.org
- **Node.js 18+** (needed for MCP servers in Weeks 3 and 5)
  - Install from nodejs.org or `brew install node`
- **Git**
- **An Anthropic API key** (get one at https://console.anthropic.com/api-keys)

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/arctyra-ai/agentic-samples.git
cd agentic-samples
make setup    # checks Python version, creates venv, installs deps

# 2. Add your API keys
# Edit .env with your ANTHROPIC_API_KEY (required) and others (optional)

# 3. Start Week 1
make run-week W=01
```

If `make setup` fails with a Python version error, install Python 3.11+ first (see Prerequisites above).

## Structure

| Phase | Weeks | Focus |
|-------|-------|-------|
| Foundations | 1-3 | Agent loops, tool use, MCP basics |
| Real Integrations | 4-6 | RAG, custom MCP servers, LangGraph |
| Multi-Agent Systems | 7-9 | Orchestration, voting, evaluation |
| Production | 10-12 | Deploy, monitor, capstone |

Each week directory contains:
- `README.md` -- objectives, instructions, success criteria
- `*_starter.py` -- skeleton with TODOs (start here)
- `*.py` -- reference solution
- `test_*.py` -- unit tests

## Common Commands

```bash
make help          # Show all commands
make setup         # Create venv, install deps, copy .env
make test          # Run all tests
make test-local    # Run tests without API keys
make test-week W=01  # Run tests for a specific week
make run-week W=01   # Run the main exercise for a week
make clean         # Remove generated artifacts
```

## Files

| File | Purpose |
|------|---------|
| `agentic_ai_curriculum.md` | Full 12-week curriculum |
| `ARCHITECTURE_DIAGRAMS.md` | Mermaid diagrams for every major system |
| `CLAUDE_PROJECT_INSTRUCTIONS.md` | Setup Claude as your learning companion |
| `PROGRESS.md` | Checklist to track your progress |
| `shared/` | Reusable utilities (LLM client, MCP utils, eval helpers) |

## API Keys Required

- `ANTHROPIC_API_KEY` -- primary LLM provider (required)
- `OPENAI_API_KEY` -- secondary provider (optional, for comparison)
- `LANGCHAIN_API_KEY` -- LangSmith tracing (free tier, used from Week 6)

Copy `.env.example` to `.env` and fill in your keys.

## Estimated API Cost

~$18-33 for the full curriculum using Claude Sonnet. Budget $50 to be safe.

## License

This work is licensed under [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/).

You are free to use this material for learning and share it with others. You must give credit to [Arctyra AI](https://github.com/arctyra-ai). You may not use it for commercial purposes or sell it. If you adapt it, you must share your version under the same license.

See [LICENSE](LICENSE) for full terms.

---

## Projects

Applications built using multi-agent development pipelines.

### Business Plan Generator

AI-powered business plan generator with an 8-stage pipeline. Built with Next.js 14, TypeScript, and Tailwind CSS. Supports Anthropic, OpenAI, and custom LLM providers. [View Project →](./projects/business-plan-generator/)
