import httpx
import json
import logging
import time
from typing import Generator, Dict, Any, Tuple

logger = logging.getLogger(__name__)

class OllamaService:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.generate_url = f"{self.base_url}/api/generate"
        self.default_model = "qwen2.5:1.5b"
        self._timeout = 300.0  # 5 minutes for long generations

    def health_check(self) -> Tuple[bool, float, str]:
        """
        Check if Ollama server is running and the model is available.
        Returns: (is_healthy, latency_seconds, message)
        """
        try:
            start_time = time.time()
            response = httpx.get(self.base_url, timeout=5.0)
            latency = time.time() - start_time
            
            if response.status_code == 200:
                # Optionally check if model exists via /api/tags
                tags_resp = httpx.get(f"{self.base_url}/api/tags", timeout=5.0)
                if tags_resp.status_code == 200:
                    models = [m.get("name") for m in tags_resp.json().get("models", [])]
                    if any(self.default_model in m for m in models):
                        return True, latency, f"Ollama running. Model '{self.default_model}' available."
                    else:
                        return True, latency, f"Ollama running, but model '{self.default_model}' not found."
                return True, latency, "Ollama running."
            else:
                return False, latency, f"Ollama returned status {response.status_code}"
        except Exception as e:
            return False, 0.0, str(e)

    def generate(self, prompt: str, system_prompt: str = "You are a helpful research assistant.") -> str:
        """Synchronous generation using Ollama."""
        payload = {
            "model": self.default_model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.0
            }
        }
        
        logger.info(f"OLLAMA START: Generating text. Model: {self.default_model}")
        start_time = time.time()
        
        try:
            response = httpx.post(self.generate_url, json=payload, timeout=self._timeout)
            response.raise_for_status()
            data = response.json()
            
            gen_duration = time.time() - start_time
            response_text = data.get("response", "").strip()
            
            # Ollama provides performance metrics
            eval_count = data.get("eval_count", 0)
            tokens_per_sec = eval_count / gen_duration if gen_duration > 0 else 0
            
            logger.info(f"OLLAMA COMPLETE: Generation finished in {gen_duration:.2f} seconds.")
            logger.info(f"PERFORMANCE: Output tokens: {eval_count} | Tokens/sec: {tokens_per_sec:.2f}")
            
            return response_text
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise

    def stream_generate(self, prompt: str, system_prompt: str = "You are a helpful research assistant.") -> Generator[str, None, None]:
        """Streaming generation yielding tokens progressively."""
        payload = {
            "model": self.default_model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": True,
            "options": {
                "temperature": 0.0
            }
        }
        
        logger.info(f"OLLAMA START: Stream-generating text. Model: {self.default_model}")
        start_time = time.time()
        first_token_logged = False
        token_count = 0
        
        try:
            # Using httpx synchronous client for streaming
            with httpx.Client(timeout=self._timeout) as client:
                with client.stream("POST", self.generate_url, json=payload) as response:
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if line:
                            data = json.loads(line)
                            token = data.get("response", "")
                            
                            if token and not first_token_logged:
                                ttft = time.time() - start_time
                                logger.info(f"OLLAMA STREAMING: First token in {ttft:.3f}s")
                                first_token_logged = True
                                
                            token_count += 1
                            yield token
                            
                            if data.get("done"):
                                gen_duration = time.time() - start_time
                                eval_count = data.get("eval_count", token_count)
                                tokens_per_sec = eval_count / gen_duration if gen_duration > 0 else 0
                                logger.info(f"OLLAMA STREAMING COMPLETE: Total time {gen_duration:.2f}s")
                                logger.info(f"PERFORMANCE: Output tokens: {eval_count} | Tokens/sec: {tokens_per_sec:.2f}")
                                break
        except Exception as e:
            logger.error(f"Ollama stream generation failed: {e}")
            raise

ollama_service = OllamaService()
