# Retrieval Strategies — Week 7 Day 2

## 1. Overview

Day 2 focuses on improving the retrieval quality of the RAG system developed on Day 1.

On Day 1, the system used semantic/vector retrieval:

```text
User Query
    ↓
BGE-small Embedding
    ↓
FAISS Vector Search
    ↓
Relevant Document Chunks
```

Although semantic retrieval is useful for finding information based on meaning, relying only on vector similarity can sometimes miss documents containing important exact keywords.

Therefore, Day 2 introduces **Hybrid Retrieval**, which combines:

- Semantic Retrieval — BGE-small + FAISS
- Keyword Retrieval — BM25
- Reciprocal Rank Fusion (RRF)
- Metadata Filtering
- CrossEncoder Reranking
- Deduplication
- Context Size Control
- Traceable Sources

The final objective is to retrieve a small set of highly relevant, non-redundant chunks that can later be supplied to an LLM for answer generation.

---

# 2. Day 2 Retrieval Architecture

The complete Day 2 retrieval pipeline is:

```text
                         User Query
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
        Semantic Retrieval         Keyword Retrieval
          BGE + FAISS                   BM25
                │                         │
                └────────────┬────────────┘
                             │
                             ▼
                 Reciprocal Rank Fusion
                           (RRF)
                             │
                             ▼
                    Hybrid Candidates
                             │
                             ▼
                  CrossEncoder Reranker
                             │
                             ▼
                     Deduplication
                             │
                             ▼
                  Context Size Control
                             │
                             ▼
                  Final Ranked Context
                             │
                             ▼
                         Future LLM
```

This architecture separates fast retrieval from more expensive relevance evaluation.

---

# 3. Semantic Retrieval

Semantic retrieval was introduced on Day 1 and reused as one component of the Day 2 hybrid retriever.

Technologies used:

- BAAI/bge-small-en-v1.5
- Sentence Transformers
- FAISS
- IndexFlatIP

The user's query is first converted into an embedding using BGE-small.

Example:

```text
"Explain how credit underwriting works"
                ↓
            BGE-small
                ↓
       384-dimensional vector
```

FAISS then compares the query vector with the document vectors stored inside the FAISS index.

Because the embeddings are normalized, inner-product similarity can be used to rank semantically related chunks.

Semantic retrieval focuses primarily on the **meaning of the query** rather than exact keyword matching.

Example:

```text
Query:
"How does a bank determine whether someone should receive a loan?"
```

A semantic retriever may still retrieve a document about:

```text
Credit underwriting and borrower risk assessment
```

even if the exact words in the query are different.

---

# 4. Keyword Retrieval Using BM25

Day 2 introduces keyword retrieval using **BM25**.

Library used:

```text
rank-bm25
```

BM25 ranks documents based on the importance and occurrence of query terms inside document chunks.

Before using BM25, the text is tokenized.

Example:

```text
"Explain how credit underwriting works"
```

becomes approximately:

```text
[
    "explain",
    "how",
    "credit",
    "underwriting",
    "works"
]
```

BM25 then determines which chunks contain the most useful matching terms.

Unlike semantic retrieval, BM25 focuses heavily on **lexical or keyword similarity**.

---

# 5. Semantic Search vs Keyword Search

Semantic retrieval and keyword retrieval solve different problems.

## Semantic Search

Uses:

```text
BGE-small + FAISS
```

It asks:

> Which document chunk has a meaning similar to the query?

It is useful when the query and document express the same idea using different words.

---

## Keyword Search

Uses:

```text
BM25
```

It asks:

> Which document chunk contains important words from the query?

It is particularly useful for:

- technical terminology
- names
- policy numbers
- dates
- identifiers
- exact phrases
- domain-specific keywords

---

# 6. Why Hybrid Retrieval?

Neither semantic retrieval nor keyword retrieval is perfect on its own.

Semantic retrieval can understand meaning but may sometimes overlook important exact terminology.

BM25 is strong at exact keyword matching but does not understand meaning as deeply as an embedding model.

Therefore, both approaches are combined.

```text
Semantic Retrieval
        +
Keyword Retrieval
        =
Hybrid Retrieval
```

