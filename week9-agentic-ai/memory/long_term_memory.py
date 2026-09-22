import sqlite3
from datetime import datetime
from pathlib import Path


DB_PATH = (
    Path(__file__).resolve().parent
    / "long_term.db"
)


class LongTermMemory:
    """
    Persistent memory using SQLite.

    Memories remain available even after
    the Python program stops.
    """

    def __init__(self):
        self.db_path = DB_PATH

        self._initialize_database()


    def _get_connection(self):
        """
        Create a connection to the SQLite database.
        """

        return sqlite3.connect(
            self.db_path
        )


    def _initialize_database(self):
        """
        Create the memories table if it does not exist.
        """

        connection = self._get_connection()

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

            connection.commit()

        finally:
            connection.close()


    def add_memory(
        self,
        content: str,
        memory_type: str = "semantic",
    ) -> int:
        """
        Store a memory in SQLite.

        memory_type can be:
        - semantic
        - episodic
        """

        connection = self._get_connection()

        try:
            cursor = connection.cursor()

            created_at = (
                datetime.now().isoformat()
            )

            cursor.execute(
                """
                INSERT INTO memories (
                    content,
                    memory_type,
                    created_at
                )
                VALUES (?, ?, ?)
                """,
                (
                    content,
                    memory_type,
                    created_at,
                ),
            )

            connection.commit()

            return cursor.lastrowid

        finally:
            connection.close()


    def get_all_memories(self) -> list[dict]:
        """
        Return all stored memories.
        """

        connection = self._get_connection()

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    content,
                    memory_type,
                    created_at
                FROM memories
                ORDER BY id ASC
                """
            )

            rows = cursor.fetchall()

            memories = []

            for row in rows:
                memories.append(
                    {
                        "id": row[0],
                        "content": row[1],
                        "memory_type": row[2],
                        "created_at": row[3],
                    }
                )

            return memories

        finally:
            connection.close()


    def get_memories_by_type(
        self,
        memory_type: str,
    ) -> list[dict]:
        """
        Return only memories of a selected type.
        """

        connection = self._get_connection()

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    content,
                    memory_type,
                    created_at
                FROM memories
                WHERE memory_type = ?
                ORDER BY id ASC
                """,
                (
                    memory_type,
                ),
            )

            rows = cursor.fetchall()

            return [
                {
                    "id": row[0],
                    "content": row[1],
                    "memory_type": row[2],
                    "created_at": row[3],
                }
                for row in rows
            ]

        finally:
            connection.close()


    def clear(self):
        """
        Delete all stored memories.
        """

        connection = self._get_connection()

        try:
            cursor = connection.cursor()

            cursor.execute(
                "DELETE FROM memories"
            )

            connection.commit()

        finally:
            connection.close()