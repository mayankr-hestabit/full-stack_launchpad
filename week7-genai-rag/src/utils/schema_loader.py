import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "sales.db"


def load_schema(db_path=DB_PATH):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name NOT LIKE 'sqlite_%'
    """)

    tables = cursor.fetchall()

    schema_parts = []

    for (table_name,) in tables:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        column_lines = []

        for column in columns:
            column_name = column[1]
            column_type = column[2]

            column_lines.append(
                f"- {column_name} {column_type}"
            )

        table_schema = f"""
Table: {table_name}
{chr(10).join(column_lines)}
""".strip()

        schema_parts.append(table_schema)

    connection.close()

    return "\n\n".join(schema_parts)


if __name__ == "__main__":
    schema = load_schema()

    print("========== DATABASE SCHEMA ==========")
    print(schema)