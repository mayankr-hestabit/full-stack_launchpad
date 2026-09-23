# Week 9 — Agentic AI & Multi-Agent System Design

## NEXUS AI

NEXUS AI is a local multi-agent system built during Week 9 of the Agentic AI module.

The project demonstrates how multiple specialized AI agents can collaborate through planning, task delegation, tool execution, memory, reflection, optimization, validation, and reporting.

The system runs locally using a fine-tuned and quantized Qwen model served through `llama.cpp`.

---

## Project Objective

The objective of this project is to understand and implement an Agentic AI system in which an LLM is not used only as a chatbot.

Instead, multiple agents are assigned specialized responsibilities and cooperate to solve a user task.

The complete Week 9 project covers:

* AI agent fundamentals
* Multi-agent communication
* Planner-worker orchestration
* Parallel execution
* Tool-using agents
* Python execution
* SQLite database tools
* File tools
* Session memory
* Long-term memory
* FAISS vector memory
* Semantic and episodic memory
* Reflection
* Optimization
* Validation
* Logging and tracing
* Failure handling
* Final multi-agent orchestration

---

# Technology Stack

The project uses:

* Python
* Microsoft AutoGen
* Qwen/Qwen2.5-1.5B-Instruct
* llama.cpp
* GGUF
* SQLite
* FAISS
* Sentence Transformers
* BAAI/bge-small-en-v1.5
* asyncio
* Python logging

The complete system runs locally without requiring a paid LLM API.

---

# Local LLM

The project reuses the fine-tuned and quantized model created during Week 8.

Model:

```text
Qwen/Qwen2.5-1.5B-Instruct
```

Quantized model:

```text
model.gguf
```

The model is served through `llama.cpp`.

Example server:

```bash
~/llama.cpp/build/bin/llama-server \
-m /home/mayank/full-stack_launchpad/week8-llm-fine-tuning/quantized/model.gguf \
--host 127.0.0.1 \
--port 8080
```

The AutoGen model client connects to:

```text
http://127.0.0.1:8080/v1
```

---

# Project Structure

```text
week9-agentic-ai/
│
├── agents/
│   ├── research_agent.py
│   ├── summarizer_agent.py
│   ├── answer_agent.py
│   ├── worker_agent.py
│   ├── reflection_agent.py
│   ├── validator.py
│   ├── code_agent.py
│   ├── analyst_agent.py
│   ├── critic_agent.py
│   ├── optimizer_agent.py
│   ├── reporter_agent.py
│   └── memory_agent.py
│
├── orchestrator/
│   └── planner.py
│
├── tools/
│   ├── code_executor.py
│   ├── db_agent.py
│   └── file_agent.py
│
├── memory/
│   ├── session_memory.py
│   ├── long_term_memory.py
│   ├── vector_store.py
│   ├── long_term.db
│   ├── memory.index
│   └── memory_metadata.json
│
├── nexus_ai/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── orchestrator.py
│   ├── logger.py
│   ├── memory_manager.py
│   └── tool_router.py
│
├── data/
│   ├── sales.csv
│   ├── day3.db
│   └── day3_report.txt
│
├── logs/
│
├── main.py
├── day2_main.py
├── day3_main.py
├── day4_main.py
├── day4_agent.py
├── persistent_chat_demo.py
│
├── AGENT-FUNDAMENTALS.md
├── FLOW-DIAGRAM.md
├── TOOL-CHAIN.md
├── MEMORY-SYSTEM.md
├── ARCHITECTURE.md
├── FINAL-REPORT.md
└── README.md
```

---

# Day 1 — Agent Foundations

Day 1 introduced the fundamental Agentic AI workflow.

Three specialized agents were created:

```text
Research Agent
      ↓
Summarizer Agent
      ↓
Answer Agent
```

Each agent has:

* A separate role
* A dedicated system prompt
* Strict job boundaries
* A memory window

The agents communicate by passing the output of one agent into the next.

---

# Day 2 — Multi-Agent Orchestration

Day 2 introduced planner-worker orchestration.

Flow:

```text
User
 ↓
Planner
 ↓
Parallel Workers
 ↓
Reflection
 ↓
Validator
 ↓
Final Result
```

The Planner decomposes a task into executable subtasks.

Worker Agents execute independent tasks in parallel using:

```python
asyncio.gather()
```

The Reflection Agent combines and improves results.

The Validator checks whether the result sufficiently addresses the original task.

---

# Day 3 — Tool-Using Agents

Day 3 added real local tools.

Implemented capabilities:

* Python code generation
* Python execution
* SQLite queries
* TXT file read/write
* CSV file read/write
* Execution validation
* Retry and repair logic

Example flow:

```text
sales.csv
   ↓
File Tool
   ↓
Normalize Data
   ↓
Code Agent
   ↓
Generated Python Logic
   ↓
Python Executor
   ↓
Validate Result
   ↓
DB Agent
   ↓
SQLite
   ↓
File Writer
```

The system uses system-to-tool execution because the local LLM configuration does not provide native function calling.

---

# Day 4 — Memory Systems

Day 4 introduced three memory layers.

## Session Memory

Uses a bounded Python `deque`.

Purpose:

```text
Store recent conversation messages
```

---

## Long-Term Memory

Uses SQLite.

Purpose:

```text
Persist memories across application restarts
```

Database:

