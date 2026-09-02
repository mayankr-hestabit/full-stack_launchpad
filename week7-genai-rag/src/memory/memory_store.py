import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

MEMORY_FILE = BASE_DIR / "memory" / "memory.json"

MAX_MESSAGES = 5


def load_memory():
    if not MEMORY_FILE.exists():
        return []

    with open(MEMORY_FILE, "r", encoding="utf-8") as file:
        try:
            return json.load(file)

        except json.JSONDecodeError:
            return []


def save_memory(messages):
    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(
            messages,
            file,
            indent=4,
            ensure_ascii=False
        )


def add_message(role, content):
    messages = load_memory()

    message = {
        "role": role,
        "content": content
    }

    messages.append(message)

    messages = messages[-MAX_MESSAGES:]

    save_memory(messages)


def get_recent_messages():
    return load_memory()


def clear_memory():
    save_memory([])


if __name__ == "__main__":

    clear_memory()

    add_message(
        "user",
        "What is the employee leave policy?"
    )

    add_message(
        "assistant",
        "Employees receive 24 paid leave days."
    )

    add_message(
        "user",
        "What about interns?"
    )

    print("Recent Conversation:")

    for message in get_recent_messages():
        print(
            f"{message['role']}: "
            f"{message['content']}"
        )