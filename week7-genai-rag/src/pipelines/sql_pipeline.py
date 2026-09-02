import sqlite3
import re
from pathlib import Path

from generator.sql_generator import (
    generate_sql,
    correct_sql,
    summarize_results
)

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "sales.db"


FORBIDDEN_KEYWORDS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "TRUNCATE",
    "REPLACE",
    "ATTACH",
    "DETACH",
    "PRAGMA"
]


def validate_sql(sql):
    sql_clean = sql.strip()

    if not sql_clean:
        raise ValueError("SQL query is empty.")

    upper_sql = sql_clean.upper()

    if not upper_sql.startswith("SELECT"):
        raise ValueError(
            "Only SELECT queries are allowed."
        )

    for keyword in FORBIDDEN_KEYWORDS:
        pattern = rf"\b{keyword}\b"

        if re.search(pattern, upper_sql):
            raise ValueError(
                f"Unsafe SQL detected: {keyword}"
            )

    # Prevent multiple SQL statements
    statements = [
        statement.strip()
        for statement in sql_clean.split(";")
        if statement.strip()
    ]

    if len(statements) > 1:
        raise ValueError(
            "Multiple SQL statements are not allowed."
        )

    return sql_clean


def execute_sql(sql):
    connection = sqlite3.connect(DB_PATH)

    # Extra safety:
    # prevents accidental database modification
    connection.execute("PRAGMA query_only = ON")

    cursor = connection.cursor()

    try:
        cursor.execute(sql)

        rows = cursor.fetchall()

        columns = [
            description[0]
            for description in cursor.description
        ]

        results = [
            dict(zip(columns, row))
            for row in rows
        ]

        return results

    finally:
        connection.close()


def run_sql_qa(question):

    print("\n========== USER QUESTION ==========")
    print(question)

    print("\n========== GENERATED SQL ==========")

    sql = generate_sql(question)

    print(sql)

    print("\n========== VALIDATING SQL ==========")

    validated_sql = validate_sql(sql)

    print("SQL validation passed.")

    print("\n========== DATABASE RESULT ==========")

    try:
        results = execute_sql(validated_sql)

    except sqlite3.Error as error:
        print("\n========== SQL EXECUTION ERROR ==========")
        print(error)

        print("\n========== CORRECTING SQL ==========")

        corrected_sql = correct_sql(
            question,
            validated_sql,
            str(error)
        )

        print(corrected_sql)

        print("\n========== REVALIDATING SQL ==========")

        validated_sql = validate_sql(corrected_sql)

        print("Corrected SQL validation passed.")

        results = execute_sql(validated_sql)

    if not results:
      return {
          "question": question,
          "sql": validated_sql,
          "results": [],
          "answer": "No results found."
      }

    for row in results:
        print(row)

    answer = summarize_results(
        question,
        validated_sql,
        results
    )

    return {
        "question": question,
        "sql": validated_sql,
        "results": results,
        "answer": answer
    }


if __name__ == "__main__":

    question = input(
        "Ask a question about the sales database: "
    )

    try:
        run_sql_qa(question)

    except Exception as error:
        print(f"\nError: {error}")