# Full Stack Launchpad — 9 Week Engineering Journey

This repository documents my complete **9-week Full Stack Launchpad journey**, covering modern frontend development, backend engineering, DevOps, machine learning, Generative AI, LLM fine-tuning, and Agentic AI.

The program progressed from foundational software engineering concepts to building production-style AI systems using local models, retrieval pipelines, memory, tools, and multi-agent orchestration.

---

## Overview

Over the course of 9 weeks, I worked across the following areas:

```text
Week 1  → Engineering Foundations
Week 2  → Frontend Fundamentals
Week 3  → Advanced Frontend with Next.js
Week 4  → Advanced Backend Engineering
Week 5  → Docker, Infrastructure & Deployment
Week 6  → Machine Learning Engineering
Week 7  → Generative AI & RAG
Week 8  → LLM Fine-Tuning & Quantization
Week 9  → Agentic AI & Multi-Agent Systems
```

---

# Tech Stack

## Frontend

* HTML5
* CSS3
* JavaScript
* React
* Next.js
* Tailwind CSS

## Backend

* Node.js
* Express.js
* MongoDB
* Mongoose
* REST APIs
* Zod
* BullMQ
* Pino
* Redis

## DevOps & Infrastructure

* Linux
* Git & GitHub
* Docker
* Docker Compose
* NGINX
* HTTPS
* Jenkins
* AWS EC2

## Machine Learning

* Python
* Pandas
* NumPy
* Scikit-learn
* SHAP
* FastAPI

## Generative AI

* Hugging Face Transformers
* FAISS
* BGE Embeddings
* Retrieval-Augmented Generation
* Hybrid Retrieval
* Reranking
* SQLite

## LLM Engineering

* Qwen2.5
* LoRA
* QLoRA
* PEFT
* TRL
* BitsAndBytes
* GGUF
* llama.cpp
* Quantization

## Agentic AI

* Microsoft AutoGen
* Local LLMs
* Multi-Agent Systems
* Tool Calling
* Session Memory
* Long-Term Memory
* Vector Memory
* Multi-Agent Orchestration

---

# Week 1 — Engineering Foundations

Week 1 focused on strengthening core software engineering concepts before moving into application development.

## Topics Covered

* Node.js fundamentals
* Terminal usage
* Git fundamentals
* HTTP and API concepts
* Automation basics
* JavaScript ES6 concepts
* `const` and `let`
* Arrow functions
* Array methods:

  * `map()`
  * `filter()`
  * `reduce()`

I also practiced interactive JavaScript concepts through exercises involving:

* Counters
* FAQ accordions
* Modal dialogs
* Keyboard events

## Key Learning

This week established the base understanding required for working with modern frontend, backend, API, and automation workflows.

---

# Week 2 — Frontend Fundamentals

Week 2 focused on building strong frontend development fundamentals.

## Topics Covered

* Semantic HTML
* Accessibility
* CSS Box Model
* Flexbox
* CSS Grid
* Responsive design
* JavaScript ES6
* DOM manipulation
* Browser events
* LocalStorage
* Chrome DevTools debugging

## Product Listing Project

A dynamic product listing application was built using data fetched from an external API.

Features included:

* Product fetching using `fetch()`
* Dynamic rendering using `map()`
* Search using `filter()`
* Product statistics using `reduce()`
* Category filtering
* Rating display
* Error handling
* Debounced search

Example concepts:

```javascript
products.map(...)
products.filter(...)
products.reduce(...)
```

## Key Learning

This week strengthened my understanding of browser-side JavaScript and how frontend applications dynamically interact with data.

---

# Week 3 — Advanced Frontend with Next.js

Week 3 introduced modern frontend architecture using **Next.js and Tailwind CSS**.

## Technologies

* Next.js
* React
* Tailwind CSS
* App Router
* Server Components
* Client Components

## Project Features

The application contained multiple pages and nested dashboard routes.

```text
app/
├── page
├── about
├── login
└── dashboard
    ├── charts
    ├── profile
    ├── tables
    └── users
```

Reusable components included:

* Navbar
* Sidebar
* Dashboard layout
* Buttons
* Cards
* Inputs
* Badges
* Modals
* Data tables
* Area charts
* Bar charts

## Concepts Learned

* App Router
* Nested layouts
* Reusable UI components
* Props
* JSX
* Routing
* Responsive dashboards
* Component architecture

## Key Learning

I learned how to structure a scalable frontend application using reusable components and modern Next.js routing patterns.

---

# Week 4 — Advanced Backend Engineering

Week 4 focused on designing production-style backend applications using a layered architecture.

## Technologies

* Node.js
* Express.js
* MongoDB
* Mongoose
* Zod
* BullMQ
* Redis
* Pino

## Backend Architecture

```text
Client
  ↓
Routes
  ↓
Controller
  ↓
Service
  ↓
Repository
  ↓
Model
  ↓
MongoDB
```

The project followed a layered structure:

```text
config/
loaders/
routes/
controllers/
services/
repositories/
models/
middlewares/
utils/
jobs/
logs/
```

