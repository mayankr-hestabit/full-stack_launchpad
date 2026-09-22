import asyncio
import ast
import re

from agents.code_agent import create_code_agent
from tools.code_executor import execute_python_code

from tools.file_agent import (
    read_csv_file,
    write_text_file,
)

from tools.db_agent import (
    create_db_agent,
    execute_sql,
    initialize_sales_database,
)


MAX_CODE_RETRIES = 3


# =========================================================
# RESPONSE EXTRACTION
# =========================================================

def extract_python_code(text: str) -> str:
    """
    Extract Python code from a Markdown code block.
    If the model returns raw Python, return it directly.
    """

    match = re.search(
        r"```(?:python)?\s*(.*?)```",
        text,
        re.DOTALL | re.IGNORECASE,
    )

    if match:
        return match.group(1).strip()

    return text.strip()


def extract_sql(text: str) -> str:
    """
    Extract SQL from a Markdown code block.
    """

    match = re.search(
        r"```(?:sql)?\s*(.*?)```",
        text,
        re.DOTALL | re.IGNORECASE,
    )

    if match:
        return match.group(1).strip()

    return text.strip()


# =========================================================
# DATA PREPARATION
# =========================================================

def normalize_sales_data(rows: list[dict]) -> list[dict]:
    """
    Convert CSV revenue strings into numeric values.

    Example:

    {'product': 'Laptop', 'revenue': '50000'}

    becomes:

    {'product': 'Laptop', 'revenue': 50000.0}
    """

    normalized_rows = []

    for row in rows:
        normalized_rows.append(
            {
                "product": row["product"],
                "revenue": float(row["revenue"]),
            }
        )

    return normalized_rows


# =========================================================
# SYNTAX VALIDATION
# =========================================================

def validate_python_syntax(
    code: str,
) -> tuple[bool, str]:
    """
    Check generated Python syntax before execution.
    """

    try:
        ast.parse(code)
        return True, ""

    except SyntaxError as error:
        return (
            False,
            (
                f"SyntaxError on line "
                f"{error.lineno}: {error.msg}"
            ),
        )


# =========================================================
# EXPECTED RESULT
# =========================================================

def calculate_expected_values(
    rows: list[dict],
) -> dict:
    """
    Calculate trusted values used only to validate
    the agent-generated program.
    """

    number_of_products = len(rows)

    total_revenue = sum(
        row["revenue"]
        for row in rows
    )

    average_revenue = (
        total_revenue / number_of_products
    )

    highest_product = max(
        rows,
        key=lambda row: row["revenue"],
    )

    lowest_product = min(
        rows,
        key=lambda row: row["revenue"],
    )

    return {
        "count": number_of_products,
        "total": total_revenue,
        "average": average_revenue,

        "highest_product":
            highest_product["product"],

        "highest_revenue":
            highest_product["revenue"],

        "lowest_product":
            lowest_product["product"],

        "lowest_revenue":
            lowest_product["revenue"],
    }


# =========================================================
# LOGICAL VALIDATION
# =========================================================

def validate_analysis_output(
    output: str,
    rows: list[dict],
) -> tuple[bool, str]:
    """
    Verify that the generated program produced
    logically correct results.
    """

    expected = calculate_expected_values(
        rows
    )

    # Number of products
    if str(expected["count"]) not in output:
        return (
            False,
            (
                "Incorrect number of products. "
                f"Expected {expected['count']}."
            ),
        )

    # Total
    total_value = (
        f"{expected['total']:.2f}"
    )

    total_integer = (
        f"{expected['total']:.0f}"
    )

    if (
        total_value not in output
        and total_integer not in output
    ):
        return (
            False,
            (
                "Incorrect total revenue. "
                f"Expected {total_value}."
            ),
        )

    # Average
    average_value = (
        f"{expected['average']:.2f}"
    )

    if average_value not in output:
        return (
            False,
            (
                "Incorrect average revenue. "
                f"Expected {average_value}."
            ),
        )

    # Highest product
    if (
        expected["highest_product"]
        not in output
    ):
        return (
            False,
            (
                "Incorrect highest revenue product. "
                f"Expected "
                f"{expected['highest_product']}."
            ),
        )

    # Highest revenue
    highest_revenue = (
        f"{expected['highest_revenue']:.2f}"
    )

    highest_revenue_integer = (
        f"{expected['highest_revenue']:.0f}"
    )

    if (
        highest_revenue not in output
        and highest_revenue_integer not in output
    ):
        return (
            False,
            (
                "Highest revenue value missing. "
                f"Expected {highest_revenue}."
            ),
        )

    # Lowest product
    if (
        expected["lowest_product"]
        not in output
    ):
        return (
            False,
            (
                "Incorrect lowest revenue product. "
                f"Expected "
                f"{expected['lowest_product']}."
            ),
        )

    # Lowest revenue
    lowest_revenue = (
        f"{expected['lowest_revenue']:.2f}"
    )

    lowest_revenue_integer = (
        f"{expected['lowest_revenue']:.0f}"
    )

    if (
        lowest_revenue not in output
        and lowest_revenue_integer not in output
    ):
        return (
            False,
            (
                "Lowest revenue value missing. "
                f"Expected {lowest_revenue}."
            ),
        )

    return True, ""


