from abc import ABC, abstractmethod
from typing import Any


class BaseLLMClient(ABC):
    """Abstract interface for LLM provider clients (Gemini, OpenAI, Claude, Ollama, etc.)."""

    @abstractmethod
    def generate_answer(self, query: str, context: str) -> dict[str, Any]:
        """
        Generate answer from query and context.
        Returns dict containing at least:
          - 'answer': str
          - 'input_tokens': int
          - 'output_tokens': int
          - 'latency_ms': float
        """
        pass

    @abstractmethod
    def get_token_usage(self) -> dict[str, int]:
        """Return cumulative token usage (input_tokens, output_tokens, total_tokens)."""
        pass