```text
memory/long_term.db
```

---

## Vector Memory

Uses:

```text
Sentence Transformer
        ↓
Embeddings
        ↓
FAISS
```

The embedding model is:

```text
BAAI/bge-small-en-v1.5
```

FAISS retrieves relevant memories according to semantic similarity.

---

# Semantic and Episodic Memory

Semantic memory stores facts and preferences.

Example:

```text
User prefers Python for backend development.
```

Episodic memory stores previous events.

Example:

```text
User worked on a Python tool-calling agent.
```

---

# Persistence Demonstration

The project also includes:

```text
persistent_chat_demo.py
```

A memory can be stored during one program execution.

The program can then be closed and restarted.

The same memory can later be retrieved from SQLite and FAISS.

This demonstrates persistent memory across separate application runs.

---

# Day 5 — NEXUS AI

Day 5 combines the previous components into the final multi-agent system.

NEXUS includes the following major roles:

```text
Orchestrator
Planner
Workers
Analyst
Critic
Optimizer
Validator
Reporter
```

Existing specialized agents and tools are reused rather than duplicated.

---

# NEXUS Execution Flow

```text
User Task
    ↓
Memory Retrieval
    ↓
Planner
    ↓
Task Delegation
    ↓
Workers / Tools
    ↓
Analyst
    ↓
Critic
    ↓
Optimizer
    ↓
Validator
    ↓
Reporter
    ↓
Final Response
```

---

# Planner

The Planner converts the user goal into concrete subtasks.

Example:

```text
Design a scalable backend architecture.
```

can become:

```text
1. Select backend architecture.
2. Design APIs.
3. Design database structure.
4. Plan caching.
5. Plan load balancing.
6. Plan reliability.
```

---

# Worker Agents

Workers receive:

* Original user task
* Individual assigned subtask

This prevents them from losing the original context.

Independent tasks can execute concurrently.

---

# Analyst

The Analyst combines execution results and identifies useful technical findings.

It does not create a new plan or final report.

---

# Critic

The Critic reviews the result for:

* Missing information
* Weak explanations
* Contradictions
* Unsupported assumptions
* Irrelevant information

This provides the self-reflection stage.

---

# Optimizer

The Optimizer improves the result using Critic feedback.

It preserves correct information while improving weak parts.

This provides the self-improvement stage.

---

# Validator

The Validator determines whether the optimized result sufficiently addresses the original task.

Expected outputs:

```text
VALID
```

or

```text
INVALID
<reason>
```

---

# Reporter

The Reporter converts validated information into the final user-facing response.

It does not introduce new facts.

---

# Memory Integration

NEXUS retrieves semantically relevant memories before planning.

Example:

```text
Stored:
User prefers FastAPI.

User asks:
Design a backend architecture.
```

NEXUS can retrieve the FastAPI preference and provide it as context to the Planner.

Memory is used only when relevant.

---

# Tool Routing

NEXUS contains a tool router.

Example:

```text
Analyze sales.csv
```

The router can detect the CSV file and use the File Tool.

Example execution:

```text
Task
 ↓
Tool Router
 ↓
File Tool
 ↓
sales.csv rows
```

The system can therefore delegate tasks either to agents or deterministic local tools.

---

# Logging and Tracing

NEXUS writes execution logs into:

```text
logs/
```

Logs include stages such as:

```text
NEXUS execution started
Memory retrieval completed
Planner completed
Worker execution completed
Analyst completed
Critic completed
Optimizer completed
Validator completed
Reporter completed
NEXUS execution completed
```

This provides basic observability and tracing.

---

# Failure Handling

The project includes failure-handling mechanisms at different stages.

Examples:

* Worker exceptions are captured
* Python execution errors are returned to the Code Agent
* Generated code can be retried
* Logical output can be validated
* Invalid database operations return structured errors
* Memory retrieval failure does not stop the complete NEXUS workflow

The system therefore avoids treating every generated response as automatically correct.

---

# Running NEXUS AI

First start the local llama.cpp server.

Then activate the Week 9 environment:

```bash
source .venv/bin/activate
```

Run:

```bash
python -m nexus_ai.main
```

Example:

```text
Enter your task:
Design a scalable backend architecture for an e-commerce application.
```

---

# Example Memory Test

```bash
python persistent_chat_demo.py
```

Store a memory.

Close the application.

Restart it.

Retrieve the same memory.

This demonstrates persistent memory.

---

# Example Tool Test

```bash
python day3_main.py
```

The Day 3 demonstration reads:

```text
sales.csv
```

and performs Python and SQLite analysis.

---

# Documentation

The repository includes:

```text
AGENT-FUNDAMENTALS.md
FLOW-DIAGRAM.md
TOOL-CHAIN.md
MEMORY-SYSTEM.md
ARCHITECTURE.md
FINAL-REPORT.md
README.md
```

Each document describes a major stage of the Week 9 implementation.

---

# Final Outcome

The project demonstrates the evolution from simple role-based agents to a complete local multi-agent architecture.

```text
Agents
   +
Planning
   +
Parallel Execution
   +
Tools
   +
Memory
   +
Reflection
   +
Optimization
   +
Validation
   +
Logging
   ↓
NEXUS AI
```

The final system can plan tasks, delegate work, access local tools, retrieve memory, review its own results, improve them, validate them, and generate a final response.
