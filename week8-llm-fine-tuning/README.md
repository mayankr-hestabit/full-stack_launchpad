# Week 8 — LLM Fine-Tuning, Quantisation & Optimised Inference

This project implements a complete end-to-end Large Language Model workflow, starting from dataset preparation and continuing through fine-tuning, quantisation, inference benchmarking, API deployment, streaming responses, chat memory, Streamlit UI, and Docker deployment.

The selected base model is:

```text
Qwen/Qwen2.5-1.5B-Instruct
```

The final deployment uses a fine-tuned and quantised GGUF Q4_0 version of the model through `llama.cpp`.

## Project Objectives

1. Prepare and validate an instruction dataset
2. Fine-tune a pretrained LLM using QLoRA
3. Save and reuse LoRA adapters
4. Merge and quantise the fine-tuned model
5. Compare FP16, INT8, INT4, and GGUF formats
6. Benchmark inference performance
7. Implement streaming and batch inference
8. Deploy the model through FastAPI
9. Implement persistent chat sessions
10. Add generation controls
11. Build a Streamlit UI
12. Package the application using Docker
13. Prepare the API architecture for future RAG and agent integration

## Technology Stack

```text
Python
PyTorch
Hugging Face Transformers
PEFT
TRL
Accelerate
BitsAndBytes
Qwen2.5-1.5B-Instruct
LoRA / QLoRA
llama.cpp
GGUF
FastAPI
Uvicorn
HTTPX
Pydantic
Streamlit
Docker
CUDA
```

## Project Structure

```text
week8-llm-fine-tuning/
├── data/
│   ├── train.jsonl
│   └── val.jsonl
├── utils/
│   └── data_cleaner.py
├── notebooks/
│   ├── lora_train.ipynb
│   └── quantization_day3.ipynb
├── adapters/
│   ├── adapter_model.safetensors
│   └── adapter_config.json
├── quantized/
│   ├── model-int8/
│   ├── model-int4/
│   └── model.gguf
├── inference/
│   └── test_inference.py
├── benchmarks/
│   └── results.csv
├── deploy/
│   ├── app.py
│   ├── config.py
│   ├── model_loader.py
│   └── streamlit_app.py
├── compare_all_models_local.py
├── DATASET-ANALYSIS.md
├── TRAINING-REPORT.md
├── QUANTISATION-REPORT.md
├── BENCHMARK-REPORT.md
├── FINAL-REPORT.md
├── README.md
└── DOCKERFILE
```

# Day 1 — Dataset Preparation

The selected domain was Coding / Software Engineering. The dataset contained 1200 records: 400 Question Answering, 400 Reasoning, and 400 Information Extraction samples.

Validation results:

```text
Total records      : 1200
Valid records      : 1200
Invalid JSON       : 0
Rejected records   : 0
Duplicates removed : 0
```

Dataset split:

```text
Training samples   : 1080
Validation samples : 120
Random seed        : 42
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

Detailed analysis: `DATASET-ANALYSIS.md`

# Day 2 — QLoRA Fine-Tuning

Base model:

```text
Qwen/Qwen2.5-1.5B-Instruct
```

Training configuration:

```text
LoRA Rank       : 16
Learning Rate   : 2e-4
Batch Size      : 4
Epochs          : 3
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

Detailed report: `TRAINING-REPORT.md`

# Day 3 — Quantisation

Formats compared:

```text
FP16
INT8
INT4
GGUF Q4_0
```

Generated artifacts:

```text
quantized/model-int8/
quantized/model-int4/
quantized/model.gguf
```

| Model | Approximate Size | Speed | Quality |
|---|---:|---:|---|
| FP16 | 2.944 GB | 3.676 tok/s | Pass |
| INT8 | 1.668 GB | 2.253 tok/s | Pass |
| INT4 | 1.075 GB | 5.907 tok/s | Pass |
| GGUF Q4_0 | ~0.87 GB | ~11.1 tok/s | Pass |

The GGUF result used llama.cpp on CPU, so it is not a strict same-hardware comparison.

Detailed report: `QUANTISATION-REPORT.md`

# Day 4 — Inference Benchmarking

Models benchmarked:

```text
Base Qwen FP16
Fine-Tuned Qwen + LoRA FP16
GGUF Q4_0
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

Final benchmark:

| Model | Avg Latency | Avg Tokens/sec | Peak VRAM | Accuracy |
|---|---:|---:|---:|---:|
| Base Qwen FP16 | 3.018 s | 23.611 | 2.892 GB | 100% |
| Fine-Tuned Qwen + LoRA | 1.390 s | 12.335 | 2.969 GB | 100% |
| GGUF Q4_0 | 12.055 s | 7.140 | 0 GB GPU | 100% |

Base and fine-tuned models were tested on a Tesla T4 GPU. GGUF was tested using llama.cpp on CPU. GGUF latency included cold-start overhead.

Results: `benchmarks/results.csv`

Detailed report: `BENCHMARK-REPORT.md`

# Day 5 — Local LLM Deployment

Final architecture:

```text
Streamlit UI
      ↓
FastAPI
      ↓
Persistent llama-server
      ↓
Fine-Tuned GGUF Q4_0
```

The GGUF Q4_0 model was selected because it is compact, CPU-compatible, requires no GPU VRAM, and works with llama.cpp.

Approximate size:

```text
892 MB
```

## Model Caching

```text
Start API
   ↓
Start llama-server
   ↓
Load model.gguf once
   ↓
Keep model in memory
   ↓
Serve multiple requests
```

## API Endpoints

```text
POST /generate
POST /chat
```

Example `/generate` request:

```json
{
  "prompt": "Explain Docker in simple terms.",
  "system_prompt": "You are a helpful coding and software engineering assistant.",
  "temperature": 0.3,
  "top_p": 0.9,
  "top_k": 40,
  "max_tokens": 256,
  "stream": false
}
```

Example `/chat` request:

```json
{
  "message": "What is Docker?",
  "session_id": "example-session",
  "system_prompt": "You are a helpful coding assistant.",
  "temperature": 0.3,
  "top_p": 0.9,
  "top_k": 40,
  "max_tokens": 256,
  "stream": false
}
```

## Generation Controls

- **Temperature**: controls randomness.
- **Top-K**: restricts sampling to the K most probable next-token candidates.
- **Top-P**: uses cumulative probability sampling.
- **Max Tokens**: limits maximum generated tokens.
- **System Prompt**: defines assistant behaviour.

## Streaming

Streaming returns generated text incrementally instead of waiting for the full response.

## Request IDs and Logging

Each API request receives a unique UUID for debugging, monitoring, and traceability.

## Streamlit UI

Located at:

```text
deploy/streamlit_app.py
```

Modes:

```text
Generate
Chat
```

Sidebar controls:

```text
Temperature
Top-P
Top-K
Max Tokens
System Prompt
```

# Running the Project

Activate environment:

```bash
source .venv/bin/activate
```

Start FastAPI:

```bash
uvicorn deploy.app:app --host 0.0.0.0 --port 8000
```

FastAPI docs:

```text
http://127.0.0.1:8000/docs
```

Start Streamlit in another terminal:

```bash
source .venv/bin/activate
streamlit run deploy/streamlit_app.py
```

# Docker Deployment

Build:

```bash
docker build -f DOCKERFILE -t week8-local-llm .
```

Run:

```bash
docker run -p 8000:8000 week8-local-llm
```

# Final Pipeline

```text
Raw Instruction Dataset
          ↓
Validation and Cleaning
          ↓
Train / Validation Split
          ↓
Qwen2.5-1.5B-Instruct
          ↓
QLoRA Fine-Tuning
          ↓
LoRA Adapter
          ↓
Fine-Tuned Model
          ↓
Quantisation
      /      |          INT8     INT4    GGUF Q4_0
                      ↓
                  llama.cpp
                      ↓
               Persistent Server
                      ↓
                   FastAPI
                      ↓
                  Streamlit
```

# Future Integration

The API is ready for future integration with RAG, vector databases, knowledge bases, agents, external tools, and document retrieval systems.

# Final Outcome

The project successfully implemented dataset preparation, token analysis, QLoRA fine-tuning, LoRA adapters, quantisation, GGUF conversion, inference benchmarking, streaming, batching, persistent model loading, FastAPI deployment, chat history, runtime generation controls, request IDs, logging, Streamlit UI, and Docker deployment.
