# Enterprise Knowledge Intelligence System
## Day 5 — Deployment Notes

## 1. Overview

This project implements an Enterprise Knowledge Intelligence System using Retrieval-Augmented Generation (RAG), Multimodal Retrieval, Natural Language to SQL, conversational memory, evaluation, answer refinement, and API-based deployment.

The system combines the work completed throughout Week 7 into a single application.

The final system supports three major question-answering workflows:

1. Text-based RAG
2. Image/Multimodal RAG
3. Natural Language to SQL Question Answering

The application exposes these capabilities through FastAPI endpoints.

---

## 2. Final API Endpoints

The application provides the following endpoints:

### POST `/ask`

Used for text-based enterprise knowledge questions.

Example:

```json
{
  "question": "What is the employee leave policy?"
}
```

Processing flow:

```text
Question
   ↓
Hybrid Retrieval
   ↓
Semantic Search + BM25
   ↓
Relevant Text Context
   ↓
Gemini Answer Generation
   ↓
RAG Evaluation
   ↓
Refinement if Required
   ↓
Memory Storage
   ↓
Chat Logging
   ↓
Final Answer
```

---

### POST `/ask-image`

Used for questions whose answers can be retrieved from indexed images.

Example:

```json
{
  "question": "Explain the loan approval process"
}
```

Processing flow:

```text
Text Question
   ↓
CLIP Text Embedding
   ↓
Image FAISS Search
   ↓
Relevant Images
   ↓
Image Caption + OCR Text
   ↓
Multimodal Context
   ↓
Gemini Answer Generation
   ↓
RAG Evaluation
   ↓
Chat Logging
   ↓
Final Answer
```

---

### POST `/ask-sql`

Used for asking natural-language questions about structured database data.

Example:

```json
{
  "question": "What are the total sales in 2024?"
}
```

Processing flow:

```text
Natural Language Question
   ↓
Database Schema
   ↓
Gemini SQL Generation
   ↓
SQL Validation
   ↓
Safe SQLite Execution
   ↓
SQL Correction if Required
   ↓
Database Results
   ↓
Gemini Result Summarization
   ↓
Chat Logging
   ↓
Final Answer
```

---

## 3. Technology Stack

The project uses the following technologies:

### API

- FastAPI
- Uvicorn
- Pydantic

### Large Language Model

- Gemini API
- `google-genai`

The LLM is used for:

- RAG answer generation
- SQL generation
- SQL correction
- SQL result summarization
- Answer refinement

### Text Embeddings

Model:

```text
BAAI/bge-small-en-v1.5
```

Used for semantic text retrieval.

### Vector Database

FAISS is used for local vector similarity search.

Text embeddings and image embeddings are stored in separate FAISS indexes.

### Keyword Retrieval

BM25 is used for lexical keyword-based retrieval.

### Hybrid Retrieval

Semantic FAISS retrieval and BM25 retrieval are combined using Reciprocal Rank Fusion (RRF).

### Reranking

Cross-Encoder:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

is available for improving retrieval ranking.

### Image Processing

The multimodal pipeline uses:

- Tesseract OCR
- BLIP image captioning
- CLIP embeddings
- FAISS image index

CLIP model:

```text
openai/clip-vit-base-patch32
```

BLIP model:

```text
Salesforce/blip-image-captioning-base
```

### Database

SQLite is used for structured SQL question answering.

Database:

```text
data/sales.db
```

---

## 4. Text RAG Pipeline

The text RAG pipeline retrieves information from enterprise documents.

Supported document formats include:

- TXT
- PDF
- DOCX
- CSV

Documents are cleaned, chunked, embedded, and indexed.

The main text retrieval pipeline is:

```text
Documents
   ↓
Document Loading
   ↓
Cleaning
   ↓
Chunking
   ↓
Metadata Assignment
   ↓
BGE Embeddings
   ↓
FAISS Index
```

During question answering:

```text
User Question
   ↓
BGE Query Embedding
   ↓
FAISS Semantic Retrieval
        +
BM25 Keyword Retrieval
   ↓
Reciprocal Rank Fusion
   ↓
Relevant Chunks
   ↓
Context
   ↓
Gemini
   ↓
Answer
```

The API instructs Gemini to answer using the retrieved context and to report insufficient context when the retrieved information does not support an answer.

---

## 5. Multimodal RAG Pipeline

The multimodal pipeline allows textual questions to retrieve information stored in images.

Images are processed using two techniques.

### OCR

