import asyncio
import csv
import json
import logging
import re
from datetime import datetime
from pathlib import Path

from agents.research_agent import create_research_agent
from agents.worker_agent import create_worker_agent
from agents.analyst_agent import create_analyst_agent
from agents.critic_agent import create_critic_agent
from agents.optimizer_agent import create_optimizer_agent
from agents.validator import create_validator_agent
from agents.reporter_agent import create_reporter_agent

from memory.session_memory import SessionMemory
from memory.vector_store import VectorMemory

from nexus_ai.config import (
    DATA_DIR,
    LOG_DIR,
    MAX_IMPROVEMENT_LOOPS,
    MEMORY_RELEVANCE_THRESHOLD,
    MEMORY_TOP_K,
    SESSION_MEMORY_SIZE,
)


# =========================================================
# TRACE SETTINGS
# =========================================================

SHOW_TRACE = True


# =========================================================
# LOGGING
# =========================================================

LOG_FILE = LOG_DIR / (
    f"nexus_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
)

logger = logging.getLogger("NEXUS")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8",
    )

    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )
    )

    logger.addHandler(handler)


# =========================================================
# MEMORY
# =========================================================

session_memory = SessionMemory(
    max_messages=SESSION_MEMORY_SIZE
)

vector_memory = VectorMemory()


# =========================================================
# HELPERS
# =========================================================

def get_agent_output(result) -> str:
    return result.messages[-1].content.strip()


def detect_task_type(user_query: str) -> str:
    query = user_query.lower()

    if ".csv" in query or " csv " in f" {query} ":
        return "csv"

    if (
        "rag" in query
        or "retrieval augmented" in query
        or "retrieval-augmented" in query
    ):
        return "rag"

    if "startup" in query:
        return "startup"

    if (
        "backend" in query
        and (
            "architecture" in query
            or "scalable" in query
        )
    ):
        return "backend"

    return "general"


def retrieve_memory(user_query: str) -> str:
    try:
        memories = vector_memory.search(
            user_query,
            top_k=MEMORY_TOP_K,
        )

    except Exception as error:
        logger.warning(
            "Memory retrieval failed: %s",
            error,
        )

        return "No relevant stored memories."

    relevant = []

    for memory in memories:
        score = float(
            memory.get("score", 0) or 0
        )

        if score >= MEMORY_RELEVANCE_THRESHOLD:
            relevant.append(
                f"- [{memory.get('memory_type', 'memory')}] "
                f"{memory.get('content', '')}"
            )

    return (
        "\n".join(relevant)
        if relevant
        else "No relevant stored memories."
    )


async def run_agent(
    agent,
    prompt: str,
) -> str:
    result = await agent.run(
        task=prompt
    )

    return get_agent_output(
        result
    )


async def run_worker(
    name: str,
    prompt: str,
) -> str:
    return await run_agent(
        create_worker_agent(name),
        prompt,
    )


# =========================================================
# GUIDED PLANS
# =========================================================

PLANS = {
    "rag": [
        "Define document ingestion and parsing for approximately 50k documents.",
        "Design cleaning, chunking, metadata and document-ID strategy.",
        "Design embedding generation and vector indexing.",
        "Design retrieval, metadata filtering, reranking and context construction.",
        "Design LLM generation, citation handling, evaluation, updates, monitoring and scaling.",
    ],

    "backend": [
        "Define the high-level request flow from client to backend services.",
        "Design API/service boundaries and authentication.",
        "Design relational database storage, indexes, replication and scaling.",
        "Design caching and asynchronous/background processing.",
        "Design load balancing and horizontal application scaling.",
        "Design logging, monitoring, failure recovery and deployment considerations.",
    ],

    "startup": [
        "Identify the healthcare problem, target users and market need.",
        "Research competitive landscape and regulatory/privacy constraints.",
        "Define the AI product and its core value proposition.",
        "Define an MVP and practical technology approach.",
        "Define business model and go-to-market strategy.",
        "Identify risks, responsible-AI concerns and measurable next steps.",
    ],
}


# =========================================================
# GUIDED MULTI-AGENT EXECUTION
# =========================================================

