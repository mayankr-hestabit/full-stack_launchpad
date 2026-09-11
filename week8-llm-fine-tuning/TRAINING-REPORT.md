# Week 8 — Day 2: QLoRA Fine-Tuning Report

## 1. Objective

The objective of Day 2 was to fine-tune a lightweight instruction-following LLM using PEFT with QLoRA.

The base model used was:

```text
Qwen/Qwen2.5-1.5B-Instruct
```

The training configuration followed the Day 2 assignment requirements:

```text
LoRA rank (r): 16
Learning rate: 2e-4
Batch size: 4
Epochs: 3
Base model loading: 4-bit
```

The goal was to update only a small percentage of parameters while keeping the base model frozen, so that fine-tuning remained memory-efficient.

---

## 2. Dataset

The Day 1 cleaned dataset was used.

```text
Training samples:   1080
Validation samples: 120
```

The dataset was instruction-style JSONL data created for Coding / Software Engineering tasks.

It included:

- Question Answering
- Reasoning
- Extraction

The tokenizer used was:

```text
Qwen/Qwen2.5-1.5B-Instruct
```

---

## 3. Training Environment

Training was performed in Google Colab using a T4 GPU.

The main libraries used were:

```text
transformers
peft
trl
accelerate
bitsandbytes
```

During the final working setup, the environment included:

```text
Transformers: 5.16.1
TRL:          1.12.0
PEFT:         0.20.0
```

The model was loaded with 4-bit BitsAndBytes quantisation for QLoRA training.

The important quantisation settings were:

```text
4-bit quantisation: enabled
Quantisation type: NF4
Compute dtype: float16
Double quantisation: enabled
```

For trainer stability, the final notebook used:

```text
fp16 = False
bf16 = False
```

while BitsAndBytes computation still used `torch.float16`.

---

## 4. QLoRA Configuration

QLoRA combines:

```text
4-bit quantised base model
+
LoRA trainable adapter layers
```

The base model weights remained frozen, while LoRA parameters were trained.

The LoRA configuration used:

```text
r = 16
```

Target modules included:

```text
q_proj
k_proj
v_proj
o_proj
gate_proj
up_proj
down_proj
```

These modules cover the attention projections and feed-forward projections of the Qwen architecture.

---

## 5. Trainable Parameters

The final model parameter statistics were:

```text
Trainable parameters: 18,464,768
Total parameters:     1,562,179,072
Trainable percentage: 1.1820%
```

This is close to the expected approximately 1% trainable-parameter target for PEFT / LoRA.

---

## 6. Training Results

The model was trained for 3 epochs.

### Epoch 1

```text
Training loss:        0.137857
Validation loss:      0.131067
Entropy:              0.132629
Number of tokens:     96,469
Mean token accuracy:  0.953796
```

### Epoch 2

```text
Training loss:        0.121870
Validation loss:      0.116398
Entropy:              0.120509
Number of tokens:     192,938
Mean token accuracy:  0.955374
```

### Epoch 3

```text
Training loss:        0.109037
Validation loss:      0.113713
Entropy:              0.113836
Number of tokens:     289,407
Mean token accuracy:  0.955407
```

---

## 7. Training Progress

Training loss decreased across the three epochs:

```text
Epoch 1: 0.137857
Epoch 2: 0.121870
Epoch 3: 0.109037
```

Validation loss also improved:

```text
Epoch 1: 0.131067
Epoch 2: 0.116398
Epoch 3: 0.113713
```

This indicates that the model continued learning throughout training without an obvious increase in validation loss.

---

## 8. Final Training Metrics

```text
Training steps:        810 / 810
Epochs completed:      3 / 3
Training runtime:      899.3703 seconds
Approximate runtime:   14 minutes 59 seconds
Train samples/sec:     3.603
Train steps/sec:       0.901
Total FLOPs:           2904024420925440.0
Overall training loss: 0.18654467191225216
```