Tesseract extracts visible text from images.

### Image Captioning

BLIP generates a textual description of image content.

The image itself is converted into a CLIP embedding.

```text
Image
   ├── Tesseract → OCR Text
   ├── BLIP → Caption
   └── CLIP → Image Embedding
                     ↓
                   FAISS
```

During search:

```text
Text Question
   ↓
CLIP Text Embedding
   ↓
FAISS Image Search
   ↓
Relevant Images
   ↓
Caption + OCR
   ↓
Image Context
   ↓
Gemini
   ↓
Answer
```

This provides text-to-image retrieval while allowing the LLM to reason over textual information extracted from the retrieved images.

---

## 6. SQL Question Answering

The SQL pipeline converts natural-language questions into safe SQL queries.

Example:

```text
What are the total sales in 2024?
```

Generated SQL:

```sql
SELECT SUM(quantity * unit_price) AS total_sales
FROM sales
WHERE strftime('%Y', sale_date) = '2024';
```

The SQL query is validated before execution.

Only `SELECT` statements are allowed.

The following operations are blocked:

```text
INSERT
UPDATE
DELETE
DROP
ALTER
CREATE
TRUNCATE
REPLACE
ATTACH
DETACH
PRAGMA
```

Multiple SQL statements are also rejected.

The SQLite connection additionally enables:

```sql
PRAGMA query_only = ON;
```

This provides an additional read-only safety layer.

If a generated SQL query produces a SQLite execution error, the error, question, and failed query are sent to the SQL correction function.

The corrected query is validated again before execution.

---

## 7. Conversational Memory

The system stores recent conversation messages using:

```text
memory/memory.json
```

The memory implementation keeps the latest:

```text
5 messages
```

Messages use the structure:

```json
{
  "role": "user",
  "content": "What is the employee leave policy?"
}
```

or:

```json
{
  "role": "assistant",
  "content": "Employees are entitled to 24 paid leave days per year."
}
```

Older messages are automatically removed once the configured memory limit is exceeded.

Recent memory is provided to the text RAG generation prompt.

This allows follow-up questions such as:

```text
User:
What is the employee leave policy?

Assistant:
Employees receive 24 paid leave days per year...

User:
What about interns?
```

The system can use the recent conversation to understand that the follow-up question refers to the previously discussed leave policy.

---

## 8. RAG Evaluation

RAG responses are evaluated using:

```text
evaluation/rag_eval.py
```

The evaluator calculates four main indicators.

### Context Match Score

Measures lexical overlap between the user question and retrieved context.

Conceptually:

```text
Question ↔ Retrieved Context
```

A higher value indicates that the retrieved context contains more information related to the question.

### Faithfulness Score

Measures lexical overlap between the generated answer and retrieved context.

Conceptually:

```text
Generated Answer ↔ Retrieved Context
```

A higher score suggests that more of the answer is supported by the retrieved context.

### Hallucination Detection

The baseline system marks an answer as potentially hallucinated when its faithfulness score falls below the configured threshold.

Default threshold:

```text
0.5
```

### Confidence Score

The baseline confidence indicator combines context match and faithfulness:

```text
Confidence =
(Context Match + Faithfulness) / 2
```

This is an application-level heuristic indicator and should not be interpreted as a calibrated statistical probability.

---

## 9. Evaluation Normalization

Before calculating lexical overlap, text is normalized.

Normalization includes:

- lowercase conversion
- token extraction
- common stop-word removal
- basic plural normalization

For example:

```text
employees → employee
```

This reduces obvious mismatches during lexical comparison.

The current evaluation system is intentionally lightweight.

A production system could replace or supplement it with:

- embedding similarity
- NLI models
- LLM-as-a-judge evaluation
- dedicated RAG evaluation frameworks

---

## 10. Answer Refinement

The system includes a refinement loop.

Initial flow:

```text
Context
   ↓
Gemini
   ↓
Draft Answer
   ↓
Evaluation
```

The evaluator determines whether refinement is necessary.

Refinement is triggered when:

- hallucination is detected, or
- confidence is below the configured threshold.

Default confidence threshold:

```text
0.6
```

When refinement is required:

```text
Question
+
Retrieved Context
+
Previous Answer
+
Evaluation
       ↓
Answer Refiner
       ↓
Improved Answer
       ↓
Re-evaluation
```

The refinement prompt instructs the LLM to:

- use only retrieved context
- remove unsupported claims
- avoid inventing information
- state when context is insufficient
- keep the response concise and relevant

