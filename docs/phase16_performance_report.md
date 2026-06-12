# Phase 16A LLM Performance Report

## Issue Diagnosis
Users experienced severe latency across all tasks (60–180 seconds for Summaries, 60–120 seconds for Comparisons, and 30–90 seconds for Chat). A full audit of the local inference stack was required to document lifecycle behavior.

## Investigation Findings
1. **Model Instantiation:** 
   The application uses Hugging Face's `AutoModelForCausalLM` via the `LLMService` class. 
2. **Lifecycle Scope:** 
   The `LLMService` functions securely as a singleton object, ensuring the model weights are loaded into memory exactly *once* during startup or the first agent invocation, preventing memory leaks or repetitive model loading.
3. **Execution Device Configuration:**
   The model checks for `torch.cuda.is_available()` automatically. If no CUDA capable GPU is accessible, the model executes the billions of FP16/FP32 operations serially on the CPU, heavily dragging inference throughput.

## Resolution & Improvements
1. **Response Caching Integration:** 
   To circumvent physical generation limits, database caching was applied to the `SummaryAgent` and `ComparisonAgent`. Identical tasks now bypass the LLM entirely, resulting in sub-100ms response times for previously computed analyses.
2. **Diagnostic Telemetry:** 
   Granular logging was added into `LLMService` to track device resolution (CPU vs CUDA), prompt length inputs, response output lengths, overall generation latency (in seconds), and generation speed (tokens/sec).

## Conclusion
While base hardware limits the generation speed on CPU, caching mechanisms have drastically cut the *experienced* latency for users, and telemetry now allows us to observe the model's throughput properly.
