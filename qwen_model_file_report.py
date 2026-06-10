import os
import json
from huggingface_hub import snapshot_download

def get_dir_size(path="."):
    total = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # handle symlinks if necessary
            if os.path.islink(fp):
                fp = os.path.realpath(fp)
            try:
                total += os.path.getsize(fp)
            except OSError:
                pass
    return total

def main():
    model_id = "Qwen/Qwen2.5-1.5B-Instruct"
    print(f"Inspecting local cache for: {model_id}")
    
    try:
        model_path = snapshot_download(model_id, local_files_only=True)
        print(f"Found at: {model_path}")
    except Exception as e:
        print(f"Error finding model in cache: {e}")
        # Manual fallback
        home = os.path.expanduser("~")
        model_path = os.path.join(home, ".cache", "huggingface", "hub", "models--Qwen--Qwen2.5-1.5B-Instruct")
        if not os.path.exists(model_path):
            print("Fallback also failed.")
            return
        
        # find the snapshots folder
        snapshots_dir = os.path.join(model_path, "snapshots")
        if os.path.exists(snapshots_dir):
            snapshots = os.listdir(snapshots_dir)
            if snapshots:
                model_path = os.path.join(snapshots_dir, snapshots[0])
            else:
                return
        else:
            return

    files = []
    for f in os.listdir(model_path):
        if os.path.isfile(os.path.join(model_path, f)):
            files.append(f)
            
    safetensors = [f for f in files if f.endswith('.safetensors')]
    num_shards = len(safetensors)
    
    total_size_bytes = get_dir_size(model_path)
    total_size_mb = total_size_bytes / (1024 * 1024)
    total_size_gb = total_size_bytes / (1024 * 1024 * 1024)
    
    tokenizer_files = [f for f in files if "token" in f or "vocab" in f or "merges" in f]
    
    config_arch = "Unknown"
    if "config.json" in files:
        try:
            with open(os.path.join(model_path, "config.json"), "r", encoding="utf-8") as f:
                config = json.load(f)
                config_arch = config.get("architectures", ["Unknown"])[0]
        except Exception as e:
            print(f"Error reading config: {e}")

    report = [
        "# Qwen Model File Inspection Report\n",
        f"**Model ID:** `{model_id}`",
        f"**Local Cache Path:** `{model_path}`\n",
        "## Analysis Metrics",
        f"- **Total Safetensor Shards:** {num_shards}",
        f"- **Total Size on Disk:** {total_size_mb:.2f} MB ({total_size_gb:.2f} GB)",
        f"- **Config Architecture:** `{config_arch}`",
        f"- **Tokenizer Files:** {', '.join(tokenizer_files) if tokenizer_files else 'None found'}\n",
        "## Exact File Manifest",
    ]
    
    for f in sorted(files):
        size_mb = os.path.getsize(os.path.realpath(os.path.join(model_path, f))) / (1024 * 1024)
        report.append(f"- `{f}` ({size_mb:.2f} MB)")
        
    os.makedirs("docs", exist_ok=True)
    with open("docs/qwen_model_file_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report))
        
    print("Report generated successfully: docs/qwen_model_file_report.md")

if __name__ == "__main__":
    main()
