import logging
from typing import List

from ..config import settings

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
except ImportError:  # fallback to allow install later
    AutoTokenizer = None
    AutoModelForCausalLM = None
    pipeline = None

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.model_name = settings.llm_model_name
        self.tokenizer = None
        self.model = None
        self.pipeline = None

    def load(self):
        if AutoTokenizer is None or AutoModelForCausalLM is None or pipeline is None:
            raise RuntimeError("transformers is required for LLMService")

        logger.info("Loading local LLM: %s", self.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name, trust_remote_code=True)
        self.pipeline = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer, device_map="auto")

    def generate(self, prompt: str, max_tokens: int = 256) -> str:
        if self.pipeline is None:
            self.load()
        result = self.pipeline(prompt, max_new_tokens=max_tokens, do_sample=False)
        return result[0]["generated_text"].strip()

llm_service = LLMService()
