import asyncio

from orchestrator.planner import create_planner_agent, parse_plan
from agents.worker_agent import create_worker_agent
from agents.reflection_agent import create_reflection_agent
from agents.validator import create_validator_agent


async def run_worker(worker_name, task):
    worker = create_worker_agent(worker_name)

    result = await worker.run(
        task=f"""
Assigned task:
{task}
"""
    )

    return result.messages[-1].content


async def main():
    user_query = input("\nEnter your task: ")

    # ---------------------------------------------------------
    # 1. PLANNER
    # ---------------------------------------------------------

    planner = create_planner_agent()

    plan_result = await planner.run(
        task=f"""
Create an execution plan for this user task:

{user_query}
"""
    )

    plan_text = plan_result.messages[-1].content
    tasks = parse_plan(plan_text)

    print("\n--- Execution Plan ---")
    print(plan_text)

    if not tasks:
        print("\nPlanner did not generate executable tasks.")
        return

    # ---------------------------------------------------------
    # 2. PARALLEL WORKERS
    # ---------------------------------------------------------

    worker_jobs = []

    for index, task in enumerate(tasks, start=1):
        worker_jobs.append(
            run_worker(
                f"worker_{index}",
                task
            )
        )

    worker_results = await asyncio.gather(*worker_jobs)

    print("\n--- Worker Results ---")

    for index, result in enumerate(worker_results, start=1):
        print(f"\nWorker {index}:")
        print(result)

    combined_results = "\n\n".join(
        f"Worker {i + 1}: {result}"
        for i, result in enumerate(worker_results)
    )

    # ---------------------------------------------------------
    # 3. REFLECTION
    # ---------------------------------------------------------

    reflection_agent = create_reflection_agent()

    reflection_result = await reflection_agent.run(
        task=f"""
Original user task:
{user_query}

Execution plan:
{plan_text}

Worker outputs:
{combined_results}

Combine and improve the worker outputs into one coherent result
that addresses the original user task.
"""
    )

    refined_output = reflection_result.messages[-1].content

    print("\n--- Reflection Output ---")
    print(refined_output)

    # ---------------------------------------------------------
    # 4. VALIDATOR
    # ---------------------------------------------------------

    validator_agent = create_validator_agent()

    validation_result = await validator_agent.run(
        task=f"""
Original user task:
{user_query}

Execution plan:
{plan_text}

Improved result:
{refined_output}

Validate whether the improved result correctly and sufficiently
addresses the original user task.
"""
    )

    validated_output = validation_result.messages[-1].content

    print("\n--- Validator / Final Output ---")
    print(validated_output)

    # ---------------------------------------------------------
    # 5. EXECUTION TREE
    # ---------------------------------------------------------

    print("\n--- Execution Tree ---")

    print("User Query")
    print("└── Planner")

    for index, task in enumerate(tasks, start=1):
        print(f"    ├── Worker {index}: {task}")

    print("    └── Reflection Agent")
    print("        └── Validator Agent")
    print("            └── Final Output")


if __name__ == "__main__":
    asyncio.run(main())