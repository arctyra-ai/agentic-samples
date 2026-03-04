#!/usr/bin/env python3
"""
Week 4-5: Claude Code Configuration for CrewAI
Shows how to configure CrewAI agents to use Anthropic/Claude models.

CrewAI supports multiple LLM providers. To use Claude instead of OpenAI:
1. Set ANTHROPIC_API_KEY in .env
2. Set the llm parameter on each Agent

Usage:
    from claude_code_config import create_claude_agent
    agent = create_claude_agent(role="...", goal="...", backstory="...")
"""

import os
from dotenv import load_dotenv

load_dotenv()


def get_claude_llm():
    """
    Create a Claude LLM instance for use with CrewAI.

    CrewAI supports LiteLLM format for model specification.
    Prefix with 'anthropic/' to route through LiteLLM.
    """
    # Option 1: Using LiteLLM format (recommended)
    # CrewAI uses LiteLLM under the hood, so you can specify:
    return "anthropic/claude-sonnet-4-20250514"


def create_claude_agent(role, goal, backstory, tools=None, verbose=True):
    """
    Create a CrewAI Agent configured to use Claude.

    Example:
        agent = create_claude_agent(
            role="Task Manager",
            goal="Parse user requests",
            backstory="Expert at understanding intent"
        )
    """
    from crewai import Agent

    return Agent(
        role=role,
        goal=goal,
        backstory=backstory,
        tools=tools or [],
        verbose=verbose,
        llm=get_claude_llm()
    )


# ============================================================================
# Example: Recreate Week 4 agents with Claude
# ============================================================================

if __name__ == "__main__":
    print("Creating CrewAI agents with Claude...")

    task_manager = create_claude_agent(
        role="Task Manager",
        goal="Understand user intent and break down requests",
        backstory="Expert at parsing user requests"
    )

    storage_agent = create_claude_agent(
        role="Storage Specialist",
        goal="Execute CRUD operations safely",
        backstory="Responsible for data integrity"
    )

    validator_agent = create_claude_agent(
        role="Data Validator",
        goal="Validate operations before execution",
        backstory="Catches errors proactively"
    )

    print(f"Task Manager LLM: {task_manager.llm}")
    print(f"Storage Agent LLM: {storage_agent.llm}")
    print(f"Validator Agent LLM: {validator_agent.llm}")
    print("\nAll agents configured for Claude.")