# =========================================================
# CODE AGENT
# =========================================================

async def generate_analysis_code(
    previous_code: str | None = None,
    previous_error: str | None = None,
) -> str:
    """
    Ask the Code Agent to generate only analysis logic.

    The variable `data` is injected by the application
    before execution.
    """

    code_agent = create_code_agent()

    repair_context = ""

    if previous_code and previous_error:
        repair_context = f"""

The previous program failed.

Previous code:

{previous_code}

Failure:

{previous_error}

Generate a corrected COMPLETE program.

Do not repeat the same mistake.
"""

    task = f"""
Write executable Python code to analyze sales data.

IMPORTANT:

A variable named `data` ALREADY EXISTS in the Python
runtime before your code executes.

It has this structure:

[
    {{
        "product": "Laptop",
        "revenue": 50000.0
    }},
    ...
]

Revenue values are ALREADY numeric floats.

DO NOT define or replace the `data` variable.

Use the existing `data` variable.

Your program must:

1. Calculate the number of products.

2. Calculate total revenue.

3. Calculate average revenue using:

   total_revenue / number_of_products

4. Find the complete dictionary having
   the highest revenue.

5. Find the complete dictionary having
   the lowest revenue.

6. Print output using exactly these labels:

Number of Products:
Total Revenue:
Average Revenue:
Highest Revenue Product:
Lowest Revenue Product:

7. Highest Revenue Product must print
   product name and revenue.

8. Lowest Revenue Product must print
   product name and revenue.

9. Round the average revenue to two
   decimal places when printing.


Example logic patterns:

total_revenue = sum(
    row["revenue"]
    for row in data
)

highest_product = max(
    data,
    key=lambda row: row["revenue"]
)

lowest_product = min(
    data,
    key=lambda row: row["revenue"]
)


Rules:

- Return Python code only.
- Do not use Markdown.
- Do not define `data`.
- Do not hardcode the answers.
- Calculate everything from `data`.
- Define variables before using them.
- Print all required results.

{repair_context}
"""

    result = await code_agent.run(
        task=task
    )

    generated_text = (
        result.messages[-1].content
    )

    return extract_python_code(
        generated_text
    )


# =========================================================
# PYTHON EXECUTION
# =========================================================