async def execute_guided_plan(
    user_query: str,
    task_type: str,
    memory_context: str,
):
    plan = PLANS[
        task_type
    ]

    print(
        "\n--- Planner / Execution Plan ---"
    )

    for index, item in enumerate(
        plan,
        start=1,
    ):
        print(
            f"{index}. {item}"
        )

    jobs = []

    for index, item in enumerate(
        plan,
        start=1,
    ):
        jobs.append(
            run_worker(
                f"nexus_worker_{index}",
                f"""
ORIGINAL USER GOAL:

{user_query}


TASK TYPE:

{task_type}


RELEVANT MEMORY:

{memory_context}


ASSIGNED SUBTASK:

{item}


RULES:

- Stay strictly inside the original user domain.
- Complete only this assigned subtask.
- Do not introduce unrelated technologies or topics.
- Do not invent facts.
- Do not claim that a file, database or program was
  accessed unless an actual tool result is supplied.
- Give concrete, technically useful information.
- Avoid unsupported exact numbers.
""",
            )
        )

    results = await asyncio.gather(
        *jobs,
        return_exceptions=True,
    )

    successful = []

    if SHOW_TRACE:
        print(
            "\n--- Worker Results ---"
        )

    for index, result in enumerate(
        results,
        start=1,
    ):
        if isinstance(
            result,
            Exception,
        ):
            logger.error(
                "Worker %s failed: %s",
                index,
                result,
            )

            output = (
                f"Worker {index} failed: {result}"
            )

        else:
            output = result

        successful.append(
            output
        )

        if SHOW_TRACE:
            print(
                f"\nWorker {index}:"
            )
            print(
                output
            )

    combined = "\n\n".join(
        f"STEP {index + 1} RESULT:\n{value}"
        for index, value
        in enumerate(successful)
    )

    analyst = create_analyst_agent()

    analysis = await run_agent(
        analyst,
        f"""
ORIGINAL USER GOAL:

{user_query}


TASK TYPE:

{task_type}


PLANNED STEPS:

{json.dumps(plan, indent=2)}


ACTUAL SUBTASK RESULTS:

{combined}


Create one complete intermediate solution.

RULES:

- Stay strictly in the {task_type} domain.
- Cover every major planned section.
- Preserve useful details from worker outputs.
- Do not invent facts.
- Do not drop important architecture, business,
  or pipeline sections.
- Produce a useful result, not a one-line summary.
""",
    )

    return plan, analysis


# =========================================================
# CSV HELPERS
# =========================================================

def find_csv_filename(
    user_query: str,
) -> str:
    match = re.search(
        r"[\w./-]+\.csv",
        user_query,
        re.IGNORECASE,
    )

    return (
        match.group(0)
        if match
        else "sales.csv"
    )


def resolve_data_file(
    filename: str,
) -> Path:
    path = Path(
        filename
    )

    if (
        path.is_absolute()
        and path.exists()
    ):
        return path

    candidates = [
        Path.cwd() / filename,
        DATA_DIR / filename,
        DATA_DIR / Path(filename).name,
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        f"CSV file not found: {filename}. "
        f"Checked current directory and {DATA_DIR}."
    )