## Features Implemented

* User and Product models
* Repository Pattern
* CRUD APIs
* Search
* Filtering
* Sorting
* Pagination
* Soft delete
* Centralized error handling
* Request validation
* Security middleware
* Rate limiting
* Logging
* Background jobs

## Query Engine

The API supported dynamic product queries such as:

```text
search
category
minPrice
maxPrice
sort
pagination
```

## Documentation

Documentation included architecture explanations and query-engine behavior.

## Key Learning

I learned how to separate backend responsibilities into layers so that applications remain maintainable, testable, and scalable.

---

# Week 5 — Docker, Infrastructure & Deployment

Week 5 introduced infrastructure and containerization.

## Technologies

* Docker
* Docker Compose
* Linux
* NGINX
* HTTPS
* Node.js
* React
* MongoDB

## Docker

Applications were containerized using Dockerfiles.

Example architecture:

```text
Docker
├── Frontend
├── Backend
└── MongoDB
```

## Docker Compose

Docker Compose was used to run multiple services together.

```text
Client
  ↓
NGINX
  ↓
Backend Containers
  ↓
MongoDB
```

## NGINX

NGINX was configured as:

* Reverse proxy
* Load balancer
* HTTPS entry point

Multiple backend containers were used to demonstrate round-robin load balancing.

## Other Concepts

* Health checks
* Docker volumes
* Environment variables
* Container logging
* HTTPS using local certificates
* Deployment automation

## Key Learning

This week helped me understand how applications move from source code to containerized infrastructure.

---

# Week 6 — Machine Learning Engineering

Week 6 introduced an end-to-end machine learning workflow using a customer churn dataset.

## Workflow

```text
Raw Data
   ↓
Cleaning
   ↓
EDA
   ↓
Feature Engineering
   ↓
Feature Selection
   ↓
Model Training
   ↓
Model Evaluation
   ↓
Explainability
   ↓
FastAPI Deployment
   ↓
Drift Monitoring
```

## Data Processing

The project handled:

* Missing values
* Duplicate records
* Outliers
* Class imbalance
* Feature distributions
* Correlations

The processed dataset contained approximately:

```text
1,500 customer records
```

## Models

Multiple machine-learning models were evaluated.

The strongest result in the project came from **Logistic Regression**.

Evaluation included:

* Accuracy
* ROC-AUC
* Confusion matrix
* Cross-validation

## Explainability

SHAP was used to understand feature influence.

## Error Analysis

Prediction errors were inspected to understand:

* False positives
* False negatives
* Model weaknesses

## Deployment

A FastAPI endpoint exposed predictions:

```text
POST /predict
```

## Drift Monitoring

A drift checker was implemented to detect changes between training and incoming data distributions.

## Key Learning

I learned that machine learning engineering involves much more than model training—it includes data quality, evaluation, explainability, serving, and monitoring.

---

# Week 7 — Generative AI & RAG

Week 7 focused on building a production-style **Retrieval-Augmented Generation system**.

## Core Architecture

```text
Documents
   ↓
Load
   ↓
Clean
   ↓
Chunk
   ↓
Embeddings
   ↓
FAISS
   ↓
Retriever
   ↓
Reranker
   ↓
Context Builder
   ↓
LLM
   ↓
Answer
```

## Technologies

* Python
* FAISS
* BAAI/bge-small-en-v1.5
* BM25
* Cross-encoder reranking
* SQLite
* FastAPI

## Document Processing

The system supported:

* TXT
* PDF
* DOCX
* CSV

Documents were:

* Extracted
* Cleaned
* Chunked
* Enriched with metadata
* Embedded
* Indexed in FAISS

## Hybrid Retrieval

The retrieval system combined:

```text
Dense Retrieval
+
BM25
+
Reciprocal Rank Fusion
```

## Reranking

A cross-encoder reranker improved retrieved-context relevance.

## Metadata Filtering

Queries could filter documents by:

* Source
* Type
* Year
* File type

## RAG Capabilities

The broader system explored:

* Text retrieval
* Image retrieval
* SQL-based retrieval
* Conversation memory
* Hallucination detection
* Confidence scoring

## Key Learning

I learned how retrieval quality, chunking, embeddings, reranking, and context construction directly affect the quality of generated answers.

---

# Week 8 — LLM Fine-Tuning, Quantization & Optimized Inference

Week 8 focused on understanding the complete lifecycle of a local Large Language Model.

## Base Model

```text
Qwen/Qwen2.5-1.5B-Instruct
```

## Workflow

```text
Dataset
   ↓
Cleaning
   ↓
Tokenization
   ↓
QLoRA Fine-Tuning
   ↓
LoRA Adapter
   ↓
Model Merge
   ↓
Quantization
   ↓
GGUF
   ↓
llama.cpp
   ↓
Local Inference
```

## Dataset Preparation

The instruction dataset contained approximately:

```text
1,200 JSONL records
```

It was split into:

```text
1080 training samples
120 validation samples
```

