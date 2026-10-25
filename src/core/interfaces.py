from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseLLMClient(ABC):
    """Abstract interface for LLM provider clients (Gemini, OpenAI, Claude, Ollama, etc.)."""

    @abstractmethod
    def generate_answer(self, query: str, context: str) -> Dict[str, Any]:
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
    def get_token_usage(self) -> Dict[str, int]:
        """Return cumulative token usage (input_tokens, output_tokens, total_tokens)."""
        pass
