# WEEK 7 — GENAI & MULTIMODAL RAG ENGINEERING

## 1. Overall Goal

The goal of Week 7 is to build an **enterprise-grade GenAI knowledge system** using Retrieval-Augmented Generation (RAG).

The final system should be capable of answering questions from three major types of enterprise information:

1. **Documents**

   * PDF
   * DOCX
   * TXT
   * CSV

2. **Images**

   * JPG/PNG
   * Diagrams
   * Forms
   * Charts
   * Scanned PDFs

3. **Structured databases**

   * SQLite or PostgreSQL

Instead of asking an LLM to answer everything using only the knowledge it learned during training, we will provide it with relevant information retrieved from our own data.

The final idea is:

**User Question → Find Relevant Enterprise Data → Give Context to LLM → Generate Grounded Answer**

This approach is called **Retrieval-Augmented Generation (RAG).**

---

# 2. What Are We Actually Building?

Think of the final application as an **AI assistant for a company**.

Suppose a company has:

* 500 policy PDFs
* employee documents
* product manuals
* diagrams
* scanned forms
* sales databases
* transaction tables

Normally, employees would manually search through all this information.

Our system will allow someone to simply ask:

> "What is the company's leave policy?"

The system searches the documents and answers from the relevant policy.

Someone could ask:

> "Find diagrams related to this engineering diagram."

The Image-RAG system retrieves similar images.

Someone could also ask:

> "What were total sales in 2025?"

The system converts the question into SQL, executes it against the database, and explains the result.

Therefore, our final Week 7 system combines:

**Text RAG + Image RAG + SQL QA + Hybrid Retrieval + Memory + Evaluation**

---

# 3. Core RAG Architecture

The basic pipeline we will build is:

```text
                    ENTERPRISE DATA
                          │
          ┌───────────────┼───────────────┐
          │               │               │
       Documents        Images        SQL Database
      PDF/DOCX/TXT     JPG/PNG          Tables
          │               │               │
          ▼               ▼               ▼
     Text Extraction      OCR        Schema Loader
          │               │
          ▼               ▼
       Chunking       Image/Text
          │           Embeddings
          ▼               │
      Embeddings           │
          │               │
          └───────┬───────┘
                  ▼
             Vector Store
          FAISS / Qdrant etc.
                  │
                  ▼
             RETRIEVAL
                  │
                  ▼
          Relevant Context
                  │
                  ▼
                LLM
                  │
                  ▼
          Grounded Answer
```

The important idea is that the LLM does **not blindly answer the question**.

We first retrieve relevant information and then ask the LLM to answer using that information.

---

# 4. Model Strategy

The assignment provides two possible paths.

## Path A — Local/Open-Source

Possible LLMs include:

* Mistral
* LLaMA
* Qwen
* Phi

Possible embedding models include:

* BGE
* Instructor
* GTE
* CLIP

Everything can run locally.

## Path B — Hosted LLM API

The same RAG architecture can use hosted models through providers such as OpenAI, Anthropic, or Google.

The assignment specifically wants the architecture to remain mostly independent of the model provider.

A configuration such as:

```yaml
provider: local
model_name: chosen-model
api_key_env: API_KEY_VARIABLE
```

can determine which model implementation is used.

The provider-specific implementation should primarily remain inside:

```text
generator/llm_client.py
```

That means retrieval, chunking, embeddings, evaluation, and the remaining architecture don't need to be rewritten simply because the LLM provider changes.

---

# 5. DAY 1 — Basic RAG + Ingestion Pipeline

## Goal

Day 1 establishes the **foundation of the entire Week 7 system**.

We will learn how documents become searchable by an AI system.

The pipeline will approximately be:

```text
Documents
   ↓
Load documents
   ↓
Clean text
   ↓
Split into chunks
   ↓
Attach metadata
   ↓
Generate embeddings
   ↓
Store embeddings
   ↓
Vector Database
   ↓
Retriever
```

## Step 1 — Document Loading

