.PHONY: help setup test test-local test-week lint run-week clean

PYTHON ?= python
PYTEST ?= pytest

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Create venv, install deps, copy .env.example
	$(PYTHON) -m venv venv
	. venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	@test -f .env || cp .env.example .env
	@echo "Setup complete. Activate with: source venv/bin/activate"
	@echo "Then edit .env with your API keys."

test: ## Run all tests
	$(PYTEST) -v

test-local: ## Run tests that do not require API keys
	$(PYTEST) -v -k "not Integration and not requires_api"

test-week: ## Run tests for a specific week (usage: make test-week W=01)
	$(PYTEST) week$(W)_*/test_*.py -v

run-week: ## Run the main exercise for a week (usage: make run-week W=01)
	@case $(W) in \
		01) $(PYTHON) week01_agent_fundamentals/agent.py ;; \
		02) $(PYTHON) week02_tool_use_deep_dive/research_agent.py ;; \
		03) $(PYTHON) week03_mcp_foundations/mcp_agent.py ;; \
		04) $(PYTHON) week04_rag_agents/rag_agent.py index --docs-dir week04_rag_agents/docs ;; \
		05) $(PYTHON) week05_custom_mcp_servers/project_mcp_server.py ;; \
		06) $(PYTHON) week06_langgraph_orchestration/document_pipeline.py ;; \
		07) $(PYTHON) week07_multi_agent_systems/code_review_agents.py ;; \
		08) $(PYTHON) week08_voting_and_conflicts/voting.py ;; \
		09) $(PYTHON) week09_evaluation_and_observability/evaluation.py ;; \
		10) streamlit run week10_production_deployment/app.py ;; \
		11) $(PYTHON) week11_capstone_build/capstone_scaffold.py ;; \
		*) echo "Usage: make run-week W=01 (01-11)" ;; \
	esac

lint: ## Run basic Python checks
	$(PYTHON) -m py_compile shared/llm_client.py
	$(PYTHON) -m py_compile shared/mcp_utils.py
	$(PYTHON) -m py_compile shared/eval_helpers.py
	@echo "Compile checks passed."

clean: ## Remove generated artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf chroma_db/ sessions/ *.db eval_results/
	@echo "Cleaned."