async def run_code_analysis(
    rows: list[dict],
) -> dict:
    """
    Generate Python code and execute it.

    The actual data variable is injected by the
    orchestration layer rather than generated by the LLM.
    """

    previous_code = None
    previous_error = None

    for attempt in range(
        1,
        MAX_CODE_RETRIES + 1,
    ):

        print(
            f"\n--- Code Generation Attempt "
            f"{attempt}/{MAX_CODE_RETRIES} ---"
        )

        generated_code = (
            await generate_analysis_code(
                previous_code=previous_code,
                previous_error=previous_error,
            )
        )

        print(
            "\n--- Agent Generated Logic ---"
        )

        print(
            generated_code
        )

        # =================================================
        # INJECT ACTUAL DATA
        # =================================================

        executable_code = (
            f"data = {repr(rows)}\n\n"
            f"{generated_code}"
        )

        print(
            "\n--- Final Executable Program ---"
        )

        print(
            executable_code
        )

        # =================================================
        # SYNTAX CHECK
        # =================================================

        syntax_valid, syntax_error = (
            validate_python_syntax(
                executable_code
            )
        )

        if not syntax_valid:

            print(
                "\n--- Syntax Validation Failed ---"
            )

            print(
                syntax_error
            )

            previous_code = (
                generated_code
            )

            previous_error = (
                syntax_error
            )

            continue

        print(
            "\nSyntax validation passed."
        )

        # =================================================
        # EXECUTE
        # =================================================

        execution_result = (
            execute_python_code(
                executable_code
            )
        )

        print(
            "\n--- Execution Result ---"
        )

        print(
            execution_result
        )

        # =================================================
        # RUNTIME ERROR
        # =================================================

        if not execution_result[
            "success"
        ]:

            previous_code = (
                generated_code
            )

            previous_error = (
                "Runtime error:\n"
                + execution_result[
                    "stderr"
                ]
            )

            print(
                "\n--- Runtime Validation Failed ---"
            )

            continue

        # =================================================
        # NO OUTPUT
        # =================================================

        if not execution_result[
            "stdout"
        ]:

            previous_code = (
                generated_code
            )

            previous_error = (
                "The program ran successfully "
                "but printed no results."
            )

            print(
                "\n--- Output Validation Failed ---"
            )

            continue

        # =================================================
        # LOGICAL VALIDATION
        # =================================================

        valid, validation_error = (
            validate_analysis_output(
                execution_result[
                    "stdout"
                ],
                rows,
            )
        )

        if not valid:

            print(
                "\n--- Logical Validation Failed ---"
            )

            print(
                validation_error
            )

            previous_code = (
                generated_code
            )

            previous_error = (
                "The program executed, but its "
                "result was logically incorrect.\n"
                + validation_error
            )

            continue

        # =================================================
        # SUCCESS
        # =================================================

        print(
            "\nPython analysis validated successfully."
        )

        return {
            "success": True,
            "stdout": execution_result[
                "stdout"
            ],
            "stderr": "",
            "attempts": attempt,
            "generated_code":
                generated_code,
        }

    return {
        "success": False,
        "stdout": "",
        "stderr": (
            f"Code Agent failed after "
            f"{MAX_CODE_RETRIES} attempts.\n\n"
            f"Last problem:\n"
            f"{previous_error}"
        ),
        "attempts":
            MAX_CODE_RETRIES,

        "generated_code":
            previous_code,
    }


# =========================================================
# DATABASE AGENT
# =========================================================

async def run_database_analysis() -> dict:
    """
    Ask the DB Agent to generate SQL and execute
    the query using SQLite.
    """

    db_agent = create_db_agent()

    result = await db_agent.run(
        task="""
Database schema:

sales(
    id INTEGER,
    product TEXT,
    revenue REAL
)

Generate one SQLite query that returns:

- product
- revenue

for the product having the highest revenue.

Requirements:

- Sort revenue descending.
- Return only one row.
- Return SQL only.
"""
    )

    generated_sql = (
        result.messages[-1].content
    )

    sql_query = extract_sql(
        generated_sql
    )

    print(
        "\n--- Generated SQL ---"
    )

    print(
        sql_query
    )

    db_result = execute_sql(
        sql_query
    )

    return {
        **db_result,
        "generated_sql":
            sql_query,
    }


# =========================================================
# MAIN
# =========================================================