The pipeline needs to support:

```text
PDF
TXT
CSV
DOCX
```

We extract usable text from these documents.

## Step 2 — Cleaning

Extracted text may contain:

* unnecessary spaces
* broken lines
* formatting artifacts
* repeated content

We normalize this before indexing.

## Step 3 — Chunking

Large documents cannot simply be sent entirely to an LLM.

Therefore, documents are divided into approximately:

```text
500–800 token chunks
```

with an overlap strategy where appropriate.

Example:

```text
100-page PDF
      ↓
Chunk 1
Chunk 2
Chunk 3
...
Chunk 150
```

## Step 4 — Metadata

Each chunk should contain information such as:

```text
source
page number
tags
```

This allows us to trace where an answer came from.

## Step 5 — Embeddings

Each text chunk is converted into a numerical vector.

Conceptually:

```text
"Employees receive annual leave"
             ↓
       Embedding Model
             ↓
[0.21, -0.72, 0.13, ...]
```

Semantically similar sentences should have similar vector representations.

## Step 6 — Vector Database

These embeddings will be stored using a vector index such as:

```text
FAISS
```

or Qdrant.

## Step 7 — Retriever

When a user asks:

```text
"What is the annual leave policy?"
```

we embed the question and search for the most semantically similar document chunks.

### Day 1 Deliverables

```text
pipelines/ingest.py
embeddings/embedder.py
vectorstore/index.faiss
retriever/query_engine.py
RAG-ARCHITECTURE.md
```

### Day 1 Result

By the end of Day 1:

**Question → Relevant document chunks**

should work.

---

# 6. DAY 2 — Advanced Retrieval & Context Engineering

## Goal

Day 1 gives us retrieval.

Day 2 makes that retrieval **much more accurate**.

Pure vector similarity isn't always enough.

Therefore we combine several techniques.

## Hybrid Retrieval

We combine:

```text
Semantic Search
       +
Keyword Search (BM25)
       ↓
Candidate Documents
       ↓
Reranking
       ↓
Deduplication
       ↓
Best Context
```

### Semantic search

Finds information based on **meaning**.

For example:

```text
Query:
"How are loans approved?"
```

could retrieve content containing:

```text
"Credit underwriting determines borrower eligibility..."
```

even though the exact words differ.

### Keyword/BM25 Search

Useful when exact words matter, such as:

```text
Policy-2024
Invoice-29384
Employee ID
Product Name
```

### Reranking

Suppose retrieval initially returns 20 chunks.

A reranker determines which ones are actually most useful.

```text
20 candidate chunks
        ↓
     Reranker
        ↓
Best 5 chunks
```

### Deduplication

Repeated or highly similar chunks are removed.

### Metadata filtering

Queries can also use filters:

```python
filters = {
    "year": "2024",
    "type": "policy"
}
```

### Day 2 Deliverables

```text
retriever/hybrid_retriever.py
retriever/reranker.py
pipelines/context_builder.py
RETRIEVAL-STRATEGIES.md
```

### Day 2 Result

Our system evolves from:

**Basic RAG**

to:

**Hybrid + reranked + traceable RAG**

---

# 7. DAY 3 — Image RAG / Multimodal RAG

## Goal

Until Day 2, our RAG system mainly understands text.

Day 3 adds **images**.

The system should support:

```text
PNG
JPG
Scanned PDFs
Forms
Charts
Diagrams
```

Three important technologies are introduced.

## OCR

OCR extracts text from images.

```text
Scanned document
       ↓
   Tesseract
       ↓
Extracted text
```

## CLIP

CLIP can represent images and text in a shared embedding space.

Therefore we can perform:

```text
Text → Image Search
```

and:

```text
Image → Image Search
```

## Image Captioning

A captioning model such as BLIP can generate a textual description of an image.

Example:

```text
Engineering diagram
        ↓
      BLIP
        ↓
"Diagram showing a hydraulic pump system"
```

## Complete Image Pipeline

