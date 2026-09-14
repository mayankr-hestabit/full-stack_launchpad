# FINAL REPORT
## Week 8 — LLM Fine-Tuning, Quantisation & Optimised Inference

# 1. Introduction

The objective of Week 8 was to understand and implement the complete lifecycle of a Large Language Model, beginning with dataset preparation and ending with a locally deployable inference service.

The project covered five stages:

```text
Day 1 — Dataset Preparation
Day 2 — QLoRA Fine-Tuning
Day 3 — Quantisation
Day 4 — Inference Benchmarking
Day 5 — Local LLM API Deployment
```

Base model:

```text
Qwen/Qwen2.5-1.5B-Instruct
```

Final deployment:

```text
Fine-Tuned Qwen
        ↓
GGUF Q4_0
        ↓
llama.cpp
        ↓
FastAPI
        ↓
Streamlit
```

# 2. Project Goals

The project aimed to prepare an instruction dataset, fine-tune an open-source LLM with QLoRA, quantise the resulting model, benchmark inference performance, implement streaming and batching, deploy a local API, support multi-turn chat, expose sampling controls, add logging and request IDs, build a Streamlit UI, and package the application using Docker.

# 3. Day 1 — Dataset Preparation

## Objective

A coding and software engineering instruction dataset was prepared for supervised fine-tuning.

Dataset:

```text
1200 total records
400 Question Answering
400 Reasoning
400 Information Extraction
```

Validation:

```text
Total records      : 1200
Valid records      : 1200
Invalid JSON       : 0
Rejected records   : 0
Duplicates removed : 0
```

Split:

```text
Training   : 1080
Validation : 120
Seed       : 42
```

Tokenizer:

```text
Qwen/Qwen2.5-1.5B-Instruct
```

Token statistics:

```text
Minimum : 19
Maximum : 105
Average : 61.91
Median  : 65
Q1      : 35.75
Q3      : 79
IQR     : 43.25
Outliers: 0
```

Day 1 outputs:

```text
data/train.jsonl
data/val.jsonl
utils/data_cleaner.py
DATASET-ANALYSIS.md
```

# 4. Day 2 — QLoRA Fine-Tuning

## Objective

The pretrained Qwen model was adapted to the coding domain using QLoRA.

QLoRA combines a quantised base model with LoRA adapters so only a small fraction of parameters need to be trained.

Training configuration:

```text
LoRA Rank      : 16
Learning Rate  : 2e-4
Batch Size     : 4
Epochs         : 3
```

Target modules:

```text
q_proj
k_proj
v_proj
o_proj
gate_proj
up_proj
down_proj
```

Parameter efficiency:

```text
Trainable parameters : 18,464,768
Total parameters     : 1,562,179,072
Trainable percentage : 1.1820%
```

Training results:

```text
Epoch 1: train 0.137857 | val 0.131067
Epoch 2: train 0.121870 | val 0.116398
Epoch 3: train 0.109037 | val 0.113713
Final mean token accuracy: ~95.54%
Training runtime: ~899 seconds
```

Adapter output:

```text
adapters/adapter_model.safetensors
adapters/adapter_config.json
```

Conceptually:

```text
Qwen Base Model
+
LoRA Adapter
=
Fine-Tuned Qwen
```

# 5. Day 3 — Quantisation

## Objective

The goal was to reduce model size and memory requirements while preserving useful output quality.

Formats compared:

```text
FP16
INT8
INT4
GGUF Q4_0
```

Artifacts:

```text
quantized/model-int8/
quantized/model-int4/
quantized/model.gguf
```

Results:

| Model | Approx Size | Tokens/sec | Quality |
|---|---:|---:|---|
| FP16 | 2.944 GB | 3.676 | Pass |
| INT8 | 1.668 GB | 2.253 | Pass |
| INT4 | 1.075 GB | 5.907 | Pass |
| GGUF Q4_0 | ~0.87 GB | ~11.1 | Pass |

INT4 gave a strong balance of size, speed, and quality. GGUF Q4_0 produced the smallest deployment artifact and enabled lightweight CPU inference through llama.cpp.

The GGUF result used CPU llama.cpp, so it is not a strict same-hardware comparison with the other formats.

# 6. Day 4 — Inference Optimisation and Benchmarking

## Objective

The following were benchmarked:

```text
Base Qwen FP16
Fine-Tuned Qwen + LoRA FP16
Fine-Tuned GGUF Q4_0
```

Metrics:

```text
Latency
Tokens per second
Peak VRAM
Semantic correctness
Streaming
Batch inference
Multi-prompt inference
KV caching
```

Environment:

```text
Base/Fine-Tuned: Tesla T4 GPU
GGUF: llama.cpp on CPU
```

Final results:

| Model | Average Latency | Avg Tokens/sec | Peak VRAM | Accuracy |
|---|---:|---:|---:|---:|
| Base Qwen FP16 | 3.018 s | 23.611 | 2.892 GB | 100% |
| Fine-Tuned + LoRA | 1.390 s | 12.335 | 2.969 GB | 100% |
| GGUF Q4_0 | 12.055 s | 7.140 | 0 GB | 100% |

The base model produced the highest raw throughput. The fine-tuned model produced shorter, more direct answers and therefore achieved lower average latency. GGUF ran with no GPU VRAM and demonstrated CPU-friendly inference.

GGUF latency included cold-start overhead:

```text
Process startup
Model loading
Prompt processing
Generation
```

Day 4 outputs:

```text
inference/test_inference.py
benchmarks/results.csv
BENCHMARK-REPORT.md
```

# 7. Streaming, Batching and KV Cache

