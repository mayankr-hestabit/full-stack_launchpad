# Week 8 — Day 4: Inference Optimisation & Benchmark Report

## 1. Objective

The objective of Day 4 was to benchmark and compare inference performance across three versions of the Qwen model:

1. **Base model** — `Qwen/Qwen2.5-1.5B-Instruct`
2. **Fine-tuned model** — Qwen FP16 with the trained LoRA adapter attached
3. **Quantized model** — fine-tuned GGUF Q4_0 model executed using `llama.cpp`

The main metrics evaluated were:
;
- latency
- tokens per second
- VRAM usage
- response correctness / quality

The Day 4 exercise also demonstrated:

- streaming output
- batch inference
- multi-prompt inference

---

## 2. Models Evaluated

### 2.1 Base Qwen FP16

The original instruction-tuned model was used without the Day 2 LoRA adapter:

```text
Qwen/Qwen2.5-1.5B-Instruct
```

It was loaded in FP16 and executed on a Tesla T4 GPU.

### 2.2 Fine-tuned Qwen + LoRA FP16

The fine-tuned model was reconstructed as:

```text
Qwen base model
+
Day 2 LoRA adapter
```

The adapter files were:

```text
adapters/
├── adapter_model.safetensors
└── adapter_config.json
```

The model was executed in FP16 on the Tesla T4 GPU.

### 2.3 GGUF Q4_0

The fine-tuned model had previously been converted to GGUF and quantized using Q4_0:

```text
quantized/model.gguf
```

It was executed through `llama.cpp` using CPU inference.

---

## 3. Benchmark Environment

The Day 4 benchmark was executed in Google Colab.

### Transformers models

```text
GPU: Tesla T4
CUDA: Available
Precision: FP16
Runtime: Hugging Face Transformers + PEFT
```

The base and fine-tuned models used the T4 GPU.

### GGUF model

```text
Runtime: llama.cpp
Quantization: Q4_0
Execution: CPU
GPU offload: 0 layers
```

Therefore, the GGUF speed and latency values are **not a strict same-hardware comparison** against the FP16 Transformer models.

---

## 4. Test Prompts

The same five prompts were used for all three models:

```text
1. Explain Docker containers in simple terms.
2. What is GitHub?
3. What is an API?
4. What does HTTP stand for?
5. What is a Python list?
```

This provides a consistent multi-prompt test across all model variants.

---

## 5. Metrics

### Latency

Latency represents the elapsed time required to complete generation for a prompt.

```text
Lower latency = faster response completion
```

### Tokens per second

Tokens per second measures generation throughput.

```text
Higher tokens/sec = faster text generation
```

### VRAM

Peak GPU memory usage was measured for the FP16 Transformer models.

The GGUF model ran on CPU, so its GPU VRAM usage was:

```text
0 GB
```

### Accuracy / quality

The generated responses were reviewed for semantic correctness.

The original automated keyword checker produced two false negatives on the API prompt even though the answers were valid. These two entries were corrected by semantic review in the final `results.csv`.

---

## 6. Final Benchmark Summary

| Model | Avg Latency (s) | Avg Tokens/sec | Peak VRAM (GB) | Accuracy |
|---|---:|---:|---:|---:|
| Base Qwen FP16 | 3.018 | 23.611 | 2.892 | 100% |
| Fine-tuned Qwen + LoRA FP16 | 1.390 | 12.335 | 2.969 | 100% |
| GGUF Q4_0 | 12.055 | 7.140 | 0.000 | 100% |

---

## 7. Base Qwen FP16 Results

Per-prompt performance:

| Prompt | Latency (s) | Tokens/sec | Peak VRAM (GB) | Correct |
|---|---:|---:|---:|---:|
| Docker | 4.076 | 19.629 | 2.892 | Yes |
| GitHub | 3.169 | 25.242 | 2.891 | Yes |
| API | 3.015 | 26.533 | 2.892 | Yes |
| HTTP | 0.870 | 26.439 | 2.889 | Yes |
| Python list | 3.958 | 20.211 | 2.892 | Yes |

Average results:

```text
Average latency:    3.018 sec
Average throughput: 23.611 tokens/sec
Peak VRAM:          2.892 GB
Accuracy:           100%
```

The base model generally produced longer and more detailed responses.

---

## 8. Fine-tuned Qwen + LoRA FP16 Results

Per-prompt performance:

| Prompt | Latency (s) | Tokens/sec | Peak VRAM (GB) | Correct |
|---|---:|---:|---:|---:|
| Docker | 1.291 | 13.172 | 2.969 | Yes |
| GitHub | 2.022 | 12.861 | 2.969 | Yes |
| API | 1.651 | 12.721 | 2.969 | Yes |
| HTTP | 0.916 | 9.829 | 2.969 | Yes |
| Python list | 1.069 | 13.094 | 2.969 | Yes |

Average results:

```text
Average latency:    1.390 sec
Average throughput: 12.335 tokens/sec
Peak VRAM:          2.969 GB
Accuracy:           100%
```

The fine-tuned model generated much shorter answers than the base model. Because fewer tokens were generated, its end-to-end latency was lower even though its token generation throughput was lower.

This distinction is important:

```text
lower total latency does not necessarily mean higher tokens/sec
```

---

## 9. GGUF Q4_0 Results

The raw script initially recorded `0.0` tokens/sec because it searched for the phrase `tokens per second`, while this llama.cpp build reported performance using:

```text
Generation: X.X t/s
```

The final CSV therefore uses the actual generation rates reported by llama.cpp.