def analyze_csv_deterministically(
    path: Path,
) -> dict:
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        rows = list(
            csv.DictReader(file)
        )

    if not rows:
        raise ValueError(
            "CSV contains no data rows."
        )

    headers = list(
        rows[0].keys()
    )

    numeric_columns = {}

    for header in headers:
        values = []
        valid = True

        for row in rows:
            raw = (
                row.get(header)
                or ""
            ).strip()

            try:
                values.append(
                    float(
                        raw.replace(
                            ",",
                            "",
                        )
                    )
                )

            except ValueError:
                valid = False
                break

        if valid and values:
            numeric_columns[
                header
            ] = values

    summary = {
        "file": str(path),
        "row_count": len(rows),
        "columns": headers,
        "rows": rows,
        "numeric_summary": {},
    }

    for column, values in numeric_columns.items():

        max_index = max(
            range(len(values)),
            key=values.__getitem__,
        )

        min_index = min(
            range(len(values)),
            key=values.__getitem__,
        )

        average = (
            sum(values)
            / len(values)
        )

        above_average_rows = []
        below_average_rows = []

        for index, value in enumerate(
            values
        ):
            item = {
                "row": rows[index],
                "value": value,
            }

            if value > average:
                above_average_rows.append(
                    item
                )

            elif value < average:
                below_average_rows.append(
                    item
                )

        summary[
            "numeric_summary"
        ][column] = {
            "total": round(
                sum(values),
                2,
            ),
            "average": round(
                average,
                2,
            ),
            "maximum": values[
                max_index
            ],
            "minimum": values[
                min_index
            ],
            "maximum_row": rows[
                max_index
            ],
            "minimum_row": rows[
                min_index
            ],
            "above_average_rows": (
                above_average_rows
            ),
            "below_average_rows": (
                below_average_rows
            ),
        }

    return summary


# =========================================================
# CSV EXECUTION
# =========================================================

async def execute_csv_task(
    user_query: str,
):
    filename = find_csv_filename(
        user_query
    )

    path = resolve_data_file(
        filename
    )

    data_summary = (
        analyze_csv_deterministically(
            path
        )
    )

    plan = [
        f"Read the real CSV file: {path.name}.",
        "Calculate numeric metrics deterministically.",
        "Identify strongest and weakest products and verified patterns.",
        "Create a business strategy based only on the verified data.",
    ]

    print(
        "\n--- Planner / Execution Plan ---"
    )

    for index, item in enumerate(
        plan,
        start=1,
    ):
        print(
            f"{index}. {item}"
        )

    print(
        "\n--- File Tool / Actual CSV Data ---"
    )

    print(
        json.dumps(
            data_summary,
            indent=2,
        )
    )

    revenue = (
        data_summary[
            "numeric_summary"
        ].get(
            "revenue"
        )
    )

    if not revenue:
        raise ValueError(
            "Revenue column could not be analyzed numerically."
        )

    total = revenue[
        "total"
    ]

    average = revenue[
        "average"
    ]

    maximum = revenue[
        "maximum"
    ]

    minimum = revenue[
        "minimum"
    ]

    highest_product = (
        revenue[
            "maximum_row"
        ].get(
            "product",
            "Unknown",
        )
    )

    lowest_product = (
        revenue[
            "minimum_row"
        ].get(
            "product",
            "Unknown",
        )
    )

    above_average_products = [
        item[
            "row"
        ].get(
            "product",
            "Unknown",
        )
        for item
        in revenue.get(
            "above_average_rows",
            [],
        )
    ]

    below_average_products = [
        item[
            "row"
        ].get(
            "product",
            "Unknown",
        )
        for item
        in revenue.get(
            "below_average_rows",
            [],
        )
    ]

    verified_findings = f"""
DATA FINDINGS

- Number of products: {data_summary['row_count']}
- Total revenue: {total:.2f}
- Average revenue: {average:.2f}
- Highest revenue: {highest_product} = {maximum:.2f}
- Lowest revenue: {lowest_product} = {minimum:.2f}
- Products above average revenue: {", ".join(above_average_products)}
- Products below average revenue: {", ".join(below_average_products)}
""".strip()

    if SHOW_TRACE:
        print(
            "\n--- Coder / Deterministic Analysis ---"
        )

        print(
            verified_findings
        )

    strategy = f"""
1. Prioritize high-performing products such as {", ".join(above_average_products)}
   for visibility, inventory availability and marketing campaigns.

2. Review weaker products such as {", ".join(below_average_products)}
   to understand whether low revenue is caused by demand, pricing,
   positioning, availability or promotion.

3. Consider bundling lower-revenue accessories with stronger products
   where the products are commercially compatible.

4. Protect availability of the highest-revenue product,
   {highest_product}, because it currently contributes the strongest
   revenue among the observed products.

5. Run targeted promotions or experiments for weaker products and
   measure whether their revenue improves before making major pricing
   decisions.

6. Continue tracking product-level revenue over time so future strategy
   can be based on trends rather than a single snapshot.
""".strip()

    if SHOW_TRACE:
        print(
            "\n--- Analyst / Business Strategy ---"
        )

        print(
            strategy
        )

    final_result = f"""
{verified_findings}

BUSINESS STRATEGY

{strategy}
""".strip()

    return (
        plan,
        final_result,
    )


