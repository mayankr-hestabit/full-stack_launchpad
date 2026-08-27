# RAG Architecture — Week 7 Day 1

## 1. Overview

This project implements the foundational retrieval pipeline for an Enterprise Knowledge Intelligence System using Retrieval-Augmented Generation (RAG).

The Day 1 system is responsible for:

* Loading enterprise documents
* Cleaning extracted text
* Splitting documents into manageable chunks
* Assigning metadata to chunks
* Generating semantic embeddings
* Storing embeddings in a FAISS vector index
* Retrieving relevant chunks using natural-language queries

The pipeline supports the following document formats:

* PDF
* DOCX
* TXT
* CSV

---

# 2. What is RAG?

RAG stands for **Retrieval-Augmented Generation**.

A traditional Large Language Model generates answers primarily from information learned during model training.

A RAG system introduces an external knowledge source.

Instead of depending only on the model's internal knowledge, relevant information is first retrieved from enterprise documents and can then be supplied as context to a language model.

The general architecture is:

```text
User Question
      ↓
Retriever
      ↓
Relevant Context
      ↓
Generator / LLM
      ↓
Grounded Answer
```

Day 1 focuses primarily on building the ingestion, embedding, vector indexing, and basic retrieval foundation.

---

# 3. Day 1 Architecture

The implemented pipeline is:

```text
                RAW DOCUMENTS
                     │
        ┌────────────┼────────────┐
        │            │            │
       PDF          DOCX         TXT/CSV
        │            │            │
        └────────────┼────────────┘
                     ↓
              Document Loader
                     ↓
                Text Cleaning
                     ↓
              Token Chunking
                     ↓
             Metadata Assignment
                     ↓
              Embedding Model
                     ↓
             Embedding Vectors
                     ↓
                 FAISS Index
                     ↓
              Semantic Search
                     ↓
             Relevant Chunks
```

---

# 4. Project Structure

```text
src/
├── data/
│   ├── raw/
│   ├── cleaned/
│   └── chunks/
│
├── embeddings/
│   ├── __init__.py
│   └── embedder.py
│
├── vectorstore/
│   ├── __init__.py
│   ├── build_index.py
│   ├── index.faiss
│   └── metadata.json
│
├── retriever/
│   ├── __init__.py
│   └── query_engine.py
│
├── generator/
├── pipelines/
│   ├── __init__.py
│   └── ingest.py
│
├── prompts/
├── models/
├── evaluation/
├── utils/
├── config/
├── logs/
│
└── RAG-ARCHITECTURE.md
```

---

# 5. Document Ingestion Pipeline

The ingestion pipeline is implemented in:

```text
pipelines/ingest.py
```

Its responsibility is to convert different document formats into a common representation that can later be embedded and retrieved.

The pipeline follows:

```text
Document
   ↓
Load
   ↓
Extract Text
   ↓
Clean
   ↓
Chunk
   ↓
Assign Metadata
```

---

# 6. Document Loading

Different file formats require different extraction mechanisms.

## TXT

TXT files are read directly as UTF-8 text.

```text
TXT
 ↓
Python file reader
 ↓
Raw text
```

## PDF

PDF files are processed using `pypdf`.

Text is extracted page-by-page.

Processing PDFs page-by-page allows the system to preserve the original page number as metadata.

```text
PDF
 ↓
PdfReader
 ↓
Page 1 → Text
Page 2 → Text
Page 3 → Text
```

## DOCX

DOCX files are processed using `python-docx`.

The paragraphs are extracted and combined into textual content.

```text
DOCX
 ↓
Document
 ↓
Paragraphs
 ↓
Text
```

DOCX page numbers are not assigned because pagination depends on document rendering and is not reliably represented by the paragraph extraction process.

## CSV

CSV files are loaded using Pandas.

The structured rows and columns are converted into a textual representation so that they can enter the text retrieval pipeline.

```text
CSV
 ↓
Pandas DataFrame
 ↓
Text representation
```

Dedicated natural-language-to-SQL processing for structured databases is introduced separately during Day 4.

---

