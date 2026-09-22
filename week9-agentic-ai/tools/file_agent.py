import csv
from pathlib import Path

from autogen_agentchat.agents import AssistantAgent
from autogen_core.model_context import BufferedChatCompletionContext

from model_client import create_model_client


BASE_DIR = Path(__file__).resolve().parents[1] / "data"
BASE_DIR.mkdir(parents=True, exist_ok=True)


def get_safe_path(file_name: str) -> Path:
    """
    Return a path restricted to the project's data directory.
    """

    file_path = (BASE_DIR / file_name).resolve()
    base_path = BASE_DIR.resolve()

    if base_path not in file_path.parents and file_path != base_path:
        raise ValueError("File must remain inside the data directory.")

    return file_path


def read_text_file(file_name: str) -> dict:
    try:
        file_path = get_safe_path(file_name)

        content = file_path.read_text(
            encoding="utf-8"
        )

        return {
            "success": True,
            "content": content,
            "error": "",
        }

    except Exception as error:
        return {
            "success": False,
            "content": "",
            "error": str(error),
        }


def write_text_file(
    file_name: str,
    content: str
) -> dict:
    try:
        file_path = get_safe_path(file_name)

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        file_path.write_text(
            content,
            encoding="utf-8"
        )

        return {
            "success": True,
            "path": str(file_path),
            "error": "",
        }

    except Exception as error:
        return {
            "success": False,
            "path": "",
            "error": str(error),
        }


def read_csv_file(file_name: str) -> dict:
    try:
        file_path = get_safe_path(file_name)

        with file_path.open(
            mode="r",
            newline="",
            encoding="utf-8"
        ) as csv_file:

            reader = csv.DictReader(csv_file)
            rows = list(reader)

        return {
            "success": True,
            "rows": rows,
            "error": "",
        }

    except Exception as error:
        return {
            "success": False,
            "rows": [],
            "error": str(error),
        }


def write_csv_file(
    file_name: str,
    rows: list[dict]
) -> dict:
    try:
        if not rows:
            return {
                "success": False,
                "path": "",
                "error": "No rows provided.",
            }

        file_path = get_safe_path(file_name)

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        fieldnames = list(rows[0].keys())

        with file_path.open(
            mode="w",
            newline="",
            encoding="utf-8"
        ) as csv_file:

            writer = csv.DictWriter(
                csv_file,
                fieldnames=fieldnames
            )

            writer.writeheader()
            writer.writerows(rows)

        return {
            "success": True,
            "path": str(file_path),
            "error": "",
        }

    except Exception as error:
        return {
            "success": False,
            "path": "",
            "error": str(error),
        }


def create_file_agent():
    model_client = create_model_client()

    model_context = BufferedChatCompletionContext(
        buffer_size=10
    )

    return AssistantAgent(
        name="file_agent",
        model_client=model_client,
        model_context=model_context,
        system_message="""
You are a File Agent.

Your responsibility is to determine the file operation
required for the assigned task.

Supported file operations:
- Read TXT
- Write TXT
- Read CSV
- Write CSV

Rules:
- Use only file information supplied in the task.
- Do not invent file contents.
- Do not claim a file was read or written unless the system performs it.
- Keep responses concise and task-focused.
"""
    )