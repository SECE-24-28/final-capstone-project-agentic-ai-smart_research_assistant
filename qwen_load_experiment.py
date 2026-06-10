import os
import time
import gc
import psutil
import threading

from transformers import AutoModelForCausalLM

def get_ram_mb():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

class MemoryMonitor:
    def __init__(self):
        self.keep_measuring = True
        self.peak_ram = 0.0
        self.thread = None

    def measure(self):
        while self.keep_measuring:
            ram = get_ram_mb()
            if ram > self.peak_ram:
                self.peak_ram = ram
            time.sleep(0.1)

    def start(self):
        self.keep_measuring = True
        self.peak_ram = get_ram_mb()
        self.thread = threading.Thread(target=self.measure, daemon=True)
        self.thread.start()

    def stop(self):
        self.keep_measuring = False
        if self.thread:
            self.thread.join(timeout=1.0)
        return self.peak_ram

def write_report(lines):
    os.makedirs("docs", exist_ok=True)
    with open("docs/qwen_loading_benchmark.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        f.write("\n")

def main():
    model_name = "Qwen/Qwen2.5-1.5B-Instruct"
    
    report = [
        "# Qwen LLM Loading Strategies Benchmark",
        "\nThis report tracks execution time and exact memory footprint (peak RAM spike vs final RAM) for different PyTorch loading configurations.\n",
        "| Strategy | Status | Load Time (s) | Peak RAM Δ (MB) | Final RAM Δ (MB) |",
        "|----------|--------|---------------|-----------------|------------------|"
    ]
    write_report(report)
    
    strategies = [
        ("Strategy B (low_cpu_mem_usage)", {"low_cpu_mem_usage": True}),
        ("Strategy C (low_cpu + torch_dtype=auto)", {"low_cpu_mem_usage": True, "torch_dtype": "auto"})
    ]

    for name, kwargs in strategies:
        print(f"Testing {name}...", flush=True)
        
        # Aggressive memory cleanup between runs
        gc.collect()
        time.sleep(2)
        start_ram = get_ram_mb()
        
        report.append(f"| {name} | ⏳ IN_PROGRESS (Frozen) | - | - | - |")
        write_report(report)
        
        monitor = MemoryMonitor()
        monitor.start()
        start_time = time.time()
        
        try:
            model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True, **kwargs)
            
            end_time = time.time()
            peak_ram = monitor.stop()
            final_ram = get_ram_mb()
            
            duration = end_time - start_time
            peak_diff = peak_ram - start_ram
            final_diff = final_ram - start_ram
            
            print(f"  -> SUCCESS in {duration:.2f}s. Peak RAM: +{peak_diff:.2f}MB, Final RAM: +{final_diff:.2f}MB")
            report[-1] = f"| {name} | ✅ SUCCESS | {duration:.2f} | +{peak_diff:.2f} | +{final_diff:.2f} |"
            write_report(report)
            
            # Unload model and free up RAM immediately
            del model
            gc.collect()
            time.sleep(2)
            
        except Exception as e:
            end_time = time.time()
            peak_ram = monitor.stop()
            final_ram = get_ram_mb()
            
            duration = end_time - start_time
            peak_diff = peak_ram - start_ram
            final_diff = final_ram - start_ram
            
            err_type = type(e).__name__
            print(f"  -> FAILED: {err_type} - {str(e)}")
            report[-1] = f"| {name} | ❌ FAILED ({err_type}) | {duration:.2f} | +{peak_diff:.2f} | +{final_diff:.2f} |"
            report.append(f"\n**Error in {name}:** `{err_type}: {str(e)}`\n")
            write_report(report)

    print("Benchmarking complete.")

if __name__ == "__main__":
    main()