```text
Image
  │
  ├──→ OCR → Extracted Text
  │
  ├──→ CLIP → Image Embedding
  │
  └──→ BLIP → Caption
                 │
                 ▼
        Multimodal Index
```

The resulting system should support:

```text
Text → Image
Image → Image
Image → Text Answer
```

### Day 3 Deliverables

```text
pipelines/image_ingest.py
embeddings/clip_embedder.py
retriever/image_search.py
MULTIMODAL-RAG.md
```

### Day 3 Result

Our AI can now retrieve knowledge from:

**Documents + Images**

instead of only text.

---

# 8. DAY 4 — Natural Language → SQL → Answer

## Goal

Documents and images contain unstructured information.

Companies also have structured information stored in databases.

For example:

| Product |  Sales | Year |
| ------- | -----: | ---: |
| Laptop  | 100000 | 2025 |
| Phone   |  80000 | 2025 |

Instead of manually writing SQL, the user could ask:

> "What were the total sales in 2025?"

The pipeline becomes:

```text
Natural Language Question
          ↓
     Read DB Schema
          ↓
          LLM
          ↓
      Generate SQL
          ↓
     Validate Query
          ↓
      Execute SQL
          ↓
      SQL Results
          ↓
          LLM
          ↓
Natural Language Answer
```

## Schema Loader

The LLM needs to understand available:

```text
tables
columns
relationships
data types
```

before generating SQL.

## SQL Generator

Example:

```text
User:
"Show total sales by artist for 2023."
```

could produce a corresponding SQL query.

## SQL Validation

We don't blindly execute generated SQL.

The generated statement must first be validated.

This is especially important because enterprise systems must prevent unsafe or destructive operations.

## Safe Executor

Only approved queries should reach the database.

## Result Summarizer

Instead of dumping database rows, the LLM converts the result into a useful natural-language explanation.

### Day 4 Deliverables

```text
pipelines/sql_pipeline.py
generator/sql_generator.py
utils/schema_loader.py
SQL-QA-DOC.md
```

### Day 4 Result

Our system can now answer questions from:

**Documents + Images + SQL databases**

---

# 9. DAY 5 — Memory + Evaluation + Final Application

## Goal

Day 5 combines everything and makes the system closer to a production application.

The assignment requires three main interfaces:

```text
/ask
/ask-image
/ask-sql
```

## /ask

Used for document RAG.

```text
Question
   ↓
Hybrid Retriever
   ↓
Context
   ↓
LLM
   ↓
Answer
```

## /ask-image

Used for multimodal/Image RAG.

```text
Image / Text
      ↓
Image Retrieval
      ↓
Related Images + Text
      ↓
LLM
      ↓
Answer
```

## /ask-sql

Used for database questions.

```text
Question
   ↓
SQL Generation
   ↓
Validation
   ↓
Execution
   ↓
Summary
```

---

# 10. Conversational Memory

Our application should remember approximately the **last five messages**.

Example:

```text
User:
"What is the company's leave policy?"

AI:
"Employees receive..."

User:
"What about interns?"
```

Without memory, the second question lacks context.

With memory, the system understands that:

```text
"What about interns?"
```

means:

```text
"What is the leave policy for interns?"
```

---

# 11. Refinement / Self-Critique

The initial answer can be evaluated before being returned.

Conceptually:

```text
Generated Answer
       ↓
Check against retrieved context
       ↓
Is the answer supported?
       ↓
     NO → Refine
       ↓
     YES
       ↓
Return Answer
```

This is designed to reduce hallucination.

---

# 12. RAG Evaluation

We won't simply check whether the application "looks correct."

We will evaluate things such as:

### Context Match

Did retrieval actually find information relevant to the question?

### Faithfulness

Is the generated answer supported by retrieved information?

### Confidence

How confident should the application be in its answer?

### Human Feedback

User feedback can also be logged for later analysis.

---

# 13. Logging and Tracing

The final application should record useful debugging information.

Conceptually:

```text
Question
Retrieved chunks
Sources
Scores
Generated answer
Confidence
Evaluation
```

This helps diagnose why the system produced a particular answer.

---

# 14. Final Week 7 Architecture

By the end of Day 5, the system should conceptually look like:

```text
                         USER
                           │
              ┌────────────┼────────────┐
              │            │            │
         Text Question    Image      SQL Question
              │            │            │
              ▼            ▼            ▼
          Text RAG      Image RAG     SQL QA
              │            │            │
              ▼            ▼            ▼
        Hybrid Search   CLIP/OCR     SQL Generator
              │            │            │
          Reranking         │       SQL Validator
              │            │            │
              └────────────┼────────────┘
                           │
                           ▼
                     Context Builder
                           │
                           ▼
                          LLM
                           │
                     ┌─────┴─────┐
                     │           │
                  Memory      Evaluation
                     │           │
                     └─────┬─────┘
                           ▼
                    FINAL ANSWER
```

---

# 15. Five-Day Roadmap

| Day       | Main Focus          | What We Build                                                            |
| --------- | ------------------- | ------------------------------------------------------------------------ |
| **Day 1** | RAG Fundamentals    | Document ingestion, chunking, embeddings, vector DB, basic retriever     |
| **Day 2** | Advanced Retrieval  | BM25 + semantic retrieval + reranking + deduplication + context building |
| **Day 3** | Multimodal RAG      | OCR + CLIP + captions + image retrieval                                  |
| **Day 4** | SQL QA              | Natural language → SQL → validation → execution → answer                 |
| **Day 5** | Production Capstone | Memory + evaluation + hallucination checks + API/UI + logging            |

---

# 16. How Each Day Depends on the Previous Day

This week should not be viewed as five unrelated assignments.

We are progressively building **one system**.

```text
DAY 1
Basic Text RAG
     │
     ▼
DAY 2
Advanced Text RAG
     │
     ▼
DAY 3
Text RAG + Image RAG
     │
     ▼
DAY 4
Text + Image + SQL
     │
     ▼
DAY 5
Text + Image + SQL
+ Memory
+ Evaluation
+ API/UI
+ Monitoring
     │
     ▼
FINAL ENTERPRISE
KNOWLEDGE INTELLIGENCE SYSTEM
```

---

# 17. What I Will Be Able to Explain After Week 7

After completing the project, I should be able to explain:

* What RAG is and why companies use it.
* Why an LLM alone is insufficient for private enterprise knowledge.
* How documents are ingested and cleaned.
* Why documents need chunking.
* What embeddings are.
* How vector similarity search works.
* What FAISS/Qdrant does.
* How semantic retrieval works.
* What BM25 keyword retrieval does.
* Why hybrid retrieval improves search.
* What reranking and MMR are.
* How metadata filtering works.
* How RAG reduces hallucinations.
* How OCR extracts information from images.
* How CLIP enables image retrieval.
* How multimodal RAG works.
* How natural-language questions can be translated into SQL.
* Why generated SQL must be validated before execution.
* How conversational memory works.
* How RAG answers can be evaluated for context relevance and faithfulness.
* How the complete system can expose document, image, and SQL capabilities through an application/API.

---

# 18. Week 7 in One Sentence

**Week 7 is about building an enterprise AI assistant that retrieves trustworthy information from documents, images, and databases and uses an LLM to generate grounded, traceable answers instead of relying solely on the LLM's internal knowledge.**

---

# Final Objective

By the end of the week, our progression should be:

```text
Documents ──┐
            │
Images ─────┼──→ Retrieval / SQL Layer
            │
Database ───┘
                    ↓
                 Context
                    ↓
                   LLM
                    ↓
          Evaluation + Memory
                    ↓
            Grounded Answer
```

The important mindset for this week is:

**We are not primarily training an AI model.**

We are **engineering a system around an LLM** that knows how to find the right enterprise information, provide it as context, generate an answer, trace its sources, remember conversations, and evaluate whether the generated response is actually supported by the retrieved information.