This allows the system to benefit from both semantic understanding and exact keyword matching.

---

# 7. Hybrid Retriever

The Day 2 hybrid retrieval implementation is located at:

```text
retriever/hybrid_retriever.py
```

The hybrid retriever performs:

```text
Query
  │
  ├── Semantic Search
  │      ↓
  │   BGE-small
  │      ↓
  │    FAISS
  │
  └── Keyword Search
         ↓
        BM25
```

Both retrieval methods initially produce their own ranked results.

These rankings are then combined using Reciprocal Rank Fusion.

---

# 8. Reciprocal Rank Fusion (RRF)

The scores generated by FAISS and BM25 should not be directly added together because they belong to different scoring systems.

For example:

```text
FAISS Score = 0.8379
BM25 Score  = 1.8570
```

These values are not directly comparable.

Instead of combining raw scores, the project uses **Reciprocal Rank Fusion (RRF)**.

RRF focuses on the ranking position of each chunk.

The simplified RRF formula is:

```text
RRF Score = 1 / (k + rank)
```

where:

```text
k = RRF constant
rank = position of the document
```

The implementation uses:

```text
k = 60
```

If a chunk performs well in both semantic and keyword retrieval, it receives contributions from both ranking lists.

Example:

```text
Semantic Search

Chunk A → Rank 1
Chunk B → Rank 2
Chunk C → Rank 3


BM25 Search

Chunk C → Rank 1
Chunk A → Rank 2
Chunk D → Rank 3
```

RRF combines these rankings.

Chunks appearing near the top of both lists generally receive stronger final RRF scores.

---

# 9. RRF Is Fusion, Not Final Relevance Evaluation

An important distinction in the architecture is that RRF and the CrossEncoder reranker perform different jobs.

RRF asks:

> Which chunks performed well across our retrieval systems?

It combines rankings produced by FAISS and BM25.

However, RRF does not deeply evaluate the query and chunk together.

Therefore, the output of RRF should be considered a set of **strong retrieval candidates** rather than the final relevance judgment.

---

# 10. Metadata Filtering

The hybrid retriever also supports metadata-based filtering.

Example:

```python
filters = {
    "year": "2024",
    "type": "policy"
}
```

Filtering allows the retrieval system to restrict results to information satisfying particular conditions.

Supported filtering in the current implementation includes:

```text
year
type
source
file_type
```

For example:

```text
Query:
"Explain how credit underwriting works"

Filters:
year = 2024
type = policy
```

The objective is to retrieve relevant information specifically associated with the required policy and year.

---

# 11. Current Metadata Filtering Limitation

The current implementation does not yet store `year` and `type` as dedicated structured metadata fields for every chunk.

The existing chunk metadata primarily contains fields such as:

```json
{
    "chunk_id": 1,
    "source": "credit_underwriting.txt",
    "file_type": ".txt",
    "page_number": null,
    "tags": ["text"]
}
```

Therefore, the current filtering logic may inspect the source name, tags, or chunk text when evaluating filters such as `year` and `type`.

A stronger future implementation would store structured metadata directly:

```json
{
    "chunk_id": 1,
    "source": "credit_underwriting.txt",
    "file_type": ".txt",
    "year": "2024",
    "type": "policy",
    "page_number": null
}
```

This would make filtering more reliable because every chunk belonging to a document would inherit the document-level metadata.

---

# 12. CrossEncoder Reranking

After hybrid retrieval, the system performs a second relevance-ranking stage.

Implementation:

```text
retriever/reranker.py
```

Model used:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

The hybrid retriever first produces candidate chunks.

The CrossEncoder then evaluates:

```text
(Query, Chunk 1)
(Query, Chunk 2)
(Query, Chunk 3)
...
```

and produces relevance scores.

The chunks are sorted again according to these scores.

---

# 13. Why Is a CrossEncoder Needed After RRF?

RRF already produces a ranking, but its ranking is based on the positions produced by the retrieval systems.

For example:

```text
Semantic:

Chunk A → Rank 1
Chunk B → Rank 2


BM25:

Chunk B → Rank 1
Chunk A → Rank 2
```