| Prompt | Latency (s) | Generation Speed (tokens/sec) | GPU VRAM | Correct |
|---|---:|---:|---:|---:|
| Docker | 27.339 | 6.1 | 0 GB | Yes |
| GitHub | 10.619 | 7.4 | 0 GB | Yes |
| API | 8.178 | 7.4 | 0 GB | Yes |
| HTTP | 6.646 | 7.4 | 0 GB | Yes |
| Python list | 7.493 | 7.4 | 0 GB | Yes |

Average results:

```text
Average latency:    12.055 sec
Average throughput: 7.140 tokens/sec
GPU VRAM:           0 GB
Accuracy:           100%
```

### GGUF latency caveat

For every prompt, the benchmark started a new `llama-cli` process and loaded `model.gguf` again.

Therefore, the GGUF latency includes:

```text
process startup
+
model loading
+
prompt processing
+
generation
```

It should be interpreted as **cold-start / end-to-end latency**, not generation-only latency.

This also explains why the first GGUF request had especially high latency.

---

## 10. Streaming Output

Streaming inference was demonstrated for:

```text
Base Qwen FP16
Fine-tuned Qwen + LoRA FP16
```

Instead of waiting for the complete answer, generated text was displayed incrementally as tokens became available.

Streaming improves the user's perceived responsiveness even when total generation time does not change significantly.

---

## 11. Batch Inference

Batch inference was tested using three prompts simultaneously.

### Base Qwen FP16

```text
Batch size:     3
Batch latency:  2.970 sec
Peak VRAM:      2.910 GB
```

### Fine-tuned Qwen + LoRA FP16

```text
Batch size:     3
Batch latency:  2.699 sec
Peak VRAM:      2.979 GB
```

Batching allows multiple requests to be processed together and can improve overall throughput when serving multiple prompts.

It also slightly increases memory usage because multiple prompt sequences are processed at the same time.

---

## 12. Multi-Prompt Test

Five different technical questions were used rather than benchmarking on only one prompt.

This tested whether performance and output quality remained consistent across different types of queries.

All three model variants produced semantically acceptable responses for all five prompts in the final manual review.

---

## 13. Key Observations

1. **Base Qwen had the highest GPU generation throughput**, averaging approximately `23.61` tokens/sec.

2. **The fine-tuned model had the lowest average end-to-end latency**, approximately `1.39` seconds, largely because its answers were significantly shorter and more direct.

3. Fine-tuning increased peak VRAM only slightly:

```text
Base:       2.892 GB
Fine-tuned: 2.969 GB
```

4. The fine-tuned model generated concise task-oriented responses compared with the more verbose base model.

5. **GGUF Q4_0 used no GPU VRAM** in this benchmark because it ran entirely through CPU `llama.cpp`.

6. GGUF averaged approximately `7.14` generation tokens/sec on CPU.

7. GGUF latency should not be directly compared with the already-loaded GPU models because each GGUF prompt included model startup/loading overhead.

8. Streaming worked correctly and provided incremental output.

9. Batch inference successfully handled three prompts at once for both FP16 Transformer models.

10. All three model variants achieved **100% semantic correctness** across the five selected prompts after manual review of the two automated false negatives.

---

## 14. Inference Optimisation Concepts Demonstrated

### KV Cache

The Transformer generation calls used:

```python
use_cache=True
```

This enables reuse of previously computed key/value attention states during autoregressive generation instead of recomputing the full sequence at every token.

### Streaming

`TextIteratorStreamer` was used to emit generated text progressively.

### Batching

Multiple prompts were tokenized and passed to the model in a single generation call.

### CPU vs GPU Inference

The benchmark demonstrated both execution modes:

```text
Base/Fine-tuned → Tesla T4 GPU
GGUF Q4_0       → CPU with llama.cpp
```

### Quantized inference

GGUF Q4_0 demonstrated lower-precision deployment of the fine-tuned model using llama.cpp.

---

## 15. vLLM, Speculative Decoding, and Prompt Compression

These are important Day 4 inference-optimisation concepts, but they were not required to generate the measured `results.csv` used in this benchmark.

### vLLM

vLLM is an inference engine designed for high-throughput LLM serving, especially when handling many concurrent requests.

### Speculative Decoding

Speculative decoding uses a smaller draft model to propose tokens that are then verified by the larger model, potentially reducing generation latency.

### Prompt Compression

Prompt compression reduces unnecessary prompt/context tokens so that the model processes less input, which can reduce inference cost and latency.

These concepts complement the practical techniques demonstrated in the benchmark: KV caching, streaming, batching, quantization, and CPU/GPU inference.

---

## 16. Conclusion

Day 4 successfully benchmarked:

```text
Base Qwen FP16
vs
Fine-tuned Qwen + LoRA FP16
vs
GGUF Q4_0
```

across latency, throughput, VRAM usage, and response correctness.

The base model achieved the highest raw GPU tokens/sec, while the fine-tuned model gave the lowest average end-to-end latency because it generated more concise responses.

The GGUF Q4_0 model successfully demonstrated CPU-only quantized inference through `llama.cpp`, using no GPU VRAM while preserving correct outputs.

Streaming, batch inference, and multi-prompt evaluation were also successfully demonstrated.

---

## 17. Day 4 Deliverables

The required Day 4 deliverables are:

```text
inference/
└── test_inference.py

benchmarks/
└── results.csv

BENCHMARK-REPORT.md
```

`results.csv` contains the cleaned, corrected raw benchmark measurements used by this report.
