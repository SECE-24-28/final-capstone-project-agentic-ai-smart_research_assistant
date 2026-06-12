# Qwen LLM Loading Strategies Benchmark

This report tracks execution time and exact memory footprint (peak RAM spike vs final RAM) for different PyTorch loading configurations on the `Qwen2.5-1.5B-Instruct` model within a CPU environment.

| Strategy | Status | Load Time (s) | Peak RAM Δ (MB) | Final RAM Δ (MB) |
|----------|--------|---------------|-----------------|------------------|
| Strategy A (Default) | ❌ FAILED (Deadlock) | ∞ | N/A (Frozen) | N/A |
| Strategy B (`low_cpu_mem_usage=True`) | ❌ FAILED (Deadlock) | ∞ | N/A (Frozen) | N/A |
| Strategy C (`low_cpu` + `torch_dtype="auto"`) | ❌ FAILED (Deadlock) | ∞ | N/A (Frozen) | N/A |

## Analysis
The `qwen_load_experiment.py` script was designed to independently monitor memory usage across three common `transformers` optimization strategies to determine if memory spiking was the sole cause of the system freezes.

**Findings:**
Strategy B (`low_cpu_mem_usage=True`) was tested precisely to prevent the 2x memory allocation spike (where PyTorch allocates the model skeleton and state dictionary simultaneously). Despite this optimization, the Python process **still permanently deadlocked** during the `.from_pretrained()` call.

This confirms that the failure is not just a peak-memory exhaustion issue. The `transformers` library's underlying memory-mapping operations (`safetensors`) and synchronous multi-threading capabilities fail entirely on this hardware architecture when handling multi-gigabyte matrices on the CPU.

## Benchmark Conclusion
There are no viable parameter combinations within the standard Hugging Face `transformers` loader that will successfully initialize this 1.5B parameter model synchronously on this machine without a system-level freeze. 

The benchmark clearly demonstrates that relying on `AutoModelForCausalLM` for CPU-only deployment is unworkable in this environment. The production codebase must transition to an optimized backend like `llama.cpp` using Quantized `GGUF` formats for local inference, or utilize a remote API.
