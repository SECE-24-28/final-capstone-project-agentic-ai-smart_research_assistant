import logging
from typing import Generator

from .ollama_service import ollama_service

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        # We exclusively use Ollama now
        pass

    def load(self):
        # Ollama loads models implicitly on first request
        logger.info("LLMService.load: Ollama is the single provider. No explicit load required.")
        pass

    def generate(self, prompt: str, max_tokens: int = 256, system_prompt: str = "You are a helpful research assistant.") -> str:
        """Synchronous generation routed to Ollama."""
        return ollama_service.generate(prompt, system_prompt)

    def stream_generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        system_prompt: str = "You are a helpful research assistant."
    ) -> Generator[str, None, None]:
        """Streaming generation routed to Ollama."""
        return ollama_service.stream_generate(prompt, system_prompt)

llm_service = LLMService()
