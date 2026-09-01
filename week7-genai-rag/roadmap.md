files:

WEEK 7
│
├── DAY 1 — BASIC SEMANTIC RAG
│   │
│   ├── pipelines/ingest.py
│   │      ├── Document loading
│   │      ├── Cleaning
│   │      ├── Tokenization
│   │      ├── Chunking
│   │      └── Metadata
│   │
│   ├── embeddings/embedder.py
│   │      ├── BGE-small
│   │      ├── Text → vectors
│   │      ├── 384 dimensions
│   │      └── Normalized embeddings
│   │
│   ├── vectorstore/build_index.py
│   │      ├── Generate embeddings
│   │      ├── FAISS IndexFlatIP
│   │      ├── index.faiss
│   │      └── metadata.json
│   │
│   ├── retriever/query_engine.py
│   │      ├── Query → embedding
│   │      ├── FAISS similarity search
│   │      └── Vector → original chunk
│   │
│   └── RAG-ARCHITECTURE.md
│
│
└── DAY 2 — ADVANCED RETRIEVAL
    │
    ├── retriever/hybrid_retriever.py
    │      ├── Semantic retrieval
    │      │      └── BGE + FAISS
    │      ├── Keyword retrieval
    │      │      └── BM25
    │      ├── Metadata filtering
    │      └── RRF fusion
    │
    ├── retriever/reranker.py
    │      └── CrossEncoder reranking
    │
    ├── pipelines/context_builder.py
    │      ├── Deduplication
    │      ├── similarity_threshold
    │      ├── Token counting
    │      ├── Context-size control
    │      └── Traceable sources
    │
    └── RETRIEVAL-STRATEGIES.md



workflow:

Day1:

RAW DOCUMENTS
      │
      ▼
┌────────────────────────────┐
│ 1. pipelines/ingest.py     │
│                            │
│ Load documents             │
│ Clean text                 │
│ Split into ~600-token      │
│ chunks with overlap        │
│ Attach metadata            │
└─────────────┬──────────────┘
              │
              ▼
        Text Chunks
              │
              ▼
┌────────────────────────────┐
│ 2. embeddings/embedder.py  │
│                            │
│ Load BGE-small             │
│ Test text → embedding      │
│ Verify 384 dimensions      │
└─────────────┬──────────────┘
              │
              ▼
       BGE is working
              │
              ▼
┌────────────────────────────┐
│ 3. build_index.py          │
│                            │
│ Calls ingest.py            │
│ Calls embedder.py          │
│ Embeds ALL chunks          │
│ Creates FAISS index        │
│ Saves index.faiss          │
│ Saves metadata.json        │
└─────────────┬──────────────┘
              │
              ▼
       KNOWLEDGE BASE
              │
       ┌──────┴──────┐
       ▼             ▼
 index.faiss    metadata.json
   vectors       original text
       │             │
       └──────┬──────┘
              ▼
┌────────────────────────────┐
│ 4. query_engine.py         │
│                            │
│ Take user query            │
│ BGE → query vector         │
│ Search index.faiss         │
│ Find closest vector IDs    │
│ Use metadata.json          │
│ Return original chunks     │
└────────────────────────────┘

Day2:

Existing Day 1
index.faiss + metadata.json
           │
           ▼
hybrid_retriever.py
           │
     ┌─────┴─────┐
     ▼           ▼
BGE + FAISS     BM25
     │           │
     └─────┬─────┘
           ▼
          RRF
           ↓
    Hybrid candidates
           ↓
      reranker.py
           ↓
     CrossEncoder
           ↓
  Better-ranked chunks
           ↓
  context_builder.py
           ↓
  Dedup + token control
           ↓
    Final context