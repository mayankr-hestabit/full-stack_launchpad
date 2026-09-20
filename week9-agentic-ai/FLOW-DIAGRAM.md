# Week 9 — Day 2: Multi-Agent Orchestration Flow

## Overview

Day 2 implements a multi-agent orchestration system based on the following architecture:

```text
User Query
   ↓
Planner / Orchestrator
   ↓
Parallel Worker Agents
   ↓
Reflection Agent
   ↓
Validator Agent
   ↓
Final Output
```

The system dynamically breaks a user task into smaller execution tasks, assigns them to worker agents in parallel, combines and improves their results, validates the final response, and displays the execution tree.

---

# Main Architecture

```text
                         USER QUERY
                             │
                             ▼
                    ┌─────────────────┐
                    │ Planner Agent   │
                    │                 │
                    │ Breaks task     │
                    │ into subtasks   │
                    └────────┬────────┘
                             │
               ┌─────────────┼─────────────┐
               │             │             │
               ▼             ▼             ▼
        ┌────────────┐ ┌────────────┐ ┌────────────┐
        │ Worker 1   │ │ Worker 2   │ │ Worker N   │
        │            │ │            │ │            │
        │ Task 1     │ │ Task 2     │ │ Task N     │
        └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
              │              │              │
              └──────────────┼──────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Reflection      │
                    │ Agent           │
                    │                 │
                    │ Combines and    │
                    │ improves output │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Validator Agent │
                    │                 │
                    │ Checks quality  │
                    │ and coverage    │
                    └────────┬────────┘
                             │
                             ▼
                      FINAL OUTPUT
```

---

# 1. Planner Agent

The Planner Agent receives the original user task.

Its responsibility is to divide the task into clear and executable subtasks.

Example:

```text
User Task:
Design a scalable backend architecture for an e-commerce application.
```

Possible planner output:

```text
1. Choose an appropriate technology stack.
2. Design database scaling strategy.
3. Design load balancing setup.
4. Define API and service boundaries.
5. Design caching strategy.
6. Define reliability and failure-handling mechanisms.
```

The Planner Agent does not solve the task itself.

It only creates the execution plan.

---

# 2. Task Parsing

The planner returns a numbered list.

The `parse_plan()` function converts this output into Python tasks.

Example input:

```text
1. Design database scaling strategy.
2. Design caching strategy.
3. Design load balancing.
```

Converted result:

```python
[
    "Design database scaling strategy.",
    "Design caching strategy.",
    "Design load balancing."
]
```

These tasks are then assigned to individual worker agents.

---

# 3. Worker Agents

A separate Worker Agent is created for each planner task.

Example:

```text
Worker 1
→ Technology stack

Worker 2
→ Database strategy

Worker 3
→ Load balancing

Worker 4
→ API boundaries

Worker 5
→ Caching

Worker 6
→ Reliability
```

Each worker performs only its assigned responsibility.

Workers do not:

* Create a new execution plan
* Solve unrelated tasks
* Generate the overall final answer

This maintains role separation.

---

# 4. Parallel Worker Execution

Worker tasks are executed concurrently using Python's `asyncio.gather()`.

```python
worker_results = await asyncio.gather(*worker_jobs)
```

Conceptually:

```text
                  Planner
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       Worker 1   Worker 2   Worker 3
          │          │          │
          └──────────┼──────────┘
                     ▼
               Worker Results
```

Independent tasks do not need to wait for one another before execution.

This satisfies the Day 2 parallel-worker requirement.

---

# 5. Combining Worker Results

After all workers complete their assigned tasks, their outputs are combined.

Conceptually:

```text
Worker 1 Result
+
Worker 2 Result
+
Worker 3 Result
+
...
        ↓
Combined Worker Output
```

The combined result is then passed to the Reflection Agent.

---

# 6. Reflection Agent

The Reflection Agent reviews all Worker Agent outputs.

Its responsibility is to:

* Combine useful information
* Remove repetition
* Improve clarity
* Improve organization
* Preserve relevant information
* Produce one coherent result

Flow:

```text
Multiple Worker Outputs
          ↓
   Reflection Agent
          ↓
    Improved Result
```

The Reflection Agent does not generate a new execution plan.

---

# 7. Validator Agent

The Validator Agent receives:

* Original user task
* Execution plan
* Improved Reflection output

It checks the result for:

* Missing information
* Incomplete task coverage
* Logical problems
* Contradictions
* Irrelevant information
* Unsupported assumptions

The Validator Agent returns one of two formats.

Successful validation:

```text
VALID
<validated result>
```

Failed validation:

```text
INVALID
<reason>
```

---

# 8. Complete Execution Flow

```text
User enters task
      ↓
Planner analyzes task
      ↓
Planner generates numbered subtasks
      ↓
parse_plan() extracts tasks
      ↓
Worker agents are created dynamically
      ↓
Workers execute tasks in parallel
      ↓
Worker results are combined
      ↓
Reflection Agent improves combined output
      ↓
Validator Agent checks final quality
      ↓
Validated result is produced
      ↓
Execution tree is displayed
```

---

# 9. Execution Tree

The application displays the execution structure after processing the task.

Example:

```text
User Query
└── Planner
    ├── Worker 1: Choose appropriate technology stack.
    ├── Worker 2: Design database scaling strategy.
    ├── Worker 3: Plan load balancing setup.
    ├── Worker 4: Define API/service boundaries.
    ├── Worker 5: Decide caching strategy.
    ├── Worker 6: Identify reliability mechanisms.
    └── Reflection Agent
        └── Validator Agent
            └── Final Output
```

This makes the orchestration flow visible and traceable.

---

# 10. Day 2 Components

The main Day 2 files are:

```text
week9-agentic-ai/
│
├── orchestrator/
│   └── planner.py
│
├── agents/
│   ├── worker_agent.py
│   ├── reflection_agent.py
│   └── validator.py
│
├── day2_main.py
│
└── FLOW-DIAGRAM.md
```

---

# 11. Key Concepts Covered

Day 2 covers:

* Multi-agent orchestration
* Planner–Executor architecture
* Task decomposition
* Task delegation
* Parallel worker execution
* Role-based agents
* Reflection
* Validation
* Dynamic task generation
* Execution tree
* Agent hierarchy
* Message-based coordination

---

# Final Outcome

Day 2 successfully evolves the Day 1 agent system into a hierarchical multi-agent orchestration workflow.

The final system can:

* Accept a complex user task
* Break it into multiple subtasks
* Create worker agents dynamically
* Execute independent tasks in parallel
* Combine worker outputs
* Improve the result through reflection
* Validate task coverage and quality
* Display the complete execution tree

Final architecture:

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
Final Output
```
