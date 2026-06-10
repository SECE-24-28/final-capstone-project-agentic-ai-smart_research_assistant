from transformers import AutoTokenizer, AutoModelForCausalLM
import time

MODEL = "Qwen/Qwen2.5-1.5B-Instruct"

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL)

print("Loading model...")
start = time.time()

model = AutoModelForCausalLM.from_pretrained(
    MODEL,
    trust_remote_code=True,
    low_cpu_mem_usage=True,
    torch_dtype="auto"
)

print(f"Loaded in {time.time()-start:.2f}s")

prompt = "What is machine learning?"

messages = [
    {"role": "user", "content": prompt}
]

text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)

inputs = tokenizer(text, return_tensors="pt")

print("Generating...")

outputs = model.generate(
    **inputs,
    max_new_tokens=50
)

response = tokenizer.decode(
    outputs[0],
    skip_special_tokens=True
)

print("\nRESPONSE:")
print(response)