---

## 11. Chat Logging

API conversations are logged in:

```text
CHAT-LOGS.json
```

Example:

```json
[
  {
    "timestamp": "2026-09-02T12:47:33.416288",
    "endpoint": "/ask-sql",
    "question": "what are the total sales in 2024",
    "answer": "The total sales in 2024 were 49,120.",
    "evaluation": null
  }
]
```

The log records:

- timestamp
- endpoint
- user question
- generated answer
- evaluation information where applicable

For SQL requests, evaluation may currently be `null` because the RAG lexical evaluator is designed for retrieved text/image context rather than deterministic SQL result evaluation.

---

## 12. Gemini Retry Handling

Hosted LLM APIs can temporarily become unavailable.

For example, Gemini may return:

```text
503 UNAVAILABLE
```

when the selected model experiences high demand.

The API therefore retries generation up to three times.

Conceptually:

```text
Gemini Request
   ↓
Success? ── Yes → Continue
   │
   No
   ↓
503 Server Error
   ↓
Wait
   ↓
Retry
```

This prevents a temporary provider-side overload from immediately failing the request.

---

## 13. Running the Application

Activate the virtual environment from the project directory.

Example:

```bash
source .venv/bin/activate
```

Move into:

```bash
cd src
```

Start the API:

```bash
uvicorn deployment.app:app --reload
```

The development server runs locally on port `8000` by default.

---

## 14. Swagger API Documentation

FastAPI automatically generates interactive API documentation.

After starting the application, open:

```text
http://127.0.0.1:8000/docs
```

Swagger UI can be used to test:

```text
POST /ask
POST /ask-image
POST /ask-sql
```

without requiring Postman.

---

## 15. Environment Configuration

The Gemini API key is stored in the project `.env` file.

Example:

```env
GEMINI_API_KEY=your_api_key
```

Secrets should never be committed to Git.

The `.env` file should therefore be included in `.gitignore`.

Example:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

---

## 16. Important Project Files

```text
src/
│
├── deployment/
│   └── app.py
│
├── evaluation/
│   └── rag_eval.py
│
├── memory/
│   ├── memory_store.py
│   └── memory.json
│
├── generator/
│   ├── answer_refiner.py
│   └── sql_generator.py
│
├── retriever/
│   ├── hybrid_retriever.py
│   ├── reranker.py
│   └── image_search.py
│
├── pipelines/
│   ├── ingest.py
│   ├── context_builder.py
│   ├── image_ingest.py
│   └── sql_pipeline.py
│
├── embeddings/
│   ├── embedder.py
│   └── clip_embedder.py
│
├── vectorstore/
│   ├── index.faiss
│   ├── metadata.json
│   ├── image_index.faiss
│   └── image_metadata.json
│
├── data/
│   ├── raw/
│   ├── images/
│   └── sales.db
│
├── CHAT-LOGS.json
└── DEPLOYMENT-NOTES.md
```

---

## 17. API Examples

### Text RAG

Request:

```json
{
  "question": "What is the employee leave policy?"
}
```

Example response structure:

```json
{
  "question": "What is the employee leave policy?",
  "answer": "Employees are entitled to 24 paid leave days per year...",
  "evaluation": {
    "context_match_score": 1.0,
    "faithfulness_score": 0.824,
    "hallucination_detected": false,
    "confidence_score": 0.912
  }
}
```

---

### Follow-Up Using Memory

First request:

```json
{
  "question": "What is the employee leave policy?"
}
```

Follow-up:

```json
{
  "question": "What about interns?"
}
```

Example response:

```json
{
  "question": "What about interns?",
  "answer": "Interns are entitled to 12 paid leave days during their internship period.",
  "evaluation": {
    "context_match_score": 0.5,
    "faithfulness_score": 0.769,
    "hallucination_detected": false,
    "confidence_score": 0.635
  }
}
```

---

### Image RAG

Request:

```json
{
  "question": "Explain the loan approval process"
}
```

The system searches the CLIP/FAISS image index and returns relevant image sources together with the generated answer.

Example retrieved image:

```text
loan_approval_process.png
```

---

### SQL QA

Request:

```json
{
  "question": "What are the total sales in 2024?"
}
```

Example response:

```json
{
  "question": "what are the total sales in 2024",
  "sql": "SELECT SUM(quantity * unit_price) AS total_sales FROM sales WHERE strftime('%Y', sale_date) = '2024'",
  "results": [
    {
      "total_sales": 49120
    }
  ],
  "answer": "The total sales in 2024 were 49,120."
}
```