RRF combines these ranking positions.

However, it does not deeply inspect whether Chunk A or Chunk B answers the user's exact question better.

A CrossEncoder evaluates the query and document together.

Therefore:

```text
RRF:
"Which chunks were ranked well by the retrievers?"

CrossEncoder:
"Which candidate is actually most relevant to this query?"
```

This provides a more precise final ranking.

---

# 14. Why Not Use the CrossEncoder for Every Document?

CrossEncoder reranking is more computationally expensive than FAISS or BM25 retrieval.

Suppose the system contains:

```text
100,000 chunks
```

Running:

```text
Query × 100,000 chunks
```

through a CrossEncoder would be inefficient.

Instead, the architecture uses:

```text
100,000 chunks
      ↓
FAISS + BM25
      ↓
Small candidate set
      ↓
RRF Fusion
      ↓
CrossEncoder
      ↓
Final best chunks
```

Therefore:

```text
FAISS + BM25
    → Fast candidate retrieval

RRF
    → Ranking fusion

CrossEncoder
    → Precise candidate reranking
```

---

# 15. Reranking Test

The query:

```text
Explain how credit underwriting works
```

produced reranker results such as:

```text
Chunk 1
Reranker Score: 5.8676

Chunk 5
Reranker Score: 2.2865
```

Chunk 1 contains the definition, purpose, credit application process, identity verification, and beginning of the income assessment process.

Therefore, it received a substantially stronger relevance score for the query.

---

# 16. Context Builder

After reranking, the selected chunks must be prepared before they can eventually be sent to an LLM.

This logic is implemented in:

```text
pipelines/context_builder.py
```

The Context Builder performs two major tasks:

1. Deduplication
2. Context-size control

It also preserves source information for traceability.

---

# 17. Deduplication

Documents are chunked with overlap so that information near chunk boundaries is not lost.

For example:

```text
Chunk 1
-------------------------
AAAAAAAAAAAAAAAA
BBBBBBBBBBBBBBBB


Chunk 2
-------------------------
BBBBBBBBBBBBBBBB
CCCCCCCCCCCCCCCC
```

The repeated section helps maintain context during retrieval.

However, multiple retrieved chunks may therefore contain largely repeated information.

Sending all repeated information to an LLM would:

- waste context tokens
- increase processing cost
- introduce unnecessary repetition
- reduce context quality

Therefore, the Context Builder performs deduplication.

---

# 18. Similarity Threshold

The current Context Builder uses a simple word-overlap approach for detecting duplicate or near-duplicate chunks.

The configured threshold is:

```python
similarity_threshold = 0.85
```

The simplified calculation is:

```text
common words
----------------
new chunk words
```

If the resulting similarity is greater than or equal to:

```text
0.85
```

the new chunk is treated as sufficiently redundant and is skipped.

Example:

```text
Similarity = 0.90
Threshold  = 0.85

0.90 >= 0.85
```

Result:

```text
Skip duplicate chunk
```

But:

```text
Similarity = 0.60
Threshold  = 0.85

0.60 < 0.85
```

Result:

```text
Keep chunk
```

This threshold is part of the project's deduplication logic. It is not a FAISS similarity score, BGE score, BM25 score, or CrossEncoder score.

---

# 19. Context Size Control

An LLM has a limited context window.

Therefore, the system should not blindly send every retrieved chunk to the generation model.

The current Context Builder uses:

```python
max_tokens = 1800
```

Each candidate chunk is tokenized using `tiktoken`.

Before adding a chunk:

```text
Current Context Tokens
        +
New Chunk Tokens
        ↓
Compare with max_tokens
```

If:

```text
total_tokens + chunk_tokens <= max_tokens
```

the chunk is accepted.

If:

```text
total_tokens + chunk_tokens > max_tokens
```

the chunk is skipped.

This prevents the final retrieval context from exceeding the configured context budget.

---

# 20. Context Builder Test

During testing, the Context Builder produced:

```text
Chunks selected: 2
Total tokens: 900
Maximum allowed tokens: 1800
```

This confirms that the final selected context remained within the configured token budget.

