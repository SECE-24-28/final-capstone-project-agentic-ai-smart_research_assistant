# Qwen 1.5B LLM Loading Analysis

This document provides a root-cause analysis of the execution freezes identified during the ML runtime diagnostics, specifically isolating the `LLMService.load()` method.

## 1. Exact Loading Code
The loading sequence in `backend/services/llm_service.py` is defined as:
```python
self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
self.model = AutoModelForCausalLM.from_pretrained(self.model_name, trust_remote_code=True)
self.pipeline = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer, device_map="auto")
```

## 2. `device_map` Settings
* **Missing in Model Instantiation:** The `AutoModelForCausalLM.from_pretrained()` call **lacks** a `device_map` argument. This forces PyTorch to load the entire model monolithically into CPU RAM before any optimizations can be applied.
* **Pipeline Usage:** The `pipeline()` call uses `device_map="auto"`, but because `model=self.model` is passed directly, the model is already fully instantiated on the default device (CPU). The pipeline's device map is effectively useless.

## 3. `torch_dtype` Settings
**None.** The code does not specify a `torch_dtype`. 
By default, the `transformers` library will instantiate model weights in 32-bit floating-point (`float32`). For a 1.5 Billion parameter model, this requires **~6 GB of continuous RAM**, rather than the standard ~3 GB required for `float16` or `bfloat16`. 

## 4. Quantization Settings
**None.** There is no integration with `bitsandbytes` (e.g., `load_in_8bit` or `load_in_4bit`). The model is attempting to run in full precision, drastically increasing memory and memory bandwidth requirements.

## 5. CPU/GPU Detection Logic
**Absent.** The code does not check for `torch.cuda.is_available()`. It completely ignores the hardware environment and relies on `transformers` default fallbacks, which natively default to CPU execution if CUDA logic isn't explicitly enforced.

## 6. Root Causes of Freezing / Deadlocking
The combination of the above configuration errors guarantees a massive system freeze on most consumer-grade CPUs:

1. **Peak Memory Spike (The 2x RAM Trap):** Without `low_cpu_mem_usage=True`, PyTorch allocates memory for the model skeleton first (~6 GB in float32) and *then* loads the `safetensors` state dictionary into a separate memory block (~6 GB), causing a momentary RAM spike of **~12 GB**. If the system cannot support this, Windows heavily relies on the page file (Disk Swapping). This "thrashing" is so slow it looks like a permanent deadlock.
2. **Float32 Inefficiency:** Attempting to run a 1.5B LLM on CPU in `float32` requires massive memory bandwidth. 
3. **Improper Device Mapping:** Because the `device_map="auto"` isn't passed to `from_pretrained`, the Hugging Face `accelerate` library cannot intelligently shard the model across available RAM/Disk resources. 

### Conclusion
The code is freezing because the hardware is running out of physical RAM and paging to the hard drive during the synchronous monolithic `float32` loading sequence, causing a system-level I/O bottleneck.
