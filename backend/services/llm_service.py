import logging
import time
from typing import List

from ..config import settings

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
except ImportError:
    AutoTokenizer = None
    AutoModelForCausalLM = None
    torch = None

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.model_name = settings.llm_model_name
        self.tokenizer = None
        self.model = None
        self._is_loaded = False

    def load(self):
        if self._is_loaded:
            return
            
        if AutoTokenizer is None or AutoModelForCausalLM is None:
            raise RuntimeError("transformers is required for LLMService")

        logger.info(f"START: Loading local LLM: {self.model_name}")
        load_start = time.time()
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name, 
            trust_remote_code=True,
            low_cpu_mem_usage=True,
            torch_dtype="auto"
        )
        
        # If CUDA is available, move the model
        if torch and torch.cuda.is_available():
            self.model.to("cuda")
            
        load_duration = time.time() - load_start
        logger.info(f"COMPLETE: Model loaded successfully in {load_duration:.2f} seconds.")
        self._is_loaded = True

    def generate(self, prompt: str, max_tokens: int = 256) -> str:
        if not self._is_loaded:
            self.load()
            
        logger.info(f"START: Generating text (max_tokens={max_tokens})")
        gen_start = time.time()
        
        messages = [
            {"role": "system", "content": "You are a helpful research assistant."},
            {"role": "user", "content": prompt}
        ]
        
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        inputs = self.tokenizer(text, return_tensors="pt")
        
        if torch and torch.cuda.is_available():
            inputs = {k: v.to("cuda") for k, v in inputs.items()}
            
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=False,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        # Strip the input prompt from the generated response
        input_len = inputs['input_ids'].shape[1]
        response_ids = outputs[0][input_len:]
        
        response_text = self.tokenizer.decode(
            response_ids,
            skip_special_tokens=True
        ).strip()
        
        gen_duration = time.time() - gen_start
        logger.info(f"COMPLETE: Generation finished in {gen_duration:.2f} seconds.")
        
        return response_text

llm_service = LLMService()
