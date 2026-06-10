import sys
import os
import logging
from backend.services.llm_service import llm_service

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_generation():
    print("Testing LLMService initialization and generation...")
    try:
        # We explicitly load to verify logging
        llm_service.load()
        
        prompt = "What is machine learning in one sentence?"
        print(f"\nPrompt: {prompt}")
        
        response = llm_service.generate(prompt, max_tokens=50)
        
        print("\nResponse:")
        print(response)
        
        print("\nTest SUCCESS")
    except Exception as e:
        print(f"\nTest FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_generation()