Streaming returns generated text incrementally, improving perceived responsiveness.

Batch inference allows multiple prompts to be processed together, improving hardware utilisation in suitable workloads.

KV caching stores previously computed attention key and value states so they can be reused during autoregressive generation, reducing repeated work.

# 8. Day 5 — Local LLM Deployment

## Objective

The final quantised model was deployed as a reusable local LLM microservice.

Architecture:

```text
Streamlit
    ↓
FastAPI
    ↓
Persistent llama-server
    ↓
model.gguf
```

GGUF Q4_0 was selected because it is approximately 892 MB, CPU-compatible, requires no GPU VRAM, works with llama.cpp, and preserved useful response quality.

# 9. Persistent Model Loading

Cold-start style:

```text
Request
↓
Start llama-cli
↓
Load model
↓
Generate
↓
Exit
```

Day 5 deployment:

```text
Start Application
↓
Start llama-server
↓
Load model once
↓
Keep model in RAM
↓
Serve multiple requests
```

This implements model caching.

# 10. FastAPI Service

Endpoints:

```text
POST /generate
POST /chat
```

`POST /generate` handles one-off generation.

`POST /chat` supports multi-turn conversation using a `session_id`.

# 11. Generation Parameters

## Temperature

Controls randomness. Lower values are more focused and predictable; higher values are more varied.

## Top-K

Restricts sampling to the K most probable next-token candidates.

## Top-P

Keeps the smallest set of highly probable next tokens whose cumulative probability reaches the configured threshold.

## Maximum Tokens

Limits how many output tokens may be generated.

## System Prompt

Controls the intended behaviour and role of the assistant.

# 12. Request IDs and Logging

Each API request receives a UUID for debugging, monitoring, traceability, and log analysis.

# 13. Streamlit UI

The Streamlit interface provides:

```text
Generate mode
Chat mode
```

Sidebar controls:

```text
Temperature
Top-P
Top-K
Max Tokens
System Prompt
```

The UI allows generation behaviour to be changed without modifying code.

# 14. Docker Deployment

Docker packages the application runtime, FastAPI dependencies, Streamlit dependencies, llama.cpp, and application source code into a reproducible environment.

# 15. Complete Architecture

```text
                         RAW DATA
                            ↓
                  Cleaning / Validation
                            ↓
                  Train / Validation Split
                            ↓
                Qwen2.5-1.5B-Instruct
                            ↓
                         QLoRA
                            ↓
                      LoRA Adapter
                            ↓
                  Fine-Tuned Qwen Model
                            ↓
                       Quantisation
                 /          |                        INT8         INT4       GGUF Q4_0
                                         ↓
                                     llama.cpp
                                         ↓
                                  Persistent Server
                                         ↓
                                      FastAPI
                                         ↓
                                     Streamlit
```

# 16. Key Learnings

The project provided practical experience with instruction datasets, tokenisation, LoRA, QLoRA, parameter-efficient fine-tuning, quantisation, GGUF, llama.cpp, CPU/GPU inference, tokens-per-second benchmarking, latency measurement, VRAM measurement, streaming, batching, KV caching, sampling controls, FastAPI, chat state, model caching, request IDs, logging, Streamlit, and Docker.

# 17. Challenges Faced

## Package Compatibility

Fine-tuning required compatible versions of PyTorch, Transformers, PEFT, TRL, BitsAndBytes, and CUDA-related packages.

## Local GPU Configuration

The local GTX 1650 initially had CUDA compatibility issues. A compatible PyTorch CUDA build was later installed successfully.

## Local Memory Limitations

WSL memory was insufficient for some FP16 benchmarking tasks, so Google Colab with a Tesla T4 GPU was used for Day 4 Transformer benchmarks.

## llama.cpp Build

A CUDA-enabled llama.cpp build initially required the full CUDA toolkit and `nvcc`, so CPU llama.cpp inference was used successfully.

## Benchmark Parsing

llama.cpp reported generation speed in a format similar to:

```text
Generation: X t/s
```

The benchmark parsing logic was corrected to extract the actual generation throughput.

# 18. Final Results

The project successfully produced:

```text
Clean instruction dataset
Fine-tuned LoRA adapter
INT8 model
INT4 model
GGUF Q4_0 model
Inference benchmarks
FastAPI inference API
Multi-turn chat API
Streaming generation
Streamlit interface
Docker configuration
```

Final GGUF size:

```text
~892 MB
```

FP16 representation:

```text
~2.944 GB
```

This demonstrates a substantial reduction in model storage while maintaining useful response quality.

# 19. Future RAG and Agent Integration

The API can later be connected to retrievers, vector databases, knowledge bases, agents, and external tools.

Example:

```text
User Query
    ↓
Retriever
    ↓
Relevant Context
    ↓
Prompt Builder
    ↓
FastAPI
    ↓
Local LLM
```

# 20. Conclusion

Week 8 implemented a complete LLM engineering pipeline:

```text
Dataset Preparation
        ↓
QLoRA Fine-Tuning
        ↓
Model Quantisation
        ↓
Inference Benchmarking
        ↓
Optimised Local Deployment
```

The project began with a 1200-record software-engineering instruction dataset, fine-tuned Qwen2.5-1.5B-Instruct using QLoRA, produced INT8, INT4, and GGUF artifacts, benchmarked base, fine-tuned, and quantised inference, and deployed the GGUF model using llama.cpp, FastAPI, and Streamlit.

The final result is a lightweight, locally deployable coding-focused language model with streaming, multi-turn chat, runtime sampling controls, model caching, logging, request IDs, and Docker support.
