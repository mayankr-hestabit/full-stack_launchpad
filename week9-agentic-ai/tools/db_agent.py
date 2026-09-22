import sqlite3
from pathlib import Path

from autogen_agentchat.agents import AssistantAgent
from autogen_core.model_context import BufferedChatCompletionContext

from model_client import create_model_client


DB_PATH = Path(__file__).resolve().parents[1] / "data" / "day3.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def execute_sql(query: str) -> dict:
    """
    Execute one SQLite query and return its result.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(query)

        # cursor.description exists when the statement returns rows
        if cursor.description is not None:
            rows = cursor.fetchall()

            columns = [
                description[0]
                for description in cursor.description
            ]

            return {
                "success": True,
                "columns": columns,
                "rows": rows,
                "error": "",
            }

        connection.commit()

        return {
            "success": True,
            "columns": [],
            "rows": [],
            "error": "",
        }

    except sqlite3.Error as error:
        return {
            "success": False,
            "columns": [],
            "rows": [],
            "error": str(error),
        }

    finally:
        connection.close()


def initialize_sales_database(rows: list[dict]) -> dict:
    """
    Create/reset the sales table using CSV data.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT NOT NULL,
            revenue REAL NOT NULL
        )
        """)

        # Reset demo data so repeated runs do not create duplicates.
        cursor.execute("DELETE FROM sales")

        for row in rows:
            cursor.execute(
                """
                INSERT INTO sales (product, revenue)
                VALUES (?, ?)
                """,
                (
                    row["product"],
                    float(row["revenue"]),
                ),
            )

        connection.commit()

        return {
            "success": True,
            "error": "",
        }

    except sqlite3.Error as error:
        return {
            "success": False,
            "error": str(error),
        }

    finally:
        connection.close()


def create_db_agent():
    model_client = create_model_client()

    model_context = BufferedChatCompletionContext(
        buffer_size=10
    )

    return AssistantAgent(
        name="db_agent",
        model_client=model_client,
        model_context=model_context,
        system_message="""
You are a Database Agent.

Your responsibility is to generate SQLite-compatible SQL queries.

Rules:
- Generate only the SQL needed for the assigned task.
- Use SQLite syntax.
- Use only tables and columns supplied in the task.
- Do not invent tables or columns.
- Do not invent database results.
- Do not claim that the query was executed.
- Return the SQL inside one SQL code block.
"""
    )