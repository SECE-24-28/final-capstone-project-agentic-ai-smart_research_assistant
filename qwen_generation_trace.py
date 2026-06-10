import time
import os
import gc
import psutil
import threading
from datetime import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

def get_ram_mb():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

def write_report(content):
    os.makedirs("docs", exist_ok=True)
    with open("docs/qwen_generation_trace.md", "w", encoding="utf-8") as f:
        f.write(content)

def main():
    model_name = "Qwen/Qwen2.5-1.5B-Instruct"
    
    trace_log = [
        "# Qwen Generation Trace Report\n",
        f"**Model:** `{model_name}`",
        f"**Trace Started at:** `{datetime.now().isoformat()}`\n",
        "## Trace Log\n",
        "```text"
    ]
    
    def log_event(msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {msg}"
        print(line, flush=True)
        trace_log.append(line)
        write_report("\n".join(trace_log) + "\n```")

    log_event("1. Starting trace script.")
    gc.collect()
    log_event(f"Initial RAM: {get_ram_mb():.2f} MB")
    
    log_event("2. Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    log_event("3. Tokenizer loaded successfully.")
    
    is_loading = True
    
    def memory_monitor():
        while is_loading:
            log_event(f"    [MONITOR] Current RAM: {get_ram_mb():.2f} MB")
            for _ in range(100): # Sleep 10s in 0.1s intervals
                if not is_loading:
                    break
                time.sleep(0.1)

    monitor_thread = threading.Thread(target=memory_monitor, daemon=True)
    
    log_event("4. Starting model load (AutoModelForCausalLM.from_pretrained)...")
    monitor_thread.start()
    
    load_start = time.time()
    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            low_cpu_mem_usage=True,
            torch_dtype="auto"
        )
        is_loading = False
        monitor_thread.join()
        
        load_time = time.time() - load_start
        log_event(f"5. Model loaded successfully in {load_time:.2f}s. Final RAM: {get_ram_mb():.2f} MB")
        
        log_event("6. Building pipeline...")
        pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, device_map="auto")
        
        log_event("7. Starting generation: 'Hello' (5 tokens)...")
        gen_start = time.time()
        result = pipe("Hello", max_new_tokens=5, do_sample=False)
        gen_time = time.time() - gen_start
        
        output_text = result[0]['generated_text']
        log_event(f"8. Generation SUCCESS in {gen_time:.2f}s. Output: '{output_text}'")
        
    except Exception as e:
        is_loading = False
        monitor_thread.join()
        log_event(f"❌ ERROR DURING LOAD: {type(e).__name__} - {e}")

if __name__ == "__main__":
    main()
