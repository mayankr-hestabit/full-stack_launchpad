# Week 9 — Final Report

## Agentic AI & Multi-Agent System Design

## Project: NEXUS AI

---

# 1. Introduction

Week 9 focused on Agentic AI and multi-agent system design.

The project progressed from basic role-based agents to a complete local multi-agent architecture called NEXUS AI.

The system uses multiple specialized agents rather than relying on a single LLM for every responsibility.

The final project combines:

* Planning
* Task delegation
* Parallel execution
* Tools
* Memory
* Reflection
* Optimization
* Validation
* Reporting
* Logging
* Failure handling

---

# 2. Project Goal

The main goal was to build a local Agentic AI system capable of handling a user task through multiple coordinated stages.

Instead of:

```text
User
 ↓
LLM
 ↓
Answer
```

the final architecture uses:

```text
User
 ↓
Planner
 ↓
Agents / Tools
 ↓
Analysis
 ↓
Reflection
 ↓
Optimization
 ↓
Validation
 ↓
Reporting
```

---

# 3. Day 1 — Agent Fundamentals

Day 1 introduced the basic Agentic AI model.

Three agents were implemented:

* Research Agent
* Summarizer Agent
* Answer Agent

Flow:

```text
User
 ↓
Research Agent
 ↓
Summarizer Agent
 ↓
Answer Agent
```

Each agent had:

* A separate role
* A dedicated system prompt
* Strict job boundaries
* A limited memory context

This demonstrated role isolation and message passing.

---

# 4. Day 1 Memory Window

Agents used:

```text
BufferedChatCompletionContext
```

with:

```text
buffer_size = 10
```

Testing confirmed that only the latest messages remained available once the context limit was exceeded.

This demonstrated short conversational context management.

---

# 5. Day 2 — Planner and Multi-Agent Orchestration

Day 2 introduced task decomposition.

Architecture:

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
```

The Planner converted a complex user goal into concrete subtasks.

Workers executed independent tasks.

`asyncio.gather()` was used for parallel execution.

---

# 6. Reflection and Validation

The Reflection Agent combined Worker outputs and improved clarity.

The Validator checked:

* Task coverage
* Missing information
* Logical consistency
* Contradictions
* Unsupported assumptions

This introduced review before accepting a result.

---

# 7. Day 3 — Tool-Using Agents

Day 3 introduced interaction with real local systems.

The following tools were implemented:

* Python executor
* SQLite database tool
* TXT file read/write
* CSV file read/write

The local LLM generated instructions, Python, or SQL while the Python application performed actual execution.

---

# 8. Python Execution

The Code Agent generates analysis logic.

The system then injects real runtime data before executing the generated program.

Example:

```text
CSV
 ↓
Normalize data
 ↓
Code Agent
 ↓
Generate analysis logic
 ↓
Inject actual data
 ↓
Python Executor
```

This prevents the model from needing to reproduce input data manually.

---

# 9. Python Validation

Generated code is not automatically trusted.

The pipeline supports:

```text
Syntax Check
 ↓
Execution
 ↓
Runtime Check
 ↓
Logical Validation
```

If execution fails, the error can be provided back to a fresh Code Agent for repair.

This demonstrated execution feedback and failure recovery.

---

# 10. SQLite Tool

A SQLite database was used to demonstrate database operations.

The DB Agent generated SQL.

The application executed the SQL against the real local database.

Example:

```sql
SELECT product, revenue
FROM sales
ORDER BY revenue DESC
LIMIT 1;
```

The database returned:

```text
Laptop
50000
```

---

# 11. Day 4 — Session Memory

Session memory was implemented using a bounded `deque`.

Purpose:

```text
Store recent messages while the application is running
```

When the memory limit is exceeded, the oldest item is removed.

---

# 12. Long-Term Memory

SQLite was used for persistent memory.

Database:

```text
memory/long_term.db
```

Memories remain stored when the application stops.

The system supports:

* Semantic memories
* Episodic memories

---

# 13. Semantic Memory

Semantic memories represent facts or preferences.

Example:

```text
User prefers Python for backend development.
```

---

# 14. Episodic Memory

Episodic memories represent previous events.

Example:

```text
User worked on a Python tool-calling agent.
```

---

# 15. Vector Memory

FAISS was used for semantic memory retrieval.

Embedding model:

```text
BAAI/bge-small-en-v1.5
```

Flow:

```text
Memory Text
 ↓
Embedding
 ↓
FAISS Index
```

Query:

```text
What should I use to build a backend API?
```

can retrieve memories such as:

```text
User prefers Python for backend development.

User prefers FastAPI for building APIs.
```

even without exact keyword matching.

---

# 16. Persistent Memory Demonstration

A separate persistence demonstration was implemented.

Flow:

```text
First Program Run
 ↓
Store memory
 ↓
Close application

Second Program Run
 ↓
Load stored memory
 ↓
Retrieve using SQLite / FAISS
```

This demonstrated that long-term memory survives application restarts.

---

# 17. Day 5 — NEXUS AI

Day 5 integrated the previous components.

The NEXUS architecture includes:

* Orchestrator
* Planner
* Worker Agents
* Analyst
* Critic
* Optimizer
* Validator
* Reporter
* Memory Manager
* Tool Router
* Logging

---

# 18. NEXUS Workflow

```text
User Task
 ↓
Memory Retrieval
 ↓
Planner
 ↓
Task Delegation
 ↓
Agents / Tools
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

# 19. Memory-Aware Planning

Before creating the plan, NEXUS retrieves relevant vector memories.

Example retrieved context:

```text
User prefers FastAPI for building APIs.

User prefers Python for backend development.
```

