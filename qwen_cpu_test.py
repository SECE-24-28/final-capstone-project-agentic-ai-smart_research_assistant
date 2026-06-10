import os
import time
import gc
import psutil
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

def get_ram_mb():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

def write_report(lines):
    os.makedirs("docs", exist_ok=True)
    with open("docs/qwen_cpu_test_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        f.write("\n")

def main():
    model_name = "Qwen/Qwen2.5-1.5B-Instruct"
    
    report = [
        "# Qwen CPU Test Report\n",
        "Testing isolated loading strategy with `low_cpu_mem_usage=True` and `torch_dtype=\"auto\"`.\n",
        "| Metric | Value |",
        "|--------|-------|"
    ]
    
    print("Testing isolated Qwen CPU Load...")
    gc.collect()
    time.sleep(1)
    
    start_ram = get_ram_mb()
    report.append(f"| Initial RAM | {start_ram:.2f} MB |")
    write_report(report)
    
    report.append("| Status | ⏳ IN_PROGRESS (Frozen) |")
    write_report(report)
    
    start_time = time.time()
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            low_cpu_mem_usage=True,
            torch_dtype="auto"
        )
        
        load_time = time.time() - start_time
        after_load_ram = get_ram_mb()
        
        print(f"Loaded successfully in {load_time:.2f}s. RAM: {after_load_ram:.2f} MB")
        report[-1] = "| Status | ✅ Model Loaded |"
        report.append(f"| Load Time | {load_time:.2f} s |")
        report.append(f"| RAM After Load | {after_load_ram:.2f} MB |")
        write_report(report)
        
        print("Running generation test...")
        report.append("| Generation | ⏳ IN_PROGRESS |")
        write_report(report)
        
        pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, device_map="auto")
        
        gen_start = time.time()
        result = pipe("Hello", max_new_tokens=5, do_sample=False)
        gen_time = time.time() - gen_start
        
        print(f"Generation output: {result}")
        report[-1] = f"| Generation | ✅ SUCCESS ({gen_time:.2f} s) |"
        report.append(f"| Output | `{result[0]['generated_text']}` |")
        write_report(report)
        
    except Exception as e:
        end_time = time.time()
        err_type = type(e).__name__
        print(f"FAILED: {err_type} - {e}")
        report[-1] = f"| Status | ❌ FAILED ({err_type}) |"
        report.append(f"| Failed After | {end_time - start_time:.2f} s |")
        report.append(f"\n**Error Details:** `{err_type}: {str(e)}`")
        write_report(report)

if __name__ == "__main__":
    main()