# 7. Text Cleaning

Extracted documents may contain:

* Excessive whitespace
* Newlines
* Tabs
* Formatting artifacts

The cleaning stage normalizes whitespace before chunking.

Example:

```text
Employees receive annual leave.


Employees must submit requests.
```

becomes:

```text
Employees receive annual leave. Employees must submit requests.
```

This produces cleaner input for chunking and embedding.

---

# 8. Document Chunking

Large documents should not be treated as one enormous retrieval unit.

Documents are therefore divided into smaller chunks.

The implementation uses token-based chunking with:

```text
Chunk size = 600 tokens
Overlap    = 100 tokens
```

The assignment specifies approximately 500–800 token chunks, so 600 tokens provides a suitable value within that range.

Example:

```text
Large Document
      ↓
Chunk 1 → tokens 0–600
Chunk 2 → tokens 500–1100
Chunk 3 → tokens 1000–1600
Chunk 4 → tokens 1500–2100
```

---

# 9. Why Chunking is Required

Chunking improves retrieval precision.

Suppose a 100-page document contains information about:

* Leave policies
* Salaries
* Security
* Employee benefits
* Working hours

If the entire document were represented as one retrieval unit, the retrieved context would contain large amounts of irrelevant information.

Instead:

```text
Document
   ↓
Many smaller semantic chunks
   ↓
Retrieve only relevant chunks
```

This allows the system to find specific information more accurately.

---

# 10. Chunk Overlap

Chunks use an overlap of approximately 100 tokens.

Without overlap:

```text
Chunk 1:
"The employee must submit..."

Chunk 2:
"...the request five days earlier."
```

Important context could be divided between two chunks.

With overlap, some information from the end of one chunk appears at the beginning of the next.

```text
Chunk 1
████████████████

Chunk 2
            ████████████████
            ↑ overlap
```

This helps preserve contextual continuity across chunk boundaries.

---

# 11. Metadata Assignment

Every chunk contains metadata describing where the information originated.

Example:

```json
{
    "chunk_id": 1,
    "text": "Employees are entitled to 24 paid leave days per year.",
    "source": "company_policy.txt",
    "file_type": ".txt",
    "page_number": null,
    "tags": ["text"]
}
```

Metadata currently includes:

* `chunk_id`
* `source`
* `file_type`
* `page_number`
* `tags`

---

# 12. Why Metadata is Important

Metadata makes retrieval traceable.

Without metadata, the system may retrieve:

```text
Employees receive 24 paid leave days.
```

but we would not know where that information came from.

With metadata:

```text
Text:
Employees receive 24 paid leave days.

Source:
company_policy.txt

Page:
N/A
```

For PDFs, the actual page number is retained.

This becomes particularly useful for source attribution, filtering, debugging, and later advanced retrieval.

---

# 13. Embeddings

After chunking, textual chunks are converted into numerical representations called **embeddings**.

The project uses:

```text
BAAI/bge-small-en-v1.5
```

through Sentence Transformers.

The model produces:

```text
384-dimensional embeddings
```

Example:

```text
"Employees receive paid annual leave."
                 ↓
         BGE Embedding Model
                 ↓
[0.018, -0.247, 0.632, ..., 0.091]
```

---

# 14. What an Embedding Represents

An embedding represents the semantic meaning of text numerically.

For example:

```text
Employees receive annual leave.
```

and:

```text
Workers are given yearly paid holidays.
```

do not contain exactly the same words.

However, their meanings are related.

A semantic embedding model attempts to represent such semantically related sentences relatively close to each other in vector space.

This enables meaning-based retrieval rather than depending exclusively on exact keyword matching.

---

# 15. Embedding Normalization

The embedding model is configured with:

```python
normalize_embeddings=True
```

This normalizes vectors before storing and comparing them.

Normalized embeddings work conveniently with inner-product similarity for cosine-style semantic comparison.

---

# 16. Vector Store

The project uses:

```text
FAISS
```

for vector indexing and similarity search.

FAISS stores the numerical embedding vectors generated from document chunks.

The index is saved as:

```text
vectorstore/index.faiss
```

---

# 17. FAISS Index

The implementation uses:

```text
IndexFlatIP
```

where `IP` means **Inner Product**.

Because the embeddings are normalized, inner-product comparison can be used similarly to cosine similarity.

Higher similarity scores indicate stronger semantic similarity between a query and a stored chunk.

---

# 18. Metadata Storage

FAISS primarily stores and searches numerical vectors.

We still need to retain the actual:

* Text
* Source
* Page
* File type
* Tags

Therefore metadata is separately stored in:

```text
vectorstore/metadata.json
```

The position of a vector in FAISS corresponds to the position of its metadata record.

Example:

```text
FAISS vector 0
      ↕
metadata[0]

FAISS vector 1
      ↕
metadata[1]

FAISS vector 2
      ↕
metadata[2]
```

This allows retrieved vector IDs to be mapped back to the original document information.

---

# 19. Vector Index Construction

The vector index creation process is:

```text
data/raw/
    ↓
ingest_raw_documents()
    ↓
documents + chunks
    ↓
flatten chunks
    ↓
generate embeddings
    ↓
FAISS IndexFlatIP
    ↓
index.faiss
```

At the same time:

```text
Chunk metadata
      ↓
metadata.json
```

is persisted for later retrieval.

---

# 20. Query Retrieval

The retrieval system is implemented in:

```text
retriever/query_engine.py
```

The query engine loads:

```text
index.faiss
metadata.json
embedding model
```

and accepts a natural-language question.

Example:

```text
How many paid leave days do employees receive?
```

---

# 21. Query Embedding

The user's question is passed through the same embedding model used for the document chunks.

```text
User Question
      ↓
BGE-small-en-v1.5
      ↓
384-dimensional query vector
```

Using the same embedding space for documents and queries allows their semantic similarity to be compared.

---

# 22. Semantic Search

The query embedding is sent to FAISS.

```text
Query Vector
      ↓
FAISS
      ↓
Compare against stored vectors
      ↓
Rank by similarity
      ↓
Top-K chunks
```

FAISS returns:

* Similarity scores
* Matching vector indices

The vector indices are then mapped to `metadata.json`.

---

# 23. Example Retrieval

Test query:

```text
How many paid leave days do employees receive?
```

Retrieved result:

```text
Similarity Score: 0.8398

Source:
company_policy.txt

Chunk ID:
1

Text:
Employees are entitled to 24 paid leave days per year.
Employees must submit planned leave requests at least
five working days in advance...
```

This demonstrates that semantic retrieval works even when the user's exact wording differs from the wording stored in the document.

---

# 24. Current End-to-End Pipeline

The completed Day 1 implementation currently works as:

```text
PDF / DOCX / TXT / CSV
          ↓
     Document Loader
          ↓
      Text Cleaning
          ↓
     Token Chunking
          ↓
        Metadata
          ↓
    BGE Embeddings
          ↓
     FAISS Index
          ↓
      User Query
          ↓
    Query Embedding
          ↓
   Similarity Search
          ↓
   Relevant Document
        Chunks
```

---

# 25. Retriever vs Generator

The current Day 1 implementation focuses primarily on retrieval.

Currently:

```text
Question
   ↓
Retriever
   ↓
Relevant Context
```

A complete RAG system can extend this into:

```text
Question
   ↓
Retriever
   ↓
Relevant Context
   ↓
Generator / LLM
   ↓
Grounded Answer
```

The project architecture keeps retrieval separate from generation so that different local or hosted LLM providers can later be integrated without redesigning the retrieval pipeline.

---

# 26. Model Strategy

The project follows the hosted API path described in the Week 7 specification.

The architecture therefore allows the generation layer to use a hosted LLM while the retrieval components can remain locally controlled.

Current retrieval stack:

```text
Embedding Model → BAAI/bge-small-en-v1.5
Vector Store    → FAISS
Chunking        → Token-based
Retriever       → Semantic similarity search
```

The generation provider can be integrated separately without changing the document ingestion and retrieval architecture.

---

