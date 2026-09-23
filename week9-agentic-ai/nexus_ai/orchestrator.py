import asyncio

from orchestrator.planner import (
    create_planner_agent,
    parse_plan,
)

from agents.worker_agent import (
    create_worker_agent,
)

from agents.analyst_agent import (
    create_analyst_agent,
)

from agents.critic_agent import (
    create_critic_agent,
)

from agents.optimizer_agent import (
    create_optimizer_agent,
)

from agents.validator import (
    create_validator_agent,
)

from agents.reporter_agent import (
    create_reporter_agent,
)

from nexus_ai.logger import (
    create_logger,
)

from nexus_ai.memory_manager import (
    NexusMemoryManager,
)

from nexus_ai.tool_router import (
    execute_tool_for_task,
)


logger = create_logger()

memory_manager = NexusMemoryManager()


# =========================================================
# WORKER EXECUTION
# =========================================================

async def run_worker(
    worker_name: str,
    task: str,
    user_query: str,
):
    """
    Execute one planner-generated subtask.

    The orchestrator first checks whether a local tool
    can directly handle the task.

    If no suitable tool is found, a Worker Agent handles it.
    """

    # =====================================================
    # 1. TOOL ROUTING
    # =====================================================

    tool_result = execute_tool_for_task(
        task
    )

    if tool_result is not None:

        logger.info(
            "%s routed to %s",
            worker_name,
            tool_result["tool"],
        )

        return (
            f"Assigned Task:\n"
            f"{task}\n\n"
            f"Tool Used:\n"
            f"{tool_result['tool']}\n\n"
            f"Tool Result:\n"
            f"{tool_result['result']}"
        )

    # =====================================================
    # 2. NORMAL WORKER AGENT
    # =====================================================

    worker = create_worker_agent(
        worker_name
    )

    result = await worker.run(
        task=f"""
Original user task:

{user_query}


Assigned subtask:

{task}


Execute only this assigned subtask.

Rules:
- Keep the original user goal in mind.
- Do not create another execution plan.
- Do not solve unrelated subtasks.
- Do not generate the overall final answer.
- Do not say the task is unclear if the original
  user task provides enough context.
- If exact traffic, budget, hardware, or scale
  numbers are missing, use reasonable general
  design principles.
- Do not invent unsupported exact numbers.
- Return a concrete and technically useful result.
- Keep the response concise and self-contained.
"""
    )

    return result.messages[-1].content


# =========================================================
# NEXUS ORCHESTRATOR
# =========================================================