---

## 9. Final Evaluation Metrics

```text
Evaluation loss:       0.11371329426765442
Evaluation entropy:    0.1138362355530262
Evaluation tokens:     289407
Mean token accuracy:   0.9554066677888234
```

The final mean token accuracy was approximately:

```text
95.54%
```

---

## 10. Adapter Artifacts

The trained LoRA adapter was saved in:

```text
adapters/
├── adapter_model.safetensors
└── adapter_config.json
```

### adapter_model.safetensors

Contains the learned LoRA weights. It stores the parameter updates learned during fine-tuning rather than the entire Qwen base model.

### adapter_config.json

Stores the PEFT / LoRA configuration required to correctly attach the adapter to the base model, including information such as LoRA rank, alpha, target modules, and base-model configuration.

---

## 11. Why `.safetensors` Instead of `.bin`

The original assignment mentioned:

```text
/adapters/adapter_model.bin
```

The installed modern PEFT version saved the adapter as:

```text
adapter_model.safetensors
```

This is the modern equivalent for storing the learned adapter weights, so retraining was not required simply to produce a `.bin` extension.

---

## 12. Reconstructing the Fine-Tuned Model

The adapter is not a complete standalone model.

The fine-tuned model is reconstructed as:

```text
Qwen base model
+
adapter_model.safetensors
+
adapter_config.json
=
fine-tuned Qwen model
```

Conceptually:

```python
base_model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-1.5B-Instruct"
)

model = PeftModel.from_pretrained(
    base_model,
    "adapters"
)
```

If a standalone merged model is required:

```python
model = model.merge_and_unload()
```

This merged fine-tuned model was later used during Day 3 quantisation.

---

## 13. Day 2 Flow

```text
Day 1 training dataset
        ↓
Load Qwen tokenizer
        ↓
Load Qwen base model in 4-bit
        ↓
Prepare model for k-bit training
        ↓
Attach LoRA layers
        ↓
Train only LoRA parameters
        ↓
Evaluate on validation dataset
        ↓
Save LoRA adapter
```

In simplified form:

```text
Qwen base model
+
4-bit loading
+
LoRA
+
1080 training samples
        ↓
QLoRA fine-tuning
        ↓
adapter_model.safetensors
adapter_config.json
```

---

## 14. Key Observations

1. QLoRA allowed the 1.5B Qwen model to be fine-tuned efficiently using a T4 GPU.
2. Only 1.1820% of the total model parameters were trainable.
3. Training loss decreased from 0.137857 in Epoch 1 to 0.109037 in Epoch 3.
4. Validation loss decreased from 0.131067 to 0.113713.
5. Mean token accuracy remained around 95.5%.
6. The full run completed successfully after 810 steps and 3 epochs.
7. The fine-tuning changes were stored as lightweight LoRA adapter files instead of saving another full copy of Qwen.
8. The adapter was later used to reconstruct and merge the fine-tuned model for Day 3 quantisation.

---

## 15. Conclusion

Day 2 successfully fine-tuned:

```text
Qwen/Qwen2.5-1.5B-Instruct
```

using QLoRA.

The model was loaded in 4-bit and LoRA adapters were trained while the original base-model parameters remained frozen.

Only approximately 1.18% of the total parameters were trainable.

Training and validation loss decreased across all three epochs, while mean token accuracy remained around 95.5%.

The final learned adapter was saved as:

```text
adapters/
├── adapter_model.safetensors
└── adapter_config.json
```

These artifacts were later used to reconstruct the fine-tuned model for Day 3 quantisation.

---

## 16. Day 2 Deliverables

```text
notebooks/
└── lora_train.ipynb

adapters/
├── adapter_model.safetensors
└── adapter_config.json

TRAINING-REPORT.md
```

`adapter_model.safetensors` serves the same role as the adapter weight file requested as `adapter_model.bin` in the assignment.
