# SQL QUESTION ANSWERING SYSTEM

## 1. Overview

The SQL Question Answering system allows users to query structured database information using natural language.

Instead of requiring users to manually write SQL, the system converts a natural-language question into SQL, validates the generated query, executes it safely on SQLite, and summarizes the result.

Example:

```text
User:
Show total sales by artist for 2023
```

The system performs:

```text
Natural Language
      ↓
Schema Loader
      ↓
LLM SQL Generation
      ↓
SQL Validation
      ↓
Safe Execution
      ↓
Database Results
      ↓
Result Summarization
      ↓
Final Answer
```

---

## 2. Technology Stack

The SQL-QA system uses:

- Python
- SQLite
- Gemini API
- google-genai
- python-dotenv
- sqlite3
- Regular expressions for SQL validation

---

## 3. Project Structure

```text
src/
│
├── data/
│   └── sales.db
│
├── generator/
│   └── sql_generator.py
│
├── pipelines/
│   └── sql_pipeline.py
│
├── utils/
│   └── schema_loader.py
│
└── SQL-QA-DOC.md
```

---

## 4. Database Structure

The SQLite database contains three tables.

### artists

```text
id INTEGER
name TEXT
```

### albums

```text
id INTEGER
title TEXT
artist_id INTEGER
```

### sales

```text
id INTEGER
album_id INTEGER
quantity INTEGER
unit_price REAL
sale_date TEXT
```

Relationships:

```text
artists
   ↓
albums
   ↓
sales
```

`albums.artist_id` references `artists.id`.

`sales.album_id` references `albums.id`.

---

## 5. Automatic Schema Loader

The schema loader is implemented in:

```text
utils/schema_loader.py
```

Its purpose is to inspect the SQLite database automatically.

The flow is:

```text
sales.db
   ↓
sqlite_master
   ↓
Discover Tables
   ↓
PRAGMA table_info()
   ↓
Discover Columns
   ↓
Schema Context
```

Example schema:

```text
Table: artists
- id INTEGER
- name TEXT

Table: albums
- id INTEGER
- title TEXT
- artist_id INTEGER

Table: sales
- id INTEGER
- album_id INTEGER
- quantity INTEGER
- unit_price REAL
- sale_date TEXT
```

This schema is provided to the LLM so that SQL is generated using real table and column names.

---

## 6. Natural Language to SQL

SQL generation is implemented in:

```text
generator/sql_generator.py
```

The system sends the following information to Gemini:

```text
User Question
+
Database Schema
+
SQL Generation Rules
```

Example:

```text
Question:
Show total sales by artist for 2023
```

Generated SQL:

```sql
SELECT
    artists.name,
    SUM(sales.quantity * sales.unit_price) AS total_sales
FROM artists
JOIN albums ON artists.id = albums.artist_id
JOIN sales ON albums.id = sales.album_id
WHERE strftime('%Y', sales.sale_date) = '2023'
GROUP BY artists.id, artists.name;
```

This demonstrates schema-aware SQL generation.

---

## 7. SQL Validation

Generated SQL is not executed directly.

It is first passed through a validator in:

```text
pipelines/sql_pipeline.py
```

Only read-only queries are allowed.

The validator ensures that the query:

- Is not empty
- Starts with `SELECT`
- Does not contain dangerous operations
- Does not contain multiple SQL statements

Blocked keywords include:

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

This reduces the risk of destructive or malicious SQL execution.

---

## 8. Safe SQL Execution

The validated SQL is executed against SQLite.

Additional protection is applied using:

```python
PRAGMA query_only = ON
```

This makes the connection read-only for query execution.

The safe execution flow is:

```text
Generated SQL
     ↓
Validator
     ↓
Safe SELECT Query
     ↓
SQLite Read-Only Connection
     ↓
Result Rows
```

---

## 9. SQL Error Correction

A query can be safe but still be invalid.

For example:

```sql
SELECT artist_name
FROM sales;
```

This query is read-only, but `artist_name` does not exist.

