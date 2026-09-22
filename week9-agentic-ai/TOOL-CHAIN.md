# Week 9 — Day 3: Tool-Calling Agents

## Overview

Day 3 extends the multi-agent system by allowing agents to work with real tools.

The implementation supports:

* Python code execution
* SQLite database queries
* TXT file reading and writing
* CSV file reading and writing
* System-to-tool execution
* Execution feedback and retry

The system runs completely locally.

---

## Tool Architecture

```text
User Task
   ↓
Agent / Orchestrator
   ↓
Determine Required Operation
   ↓
Tool
   ├── Python Executor
   ├── SQLite
   └── File System
   ↓
Tool Result
   ↓
Agent / System
   ↓
Final Result
```

---

# Code Agent

The Code Agent generates Python code for an assigned computational task.

It does not execute Python directly.

```text
Task
 ↓
Code Agent
 ↓
Python Code
 ↓
Code Executor
 ↓
Runtime Output
```

The Code Agent is instructed to:

* Generate executable Python
* Use supplied data only
* Define variables correctly
* Print requested results
* Avoid inventing execution output

Because the local Qwen model does not expose native function calling, tool execution is controlled by the surrounding Python application.

---

# Python Code Executor

`tools/code_executor.py` executes generated Python code using a temporary file and the active Python interpreter.

The executor captures:

* Success status
* Standard output
* Standard error

Example result:

```text
{
    "success": true,
    "stdout": "Total Revenue: 140000",
    "stderr": ""
}
```

Execution also contains a timeout to prevent a generated program from running indefinitely.

---

# Execution Feedback and Retry

Generated code may occasionally contain errors.

The system therefore supports a retry loop:

```text
Generate Code
     ↓
Execute
     ↓
Success?
 ┌───┴────┐
Yes       No
 ↓         ↓
Result    Capture Error
           ↓
      Fresh Code Agent
           ↓
      Corrected Code
```

The previous program and runtime error are supplied to a fresh Code Agent.

A deterministic fallback is available if the local model fails repeatedly.

---

# Database Agent

The Database Agent generates SQLite-compatible SQL.

Flow:

```text
Database Task
     ↓
DB Agent
     ↓
SQL Query
     ↓
SQLite Executor
     ↓
Database Result
```

The DB Agent does not claim that a query was executed.

Actual query execution is performed by `execute_sql()`.

---

# SQLite Database

The project uses a local SQLite database:

```text
data/day3.db
```

The demonstration database contains a `sales` table:

```text
sales
├── id
├── product
└── revenue
```

CSV data is loaded into the SQLite table before database analysis.

The database is reset before each demonstration run so repeated execution does not create duplicate rows.

---

# File Agent

The File Agent and file utilities support:

```text
TXT
├── Read
└── Write

CSV
├── Read
└── Write
```

Files are restricted to the project's `data/` directory.

Example:

```text
sales.csv
   ↓
read_csv_file()
   ↓
Python list of dictionaries
```

---

# CSV Analysis Flow

The main Day 3 demonstration uses:

```text
sales.csv
   ↓
File Tool
   ↓
CSV Rows
   ↓
Code Agent
   ↓
Generated Python
   ↓
Python Executor
   ↓
Sales Analysis
```

The analysis calculates:

* Number of products
* Total revenue
* Average revenue
* Highest-revenue product
* Lowest-revenue product

---

# Database Analysis Flow

After reading the CSV:

```text
CSV Rows
   ↓
SQLite Initialization
   ↓
sales Table
   ↓
DB Agent
   ↓
Generated SQL
   ↓
SQL Executor
   ↓
Database Result
```

This demonstrates an LLM-generated SQL query being executed against a real local database.

---

# Report Generation

After tool execution, results are written to:

```text
data/day3_report.txt
```

This demonstrates a complete tool chain:

```text
Read File
   ↓
Analyze Data
   ↓
Execute Code
   ↓
Query Database
   ↓
Write Result
```

---

# Local Tool Calling

The local Qwen model does not provide native function calling through the current llama.cpp model configuration.

Therefore the project uses system-to-tool execution.

```text
LLM
 ↓
Generates instruction/code/query
 ↓
Python Application
 ↓
Executes Tool
 ↓
Returns Real Result
```

This keeps all tool execution local and avoids paid APIs.

---

# Day 3 Files

```text
week9-agentic-ai/
│
├── agents/
│   └── code_agent.py
│
├── tools/
│   ├── code_executor.py
│   ├── db_agent.py
│   └── file_agent.py
│
├── data/
│   ├── sales.csv
│   └── day3.db
│
├── day3_main.py
└── TOOL-CHAIN.md
```

---

# Key Concepts Covered

Day 3 covers:

* Tool-using agents
* Python execution
* SQLite
* SQL generation
* File reading and writing
* CSV processing
* System-to-tool execution
* Execution feedback
* Error handling
* Retry mechanisms
* Local AI tool orchestration

---

# Final Outcome

Day 3 provides agents with the ability to interact with real local tools instead of only producing text.

The final workflow is:

```text
User Task
   ↓
File Tool
   ↓
Code Agent
   ↓
Python Executor
   ↓
Database Agent
   ↓
SQLite
   ↓
File Writer
   ↓
Final Report
```

All execution remains local and does not require paid APIs.
