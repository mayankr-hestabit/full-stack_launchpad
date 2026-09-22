# Week 9 — Day 4: Memory Systems

## Overview

Day 4 focuses on adding memory capabilities to the Agentic AI system.

The memory system supports three major types of memory:

* Session memory
* Long-term memory using SQLite
* Vector memory using FAISS

The implementation also distinguishes between:

* Semantic memory
* Episodic memory

These memory systems allow the application to retain recent conversation context, persist important information across application restarts, and retrieve relevant memories using semantic similarity.

---

# Memory Architecture

```text
                    MEMORY SYSTEM
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
 Session Memory     Long-Term Memory   Vector Memory
     deque               SQLite            FAISS
        │                │                │
 Recent context     Persistent data    Semantic search
```

---

# 1. Session Memory

Session memory stores recent conversation messages while the application is running.

Implementation:

```text
memory/session_memory.py
```

It uses a Python `deque` with a fixed maximum size.

Example:

```text
Message 1
Message 2
Message 3
...
Message 10
```

When a new message is added after the memory limit is reached, the oldest message is automatically removed.

Example:

```text
Before:

Message 1
Message 2
Message 3

After adding Message 4 with max size 3:

Message 2
Message 3
Message 4
```

This creates a bounded short-term memory window.

Session memory is temporary and disappears when the application stops.

---

# 2. Long-Term Memory

Long-term memory stores information permanently using SQLite.

Implementation:

```text
memory/long_term_memory.py
```

Database:

```text
memory/long_term.db
```

The SQLite database contains a `memories` table.

```text
memories
├── id
├── content
├── memory_type
└── created_at
```

Example stored memory:

```text
User prefers Python for backend development.
```

Unlike session memory, long-term memory remains available after the program stops and restarts.

---

# 3. Semantic Memory

Semantic memory represents facts, preferences, or general knowledge.

Example:

```text
User prefers Python for backend development.
```

Another example:

```text
User prefers FastAPI for building APIs.
```

Semantic memory answers the question:

```text
What do we know?
```

---

# 4. Episodic Memory

Episodic memory stores information about previous events or experiences.

Example:

```text
User worked on a tool-calling agent using Python.
```

Another example:

```text
User debugged a Docker issue yesterday.
```

Episodic memory answers the question:

```text
What happened?
```

---

# 5. Semantic vs Episodic Memory

```text
Semantic Memory
→ Facts
→ Preferences
→ General knowledge

Episodic Memory
→ Events
→ Activities
→ Previous experiences
```

Example:

```text
Semantic:
User prefers Python.

Episodic:
User worked on a Python agent yesterday.
```

---

# 6. Vector Memory

Vector memory allows memories to be retrieved according to meaning instead of exact keyword matching.

Implementation:

```text
memory/vector_store.py
```

The project uses:

* Sentence Transformers
* BAAI/bge-small-en-v1.5
* FAISS

The embedding model converts text into numerical vectors.

Example:

```text
"User prefers Python for backend development."
                ↓
           Embedding Model
                ↓
[0.12, -0.45, 0.78, ...]
```

These vectors are stored inside FAISS.

---

# 7. Vector Search Flow

```text
Stored Memory
     ↓
Embedding Model
     ↓
Vector
     ↓
FAISS Index
```

When a query is received:

```text
User Query
    ↓
Embedding Model
    ↓
Query Vector
    ↓
FAISS Search
    ↓
Relevant Memories
```

This allows the system to find memories even when the query uses different words.

---

# 8. Example Semantic Search

Stored memories:

```text
User prefers Python for backend development.

User prefers FastAPI for building APIs.

User worked on SQLite database integration.
```

Query:

```text
What should I use to build a Python backend API?
```

Retrieved memories:

```text
User prefers Python for backend development.

User prefers FastAPI for building APIs.
```

The query does not need to exactly match the stored sentences.

FAISS retrieves memories according to semantic similarity.

