# Week 9 — Day 1: Agent Foundations & Message-Based Communication

## Overview

Day 1 focuses on understanding the fundamentals of Agentic AI and building a simple multi-agent workflow using Microsoft AutoGen and a fully local open-source language model.

The system contains three agents:

1. Research Agent
2. Summarizer Agent
3. Answer Agent

Each agent has:

* A unique role
* A unique system prompt
* Strict job separation
* A memory window of 10 messages
* Access to a local Qwen GGUF model through `llama.cpp`

The final flow is:

```text
User
  ↓
Research Agent
  ↓
Research Information
  ↓
Summarizer Agent
  ↓
Summary
  ↓
Answer Agent
  ↓
Final Answer
```

---

# Agentic AI

Agentic AI refers to AI systems that can work toward a goal through multiple steps instead of producing only a single response.

A basic agentic loop can be represented as:

```text
Perception
    ↓
Reasoning
    ↓
Action
    ↓
Observation
    ↓
Reasoning Again
```

This allows the system to understand a task, decide what to do, perform an action, inspect the result, and continue if required.

Agentic AI is useful for tasks that need:

* Multiple steps
* Tool usage
* Memory
* Planning
* Validation
* Retry logic
* Communication between agents

---

# AI Agent

An AI agent is a software component designed to perform a specific role or work toward a specific goal.

An agent may:

* Receive messages
* Understand a task
* Generate responses
* Maintain conversation context
* Use tools
* Communicate with other agents

A simple agent can be represented as:

```text
Agent
│
├── Name
├── System Prompt
├── Model
├── Context
└── Tools
```

In this project, AutoGen's `AssistantAgent` class is used to create agents.

---

# Agent vs Chatbot vs Pipeline

## Chatbot

A chatbot mainly follows:

```text
User
 ↓
LLM
 ↓
Response
```

Its primary job is conversation.

---

## Pipeline

A pipeline follows a fixed sequence.

Example:

```text
Input
 ↓
Process
 ↓
Transform
 ↓
Output
```

The flow is predefined.

---

## Agent

An agent is more goal-oriented and can participate in dynamic workflows.

```text
Goal
 ↓
Understand Task
 ↓
Decide Next Step
 ↓
Perform Action
 ↓
Observe Result
 ↓
Continue if Required
```

### Comparison

| Feature             | Chatbot              | Pipeline         | Agent                |
| ------------------- | -------------------- | ---------------- | -------------------- |
| Main purpose        | Conversation         | Fixed processing | Goal execution       |
| Workflow            | Direct               | Predefined       | Can be dynamic       |
| Multi-step tasks    | Limited              | Yes              | Yes                  |
| Tools               | Optional             | Predefined       | Can use tools        |
| Memory              | Conversation history | Usually limited  | Can maintain context |
| Agent communication | No                   | Usually no       | Yes                  |

---

# Perception, Reasoning, Action and Observation

These four concepts describe the basic behavior of an agent.

## Perception

Perception means receiving and understanding the current input.

Example:

```text
User:
Find the average revenue from sales.csv
```

The agent understands that the required information is inside a CSV file.

## Reasoning

Reasoning is the decision-making step.

Example:

```text
Read the CSV
Find the revenue column
Calculate the average
```

## Action

Action means actually performing an operation.

Examples:

```text
Read a file
Execute Python
Call a tool
Query a database
```

## Observation

Observation is the result returned after an action.

Example:

```text
Columns found:
product
quantity
revenue
```

The observation becomes new information for the next step.

---

# ReAct Pattern

ReAct stands for:

```text
Reason + Act
```

It is a pattern where the agent alternates between reasoning and actions.

```text
Reason
 ↓
Act
 ↓
Observe
 ↓
Reason
 ↓
Act
 ↓
Observe
 ↓
Final Result
```

This pattern allows the agent to change its next action based on the result of the previous action.

---

# System Prompts

A system prompt defines the role and boundaries of an agent.

Since multiple agents can use the same LLM, each agent needs separate instructions.

Example:

```text
Research Agent
→ Gather relevant information only

Summarizer Agent
→ Summarize supplied research only

Answer Agent
→ Produce final answer only
```

The system prompt also defines what an agent must not do.

---

# Role Isolation

Role isolation means every agent performs only its assigned responsibility.

Correct design:

```text
Research Agent
      ↓
Research Only

Summarizer Agent
      ↓
Summarization Only

Answer Agent
      ↓
Final Answer Only
```

This prevents different agents from performing the same job.

---

# Research Agent

The Research Agent is the first agent in the workflow.

Its responsibility is to:

* Understand the user query
* Gather relevant information
* Stay focused on the exact query
* Avoid unrelated details
* Avoid summarization
* Avoid generating the final answer

Flow:

```text
User Query
    ↓
Research Agent
    ↓
Research Findings
```

---

# Summarizer Agent

The Summarizer Agent receives the output of the Research Agent.

Its responsibility is to:

* Summarize the provided research
* Preserve all important points
* Avoid adding new facts
* Avoid using outside knowledge
* Avoid new research
* Avoid generating the final answer

Flow:

```text
Research Findings
       ↓
Summarizer Agent
       ↓
Concise Summary
```

During testing, the system prompt was strengthened because the model initially introduced information that was not present in the research output.

---

# Answer Agent

The Answer Agent receives the summary.

Its responsibility is to:

* Use only the provided summary
* Preserve the meaning
* Avoid adding new facts
* Avoid new research
* Produce a clear user-facing response