---

# 21. Traceable Sources

Each chunk retains metadata describing where the information originated.

The final context contains headers similar to:

```text
[Source 1]
File: credit_underwriting.txt
Page: None
Chunk: 1
```

This makes retrieved information traceable.

Traceability is important because later the generation layer can use this metadata for:

- source attribution
- citations
- debugging
- evaluation
- hallucination analysis

---

# 22. Complete Day 2 Retrieval Flow

The complete retrieval process developed during Day 2 is:

```text
1. User submits query
        ↓
2. Query converted into BGE embedding
        ↓
3. FAISS performs semantic retrieval
        ↓
4. BM25 performs keyword retrieval
        ↓
5. RRF combines both rankings
        ↓
6. Metadata filters restrict candidates
        ↓
7. CrossEncoder reranks candidates
        ↓
8. Duplicate/overlapping chunks are removed
        ↓
9. Context token budget is enforced
        ↓
10. Source information is preserved
        ↓
11. Final context is ready for generation
```

---

# 23. Day 1 vs Day 2

## Day 1

Day 1 implemented semantic/vector retrieval:

```text
Documents
    ↓
Chunking
    ↓
BGE-small
    ↓
Embeddings
    ↓
FAISS
    ↓
Semantic Retrieval
```

Main idea:

> Retrieve documents based on semantic similarity.

---

## Day 2

Day 2 extends the retrieval architecture:

```text
                 Query
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
   BGE + FAISS               BM25
        │                     │
        └──────────┬──────────┘
                   ▼
                  RRF
                   ▼
            Hybrid Results
                   ▼
             CrossEncoder
                   ▼
             Deduplication
                   ▼
          Context Size Control
                   ▼
             Final Context
```

Main idea:

> Combine semantic and keyword retrieval, then refine the retrieved information before generation.

---

# 24. Technologies Used on Day 2

| Component | Technology |
|---|---|
| Programming Language | Python 3.12 |
| Semantic Embeddings | BAAI/bge-small-en-v1.5 |
| Embedding Library | Sentence Transformers |
| Vector Search | FAISS |
| FAISS Index | IndexFlatIP |
| Keyword Retrieval | BM25 |
| BM25 Library | rank-bm25 |
| Rank Fusion | Reciprocal Rank Fusion (RRF) |
| Reranker | CrossEncoder |
| Reranker Model | cross-encoder/ms-marco-MiniLM-L-6-v2 |
| Token Counting | tiktoken |
| Metadata Storage | JSON |
| Deduplication | Word-overlap similarity |
| Context Control | Token-budget based selection |

---

# 25. Day 2 Deliverables

The following Day 2 components have been implemented:

```text
src/
│
├── retriever/
│   ├── query_engine.py
│   ├── hybrid_retriever.py
│   └── reranker.py
│
├── pipelines/
│   └── context_builder.py
│
└── RETRIEVAL-STRATEGIES.md
```

### hybrid_retriever.py

Responsible for:

- semantic retrieval
- BGE query embeddings
- FAISS search
- BM25 keyword retrieval
- RRF fusion
- metadata filtering

### reranker.py

Responsible for:

- receiving hybrid candidates
- evaluating query/chunk pairs
- CrossEncoder relevance scoring
- producing the final relevance ranking

### context_builder.py

Responsible for:

- receiving reranked chunks
- deduplication
- token counting
- context-size control
- source preservation
- construction of final context

---

# 26. Final Summary

Day 2 upgrades the Day 1 semantic retrieval system into a more advanced retrieval pipeline.

The final strategy can be summarized as:

```text
Semantic Search
(BGE + FAISS)
        +
Keyword Search
(BM25)
        ↓
RRF Fusion
        ↓
Metadata Filtering
        ↓
CrossEncoder Reranking
        ↓
Deduplication
        ↓
Context Size Control
        ↓
Traceable Final Context
```

The system now retrieves information using both semantic meaning and keyword matching, combines the retrieval rankings, reranks the strongest candidates, removes redundant information, controls the final context size, and preserves document sources.

This final context is ready to be passed to the generation layer of the RAG system.