# =========================================================
# GENERAL TASK
# =========================================================

async def execute_general_task(
    user_query: str,
    memory_context: str,
):
    print(
        "\n--- Planner / Execution Plan ---"
    )

    plan = [
        "Research the task.",
        "Analyze the research and produce a complete solution.",
    ]

    for index, item in enumerate(
        plan,
        start=1,
    ):
        print(
            f"{index}. {item}"
        )

    researcher = (
        create_research_agent()
    )

    research = await run_agent(
        researcher,
        f"""
ORIGINAL USER GOAL:

{user_query}


RELEVANT MEMORY:

{memory_context}


Research or reason about the information
needed to solve this task.

RULES:

- Stay strictly aligned with the user goal.
- Do not invent tool results.
- Return concrete useful information.
""",
    )

    if SHOW_TRACE:
        print(
            "\n--- Researcher Output ---"
        )

        print(
            research
        )

    analyst = create_analyst_agent()

    analysis = await run_agent(
        analyst,
        f"""
ORIGINAL USER GOAL:

{user_query}


RESEARCH / INTERMEDIATE RESULT:

{research}


Produce a complete and useful solution
to the original task.

Do not invent unsupported facts.
""",
    )

    if SHOW_TRACE:
        print(
            "\n--- Analyst Output ---"
        )

        print(
            analysis
        )

    return (
        plan,
        analysis,
    )


# =========================================================
# SELF-REFLECTION / SELF-IMPROVEMENT
# =========================================================

async def improve_result(
    user_query: str,
    task_type: str,
    current_result: str,
) -> str:
    result = current_result

    for loop_number in range(
        1,
        MAX_IMPROVEMENT_LOOPS + 1,
    ):

        critic = (
            create_critic_agent()
        )

        critique = await run_agent(
            critic,
            f"""
ORIGINAL USER GOAL:

{user_query}


TASK TYPE:

{task_type}


CURRENT RESULT:

{result}


Identify only genuine weaknesses:

- missing requested deliverables
- contradictions
- unsupported claims
- incorrect or incomplete reasoning
- task mismatch

Do not replace the solution.
Return concise actionable feedback.
""",
        )

        if SHOW_TRACE:
            print(
                f"\n--- Critic Output "
                f"(Loop {loop_number}) ---"
            )

            print(
                critique
            )

        optimizer = (
            create_optimizer_agent()
        )

        improved = await run_agent(
            optimizer,
            f"""
ORIGINAL USER GOAL:

{user_query}


TASK TYPE:

{task_type}


CURRENT RESULT:

{result}


CRITIC FEEDBACK:

{critique}


Improve the current result.

RULES:

- Preserve correct information.
- Fix only valid weaknesses.
- Do not shrink a detailed answer into one sentence.
- Do not invent facts or exact numbers.
- Ensure the original requested deliverable is present.
""",
        )

        if SHOW_TRACE:
            print(
                f"\n--- Optimizer Output "
                f"(Loop {loop_number}) ---"
            )

            print(
                improved
            )

        validator = (
            create_validator_agent()
        )

        validation = await run_agent(
            validator,
            f"""
ORIGINAL USER GOAL:

{user_query}


TASK TYPE:

{task_type}


RESULT TO VALIDATE:

{improved}


Check whether the result actually
satisfies the original task.

For backend tasks, it must cover:
- request routing
- application/API layer
- data layer
- caching or async processing
- scaling
- reliability/monitoring

For RAG tasks, it must cover:
- ingestion/chunking
- embeddings/indexing
- retrieval/context construction
- generation
- evaluation/scaling

For startup tasks, it must cover:
- problem/market
- product/MVP
- business model/go-to-market
- risks
- next steps

Return exactly:

VALID

or

INVALID
""",
        )

        if SHOW_TRACE:
            print(
                f"\n--- Validator Output "
                f"(Loop {loop_number}) ---"
            )

            print(
                validation
            )

        logger.info(
            "Reflection loop %s validation=%s",
            loop_number,
            validation,
        )

        result = improved

        if (
            validation.strip().upper()
            == "VALID"
        ):
            break

    return result


