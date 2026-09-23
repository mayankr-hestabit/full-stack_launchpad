from memory.session_memory import SessionMemory
from memory.long_term_memory import LongTermMemory
from memory.vector_store import VectorMemory

from nexus_ai.config import (
    MEMORY_TOP_K,
    SESSION_MEMORY_SIZE,
)


class NexusMemoryManager:
    """
    Combines session, SQLite and FAISS memory.
    """

    def __init__(self):
        self.session = SessionMemory(
            max_messages=SESSION_MEMORY_SIZE
        )

        self.long_term = LongTermMemory()

        self.vector = VectorMemory()


    def remember_session(
        self,
        role: str,
        content: str,
    ):
        self.session.add_message(
            role,
            content,
        )


    def retrieve_relevant(
        self,
        query: str,
    ) -> list[dict]:
        """
        Retrieve semantically relevant memories.
        """

        return self.vector.search(
            query,
            top_k=MEMORY_TOP_K,
        )


    def build_memory_context(
        self,
        query: str,
    ) -> str:
        """
        Convert retrieved memories into prompt context.
        """

        memories = self.retrieve_relevant(
            query
        )

        if not memories:
            return "No relevant stored memories."

        return "\n".join(
            (
                f"- [{memory['memory_type']}] "
                f"{memory['content']}"
            )
            for memory in memories
        )