# Phase 17: LLM Performance Optimization Audit

## 1. Current System State
* **Model Name:** `Qwen/Qwen2.5-1.5B-Instruct`
* **Parameter Count:** ~1.5 Billion
* **Quantization:** None explicit (loading with `torch_dtype="auto"`, defaulting to full precision fp32/bf16 depending on PyTorch CPU fallbacks).
* **Load Format:** PyTorch native Hugging Face Transformers (`safetensors`/`bin`).

## 2. Hardware Profile
* **CPU Model:** AMD64 Family 25 Model 124 Stepping 0 (Ryzen architecture)
* **RAM:** 15.27 GB (16 GB total)
* **GPU Availability:** None
* **CUDA:** `torch.cuda.is_available() == False`

## 3. Current Performance Profile
*(Measurements based on native PyTorch execution on CPU)*
* **Bottleneck:** The system is entirely CPU-bound. Without a GPU, the unquantized 1.5B model requires shifting ~3GB of data through memory bandwidth for *every single token generated*.
* **Generation Speed:** Extremely slow (~2-5 tokens/second), taking multiple minutes for a standard 256-token summary.
* **Context Scaling Penalty:** Comparison and Gap Analysis workflows suffer massive latency spikes because PyTorch CPU attention mechanisms scale poorly with large input documents (RAG contexts).

## 4. Evaluation of Optimization Options

### A. PyTorch GPU Inference
* **Pros:** Fastest native Hugging Face performance with zero code changes.
* **Cons:** Hardware profile shows no CUDA-compatible GPU. Not viable without cloud migration or hardware upgrades.

### B. Quantized Transformers (4-bit / 8-bit) via `bitsandbytes`
* **Pros:** Reduces memory footprint.
* **Cons:** `bitsandbytes` quantization is highly optimized for CUDA. Native 4-bit Hugging Face inference on CPUs is notoriously unoptimized and often results in slower token generation due to the overhead of CPU dequantization loops.

### C. ONNX Runtime
* **Pros:** Highly optimized for CPU execution.
* **Cons:** Extreme complexity in exporting the 1.5B causal LM to ONNX. Custom C++ or complex Python bindings required for dynamic context lengths and streaming SSE support. High code-change overhead.

### D. Ollama + GGUF (llama.cpp)
* **Pros:** The GGUF format is explicitly designed for CPU inference. It leverages CPU-specific vector instructions (AVX2/AVX-512) and executes 4-bit integer quantization (`Q4_K_M`) exceptionally fast. Ollama natively handles memory management and provides a clean REST API with streaming support.
* **Cons:** Requires running a separate local Ollama binary instead of importing PyTorch directly.

### E. Smaller Qwen Variants (e.g., Qwen2.5-0.5B)
* **Pros:** A 3x smaller model inherently yields 3x faster generation natively.
* **Cons:** Significant degradation in logical reasoning and extraction quality, which is fatal for complex multi-paper Comparison and Gap Analysis tasks.

## 5. Recommendation: Ollama + GGUF (Option D)

**The most effective method to radically reduce inference latency with minimal code changes is migrating the `LLMService` to use a local Ollama instance running a 4-bit quantized GGUF model (`qwen2.5:1.5b-instruct-q4_K_M` or `llama3.2`).**

### Expected Speedups
* **Throughput:** Expected jump from ~2 tokens/sec to **15-25 tokens/sec** natively on the AMD CPU.
* **Memory Usage:** Plummets from ~3.5 GB to **<1 GB** RAM footprint.
* **System Stability:** Decouples LLM inference from the Python Global Interpreter Lock (GIL), resolving the previously identified deadlocks between PyTorch thread pools and ChromaDB SQLite access.

### Required Code Changes (Minimal)
1. **Remove Heavy Dependencies:** Uninstall `torch`, `transformers`, and `accelerate` from `pyproject.toml`, significantly lightening the deployment size.
2. **Refactor `LLMService`:** Modify `backend/services/llm_service.py` to remove `AutoModelForCausalLM`. Replace it with standard asynchronous HTTP requests (using `httpx`) pointing to `http://localhost:11434/api/generate`.
3. **Preserve Agent Logic:** No changes are required in `SummaryAgent`, `ComparisonAgent`, `GapAgent`, or the RAG pipeline. Prompts and token streams remain exactly the same.

### Recommended Deployment Architecture
* **Frontend:** React (Vite)
* **Backend API:** FastAPI (Python)
* **Vector Store:** ChromaDB
* **LLM Engine:** Ollama (running as a local background service)