async def main():

    print(
        "\n================================"
    )

    print(
        " DAY 3 - TOOL CALLING AGENTS"
    )

    print(
        "================================"
    )

    # =====================================================
    # 1. FILE TOOL
    # =====================================================

    print(
        "\n--- File Tool: Reading sales.csv ---"
    )

    file_result = read_csv_file(
        "sales.csv"
    )

    if not file_result[
        "success"
    ]:

        print(
            "Failed to read sales.csv:"
        )

        print(
            file_result[
                "error"
            ]
        )

        return

    raw_rows = file_result[
        "rows"
    ]

    if not raw_rows:

        print(
            "sales.csv contains no data."
        )

        return

    # =====================================================
    # VALIDATE CSV STRUCTURE
    # =====================================================

    required_columns = {
        "product",
        "revenue",
    }

    actual_columns = set(
        raw_rows[0].keys()
    )

    if not required_columns.issubset(
        actual_columns
    ):

        print(
            "sales.csv must contain "
            "'product' and 'revenue' columns."
        )

        return

    print(
        "\n--- Raw CSV Data ---"
    )

    for row in raw_rows:
        print(
            row
        )

    # =====================================================
    # 2. NORMALIZE INPUT DATA
    # =====================================================

    try:

        rows = normalize_sales_data(
            raw_rows
        )

    except (
        ValueError,
        TypeError,
        KeyError,
    ) as error:

        print(
            "\nFailed to normalize CSV data:"
        )

        print(
            error
        )

        return

    print(
        "\n--- Normalized Data ---"
    )

    for row in rows:
        print(
            row
        )

    # =====================================================
    # 3. CODE AGENT + PYTHON EXECUTOR
    # =====================================================

    code_result = (
        await run_code_analysis(
            rows
        )
    )

    if not code_result[
        "success"
    ]:

        print(
            "\n--- Code Agent Failed ---"
        )

        print(
            code_result[
                "stderr"
            ]
        )

        print(
            "\nNo hardcoded fallback was used."
        )

        return

    print(
        "\n--- Final Python Analysis ---"
    )

    print(
        code_result[
            "stdout"
        ]
    )

    print(
        "\nCode Agent succeeded after "
        f"{code_result['attempts']} "
        "attempt(s)."
    )

    # =====================================================
    # 4. SQLITE DATABASE
    # =====================================================

    db_setup = (
        initialize_sales_database(
            raw_rows
        )
    )

    if not db_setup[
        "success"
    ]:

        print(
            "\nDatabase initialization failed:"
        )

        print(
            db_setup[
                "error"
            ]
        )

        return

    print(
        "\n--- SQLite Database Ready ---"
    )

    # =====================================================
    # 5. DATABASE AGENT
    # =====================================================

    db_result = (
        await run_database_analysis()
    )

    print(
        "\n--- Database Result ---"
    )

    print(
        db_result
    )

    if not db_result[
        "success"
    ]:

        print(
            "\nDatabase query failed:"
        )

        print(
            db_result[
                "error"
            ]
        )

        return

    # =====================================================
    # 6. FINAL REPORT
    # =====================================================

    report_lines = [
        "DAY 3 TOOL ANALYSIS REPORT",
        "=" * 40,
        "",
        "SOURCE",
        "sales.csv",
        "",
        "PYTHON ANALYSIS",
        code_result[
            "stdout"
        ],
        "",
        "CODE AGENT",
        (
            "Successful after "
            f"{code_result['attempts']} "
            "attempt(s)"
        ),
        "",
        "DATABASE RESULT",
        (
            f"Columns: "
            f"{db_result['columns']}"
        ),
        (
            f"Rows: "
            f"{db_result['rows']}"
        ),
        "",
        "GENERATED SQL",
        db_result[
            "generated_sql"
        ],
        "",
        "TOOL CHAIN",
        (
            "File Tool -> "
            "Data Normalization -> "
            "Code Agent -> "
            "Runtime Data Injection -> "
            "Python Executor -> "
            "Logical Validator -> "
            "DB Agent -> "
            "SQLite -> "
            "File Writer"
        ),
    ]

    report = "\n".join(
        report_lines
    )

    # =====================================================
    # 7. FILE WRITE TOOL
    # =====================================================

    write_result = (
        write_text_file(
            "day3_report.txt",
            report,
        )
    )

    print(
        "\n--- Report File ---"
    )

    if not write_result[
        "success"
    ]:

        print(
            "Report writing failed:"
        )

        print(
            write_result[
                "error"
            ]
        )

        return

    print(
        "Report written successfully:"
    )

    print(
        write_result[
            "path"
        ]
    )

    # =====================================================
    # FINAL FLOW
    # =====================================================

    print(
        "\n--- Tool Chain ---"
    )

    print(
        """
User Task
└── File Tool
    └── Read sales.csv
        └── Normalize Data
            └── Code Agent
                └── Generate Analysis Logic
                    └── Inject Runtime Data
                        └── Python Executor
                            └── Validate Result
                                └── DB Agent
                                    └── SQLite
                                        └── File Writer
                                            └── Final Report
"""
    )

    print(
        "Day 3 tool-chain completed successfully."
    )


if __name__ == "__main__":
    asyncio.run(
        main()
    )