# 27. Separation of Responsibilities

The project separates functionality across modules.

## `pipelines/ingest.py`

Responsible for:

* Document loading
* Text extraction
* Cleaning
* Chunking
* Metadata assignment

## `embeddings/embedder.py`

Responsible for:

* Loading the embedding model
* Generating document embeddings
* Generating query embeddings

## `vectorstore/build_index.py`

Responsible for:

* Running ingestion
* Flattening chunks
* Generating embeddings
* Creating the FAISS index
* Saving metadata

## `retriever/query_engine.py`

Responsible for:

* Loading the FAISS index
* Loading metadata
* Embedding user queries
* Running similarity search
* Returning relevant chunks

This modular design makes the system easier to maintain and extend.

---


# 28. Tech Stack

The Day 1 RAG system uses the following technologies:

| Component              | Technology             | Purpose                                                 |
| ---------------------- | ---------------------- | ------------------------------------------------------- |
| Programming Language   | Python 3.12            | Core development language                               |
| Document Processing    | PyPDF                  | Extract text from PDF files                             |
| DOCX Processing        | python-docx            | Extract text from DOCX documents                        |
| CSV Processing         | Pandas                 | Read and process CSV files                              |
| Tokenization           | tiktoken               | Token-based document chunking                           |
| Embedding Model        | BAAI/bge-small-en-v1.5 | Convert text into 384-dimensional semantic vectors      |
| Embedding Framework    | Sentence Transformers  | Load and run the BGE embedding model                    |
| Vector Search          | FAISS                  | Store/index embeddings and perform similarity search    |
| Vector Index           | IndexFlatIP            | Inner-product similarity search over normalized vectors |
| Metadata Storage       | JSON                   | Store chunk text, source, page number, tags, etc.       |
| LLM Strategy           | Hosted API — Path B    | Generation layer for the broader RAG architecture       |
| Environment Management | Python venv            | Isolate project dependencies                            |

## Stack Flow

```text
PDF / DOCX / TXT / CSV
          ↓
PyPDF / python-docx / Python / Pandas
          ↓
      Text Cleaning
          ↓
       tiktoken
          ↓
    600-token chunks
          ↓
BAAI/bge-small-en-v1.5
          ↓
384-dimensional embeddings
          ↓
        FAISS
          ↓
   Semantic Retrieval
```
---

# 29. Day 1 Deliverables

The following Day 1 components have been implemented:

```text
pipelines/ingest.py
embeddings/embedder.py
vectorstore/index.faiss
retriever/query_engine.py
RAG-ARCHITECTURE.md
```

Additional supporting files include:

```text
vectorstore/build_index.py
vectorstore/metadata.json
```

---

# 30. Day 1 Completion Checklist

| Requirement                 | Status   |
| --------------------------- | -------- |
| Load TXT documents          | Complete |
| Load PDF documents          | Complete |
| Load DOCX documents         | Complete |
| Load CSV documents          | Complete |
| Clean extracted text        | Complete |
| Create 500–800 token chunks | Complete |
| Add chunk overlap           | Complete |
| Assign metadata             | Complete |
| Generate local embeddings   | Complete |
| Initialize FAISS            | Complete |
| Persist vector index        | Complete |
| Preserve chunk metadata     | Complete |
| Build basic retriever       | Complete |
| Perform semantic search     | Complete |
| Trace retrieved source      | Complete |

---

# 31. Day 1 Outcome

Day 1 establishes the fundamental retrieval architecture required by the later stages of the project.

The system can now:

1. Accept multiple document formats.
2. Extract their textual information.
3. Clean the extracted text.
4. Divide the text into overlapping chunks.
5. associate metadata with those chunks.
6. Convert chunks into semantic embeddings.
7. Store embeddings inside FAISS.
8. Convert natural-language questions into query embeddings.
9. Search for semantically related chunks.
10. Return the relevant text together with source information.

This creates the foundation required for the next stage: **advanced retrieval and context engineering**, where semantic retrieval will be enhanced using techniques such as keyword search, reranking, deduplication, filtering, and improved context construction.
