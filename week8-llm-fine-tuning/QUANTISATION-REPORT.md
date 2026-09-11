# Week 8 — Day 3: Quantisation Report

## 1. Objective

The objective of Day 3 was to convert the fine-tuned Qwen model into lower-precision inference formats and compare them with the FP16 baseline.

The following model formats were evaluated:

- FP16 baseline
- INT8
- INT4
- GGUF Q4_0

The comparison focuses on:

- Model size
- Inference speed
- Latency
- Output quality

## 2. Base Model and Fine-Tuned Model

The base model used was:

```text
Qwen/Qwen2.5-1.5B-Instruct
```

The model had already been fine-tuned using QLoRA on Day 2.

The learned LoRA adapter was stored in:

```text
adapters/
├── adapter_model.safetensors
└── adapter_config.json
```

For the FP16 baseline, the Qwen base model was loaded and the Day 2 LoRA adapter was attached to reconstruct the fine-tuned model.

The same fine-tuned model was then represented in different inference formats:

```text
Fine-tuned Qwen model
        │
        ├── FP16 baseline
        ├── INT8
        ├── INT4
        └── GGUF Q4_0
```

## 3. Quantised Model Artifacts

The Day 3 artifacts are stored as:

```text
quantized/
├── model-int8/
├── model-int4/
└── model.gguf
```

### INT8

`model-int8/` contains the 8-bit quantised Hugging Face model.

INT8 reduces the precision of model weights compared with FP16, which reduces storage and memory requirements.

### INT4

`model-int4/` contains the 4-bit quantised Hugging Face model.

INT4 applies stronger compression than INT8, reducing the model size further.

### GGUF Q4_0

`model.gguf` contains the model converted to GGUF format and quantised using Q4_0.

GGUF is designed for efficient inference with runtimes such as `llama.cpp`.

The saved GGUF artifact was approximately:

```text
892 MB (~0.87 GB)
```

## 4. Test Environment

The Transformers-based models were tested locally using:

```text
GPU: NVIDIA GeForce GTX 1650
VRAM: 4 GB
CUDA available: True
```

The following models used the GPU through PyTorch/Transformers:

- FP16
- INT8
- INT4

The GGUF model was executed using:

```text
llama.cpp
llama-cli
```

The locally built `llama.cpp` runtime used the CPU backend because the full CUDA Toolkit (`nvcc`) was not installed for the llama.cpp build.

Therefore, GGUF speed should not be interpreted as a direct hardware-identical comparison with the GPU-based Transformers measurements.

## 5. Common Test Prompt

The same prompt was used for the main comparison:

```text
Explain Docker containers in simple terms.
```

Using the same prompt helps make the quality and generation-speed comparison more consistent.

## 6. FP16 Baseline Results

### Measurements

```text
Approximate weight size: 2.944 GB
Generation speed:        3.676 tokens/sec
Latency:                 4.625 sec
Quality:                 Pass
```

### Response

```text
A Docker container is an isolated running or stopped instance of a Linux container image.
```

The response was concise, relevant, and technically meaningful.

## 7. INT8 Results

The INT8 model was loaded from:

```text
quantized/model-int8/
```

### Measurements

```text
Folder size:      1.668 GB
Generation speed: 2.253 tokens/sec
Latency:          7.546 sec
Quality:          Pass
```

### Response

```text
A Docker container is an isolated running or stopped instance of a Linux container image.
```

The INT8 model produced the same response as the FP16 model for the tested prompt.

For this example, reducing the model from FP16 to INT8 did not produce an observable quality loss.

## 8. INT4 Results

The INT4 model was loaded from:

```text
quantized/model-int4/
```

### Measurements

```text
Folder size:      1.075 GB
Generation speed: 5.907 tokens/sec
Latency:          2.709 sec
Quality:          Pass
```

### Response

```text
A Docker container is an isolated running or stopped instance created from an image.
```

The response remained correct and relevant.

Compared with FP16 and INT8, INT4 produced the highest measured generation speed in the local Transformers test while also having the smallest Hugging Face model size.

## 9. GGUF Q4_0 Results

The GGUF model was loaded using `llama.cpp`.

### Model Information

```text
Model:      quantized/model.gguf
Format:     GGUF
Quant Type: Q4_0
Modality:   Text
```

### Measurements

For the Docker prompt, llama.cpp reported:

```text
Prompt processing speed: 38.9 tokens/sec
Generation speed:        11.1 tokens/sec
Quality:                 Pass
```

A separate end-to-end latency value was not present in the captured llama.cpp output, so it is not reported here.

### Response

```text
A Docker container is an isolated running instance of a container image.
```

The response was short, correct, and relevant.

## 10. Final Comparison

| Format | Size | Generation Speed | Latency | Quality |
|---|---:|---:|---:|---|
| FP16 | 2.944 GB | 3.676 tokens/sec | 4.625 sec | Pass |
| INT8 | 1.668 GB | 2.253 tokens/sec | 7.546 sec | Pass |
| INT4 | 1.075 GB | 5.907 tokens/sec | 2.709 sec | Pass |
| GGUF Q4_0 | ~0.87 GB | 11.1 tokens/sec | N/A | Pass |

> Note: FP16, INT8, and INT4 were tested using the NVIDIA GTX 1650 through Transformers, while GGUF Q4_0 was executed using the CPU-based llama.cpp runtime. Therefore, the GGUF speed should not be treated as a strict same-hardware benchmark against the other three formats.

