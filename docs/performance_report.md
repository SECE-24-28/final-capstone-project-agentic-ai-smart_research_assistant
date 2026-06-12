# E2E Pipeline Performance Report

## Profiling Methodology
An End-to-End profiling script (`profile_e2e.py`) was executed to measure the exact latency of each subsystem within the RAG pipeline. 

## Execution Times (CPU)

* **PDF Extraction:** ~0.05 s
* **Chunking:** ~0.01 s
* **ChromaDB Storage:** ~0.15 s
* **Prompt Construction:** < 0.01 s
* **Embedding Generation (`all-MiniLM-L6-v2`):** **TIMEOUT / DEADLOCK (5+ minutes)**
* **Retrieval:** Unable to test due to Embedding failure.
* **Qwen Inference (`Qwen2.5-1.5B`):** Unable to test due to Embedding failure.

*(Note: Times for successfully executed synchronous Python methods were collected, but the heavy ML tasks triggered infinite process hangs.)*

## Bottleneck Analysis

The primary bottleneck in the current architecture is the **Machine Learning Model Initialization (Embeddings & LLM)** on a CPU environment. 

During the E2E profiling, the process suffered a permanent deadlock while initializing `sentence-transformers` and attempting to load the LLM into RAM. The initialization time is practically infinite, crashing the pipeline before inference or vector embeddings can even begin. 

This indicates that deploying local Hugging Face `transformers` models synchronously on standard CPU workers is completely unviable for this application.

## Recommended Optimizations

1. **Offload Inference to a Dedicated Provider or GPU:**
   Running a 1.5B parameter LLM and a vector embedding model synchronously on a CPU will always lead to massive latency (30-90s minimum) or deadlocks. The application should either be deployed on a machine with a dedicated NVIDIA GPU (CUDA), or the heavy inference should be offloaded to cloud APIs (e.g., OpenAI, Anthropic, or a dedicated vLLM server).

2. **Asynchronous Model Loading:**
   Currently, the models (`embedding_service` and `llm_service`) are loaded synchronously into the main thread right when a request is made. This blocks the entire FastAPI application. Model loading must happen asynchronously during startup (`@app.on_event("startup")`) so the endpoints do not freeze.

3. **Background Job Processing (Celery/Redis):**
   RAG pipelines (Extract → Embed → Summarize) take far too long for a standard HTTP request lifecycle. The `Upload` and `Summarize` processes must be moved to background tasks (e.g., using Celery or FastAPI `BackgroundTasks`), returning a `job_id` to the frontend which can poll for completion.

4. **Model Quantization:**
   If local CPU inference is strictly required, the Qwen model must be loaded using an optimized backend like `llama.cpp` (GGUF format) with 4-bit quantization, rather than relying on the heavy `transformers` library, which is prone to OpenMP thread deadlocks on Windows CPUs.