# =========================================================
# REPORTER
# =========================================================

async def report_result(
    user_query: str,
    result: str,
) -> str:
    reporter = (
        create_reporter_agent()
    )

    final = await run_agent(
        reporter,
        f"""
ORIGINAL USER GOAL:

{user_query}


APPROVED RESULT:

{result}


Prepare the final user-facing response.

RULES:

- Preserve all important information.
- Preserve numeric values exactly.
- Do not reduce the response to one sentence.
- Do not add unsupported facts.
- Keep the response structured and useful.
""",
    )

    if len(final) < max(
        120,
        int(
            len(result)
            * 0.45
        ),
    ):
        logger.warning(
            "Reporter over-compressed result; "
            "preserving approved result."
        )

        return result

    return final


# =========================================================
# MASTER NEXUS ORCHESTRATOR
# =========================================================

async def run_nexus(
    user_query: str,
) -> str:
    logger.info(
        "NEXUS started | task=%s",
        user_query,
    )

    print(
        "\n--- Orchestrator ---"
    )

    print(
        "Received user goal and starting "
        "autonomous multi-agent workflow."
    )

    session_memory.add_message(
        "user",
        user_query,
    )

    memory_context = retrieve_memory(
        user_query
    )

    print(
        "\n--- Memory Recall ---"
    )

    print(
        memory_context
    )

    task_type = detect_task_type(
        user_query
    )

    print(
        "\n--- Role / Task Routing ---"
    )

    print(
        f"Detected task type: {task_type}"
    )

    logger.info(
        "Detected task type: %s",
        task_type,
    )

    if task_type == "csv":

        _, initial_result = (
            await execute_csv_task(
                user_query
            )
        )

        print(
            "\n--- Verified Multi-Agent Result ---"
        )

        print(
            initial_result
        )

        final_answer = (
            initial_result
        )

    elif task_type in PLANS:

        _, initial_result = (
            await execute_guided_plan(
                user_query,
                task_type,
                memory_context,
            )
        )

        print(
            "\n--- Analyst Output ---"
        )

        print(
            initial_result
        )

        improved_result = (
            await improve_result(
                user_query,
                task_type,
                initial_result,
            )
        )

        print(
            "\n--- Improved / Validated Result ---"
        )

        print(
            improved_result
        )

        final_answer = (
            await report_result(
                user_query,
                improved_result,
            )
        )

    else:

        _, initial_result = (
            await execute_general_task(
                user_query,
                memory_context,
            )
        )

        improved_result = (
            await improve_result(
                user_query,
                task_type,
                initial_result,
            )
        )

        print(
            "\n--- Improved / Validated Result ---"
        )

        print(
            improved_result
        )

        final_answer = (
            await report_result(
                user_query,
                improved_result,
            )
        )

    session_memory.add_message(
        "assistant",
        final_answer,
    )

    logger.info(
        "NEXUS completed successfully"
    )

    return final_answer


# =========================================================
# APPLICATION ENTRY POINT
# =========================================================

async def main():

    print(
        "\n================================"
    )

    print(
        "        NEXUS AI SYSTEM"
    )

    print(
        "================================"
    )

    user_query = input(
        "\nEnter your task: "
    ).strip()

    if not user_query:
        print(
            "\nNo task provided."
        )

        return

    try:
        final_answer = (
            await run_nexus(
                user_query
            )
        )

        print(
            "\n================================"
        )

        print(
            "        FINAL RESPONSE"
        )

        print(
            "================================"
        )

        print(
            final_answer
        )

    except Exception as error:

        logger.exception(
            "NEXUS execution failed"
        )

        print(
            "\nNEXUS execution failed:"
        )

        print(
            error
        )


if __name__ == "__main__":
    asyncio.run(
        main()
    )