If SQLite returns an error, the system provides the following back to the LLM:

```text
Original Question
+
Database Schema
+
Failed SQL
+
SQLite Error
```

The LLM then generates a corrected query.

The corrected SQL is validated again before execution.

Flow:

```text
Generated SQL
     ↓
Validation
     ↓
Execution
     ↓
SQL Error?
   /      \
 No        Yes
 ↓          ↓
Result   LLM Correction
            ↓
       Corrected SQL
            ↓
        Revalidate
            ↓
         Execute
```

This provides automatic query correction.

---

## 10. Result Summarization

Raw database results are converted into a readable answer.

Example database result:

```text
Arijit Singh      69265
Shreya Ghoshal    66995
A.R. Rahman       49800
Sonu Nigam        32130
```

The result summarizer sends the original question and database output to Gemini.

The LLM then produces a concise natural-language answer.

This improves usability because users do not need to interpret raw SQL rows.

---

## 11. Complete SQL-QA Flow

```text
User Question
     ↓
Schema Loader
     ↓
Database Schema
     ↓
Gemini
     ↓
Generated SQL
     ↓
SQL Validator
     ↓
Safe Executor
     ↓
SQLite Database
     ↓
Structured Results
     ↓
Gemini Summarizer
     ↓
Final Answer
```

If execution fails:

```text
SQL Error
   ↓
Gemini Correction
   ↓
Corrected SQL
   ↓
Validation
   ↓
Execution
```

---

## 12. Example

User question:

```text
Show total sales by artist for 2023
```

Generated SQL:

```sql
SELECT
    artists.name,
    SUM(sales.quantity * sales.unit_price) AS total_sales
FROM artists
JOIN albums ON artists.id = albums.artist_id
JOIN sales ON albums.id = sales.album_id
WHERE strftime('%Y', sales.sale_date) = '2023'
GROUP BY artists.id, artists.name;
```

Database result:

```text
Arijit Singh       69265
Shreya Ghoshal     66995
A.R. Rahman        49800
Sonu Nigam         32130
```

The system then converts these rows into a natural-language response.

---

## 13. Connection to Previous RAG Modules

Earlier modules retrieved unstructured information.

```text
Text Documents
    ↓
BGE + BM25
    ↓
FAISS
```

Image retrieval used:

```text
Images
   ↓
CLIP
   ↓
FAISS
```

SQL-QA handles structured information differently:

```text
Natural Language
      ↓
LLM
      ↓
SQL
      ↓
Relational Database
```

Therefore the project now supports multiple knowledge sources:

```text
Documents → Vector Retrieval

Images → Multimodal Retrieval

Databases → SQL Retrieval
```

---

## 14. Features Implemented

The SQL-QA module includes:

```text
✔ Natural Language to SQL
✔ Automatic Schema Loading
✔ Schema-Aware Reasoning
✔ SQL Validation
✔ Safe Read-Only Execution
✔ SQL Error Correction
✔ Result Summarization
```

---

## 15. Limitations

Current limitations include:

- SQL accuracy depends on the LLM.
- Complex schemas may require better schema selection.
- Only SQLite is currently implemented.
- The current validator is rule-based.
- Only read-only `SELECT` queries are supported.
- Very large result sets may require result limiting.

---

## 16. Future Improvements

Possible improvements include:

- PostgreSQL support
- SQL parser-based validation
- Query timeout controls
- Automatic row limits
- Better schema relationship extraction
- Query confidence scoring
- SQL execution logging
- Retry limits for correction
- Result visualization
- Role-based database permissions

---

## 17. Conclusion

The SQL Question Answering system allows users to access structured enterprise data through natural-language questions.

The system automatically loads the database schema, generates SQL using an LLM, validates the query, executes it safely, corrects SQL errors when necessary, and converts database results into readable answers.

The completed pipeline is:

```text
Text
 ↓
SQL
 ↓
Database
 ↓
Result
 ↓
Answer
```

This extends the enterprise RAG system from document and image retrieval to structured relational database querying.