---

## 18. Security Considerations

The SQL pipeline uses multiple safeguards.

### Read-Only Queries

Only SQL beginning with:

```text
SELECT
```

is accepted.

### Forbidden Operations

Database-modifying and administrative SQL keywords are blocked.

### Single Statement

Multiple SQL statements are rejected.

### SQLite Query-Only Mode

SQLite is configured with:

```sql
PRAGMA query_only = ON;
```

during execution.

### API Secrets

The Gemini API key is stored in environment variables rather than source code.

---

## 19. Error Handling

The system handles several common failure scenarios.

### Insufficient RAG Context

The LLM is instructed to explicitly state when the retrieved context is insufficient.

### SQL Generation Error

If generated SQL causes an SQLite execution error:

```text
Failed SQL
   ↓
Error Message
   ↓
Gemini SQL Correction
   ↓
Validate Again
   ↓
Execute Again
```

### Gemini Temporary Failure

Temporary Gemini server errors are retried before the request fails.

### Invalid Memory JSON

If the local memory file contains invalid JSON, the memory implementation falls back to an empty conversation history.

---

## 20. Current Limitations

The current implementation is a capstone/development system rather than a fully hardened production deployment.

Important limitations include:

1. Memory is stored in a local JSON file and is not separated by user/session.
2. Chat logs are stored locally and will grow over time.
3. Lexical RAG evaluation is relatively simple.
4. Confidence is heuristic rather than statistically calibrated.
5. The SQL database is local SQLite.
6. FAISS indexes are stored locally.
7. Hosted LLM availability depends on the Gemini API.
8. The current retry mechanism uses synchronous waiting.
9. Retrieval quality can decrease for broad or ambiguous questions.
10. Authentication, authorization, rate limiting, and persistent production databases are not yet implemented.

---

## 21. Production Improvements

For a production-scale system, the following improvements can be added:

- Redis-backed conversational memory
- user/session-specific memory
- vector-based long-term memory
- semantic evaluation models
- LLM-as-a-judge evaluation
- stronger hallucination detection
- persistent centralized logging
- structured tracing
- asynchronous LLM requests
- exponential retry backoff
- authentication and authorization
- API rate limiting
- Docker deployment
- cloud-hosted vector databases
- PostgreSQL or another production database
- automated testing
- monitoring and alerting

---

## 22. Day 5 Deliverables

The Day 5 implementation contains:

```text
deployment/app.py        ✅
evaluation/rag_eval.py   ✅
memory/memory_store.py   ✅
CHAT-LOGS.json           ✅
DEPLOYMENT-NOTES.md      ✅
```

Additional implementation:

```text
generator/answer_refiner.py
```

The application exposes:

```text
POST /ask
POST /ask-image
POST /ask-sql
```

Additional capabilities include:

```text
Conversational Memory       ✅
Last 5 Messages             ✅
Answer Refinement           ✅
Hallucination Detection     ✅
Context Match Scoring       ✅
Faithfulness Scoring        ✅
Confidence Scoring          ✅
Chat Logging                ✅
Gemini Retry Handling       ✅
Swagger API Interface       ✅
```

---

## 23. Final Architecture

```text
                         USER
                           │
                           ▼
                    FastAPI Application
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
        /ask           /ask-image       /ask-sql
          │                │                │
          ▼                ▼                ▼
 Hybrid Retrieval      CLIP Search       NL → SQL
 FAISS + BM25          Image FAISS       Schema Aware
          │                │                │
          ▼                ▼                ▼
 Text Context        OCR + Caption      SQL Validation
          │                │                │
          ▼                ▼                ▼
       Gemini            Gemini          SQLite
          │                │                │
          ▼                ▼                ▼
     RAG Answer      Multimodal Answer    Results
          │                │                │
          ▼                ▼                ▼
     Evaluation        Evaluation         Gemini
          │                │                │
          ▼                ▼                ▼
     Refinement         Confidence      Final Answer
          │                │                │
          └────────────────┼────────────────┘
                           │
                           ▼
                  Memory + Chat Logs
```

---

## 24. Conclusion

The Week 7 capstone integrates text retrieval, multimodal retrieval, structured SQL reasoning, conversational memory, evaluation, hallucination detection, refinement, and API deployment into a single Enterprise Knowledge Intelligence System.

The implementation demonstrates the complete transition from individual RAG components to an integrated question-answering service capable of working with unstructured documents, images, and structured database information.