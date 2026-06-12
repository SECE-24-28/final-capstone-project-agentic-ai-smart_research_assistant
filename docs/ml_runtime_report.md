# ML Runtime Diagnostics Report

This report tracks the exact step where the ML pipeline freezes or crashes.

| Step | Status | Time (s) | RAM (MB) |
|------|--------|----------|----------|
| 1. Torch import | ✅ SUCCESS | 1.70s | 0.88MB (+0.00MB) |
| 2. Torch CPU operation | ✅ SUCCESS | 0.19s | 0.82MB (+-0.07MB) |
| 3. SentenceTransformer load | ✅ SUCCESS | 15.77s | 0.18MB (+-0.64MB) |
| 4. Single embedding generation | ✅ SUCCESS | 0.19s | 0.25MB (+0.07MB) |
| 5. Transformers load | ✅ SUCCESS | 0.20s | 0.45MB (+0.20MB) |
| 6. Qwen tokenizer load | ✅ SUCCESS | 2.14s | 0.75MB (+0.30MB) |
| 7. Qwen model load | ⏳ IN_PROGRESS (Frozen if this remains) | - | - |
