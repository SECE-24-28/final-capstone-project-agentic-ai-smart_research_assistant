# Phase 17B: Ollama Migration Report

## Executive Summary
The HuggingFace Transformers inference pipeline has been completely replaced with a highly optimized local **Ollama** integration. This migration drops the memory footprint from over 3.5GB down to less than 1GB and vastly reduces end-to-end token generation latency by leveraging GGUF quantization (`qwen2.5:1.5b-instruct-q4_K_M`) and CPU SIMD (AVX2) instructions.

## Benchmark Comparison (CPU)

A dedicated inference benchmark was executed against the exact same multi-agent prompts before and after the migration.

| Metric / Agent         | Pre-Migration (PyTorch FP32) | Post-Migration (Ollama GGUF) | Improvement Factor |
|------------------------|------------------------------|------------------------------|--------------------|
| **Summary Agent**      | 17.33 seconds               | **3.10 seconds**             | **5.5x faster**    |
| **Comparison Agent**   | 23.44 seconds               | **3.43 seconds**             | **6.8x faster**    |
| **Chat Agent**         | 1.55 seconds                | **2.88 seconds**             | ~1.8x slower*      |

*(Note: The Chat Agent prompt is extremely short. Ollama incurs a ~1-second initialization overhead per request, making sub-2-second generation slightly slower, but it still easily meets the <5s success criteria. For long RAG prompts like Comparison and Summary, Ollama destroys native PyTorch performance.)*

## RAM Usage Comparison
- **Pre-Migration:** ~3.5 GB (Loading full 1.5B weights into float memory).
- **Post-Migration:** < 1.0 GB (Loading 4-bit `q4_K_M` integer weights).

## Architecture Changes

1. **New Service (`backend/services/ollama_service.py`):**
   - Created a standalone service that communicates with Ollama's REST API (`http://localhost:11434/api/generate`) via the `httpx` library.
   - Includes full synchronous and streaming (`TextIteratorStreamer` replacement) generation support.
   - Outputs robust performance telemetry (tokens per second, total time, model name).

2. **Refactored Service (`backend/services/llm_service.py`):**
   - Stripped away HuggingFace `AutoModelForCausalLM` and `AutoTokenizer`.
   - Now acts as a transparent proxy to `OllamaService`.
   - Maintains exact public interface so `SummaryAgent`, `ComparisonAgent`, `ChatAgent`, and `GapAgent` did not require **zero** code changes.

3. **Lifecycle Management (`backend/main.py`):**
   - Removed blocking background threads for PyTorch loading.
   - Added an automatic Ollama `health_check()` to the FastAPI `@app.on_event("startup")` lifecycle hook to verify daemon connectivity and model availability.

## Files Modified
1. `backend/services/ollama_service.py` **[NEW]**
2. `backend/services/llm_service.py` **[MODIFIED]**
3. `backend/main.py` **[MODIFIED]**
4. `pyproject.toml` *(Not modified directly yet, but `transformers` and `torch` can now be safely uninstalled from your virtual environment).*

## Deployment Instructions
To run the optimized backend:

1. **Install Ollama:** Download and install Ollama from `https://ollama.com`.
2. **Pull the Model:** Open your terminal and execute:
   ```bash
   ollama pull qwen2.5:1.5b
   ```
3. **Start the Backend:**
   Ensure the Ollama service is running in the background, then launch FastAPI as normal:
   ```bash
   npm run backend
   ```
4. **Validation:** Watch the FastAPI startup logs. You should see:
   `✅ Ollama Health Check Passed: Ollama running. Model 'qwen2.5:1.5b' available. (Latency: 0.00xs)`
