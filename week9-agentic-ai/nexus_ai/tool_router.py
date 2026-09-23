from tools.file_agent import (
    read_csv_file,
    read_text_file,
)

from tools.db_agent import (
    execute_sql,
)


def detect_required_tool(
    task: str,
) -> str | None:
    """
    Determine whether a task needs a local tool.

    This provides simple role/tool routing for NEXUS.
    """

    task_lower = task.lower()

    if ".csv" in task_lower:
        return "csv"

    if ".txt" in task_lower:
        return "text"

    if (
        "database" in task_lower
        or "sqlite" in task_lower
        or "sql query" in task_lower
    ):
        return "database"

    return None


def execute_tool_for_task(
    task: str,
) -> dict | None:
    """
    Execute supported deterministic tools when possible.
    """

    tool = detect_required_tool(
        task
    )

    if tool == "csv":
        words = task.split()

        file_name = next(
            (
                word.strip(".,:;()[]")
                for word in words
                if word.lower().endswith(".csv")
            ),
            None,
        )

        if not file_name:
            return None

        return {
            "tool": "File Tool",
            "result": read_csv_file(
                file_name
            ),
        }

    if tool == "text":
        words = task.split()

        file_name = next(
            (
                word.strip(".,:;()[]")
                for word in words
                if word.lower().endswith(".txt")
            ),
            None,
        )

        if not file_name:
            return None

        return {
            "tool": "File Tool",
            "result": read_text_file(
                file_name
            ),
        }

    return None