Flow:

```text
Summary
   ↓
Answer Agent
   ↓
Final Answer
```

---

# Message-Based Communication

The agents communicate by passing the output of one agent to the next.

```text
User Query
    ↓
Research Agent
    ↓
Research Output
    ↓
Summarizer Agent
    ↓
Summary Output
    ↓
Answer Agent
    ↓
Final Answer
```

This creates clear separation between the responsibilities of different agents.

---

# AutoGen

Microsoft AutoGen is used as the agent framework.

The main class used on Day 1 is:

```python
AssistantAgent
```

Each agent is created with:

```python
AssistantAgent(
    name=...,
    model_client=...,
    model_context=...,
    system_message=...
)
```

Important properties:

* `name` — identifies the agent
* `model_client` — connects to the local model
* `model_context` — manages conversation context
* `system_message` — defines the role

---

# Local LLM Integration

The system uses a local quantized Qwen GGUF model from Week 8.

The model runs using `llama.cpp`.

Architecture:

```text
AutoGen Agent
      ↓
Model Client
      ↓
http://127.0.0.1:8080/v1
      ↓
llama-server
      ↓
Qwen GGUF Model
```

The model server is started using:

```bash
~/llama.cpp/build/bin/llama-server \
  -m /home/mayank/full-stack_launchpad/week8-llm-fine-tuning/quantized/model.gguf \
  --host 127.0.0.1 \
  --port 8080
```

The local server exposes an OpenAI-compatible endpoint that AutoGen can use.

---

# Model Client

The shared model connection is stored in:

```text
model_client.py
```

This file contains:

* Model path
* Local API URL
* API placeholder
* Model information

The same model client configuration is reused by all agents.

```text
                model_client.py
                       │
           ┌───────────┼───────────┐
           ↓           ↓           ↓
       Research    Summarizer    Answer
        Agent         Agent       Agent
```

---

# Memory Window

Each agent uses a bounded conversation context.

The configured window size is:

```text
10 messages
```

It is implemented using:

```python
BufferedChatCompletionContext(buffer_size=10)
```

If more than 10 messages are generated, the oldest messages are removed from the active context.

Example:

```text
Generated Messages = 12

Active Context = Latest 10 Messages
```

During testing, six turns generated twelve messages, but only ten remained in the active model context.

This confirmed that the memory window was working correctly.

---

# Conversation Loop

The main program supports multiple questions in the same session.

```text
Question 1
 ↓
Answer

Question 2
 ↓
Answer

Question 3
 ↓
Answer

exit
 ↓
Program Ends
```

The same agent objects remain active during the session, allowing their conversation context to be preserved.

---

# Day 1 Architecture

```text
                       USER
                         │
                         ▼
               ┌──────────────────┐
               │  Research Agent  │
               │                  │
               │ Gather Relevant  │
               │ Information      │
               └────────┬─────────┘
                        │
                        ▼
                Research Findings
                        │
                        ▼
              ┌───────────────────┐
              │ Summarizer Agent  │
              │                   │
              │ Create Concise    │
              │ Summary           │
              └─────────┬─────────┘
                        │
                        ▼
                     Summary
                        │
                        ▼
                ┌───────────────┐
                │ Answer Agent  │
                │               │
                │ Final User    │
                │ Response      │
                └───────┬───────┘
                        │
                        ▼
                       USER
```

---

# Project Structure

```text
week9-agentic-ai/
│
├── agents/
│   ├── __init__.py
│   ├── research_agent.py
│   ├── summarizer_agent.py
│   └── answer_agent.py
│
├── model_client.py
├── main.py
├── test_agent.py
├── test_research.py
├── test_summarizer.py
├── test_answer.py
├── requirements.txt
└── AGENT-FUNDAMENTALS.md
```

---

# Testing Summary

The following tests were performed:

### Local Model Test

```bash
curl http://127.0.0.1:8080/v1/models
```

This confirmed that the local Qwen model was loaded successfully.

### AutoGen Connection Test

A temporary test agent was used to verify:

```text
AutoGen
 ↓
llama.cpp
 ↓
Qwen
```

The model returned a valid response.

### Research Agent Test

The Research Agent successfully generated information relevant to the user query.

### Summarizer Agent Test

The Summarizer Agent successfully condensed the research without introducing new information after the system prompt was improved.

### Answer Agent Test

The Answer Agent successfully generated the final response using only the provided summary.

### Complete Chain Test

The complete flow was tested successfully:

```text
User
 ↓
Research Agent
 ↓
Summarizer Agent
 ↓
Answer Agent
 ↓
Final Answer
```

---

# Key Concepts Covered

Day 1 covered:

* Agentic AI
* AI agents
* Agent vs chatbot
* Agent vs pipeline
* Perception
* Reasoning
* Action
* Observation
* ReAct
* AutoGen
* AssistantAgent
* System prompts
* Role isolation
* Message passing
* Local LLM integration
* Conversation context
* Memory window

---

# Final Outcome

Day 1 successfully implemented a simple multi-agent AI system using AutoGen and a local Qwen model.

The system can:

* Accept multiple user queries
* Route information through three specialized agents
* Maintain strict role separation
* Pass messages between agents
* Maintain a 10-message memory window
* Generate a final response through an agent chain
* Run without paid external APIs

This architecture provides the foundation for Day 2, where the project will evolve into a planner, worker, reflection, and validator-based multi-agent system.
