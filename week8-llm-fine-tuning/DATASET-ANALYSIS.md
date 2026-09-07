# Week 8 - Day 1 Dataset Analysis

## LLM Fine-Tuning, Quantisation & Optimised Inference

---

## 1. Overview

The objective of Week 8 Day 1 is to prepare a high-quality instruction-tuning dataset that can be used for Large Language Model (LLM) fine-tuning.

The selected domain for this project is:

**Coding / Software Engineering**

A custom dataset containing **1,200 instruction-tuning samples** was prepared.

The dataset contains three types of tasks:

- Question Answering
- Reasoning
- Information Extraction

The dataset was validated, cleaned, tokenized, analysed for token-length distribution, checked for outliers, and finally divided into training and validation datasets.

The final datasets will be used during Day 2 for parameter-efficient fine-tuning using **LoRA / QLoRA**.

---

## 2. Day 1 Objectives

The main objectives of Day 1 were:

- Create a domain-specific instruction-tuning dataset
- Maintain more than 1,000 samples
- Include QA, Reasoning, and Extraction tasks
- Store samples using JSONL format
- Validate the dataset structure
- Clean textual data
- Detect invalid records
- Remove duplicate records
- Perform token-length analysis
- Visualize token-length distribution
- Detect token-length outliers
- Remove outliers where required
- Split the dataset into training and validation sets
- Prepare the data for LLM fine-tuning

---

## 3. Dataset Domain

The selected domain is:

> **Coding / Software Engineering**

This domain was selected because it can be used consistently throughout the complete Week 8 workflow.

The dataset contains examples related to technologies and concepts such as:

- Python
- JavaScript
- Node.js
- REST APIs
- HTTP
- SQL
- MongoDB
- React
- Next.js
- Git
- Docker
- Nginx
- Linux
- Networking
- Algorithms
- Logs
- API specifications
- Development commands

The same dataset can therefore be used for fine-tuning, quantisation comparison, inference benchmarking, and final API deployment.

---

## 4. Dataset Size

The original dataset contains:

| Category | Samples |
|---|---:|
| Question Answering | 400 |
| Reasoning | 400 |
| Extraction | 400 |
| **Total** | **1,200** |

The dataset is balanced across all three required instruction categories.

---

## 5. Dataset Format

The dataset is stored using **JSONL (JSON Lines)** format.

In JSONL format, every line contains one independent JSON object.

Example:

```json
{"instruction":"Explain what an API is.","input":"","output":"An API is an interface that allows software applications to communicate with each other."}
{"instruction":"Identify the HTTP method.","input":"POST /users","output":"POST"}
```

The basic schema of every training sample is:

```json
{
  "instruction": "...",
  "input": "...",
  "output": "..."
}
```

---

## 6. Meaning of Dataset Fields

### 6.1 Instruction

The `instruction` field tells the model what task it needs to perform.

Example:

```text
Explain the purpose of Docker.
```

---

### 6.2 Input

The `input` field contains additional context or information required to perform the task.

Example:

```text
A development team wants to package an application with all of its dependencies.
```

Some instructions are self-contained and therefore do not require additional input.

In such cases:

```json
"input": ""
```

is valid.

---

### 6.3 Output

The `output` field contains the expected response.

This represents the answer that the model should learn to generate during fine-tuning.

Example:

```text
Docker packages applications and their dependencies into containers, helping them run consistently across different environments.
```

---

## 7. Dataset Location

The original dataset is stored at:

```text
data/raw/coding_instruction_dataset_1200.jsonl
```

The Day 1 processing pipeline is implemented in:

```text
utils/data_cleaner.py
```

---

## 8. Dataset Processing Pipeline

The complete Day 1 pipeline is:

```text
Raw Dataset
     |
     v
Load JSONL
     |
     v
Validate JSON
     |
     v
Validate Required Fields
     |
     v
Clean Text
     |
     v
Reject Invalid Samples
     |
     v
Remove Duplicates
     |
     v
Load Qwen Tokenizer
     |
     v
Calculate Token Lengths
     |
     v
Generate Distribution Graph
     |
     v
Detect Outliers using IQR
     |
     v
Remove Outliers
     |
     v
Train / Validation Split
     |
     +------------------+
     |                  |
     v                  v
train.jsonl          val.jsonl
```

---

## 9. Dataset Loading

The raw JSONL dataset was loaded line-by-line.

Python's `json.loads()` function was used to convert each JSONL line into a Python object.

The loader also checks for malformed JSON.

### Loading Results

```text
Total records loaded: 1200
Invalid JSON lines: 0
```

Therefore, all 1,200 lines were successfully parsed.

---

## 10. Schema Validation

Each record was checked for the required fields:

```text
instruction
input
output
```

A record was considered invalid if:

- it was not a JSON object
- `instruction` was missing
- `input` was missing
- `output` was missing

### Validation Results

```text
Valid records: 1200
Invalid records: 0
```

All records successfully followed the required schema.

---

