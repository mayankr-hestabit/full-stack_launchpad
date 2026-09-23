# NEXUS AI — Architecture

## Overview

NEXUS AI is the final Week 9 multi-agent architecture.

It combines the agent, orchestration, tool, memory, validation, and logging systems developed throughout the week.

The architecture is designed around specialized responsibilities instead of assigning every task to one LLM agent.

---

# High-Level Architecture

```text
                         USER
                          │
                          ▼
                 ┌─────────────────┐
                 │   NEXUS MAIN    │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  ORCHESTRATOR   │
                 └────────┬────────┘
                          │
             ┌────────────┴────────────┐
             │                         │
             ▼                         ▼
      MEMORY MANAGER               PLANNER
             │                         │
   ┌─────────┼─────────┐               │
   │         │         │               ▼
Session   SQLite     FAISS       Task Decomposition
Memory    Memory     Memory              │
                                       ▼
                               Task Delegation
                                       │
                         ┌─────────────┴─────────────┐
                         │                           │
                         ▼                           ▼
                     WORKERS                    TOOL ROUTER
                         │                           │
                         │                    ┌──────┼──────┐
                         │                    ▼      ▼      ▼
                         │                  File   DB     Python
                         │                  Tool   Tool    Tool
                         │                    │      │      │
                         └─────────────┬──────┴──────┴──────┘
                                       │
                                       ▼
                                   ANALYST
                                       │
                                       ▼
                                    CRITIC
                                       │
                                       ▼
                                  OPTIMIZER
                                       │
                                       ▼
                                  VALIDATOR
                                       │
                                       ▼
                                   REPORTER
                                       │
                                       ▼
                                 FINAL RESPONSE
```

---

# Architectural Layers

The system can be understood in five major layers:

```text
1. Interface Layer
2. Orchestration Layer
3. Agent Layer
4. Tool Layer
5. Memory Layer
```

Supporting all layers:

```text
Logging
Validation
Failure Handling
```

---

# 1. Interface Layer

Entry point:

```text
nexus_ai/main.py
```

Responsibilities:

* Accept user input
* Start NEXUS orchestration
* Handle top-level execution errors
* Display final response

Flow:

```text
User
 ↓
main.py
 ↓
run_nexus()
```

---

# 2. Orchestration Layer

Main component:

```text
nexus_ai/orchestrator.py
```

Responsibilities:

* Retrieve memory
* Invoke Planner
* Delegate subtasks
* Route tasks to agents or tools
* Execute independent work concurrently
* Combine execution results
* Trigger analysis
* Trigger reflection
* Trigger optimization
* Trigger validation
* Trigger reporting
* Log execution stages

The Orchestrator controls the lifecycle of a task.

---

# 3. Planner

Implementation:

```text
orchestrator/planner.py
```

The Planner converts a user goal into smaller concrete tasks.

Example:

```text
User:
Design a scalable backend architecture.
```

Planner:

```text
1. Design APIs.
2. Design database architecture.
3. Design caching.
4. Design load balancing.
5. Design reliability.
6. Design deployment strategy.
```

The Planner does not solve the task itself.

---

# 4. Worker Execution

Worker implementation:

```text
agents/worker_agent.py
```

Each Worker receives:

```text
Original User Task
+
Assigned Subtask
```

This allows the Worker to understand both local responsibility and overall context.

Independent worker tasks can execute concurrently through:

```python
asyncio.gather()
```

---

# 5. Tool Routing

Implementation:

```text
nexus_ai/tool_router.py
```

Tool routing allows deterministic local operations to be used when appropriate.

Example:

```text
Task mentions sales.csv
        ↓
Tool Router
        ↓
CSV File Tool
```

The current implementation supports local file-oriented routing and reuses Day 3 tool capabilities.

---

# 6. Tool Layer

## File Tool

Implementation:

```text
tools/file_agent.py
```

Supports:

```text
TXT read
TXT write
CSV read
CSV write
```

Files are restricted to the project data directory.

---

## Python Tool

Implementation:

```text
tools/code_executor.py
```

Generated Python is executed in a temporary file.

The executor returns:

```text
success
stdout
stderr
```

Execution has a timeout.

---

## Database Tool

Implementation:

```text
tools/db_agent.py
```

Uses SQLite.

Responsibilities:

* Execute SQL
* Initialize demonstration database
* Return query results
* Return structured errors

---

# 7. Analyst Agent

Implementation:

```text
agents/analyst_agent.py
```

Responsibilities:

* Analyze worker outputs
* Analyze tool results
* Identify relevant findings
* Combine useful information
* Identify gaps

The Analyst does not produce the final user-facing report.

---

# 8. Critic Agent

Implementation:

```text
agents/critic_agent.py
```

The Critic provides the self-reflection stage.

It checks:

* Missing information
* Contradictions
* Weak explanations
* Unsupported assumptions
* Irrelevant content

Flow:

```text
Current Result
     ↓
Critic
     ↓
Actionable Feedback
```

---

# 9. Optimizer Agent

Implementation:

```text
agents/optimizer_agent.py
```

The Optimizer performs self-improvement.

Flow:

```text
Analysis
   +
Critic Feedback
       ↓
Optimizer
       ↓
Improved Result
```

