"""Unified LLM client wrapper for Anthropic and OpenAI.

Provides a consistent interface for making LLM calls with automatic
token tracking and cost estimation.
"""

import os
import json
from dataclasses import dataclass, field
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic
from openai import OpenAI

load_dotenv()

# Cost per 1M tokens (March 2026 pricing, update as needed)
PRICING = {
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    "claude-haiku-3-20250307": {"input": 0.25, "output": 1.25},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}


@dataclass
class TokenUsage:
    """Track token usage and costs across calls."""
    input_tokens: int = 0
    output_tokens: int = 0
    calls: int = 0
    history: list = field(default_factory=list)

    def record(self, model: str, input_tokens: int, output_tokens: int):
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.calls += 1
        self.history.append({
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "timestamp": datetime.now().isoformat(),
        })

    def estimated_cost(self) -> float:
        """Estimate total cost based on recorded usage."""
        total = 0.0
        for entry in self.history:
            model = entry["model"]
            pricing = PRICING.get(model, {"input": 5.0, "output": 15.0})
            total += (entry["input_tokens"] / 1_000_000) * pricing["input"]
            total += (entry["output_tokens"] / 1_000_000) * pricing["output"]
        return round(total, 4)

    def summary(self) -> dict:
        return {
            "total_calls": self.calls,
            "total_input_tokens": self.input_tokens,
            "total_output_tokens": self.output_tokens,
            "estimated_cost_usd": self.estimated_cost(),
        }


class LLMClient:
    """Unified client for Anthropic and OpenAI with token tracking."""

    def __init__(self, provider: str = "anthropic", budget_usd: float = None):
        self.provider = provider
        self.budget_usd = budget_usd
        self.usage = TokenUsage()

        if provider == "anthropic":
            self.client = Anthropic()
            self.default_model = "claude-sonnet-4-20250514"
        elif provider == "openai":
            self.client = OpenAI()
            self.default_model = "gpt-4o"
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _check_budget(self):
        if self.budget_usd and self.usage.estimated_cost() >= self.budget_usd:
            raise RuntimeError(
                f"Budget exceeded: ${self.usage.estimated_cost():.4f} >= ${self.budget_usd:.2f}. "
                f"Total calls: {self.usage.calls}"
            )

    def chat(
        self,
        messages: list[dict],
        system: str = None,
        model: str = None,
        tools: list[dict] = None,
        max_tokens: int = 4096,
    ) -> dict:
        """Make an LLM call and return standardized response.

        Returns:
            dict with keys: content (list of blocks), model, usage (dict)
        """
        self._check_budget()
        model = model or self.default_model

        if self.provider == "anthropic":
            return self._anthropic_chat(messages, system, model, tools, max_tokens)
        else:
            return self._openai_chat(messages, system, model, tools, max_tokens)

    def _anthropic_chat(self, messages, system, model, tools, max_tokens) -> dict:
        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
        }
        if system:
            kwargs["system"] = system
        if tools:
            kwargs["tools"] = tools

        response = self.client.messages.create(**kwargs)
        self.usage.record(model, response.usage.input_tokens, response.usage.output_tokens)

        return {
            "content": [
                {"type": b.type, "text": getattr(b, "text", None),
                 "name": getattr(b, "name", None), "input": getattr(b, "input", None),
                 "id": getattr(b, "id", None)}
                for b in response.content
            ],
            "model": model,
            "stop_reason": response.stop_reason,
            "usage": {"input_tokens": response.usage.input_tokens,
                      "output_tokens": response.usage.output_tokens},
        }

    def _openai_chat(self, messages, system, model, tools, max_tokens) -> dict:
        oai_messages = []
        if system:
            oai_messages.append({"role": "system", "content": system})
        oai_messages.extend(messages)

        kwargs = {"model": model, "max_tokens": max_tokens, "messages": oai_messages}
        if tools:
            kwargs["tools"] = [
                {"type": "function", "function": {
                    "name": t["name"], "description": t["description"],
                    "parameters": t["input_schema"]
                }} for t in tools
            ]

        response = self.client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        usage = response.usage

        self.usage.record(model, usage.prompt_tokens, usage.completion_tokens)

        content = []
        if choice.message.content:
            content.append({"type": "text", "text": choice.message.content})
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                content.append({
                    "type": "tool_use", "name": tc.function.name,
                    "input": json.loads(tc.function.arguments), "id": tc.id,
                })

        return {
            "content": content,
            "model": model,
            "stop_reason": choice.finish_reason,
            "usage": {"input_tokens": usage.prompt_tokens,
                      "output_tokens": usage.completion_tokens},
        }

    def get_text(self, response: dict) -> str:
        """Extract text content from a standardized response."""
        texts = [b["text"] for b in response["content"] if b["type"] == "text" and b["text"]]
        return "\n".join(texts)

    def get_tool_calls(self, response: dict) -> list[dict]:
        """Extract tool use blocks from a standardized response."""
        return [b for b in response["content"] if b["type"] == "tool_use"]


if __name__ == "__main__":
    client = LLMClient(provider="anthropic", budget_usd=0.10)
    response = client.chat(
        messages=[{"role": "user", "content": "Say hello in exactly 5 words."}],
        system="You are a helpful assistant."
    )
    print(client.get_text(response))
    print(json.dumps(client.usage.summary(), indent=2))