## 11. Size Comparison

The model size decreased significantly after quantisation.

### FP16 → INT8

```text
FP16 size = 2.944 GB
INT8 size = 1.668 GB
```

Approximate reduction:

```text
(2.944 - 1.668) / 2.944 × 100
≈ 43.3%
```

### FP16 → INT4

```text
FP16 size = 2.944 GB
INT4 size = 1.075 GB
```

Approximate reduction:

```text
(2.944 - 1.075) / 2.944 × 100
≈ 63.5%
```

### FP16 → GGUF Q4_0

Using the saved GGUF size of approximately 0.87 GB:

```text
Approximate reduction ≈ 70%
```

This shows the main advantage of quantisation: lower storage and memory requirements.

## 12. Speed Comparison

For the GPU-based Transformers tests:

```text
FP16 = 3.676 tokens/sec
INT8 = 2.253 tokens/sec
INT4 = 5.907 tokens/sec
```

INT4 was the fastest of the three Transformers-based models in this local test.

INT8 was slower than FP16 in this particular environment.

This is an important observation because lower precision does not automatically guarantee higher inference speed.

Actual performance depends on factors such as:

- GPU architecture
- Quantisation implementation
- BitsAndBytes kernels
- Memory bandwidth
- Model loading strategy
- Runtime overhead

The GGUF model reported:

```text
Generation speed = 11.1 tokens/sec
```

However, because GGUF used a different runtime and CPU execution, this value should be considered separately rather than as a strict direct comparison.

## 13. Quality Comparison

All four models passed the basic quality check for the common Docker prompt.

### FP16

```text
A Docker container is an isolated running or stopped instance of a Linux container image.
```

### INT8

```text
A Docker container is an isolated running or stopped instance of a Linux container image.
```

### INT4

```text
A Docker container is an isolated running or stopped instance created from an image.
```

### GGUF Q4_0

```text
A Docker container is an isolated running instance of a container image.
```

All responses preserved the central concept that a Docker container is an isolated instance created or run from a container image.

For this test prompt, no significant degradation in output quality was observed.

A larger evaluation set would be required to make broader conclusions about model quality.

## 14. Key Observations

1. FP16 had the largest model size at approximately 2.944 GB.
2. INT8 reduced the model size to approximately 1.668 GB.
3. INT4 reduced the model size further to approximately 1.075 GB.
4. GGUF Q4_0 produced the smallest saved artifact at approximately 892 MB.
5. INT4 provided the best generation speed among the GPU-based Transformers models in this test.
6. INT8 was slower than FP16 in this environment, demonstrating that quantisation does not always guarantee faster inference.
7. All four models generated correct and relevant answers for the tested prompt.
8. GGUF Q4_0 successfully ran using `llama.cpp`, demonstrating that the fine-tuned model can be deployed outside the standard Hugging Face Transformers runtime.

## 15. FP16 vs INT8 vs INT4 vs GGUF

### FP16

Advantages:

- Higher numerical precision
- Useful as a baseline
- Minimal quantisation-related quality risk

Disadvantages:

- Largest storage requirement
- Higher memory requirement

### INT8

Advantages:

- Smaller than FP16
- Lower memory requirement
- Preserved response quality in the test

Disadvantages:

- Was slower than FP16 in the current local environment

### INT4

Advantages:

- Much smaller than FP16
- Lower memory requirement
- Fastest Transformers-based generation result in the experiment
- Preserved response quality for the test prompt

Disadvantages:

- More aggressive quantisation can potentially affect quality on harder tasks

### GGUF Q4_0

Advantages:

- Smallest artifact among the tested models
- Designed for efficient llama.cpp inference
- Can run without the Hugging Face Transformers runtime
- Successfully generated a correct response

Disadvantages:

- Uses a different runtime from the Transformers models
- Current benchmark used CPU while the other models used GPU
- Direct speed comparison is therefore not perfectly fair

## 16. Conclusion

Day 3 successfully demonstrated post-training quantisation and optimised inference using FP16, INT8, INT4, and GGUF Q4_0 representations of the fine-tuned Qwen model.

The results show that quantisation can substantially reduce model size while preserving useful output quality.

The observed sizes were:

```text
FP16       = 2.944 GB
INT8       = 1.668 GB
INT4       = 1.075 GB
GGUF Q4_0  ≈ 0.87 GB
```

Among the GPU-based Transformers models, INT4 achieved the best measured generation speed:

```text
INT4 = 5.907 tokens/sec
```

All tested formats generated correct and relevant responses for the common Docker prompt.

Overall, INT4 provided a strong balance between model size, inference speed, and output quality in the local Transformers setup, while GGUF Q4_0 provided the smallest deployment artifact and demonstrated successful inference through llama.cpp.

## 17. Day 3 Deliverables

The required Day 3 deliverables were completed:

```text
quantized/
├── model-int8/
├── model-int4/
└── model.gguf

QUANTISATION-REPORT.md
```

Supporting implementation and comparison files include:

```text
notebooks/quantization_day3.ipynb
compare_all_models_local.py
```

`quantization_day3.ipynb` was used to create the quantised artifacts, while `compare_all_models_local.py` was used to compare FP16, INT8, INT4, and GGUF Q4_0 using a common prompt.