It preserves valid findings while improving weaknesses.

---

# 10. Validator Agent

Implementation:

```text
agents/validator.py
```

The Validator checks whether the optimized result sufficiently addresses:

* Original user task
* Execution plan
* Technical requirements
* Logical consistency
* Important missing information

Expected states:

```text
VALID
```

or:

```text
INVALID
```

The Orchestrator handles cases where the Validator returns only the status word.

---

# 11. Reporter Agent

Implementation:

```text
agents/reporter_agent.py
```

The Reporter converts validated content into a clear user-facing response.

It must preserve important validated information and avoid introducing new facts.

---

# 12. Memory Architecture

NEXUS memory is managed through:

```text
nexus_ai/memory_manager.py
```

It combines three memory types.

```text
             Memory Manager
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
    Session       SQLite       FAISS
    Memory        Memory       Memory
```

---

# Session Memory

Implementation:

```text
memory/session_memory.py
```

Uses:

```text
collections.deque
```

Purpose:

```text
Maintain recent conversation context
```

It is bounded and temporary.

---

# Long-Term Memory

Implementation:

```text
memory/long_term_memory.py
```

Database:

```text
memory/long_term.db
```

Purpose:

```text
Persist information between application executions
```

Memory records contain:

```text
id
content
memory_type
created_at
```

---

# Vector Memory

Implementation:

```text
memory/vector_store.py
```

Uses:

```text
BAAI/bge-small-en-v1.5
        ↓
Embeddings
        ↓
FAISS
```

Purpose:

```text
Retrieve memories by meaning rather than exact words
```

---

# Semantic and Episodic Memory

Semantic memory:

```text
Facts and preferences
```

Example:

```text
User prefers FastAPI.
```

Episodic memory:

```text
Previous events or experiences
```

Example:

```text
User worked on a tool-calling agent.
```

---

# Memory Retrieval in NEXUS

Before planning:

```text
User Query
   ↓
Vector Search
   ↓
Relevant Memories
   ↓
Planner Context
```

Example:

```text
Stored:
User prefers FastAPI.

Query:
Design a backend architecture.

Retrieved:
User prefers FastAPI.
```

Relevant memory can therefore influence planning without requiring the user to repeat information.

---

# Persistent Memory Demonstration

File:

```text
persistent_chat_demo.py
```

Demonstration:

```text
Run 1
 ↓
Store memory
 ↓
Exit application

Run 2
 ↓
Reload SQLite + FAISS
 ↓
Retrieve old memory
```

This proves persistence across separate Python processes.

---

# System-to-Tool Execution

The local Qwen model does not use native function calling in the current configuration.

Therefore tools use system-to-tool execution.

```text
LLM / Orchestrator
       ↓
Determine action
       ↓
Python application
       ↓
Execute local tool
       ↓
Return real result
```

This separates reasoning from actual execution.

---

# Failure Handling

NEXUS contains basic failure handling.

## Worker Failure

Parallel worker execution uses:

```python
return_exceptions=True
```

This prevents one failed worker from automatically crashing all independent worker tasks.

---

## Tool Failure

Tools return structured results.

Example:

```text
success: False
error: ...
```

This allows the caller to inspect failures.

---

## Python Execution Failure

Generated Python is checked through:

```text
Syntax validation
        ↓
Execution
        ↓
Runtime validation
        ↓
Logical validation
```

Incorrect execution can trigger another generation attempt.

---

## Memory Failure

If vector-memory retrieval fails, NEXUS can continue without retrieved memory.

This prevents memory infrastructure from blocking the entire pipeline.

---

# Logging and Tracing

Implementation:

```text
nexus_ai/logger.py
```

Logs are stored inside:

```text
logs/
```

Each execution can record:

```text
Execution start
User task
Memory retrieval
Planner task count
Worker/tool execution
Analyst completion
Critic completion
Optimizer completion
Validator completion
Reporter completion
Execution completion
```

This provides execution tracing.

---

# NEXUS Execution Sequence

```text
1. Receive User Task

2. Save current message in session memory

3. Search relevant vector memories

4. Send task + relevant memory to Planner

5. Planner creates subtasks

6. Orchestrator delegates subtasks

7. Tool Router checks for deterministic tool operations

8. Workers/tools execute

9. Results are combined

10. Analyst interprets results

11. Critic reviews result

12. Optimizer improves result

13. Validator checks result

14. Reporter generates final response

15. Final response is stored in session memory

16. Execution is logged
```

---

# Current Tool Example

For:

```text
Analyze sales.csv
```

NEXUS can identify a CSV task and route file access through the File Tool.

The actual file output is returned to the orchestration pipeline rather than allowing an agent to pretend that the file was read.

---

# Design Principles

The architecture follows these principles:

* Specialized agent responsibilities
* Role isolation
* Task decomposition
* Parallel execution where possible
* Real tool execution
* Persistent memory
* Semantic retrieval
* Reflection before finalization
* Validation before reporting
* Logging and observability
* Controlled failure handling

---

# Final Architecture

```text
User
 ↓
NEXUS
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

NEXUS therefore combines reasoning, execution, memory, review, validation, and reporting within one local multi-agent architecture.