async def run_nexus(
    user_query: str,
):
    """
    Run the complete NEXUS AI pipeline.

    Flow:

    User
      ↓
    Memory Retrieval
      ↓
    Planner
      ↓
    Tool / Worker Routing
      ↓
    Parallel Execution
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
    Final Answer
    """

    # =====================================================
    # 1. START EXECUTION
    # =====================================================

    logger.info(
        "NEXUS execution started"
    )

    logger.info(
        "User task: %s",
        user_query,
    )

    # =====================================================
    # 2. SESSION MEMORY
    # =====================================================

    memory_manager.remember_session(
        "user",
        user_query,
    )

    # =====================================================
    # 3. VECTOR MEMORY RETRIEVAL
    # =====================================================

    try:

        memory_context = (
            memory_manager.build_memory_context(
                user_query
            )
        )

    except Exception as error:

        memory_context = (
            "No relevant stored memories."
        )

        logger.warning(
            "Memory retrieval failed: %s",
            error,
        )

    print(
        "\n--- Retrieved Memory ---"
    )

    print(
        memory_context
    )

    logger.info(
        "Memory retrieval completed"
    )

    # =====================================================
    # 4. PLANNER
    # =====================================================

    planner = create_planner_agent()

    plan_result = await planner.run(
        task=f"""
Create an execution plan for this user task:

{user_query}


Relevant previous memory:

{memory_context}


Rules:
- Use relevant memory only if it helps solve the task.
- Do not force unrelated memories into the plan.
- Generate concrete technical subtasks.
- Prefer independent tasks that can execute in parallel.
"""
    )

    plan_text = (
        plan_result.messages[-1].content
    )

    tasks = parse_plan(
        plan_text
    )

    print(
        "\n--- Execution Plan ---"
    )

    print(
        plan_text
    )

    logger.info(
        "Planner generated %s tasks",
        len(tasks),
    )

    if not tasks:

        logger.error(
            "Planner generated no executable tasks"
        )

        raise RuntimeError(
            "Planner generated no executable tasks."
        )

    # =====================================================
    # 5. PARALLEL WORKER / TOOL EXECUTION
    # =====================================================

    worker_jobs = []

    for index, task in enumerate(
        tasks,
        start=1,
    ):

        worker_jobs.append(
            run_worker(
                worker_name=(
                    f"nexus_worker_{index}"
                ),
                task=task,
                user_query=user_query,
            )
        )

    worker_results = await asyncio.gather(
        *worker_jobs,
        return_exceptions=True,
    )

    # =====================================================
    # 6. PROCESS EXECUTION RESULTS
    # =====================================================

    processed_results = []

    print(
        "\n--- Worker / Tool Results ---"
    )

    for index, result in enumerate(
        worker_results,
        start=1,
    ):

        print(
            f"\nTask {index}:"
        )

        if isinstance(
            result,
            Exception,
        ):

            error_message = (
                f"Task {index} failed: "
                f"{result}"
            )

            print(
                error_message
            )

            logger.error(
                error_message
            )

            processed_results.append(
                (
                    f"Task {index} failed.\n"
                    f"Error: {result}"
                )
            )

        else:

            print(
                result
            )

            processed_results.append(
                result
            )

    logger.info(
        "Worker/tool execution stage completed"
    )

    # =====================================================
    # 7. COMBINE RESULTS
    # =====================================================

    combined_results = "\n\n".join(
        (
            f"Task {index + 1}\n"
            f"Assigned Subtask: "
            f"{tasks[index]}\n\n"
            f"Result:\n"
            f"{result}"
        )
        for index, result
        in enumerate(
            processed_results
        )
    )

    # =====================================================
    # 8. ANALYST
    # =====================================================

    analyst = create_analyst_agent()

    analyst_result = await analyst.run(
        task=f"""
Original user task:

{user_query}


Execution plan:

{plan_text}


Execution results:

{combined_results}


Analyze and combine these results into one
technically meaningful response.

Rules:
- Preserve useful information from all successful tasks.
- Interpret tool results when relevant.
- Organize related findings together.
- Identify important relationships and patterns.
- Identify gaps when execution results are weak.
- Do not discard useful information.
- Do not say the original task is unclear when it
  is clearly stated above.
- Do not invent unsupported facts or exact numbers.
"""
    )

    analysis = (
        analyst_result.messages[-1].content
    )

    print(
        "\n--- Analyst Output ---"
    )

    print(
        analysis
    )

    logger.info(
        "Analyst completed"
    )

    # =====================================================
    # 9. CRITIC
    # =====================================================

    critic = create_critic_agent()

    critic_result = await critic.run(
        task=f"""
Original user task:

{user_query}


Execution plan:

{plan_text}


Current analysis:

{analysis}


Critically review the current result.

Check for:
- Missing important information
- Weak technical explanations
- Contradictions
- Unsupported assumptions
- Failure to cover planner tasks
- Irrelevant information
- Logical problems

Return concise and actionable critique.
"""
    )

    critique = (
        critic_result.messages[-1].content
    )

    print(
        "\n--- Critic Output ---"
    )

    print(
        critique
    )

    logger.info(
        "Critic completed"
    )

    # =====================================================
    # 10. OPTIMIZER
    # =====================================================

    optimizer = create_optimizer_agent()

    optimizer_result = await optimizer.run(
        task=f"""
Original user task:

{user_query}


Execution plan:

{plan_text}


Current analysis:

{analysis}


Critic feedback:

{critique}


Improve the result using the critic feedback.

Rules:
- Preserve correct findings.
- Fix valid weaknesses.
- Cover important planner tasks.
- Remove repetition.
- Improve technical completeness.
- Do not invent unsupported facts.
- Return one coherent improved result.
"""
    )

    optimized_result = (
        optimizer_result.messages[-1].content
    )

    print(
        "\n--- Optimized Result ---"
    )

    print(
        optimized_result
    )

    logger.info(
        "Optimizer completed"
    )

    # =====================================================
    # 11. VALIDATOR
    # =====================================================

    validator = create_validator_agent()

    validation_result = await validator.run(
        task=f"""
Original user task:

{user_query}


Execution plan:

{plan_text}


Result to validate:

{optimized_result}


Validate whether the result sufficiently addresses:
- the original user task
- the important execution-plan tasks
- technical correctness
- logical consistency
- completeness
"""
    )

    validator_output = (
        validation_result.messages[-1].content
    )

    print(
        "\n--- Validator Output ---"
    )

    print(
        validator_output
    )

    logger.info(
        "Validator completed"
    )

    # =====================================================
    # 12. VALIDATOR RESULT HANDLING
    # =====================================================

    validation_text = (
        validator_output.strip()
    )

    validation_upper = (
        validation_text.upper()
    )

    if validation_upper == "VALID":

        validation_status = "VALID"

        validated_content = (
            optimized_result
        )

    elif validation_upper.startswith(
        "VALID\n"
    ):

        validation_status = "VALID"

        validator_content = (
            validation_text[
                len("VALID"):
            ].strip()
        )

        if validator_content:

            validated_content = (
                validator_content
            )

        else:

            validated_content = (
                optimized_result
            )

    elif validation_upper.startswith(
        "INVALID"
    ):

        validation_status = (
            "INVALID"
        )

        validated_content = (
            optimized_result
        )

        logger.warning(
            "Validator marked result INVALID"
        )

    else:

        validation_status = (
            "UNKNOWN"
        )

        validated_content = (
            optimized_result
        )

        logger.warning(
            "Unexpected validator output format"
        )

    # =====================================================
    # 13. REPORTER
    # =====================================================

    reporter = create_reporter_agent()

    reporter_result = await reporter.run(
        task=f"""
Original user task:

{user_query}


Validation status:

{validation_status}


Validated content:

{validated_content}


Prepare the final user-facing response.

Rules:
- Preserve all important technical information.
- Do not reduce a detailed result to one small point.
- Keep the response concise but sufficiently complete.
- Organize information clearly.
- Do not mention internal agent discussions.
- Do not invent new facts.
"""
    )

    final_answer = (
        reporter_result.messages[-1].content
    )

    print(
        "\n--- Final NEXUS Response ---"
    )

    print(
        final_answer
    )

    logger.info(
        "Reporter completed"
    )

    # =====================================================
    # 14. STORE RESPONSE IN SESSION MEMORY
    # =====================================================

    memory_manager.remember_session(
        "assistant",
        final_answer,
    )

    # =====================================================
    # 15. FINISH
    # =====================================================

    logger.info(
        "NEXUS execution completed successfully"
    )

    return final_answer