## 11. Data Cleaning

After schema validation, text cleaning was performed.

The cleaning pipeline performs the following operations:

- Removes leading whitespace
- Removes trailing whitespace
- Replaces repeated whitespace with a single space
- Removes unnecessary newline characters
- Removes unnecessary tab characters
- Verifies that all fields contain strings
- Rejects empty instructions
- Rejects empty outputs

An empty `input` field is allowed because some instructions do not require additional context.

### Cleaning Results

```text
Records after cleaning: 1200
Rejected during cleaning: 0
```

All 1,200 records passed the cleaning stage.

---

## 12. Duplicate Detection

Exact duplicate detection was performed after cleaning.

A record is considered an exact duplicate when all three fields are identical:

```text
instruction
input
output
```

### Duplicate Detection Results

```text
Duplicates removed: 0
Unique records: 1200
```

No exact duplicate records were detected.

---

## 13. Tokenizer Selection

Token-length analysis was performed using the tokenizer:

```text
Qwen/Qwen2.5-1.5B-Instruct
```

The tokenizer was loaded using the Hugging Face `transformers` library.

Using the tokenizer associated with the model planned for fine-tuning is important because different LLM tokenizers can divide the same text into different token sequences.

The Qwen tokenizer will therefore provide token-length measurements relevant to the model that will be used during later stages.

---

## 14. Training Text Construction

Before tokenization, each record was converted into a training-style text sequence.

When an input exists, the format is:

```text
Instruction: <instruction>
Input: <input>
Output: <output>
```

When no input is required:

```text
Instruction: <instruction>
Output: <output>
```

The complete sequence is then passed through the tokenizer.

---

## 15. Token-Length Analysis

Token-length analysis was performed on all **1,200 unique records**.

The following results were obtained:

| Metric | Value |
|---|---:|
| Samples Analysed | 1,200 |
| Minimum Tokens | 19 |
| Maximum Tokens | 105 |
| Average Tokens | 61.91 |
| Median Tokens | 65.00 |
| Q1 | 35.75 |
| Q3 | 79.00 |

The average sample contains approximately:

```text
62 tokens
```

The shortest sample contains:

```text
19 tokens
```

while the longest contains:

```text
105 tokens
```

The relatively short sequences make the dataset suitable for resource-efficient instruction fine-tuning.

---

## 16. Token-Length Distribution

A histogram was generated to understand how token lengths are distributed throughout the dataset.

The generated graph is stored at:

```text
reports/token_length_distribution.png
```

The graph shows that the dataset contains multiple token-length clusters.

This is expected because the dataset contains different task types.

For example:

- QA examples may contain short questions and explanations.
- Reasoning examples may require longer context and responses.
- Extraction tasks may contain larger input contexts but relatively short structured outputs.

The complete token-length range is:

```text
19 - 105 tokens
```

Therefore, the dataset does not contain extremely long sequences.

---

## 17. Outlier Detection

Token-length outliers were detected using the **Interquartile Range (IQR)** method.

The IQR formula is:

```text
IQR = Q3 - Q1
```

For this dataset:

```text
Q1 = 35.75
Q3 = 79.00
```

Therefore:

```text
IQR = 79.00 - 35.75

IQR = 43.25
```

---

## 18. Outlier Boundaries

The lower outlier boundary is calculated using:

```text
Lower Bound = Q1 - (1.5 × IQR)
```

Therefore:

```text
Lower Bound
= 35.75 - (1.5 × 43.25)

= -29.12
```

The upper boundary is:

```text
Upper Bound = Q3 + (1.5 × IQR)
```

Therefore:

```text
Upper Bound
= 79.00 + (1.5 × 43.25)

= 143.88
```

The resulting IQR range is approximately:

```text
-29.12 to 143.88 tokens
```

Token counts cannot actually be negative. The negative lower boundary is simply a mathematical result of applying the IQR formula to this distribution.

---

## 19. Outlier Analysis Results

The actual token-length range of the dataset is:

```text
19 to 105 tokens
```

The calculated upper outlier boundary is:

```text
143.88 tokens
```

Since all samples fall within the calculated boundaries:

```text
Outliers detected: 0
Records after outlier removal: 1200
```

Therefore, no records needed to be removed during the outlier-removal stage.

---

## 20. Train / Validation Split

After validation, cleaning, duplicate detection, token analysis, and outlier detection, all **1,200 samples** remained available.

The dataset was divided using a:

```text
90% Training
10% Validation
```

split.

The final result is:

| Dataset | Percentage | Samples |
|---|---:|---:|
| Training | 90% | 1,080 |
| Validation | 10% | 120 |
| **Total** | **100%** | **1,200** |

---

## 21. Training Dataset

The training dataset is stored at:

```text
data/train.jsonl
```

It contains:

```text
1080 samples
```

This dataset will be used during Day 2 to train the LoRA / QLoRA adapter.

During fine-tuning, these examples contribute to the calculation of the training loss and parameter updates.

---

## 22. Validation Dataset

