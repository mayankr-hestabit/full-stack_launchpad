import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from utils.schema_loader import load_schema


BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found. Add it to your .env file."
    )

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3.6-flash"

def clean_sql_response(response_text):
    sql = response_text.strip()

    if sql.startswith("```sql"):
        sql = sql[len("```sql"):]

    if sql.startswith("```"):
        sql = sql[len("```"):]

    if sql.endswith("```"):
        sql = sql[:-3]

    return sql.strip()


def generate_sql(question):
    schema = load_schema()

    prompt = f"""
You are an expert SQLite SQL generator.

Convert the user's natural-language question into one valid SQLite query.

DATABASE SCHEMA:

{schema}

USER QUESTION:

{question}

RULES:

1. Generate only a SELECT query.
2. Do not generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE or TRUNCATE.
3. Use only tables and columns present in the provided schema.
4. Use valid SQLite syntax.
5. Use JOINs when required.
6. For dates stored as TEXT in YYYY-MM-DD format, use SQLite date functions such as strftime().
7. Return SQL only.
8. Do not include explanations.
9. Do not include markdown code fences.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    return clean_sql_response(response.text)


def correct_sql(question, failed_sql, error_message):
    schema = load_schema()

    prompt = f"""
You are an expert SQLite SQL developer.

A SQL query was generated for a user's question,
but SQLite returned an error.

DATABASE SCHEMA:

{schema}

USER QUESTION:

{question}

FAILED SQL:

{failed_sql}

SQLITE ERROR:

{error_message}

Correct the SQL query.

RULES:

1. Generate only one SELECT query.
2. Use only tables and columns from the provided schema.
3. Use valid SQLite syntax.
4. Fix the SQLite error.
5. Do not generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE or TRUNCATE.
6. Return SQL only.
7. Do not include explanations.
8. Do not include markdown code fences.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    if not response.text:
        raise ValueError("Gemini returned an empty SQL correction.")

    return clean_sql_response(response.text)


def summarize_results(question, sql_query, results):
    prompt = f"""
You are a data analyst.

A user asked the following question:

{question}

The following SQL query was executed:

{sql_query}

The database returned:

{results}

Write a concise and clear natural-language answer.

Rules:
1. Base your answer only on the provided database results.
2. Do not invent values.
3. Mention important numbers clearly.
4. Keep the answer concise.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    if not response.text:
        return "Unable to generate a summary."

    return response.text.strip()


if __name__ == "__main__":
    question = input("Enter your question: ")

    print("\n========== DATABASE SCHEMA ==========")
    print(load_schema())

    print("\n========== GENERATED SQL ==========")

    sql = generate_sql(question)

    print(sql)