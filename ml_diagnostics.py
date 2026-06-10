import time
import os
import sys

def get_ram_mb():
    try:
        import psutil
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 * 1024)
    except ImportError:
        # Fallback for windows using tasklist
        try:
            output = os.popen(f'tasklist /FI "PID eq {os.getpid()}" /FO CSV').read()
            parts = output.strip().split('\n')[-1].split(',')
            mem_str = parts[-1].replace('"', '').replace(' K', '').replace(',', '')
            return int(mem_str) / 1024
        except:
            return 0.0

def run_diagnostics():
    report = [
        "# ML Runtime Diagnostics Report\n",
        "This report tracks the exact step where the ML pipeline freezes or crashes.\n",
        "| Step | Status | Time (s) | RAM (MB) |",
        "|------|--------|----------|----------|"
    ]
    
    print("Starting ML Diagnostics...")
    
    def write_report(rep):
        os.makedirs("docs", exist_ok=True)
        with open("docs/ml_runtime_report.md", "w", encoding="utf-8") as f:
            f.write("\n".join(rep))
            f.write("\n")

    def log_step(name, func):
        print(f"Running: {name}...")
        start_time = time.time()
        start_ram = get_ram_mb()
        
        report.append(f"| {name} | ⏳ IN_PROGRESS (Frozen if this remains) | - | - |")
        write_report(report)
        
        try:
            func()
            end_time = time.time()
            end_ram = get_ram_mb()
            duration = end_time - start_time
            ram_diff = end_ram - start_ram
            
            print(f"  -> SUCCESS ({duration:.2f}s, RAM: {end_ram:.2f}MB (+{ram_diff:.2f}MB))")
            report[-1] = f"| {name} | ✅ SUCCESS | {duration:.2f}s | {end_ram:.2f}MB (+{ram_diff:.2f}MB) |"
            write_report(report)
            
        except Exception as e:
            end_time = time.time()
            end_ram = get_ram_mb()
            duration = end_time - start_time
            
            print(f"  -> FAILED: {e}")
            report[-1] = f"| {name} | ❌ FAILED | {duration:.2f}s | {end_ram:.2f}MB |"
            report.append(f"\n**Error Details:** `{type(e).__name__}: {str(e)}`")
            write_report(report)
            sys.exit(1)

    # Isolated Steps
    
    def step1():
        global torch
        import torch
    
    def step2():
        x = torch.rand(1000, 1000)
        y = torch.rand(1000, 1000)
        z = torch.matmul(x, y)
        
    def step3():
        global SentenceTransformer, embedding_model
        from sentence_transformers import SentenceTransformer
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        
    def step4():
        embedding_model.encode(["This is a test sentence."])
        
    def step5():
        global AutoModelForCausalLM, AutoTokenizer, pipeline
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
        
    def step6():
        global tokenizer
        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct", trust_remote_code=True)
        
    def step7():
        global model, pipe
        model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct", trust_remote_code=True)
        pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, device_map="auto")
        
    def step8():
        prompt = "Hello, world! Can you hear me?"
        pipe(prompt, max_new_tokens=1)

    steps = [
        ("1. Torch import", step1),
        ("2. Torch CPU operation", step2),
        ("3. SentenceTransformer load", step3),
        ("4. Single embedding generation", step4),
        ("5. Transformers load", step5),
        ("6. Qwen tokenizer load", step6),
        ("7. Qwen model load", step7),
        ("8. Single-token generation", step8),
    ]

    write_report(report)
    for name, func in steps:
        log_step(name, func)

    report.append("\n**Diagnostics Complete. All ML components executed successfully without freezing!**")
    write_report(report)

if __name__ == "__main__":
    run_diagnostics()