Dataset validation included:

* Invalid JSON detection
* Duplicate detection
* Cleaning
* Token analysis
* Train/validation split

## Fine-Tuning

QLoRA was used to efficiently fine-tune the model.

The base model remained mostly frozen while a small percentage of trainable LoRA parameters were optimized.

Technologies:

* Transformers
* PEFT
* TRL
* BitsAndBytes
* PyTorch

## Quantization

The model was exported into multiple optimized formats:

* FP16
* INT8
* INT4
* GGUF

Final GGUF size was approximately:

```text
892 MB
```

## Local Inference

The quantized model was served using:

```text
llama.cpp
```

This enabled local inference without using a paid LLM API.

## Deployment

The project also explored:

* FastAPI
* Streamlit
* Local model serving
* Inference benchmarking
* Tokens per second
* Model size comparison

## Key Learning

I learned how fine-tuning changes model behavior and how quantization makes LLMs practical for local deployment.

---

# Week 9 — Agentic AI & Multi-Agent Systems

Week 9 focused on moving from simple LLM applications to **Agentic AI systems**.

## Technologies

* Microsoft AutoGen
* Qwen local model
* llama.cpp
* FAISS
* SQLite
* Python
* asyncio

## Day 1 — Agent Foundations

Three role-based agents were created:

```text
Research Agent
      ↓
Summarizer Agent
      ↓
Answer Agent
```

Each agent had:

* Unique role
* Unique system prompt
* Strict responsibilities
* Memory window

---

## Day 2 — Planner / Worker Orchestration

A multi-agent workflow was implemented:

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
Final Answer
```

Independent workers executed using:

```python
asyncio.gather()
```

---

## Day 3 — Tool-Using Agents

Local tools were created for:

```text
Python Execution
SQLite Queries
File Operations
```

Tool files included:

```text
tools/
├── code_executor.py
├── db_agent.py
└── file_agent.py
```

This demonstrated system-to-tool execution without native function calling.

---

## Day 4 — Agent Memory

Three memory layers were implemented.

### Session Memory

Stores recent conversation context.

### Long-Term Memory

SQLite stores persistent information across program restarts.

### Vector Memory

FAISS performs similarity-based semantic memory retrieval.

Example:

```text
Query
 ↓
FAISS Search
 ↓
Relevant Memories
 ↓
Prompt Context
```

---

## Day 5 — NEXUS AI

The final capstone integrated the concepts into a multi-agent system called:

```text
NEXUS AI
```

Core concepts included:

* Multi-agent orchestration
* Memory recall
* Planning
* Role routing
* Parallel execution
* Tool usage
* Self-reflection
* Self-improvement
* Validation
* Logging
* Failure handling

Conceptual architecture:

```text
User Goal
   ↓
Orchestrator
   ↓
Memory Recall
   ↓
Planner
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

The system runs using the locally hosted Qwen model through `llama.cpp`.

---

# Engineering Progression

The most important part of this journey was the progression from application development to intelligent systems.

```text
JavaScript
   ↓
React / Next.js
   ↓
Node.js / Express / MongoDB
   ↓
Docker / Infrastructure
   ↓
Machine Learning
   ↓
RAG
   ↓
LLM Fine-Tuning
   ↓
Agentic AI
```

Each week built upon concepts learned previously.

---

# Key Concepts Learned

Across the program, I gained practical experience with:

* Component-based frontend architecture
* REST API design
* Layered backend architecture
* Database modeling
* Repository Pattern
* Search, filter, sorting and pagination
* Application security
* Logging and background jobs
* Docker and container orchestration
* Reverse proxy and load balancing
* Machine learning pipelines
* Model explainability
* Model deployment and drift monitoring
* Vector databases
* Embeddings
* Hybrid retrieval
* RAG systems
* LoRA and QLoRA
* LLM quantization
* Local LLM inference
* Multi-agent communication
* Tool-using agents
* Agent memory
* Planner–Worker–Validator patterns
* Self-reflection and self-improvement

---

# Final Outcome

This 9-week journey progressed from building traditional software systems to building local AI systems capable of retrieval, reasoning, memory, tool execution, and multi-agent collaboration.

The final progression can be summarized as:

```text
Software Development
        ↓
Backend Engineering
        ↓
Infrastructure
        ↓
Machine Learning
        ↓
Generative AI
        ↓
LLM Engineering
        ↓
Agentic AI
```

The program significantly strengthened my understanding of how modern applications and AI systems are designed, implemented, deployed, optimized, and orchestrated.

---

# Author

**Mayank Raj**

B.Tech — Computer Science
Vivekananda Institute of Technology, Jaipur

Focus Areas:

* Full Stack Development
* Backend Engineering
* Machine Learning
* Generative AI
* LLM Engineering
* Agentic AI

---

## Repository Purpose

This repository serves as a record of my hands-on learning and implementation throughout the Full Stack Launchpad program, including weekly exercises, technical documentation, experiments, and final projects from Week 1 through Week 9.