The validation dataset is stored at:

```text
data/val.jsonl
```

It contains:

```text
120 samples
```

The validation dataset is kept separate from training.

Its purpose is to evaluate how well the fine-tuned model performs on examples that were not used directly for parameter updates.

This helps determine whether the model is learning useful patterns rather than simply memorizing the training examples.

---

## 23. Reproducibility

The train/validation split uses the random seed:

```text
42
```

Using a fixed random seed makes the dataset split reproducible.

Running the same pipeline again with the same dataset and seed will generate the same training and validation split.

This is useful for consistent experiments and benchmark comparisons.

---

## 24. Final Dataset Statistics

The complete Day 1 processing results are:

| Metric | Result |
|---|---:|
| Raw Records | 1,200 |
| Invalid JSON Lines | 0 |
| Invalid Records | 0 |
| Rejected During Cleaning | 0 |
| Duplicate Records | 0 |
| Unique Records | 1,200 |
| Token Outliers | 0 |
| Final Usable Samples | 1,200 |
| Training Samples | 1,080 |
| Validation Samples | 120 |
| Minimum Tokens | 19 |
| Maximum Tokens | 105 |
| Average Tokens | 61.91 |
| Median Tokens | 65.00 |
| Q1 | 35.75 |
| Q3 | 79.00 |
| IQR | 43.25 |
| Lower Outlier Bound | -29.12 |
| Upper Outlier Bound | 143.88 |

---

## 25. Project Structure

After completing Day 1, the relevant project structure is:

```text
week8-llm-fine-tuning/
│
├── data/
│   ├── raw/
│   │   └── coding_instruction_dataset_1200.jsonl
│   │
│   ├── train.jsonl
│   └── val.jsonl
│
├── reports/
│   └── token_length_distribution.png
│
├── utils/
│   └── data_cleaner.py
│
└── DATASET-ANALYSIS.md
```

An `outliers.jsonl` file is only generated when outliers are detected.

Since this dataset contained zero token-length outliers, no outlier file was required.

---

## 26. Day 1 Deliverables

The required Day 1 deliverables have been completed:

| Deliverable | Status |
|---|---|
| `data/train.jsonl` | Completed |
| `data/val.jsonl` | Completed |
| `utils/data_cleaner.py` | Completed |
| `DATASET-ANALYSIS.md` | Completed |

Additional analysis artifact:

```text
reports/token_length_distribution.png
```

---

## 27. Day 1 Final Pipeline Summary

```text
coding_instruction_dataset_1200.jsonl
                 |
                 v
          Load 1200 Records
                 |
                 v
          JSON Validation
             0 Invalid
                 |
                 v
          Schema Validation
             1200 Valid
                 |
                 v
            Text Cleaning
             0 Rejected
                 |
                 v
        Duplicate Detection
            0 Duplicates
                 |
                 v
          1200 Unique Records
                 |
                 v
          Qwen Tokenization
                 |
                 v
       Token-Length Analysis
        Min: 19 / Max: 105
          Average: 61.91
                 |
                 v
       Distribution Analysis
                 |
                 v
       IQR Outlier Detection
            0 Outliers
                 |
                 v
        1200 Final Samples
                 |
          90 / 10 Split
                 |
        +--------+--------+
        |                 |
        v                 v
   train.jsonl        val.jsonl
  1080 samples        120 samples
```

---

## 28. Preparation for Day 2

The dataset is now ready for **Parameter-Efficient Fine-Tuning (PEFT)**.

During Day 2, the training dataset will be used to fine-tune a pretrained LLM using **QLoRA**.

The planned model is:

```text
Qwen/Qwen2.5-1.5B-Instruct
```

The planned QLoRA configuration will follow the Week 8 requirements, including:

```text
LoRA Rank (r)      = 16
Learning Rate      = 2e-4
Batch Size         = 4
Epochs             = 3
Model Loading      = 4-bit
```

Instead of updating all parameters of the base model, QLoRA will keep the quantised base model largely frozen and train a small set of LoRA adapter parameters.

This significantly reduces the GPU memory required for fine-tuning.

---

## 29. Conclusion

Week 8 Day 1 successfully prepared a custom **Coding / Software Engineering instruction-tuning dataset** for LLM fine-tuning.

The original dataset contained **1,200 samples**, consisting of balanced Question Answering, Reasoning, and Extraction examples.

The complete dataset was successfully validated and cleaned.

No malformed JSON records, invalid samples, duplicate records, or token-length outliers were detected.

Token analysis using the **Qwen/Qwen2.5-1.5B-Instruct tokenizer** produced an average sequence length of **61.91 tokens**, with sample lengths ranging from **19 to 105 tokens**.

The final dataset contains all **1,200 usable samples** and was divided into:

- **1,080 training samples**
- **120 validation samples**

The dataset and analysis artifacts are now ready for the next phase:

> **Week 8 Day 2 - Parameter-Efficient Fine-Tuning using LoRA / QLoRA**