The Planner can use this context when it is relevant to the current user task.

---

# 20. Task Delegation

The Planner decomposes a task into smaller responsibilities.

Each Worker receives:

```text
Original user task
+
Assigned subtask
```

This solved the problem of workers losing the overall context.

---

# 21. Parallel Execution

Independent worker tasks execute concurrently through:

```python
asyncio.gather()
```

This reduces unnecessary sequential execution.

---

# 22. Tool Routing

NEXUS includes a simple Tool Router.

Tasks involving supported files can be routed to deterministic tools.

Example:

```text
Analyze sales.csv
        ↓
Tool Router
        ↓
File Tool
```

The real CSV contents are returned by the tool.

This confirms that agents do not need to pretend that they accessed a file.

---

# 23. Analyst

The Analyst receives execution results and converts them into meaningful findings.

Its responsibilities include:

* Combining useful results
* Identifying patterns
* Connecting related findings
* Identifying missing areas

---

# 24. Critic

The Critic provides self-reflection.

It checks the result for:

* Missing information
* Weak explanations
* Contradictions
* Unsupported assumptions
* Irrelevant information

The Critic does not produce the final answer.

---

# 25. Optimizer

The Optimizer receives:

```text
Analysis
+
Critic Feedback
```

and produces an improved result.

This represents the self-improvement stage of NEXUS.

---

# 26. Validator

The Validator determines whether the improved result sufficiently addresses the task.

Expected output:

```text
VALID
```

or:

```text
INVALID
```

The Orchestrator also handles the case where the Validator returns only `VALID` without repeating the complete content.

---

# 27. Reporter

The Reporter receives validated content and prepares the final user-facing response.

Its responsibility is presentation rather than new reasoning.

---

# 28. Logging and Tracing

NEXUS writes execution logs to:

```text
logs/
```

Logged events include:

* Execution start
* User task
* Memory retrieval
* Planning
* Worker execution
* Analyst completion
* Critic completion
* Optimizer completion
* Validation
* Reporting
* Execution completion

This provides traceability for the multi-agent workflow.

---

# 29. Failure Handling

Several failure-handling mechanisms were implemented.

## Worker Failures

Worker tasks use:

```python
return_exceptions=True
```

so one failed parallel worker does not necessarily stop every other worker.

## Python Failures

Python execution returns runtime errors to the system.

## Memory Failures

NEXUS can continue without retrieved memory if memory search fails.

## Tool Failures

Tools return structured success/error results.

These mechanisms improve robustness.

---

# 30. Local Execution

The complete system runs locally using:

```text
Qwen
+
llama.cpp
+
AutoGen
```

No paid LLM API is required.

---

# 31. Challenges Faced

## Local Model Limitations

The small local model occasionally generated:

* Incorrect Python
* Weak Planner outputs
* Inconsistent Critic feedback
* Overly short Reporter results

These problems required stronger orchestration and validation instead of blindly trusting every LLM response.

---

# 32. Python Code Generation Issue

An early implementation expected the model to define the runtime `data` variable itself.

This caused:

```text
NameError: data is not defined
```

The final design instead injects normalized input data into the generated program before execution.

This separated:

```text
Input preparation
```

from:

```text
Generated analysis logic
```

---

# 33. Hardcoded Fallback Lesson

A task-specific safe fallback was initially considered for failed generated Python.

However, a fixed fallback cannot solve arbitrary future tasks.

Therefore the more general architecture uses:

```text
Generate
 ↓
Validate
 ↓
Execute
 ↓
Observe Error
 ↓
Repair / Retry
```

rather than depending on one task-specific hardcoded program.

---

# 34. Worker Context Issue

Workers initially received only their assigned subtask.

This caused responses such as:

```text
The task is unclear.
```

The fix was to provide both:

```text
Original user task
+
Assigned subtask
```

This significantly improved worker usefulness.

---

# 35. Validator Handling

At times the local model returned only:

```text
VALID
```

The Orchestrator was updated so that a `VALID` status preserves the existing optimized content rather than giving the Reporter only the word `VALID`.

This prevented final answers from losing useful information.

---

# 36. Key Learning

The main learning from Week 9 is that Agentic AI is not simply multiple prompts around an LLM.

A useful agent system requires:

* Clear roles
* Controlled information flow
* Real tool execution
* Memory
* Validation
* Failure handling
* Observability
* Orchestration

---

# 37. Final Project Architecture

```text
                     NEXUS AI
                         │
                    User Task
                         │
                  Memory Retrieval
                         │
                      Planner
                         │
                 Task Delegation
                    /        \
                   /          \
              Workers         Tools
                   \          /
                    \        /
                     Analyst
                        │
                      Critic
                        │
                    Optimizer
                        │
                    Validator
                        │
                     Reporter
                        │
                  Final Response
```

---

# 38. Deliverables

The Week 9 project includes:

```text
AGENT-FUNDAMENTALS.md
FLOW-DIAGRAM.md
TOOL-CHAIN.md
MEMORY-SYSTEM.md
README.md
ARCHITECTURE.md
FINAL-REPORT.md
```

and implementation for:

```text
Agents
Planner
Tools
Memory
NEXUS orchestration
Logs
```

---

# 39. Final Outcome

The Week 9 project successfully demonstrates a local Agentic AI architecture.

The system evolved through the week:

```text
Role-Based Agents
        ↓
Planner + Workers
        ↓
Tool-Using Agents
        ↓
Persistent Memory
        ↓
NEXUS Multi-Agent System
```

The final system is capable of decomposing tasks, delegating work, accessing local tools, retrieving memories, reflecting on intermediate results, improving them, validating them, tracing execution, and generating a final user-facing response.