---

# 9. Similarity Scores

The system uses normalized embeddings with FAISS inner-product search.

Example result:

```text
Python backend preference    → 0.8208

FastAPI preference           → 0.7330

Previous Python activity     → 0.6845
```

Higher scores indicate greater semantic similarity between the query and the stored memory.

---

# 10. Persistent Vector Memory

FAISS vector memory is saved using:

```text
memory/memory.index
```

Memory metadata is stored in:

```text
memory/memory_metadata.json
```

The metadata contains the original text and memory type.

Example:

```json
{
    "content": "User prefers Python for backend development.",
    "memory_type": "semantic"
}
```

The FAISS index and metadata can be loaded again when the application restarts.

---

# 11. Integrated Memory Flow

The Day 4 demonstration combines all three memory systems.

```text
User Interaction
      ↓
Session Memory
      ↓
Recent conversation stored
      ↓
Important information
      ↓
SQLite Long-Term Memory
      ↓
Embedding Generation
      ↓
FAISS Vector Memory
      ↓
Semantic Retrieval
```

---

# 12. Session Memory Test

Session memory was tested using a limited memory window.

Example:

```text
Maximum messages = 3
```

After adding four messages, the oldest message was automatically removed.

This confirmed bounded short-term memory behavior.

---

# 13. Long-Term Memory Test

The SQLite memory system stored both semantic and episodic memories.

Example semantic memory:

```text
User prefers Python for backend development.
```

Example episodic memory:

```text
User debugged a Python tool-calling agent today.
```

Both memory types were successfully retrieved separately from SQLite.

---

# 14. Vector Memory Test

The FAISS vector store was tested using the query:

```text
Which technology does the user prefer for creating backend APIs?
```

Relevant memories were retrieved according to semantic similarity.

The most relevant results included:

```text
User prefers Python for backend development.

User likes FastAPI for building APIs.
```

This verified that vector retrieval works even when the query wording differs from the stored memory.

---

# 15. Integrated Day 4 Test

The complete Day 4 flow was tested using:

```text
day4_main.py
```

The program successfully demonstrated:

```text
Session Memory
        +
SQLite Long-Term Memory
        +
FAISS Vector Memory
        +
Semantic Retrieval
```

The final memory summary confirmed:

```text
Session Memory Messages: 3

Long-Term Memories: 3

Vector Memories: 3
```

---

# Project Structure

```text
week9-agentic-ai/
│
├── memory/
│   ├── __init__.py
│   ├── session_memory.py
│   ├── long_term_memory.py
│   ├── vector_store.py
│   ├── long_term.db
│   ├── memory.index
│   └── memory_metadata.json
│
├── day4_main.py
└── MEMORY-SYSTEM.md
```

---

# Technologies Used

## Python deque

Used for bounded session memory.

```text
Purpose:
Store recent conversation context.
```

---

## SQLite

Used for persistent long-term memory.

```text
Purpose:
Store memories across application restarts.
```

---

## Sentence Transformers

Used to convert text memories into numerical embeddings.

Model:

```text
BAAI/bge-small-en-v1.5
```

---

## FAISS

Used for efficient vector similarity search.

```text
Purpose:
Retrieve semantically relevant memories.
```

---

# Key Concepts Covered

Day 4 demonstrates:

* Short-term memory
* Session memory
* Persistent memory
* SQLite memory
* Vector memory
* Embeddings
* FAISS similarity search
* Semantic memory
* Episodic memory
* Memory retrieval
* Memory persistence

---

# Final Outcome

Day 4 adds multiple levels of memory to the Agentic AI system.

The final architecture supports:

```text
Recent Conversation
        ↓
Session Memory

Persistent Information
        ↓
SQLite Memory

Meaning-Based Retrieval
        ↓
FAISS Vector Memory
```

This provides the foundation for agents that can retain context, remember useful information, and retrieve relevant memories when needed.
