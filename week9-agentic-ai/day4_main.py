from memory.session_memory import SessionMemory
from memory.long_term_memory import LongTermMemory
from memory.vector_store import VectorMemory


def main():
    print("\n================================")
    print(" DAY 4 - MEMORY SYSTEMS")
    print("================================")

    # -----------------------------------------------------
    # 1. CREATE MEMORY SYSTEMS
    # -----------------------------------------------------

    session_memory = SessionMemory(
        max_messages=5
    )

    long_term_memory = LongTermMemory()

    vector_memory = VectorMemory()

    # Clean demo vector memory
    # so repeated runs do not create duplicates.
    vector_memory.clear()

    # -----------------------------------------------------
    # 2. SESSION MEMORY
    # -----------------------------------------------------

    print(
        "\n--- Session Memory ---"
    )

    session_memory.add_message(
        "user",
        "I am building a backend application."
    )

    session_memory.add_message(
        "assistant",
        "What technology would you like to use?"
    )

    session_memory.add_message(
        "user",
        "I prefer Python and FastAPI."
    )

    for message in (
        session_memory.get_messages()
    ):
        print(message)

    # -----------------------------------------------------
    # 3. LONG-TERM MEMORY
    # -----------------------------------------------------

    print(
        "\n--- Long-Term Memory ---"
    )

    long_term_memory.clear()

    long_term_memory.add_memory(
        "User prefers Python for backend development.",
        memory_type="semantic",
    )

    long_term_memory.add_memory(
        "User prefers FastAPI for building APIs.",
        memory_type="semantic",
    )

    long_term_memory.add_memory(
        (
            "User worked on a tool-calling "
            "agent using Python."
        ),
        memory_type="episodic",
    )

    stored_memories = (
        long_term_memory.get_all_memories()
    )

    for memory in stored_memories:
        print(memory)

    # -----------------------------------------------------
    # 4. COPY LONG-TERM MEMORIES INTO VECTOR MEMORY
    # -----------------------------------------------------

    print(
        "\n--- Indexing Memories in FAISS ---"
    )

    for memory in stored_memories:
        vector_memory.add_memory(
            content=memory["content"],
            memory_type=memory["memory_type"],
        )

    print(
        f"Indexed {len(stored_memories)} memories."
    )

    # -----------------------------------------------------
    # 5. SEMANTIC SEARCH
    # -----------------------------------------------------

    query = (
        "What should I use to build "
        "a Python backend API?"
    )

    print(
        "\n--- Semantic Memory Query ---"
    )

    print(query)

    results = vector_memory.search(
        query=query,
        top_k=3,
    )

    print(
        "\n--- Retrieved Memories ---"
    )

    for result in results:
        print(
            f"[{result['memory_type']}] "
            f"{result['content']} "
            f"(score={result['score']:.4f})"
        )

    # -----------------------------------------------------
    # 6. MEMORY SUMMARY
    # -----------------------------------------------------

    print(
        "\n--- Memory System Summary ---"
    )

    print(
        "Session Memory Messages:",
        session_memory.size()
    )

    print(
        "Long-Term Memories:",
        len(stored_memories)
    )

    print(
        "Vector Memories:",
        vector_memory.index.ntotal
    )

    print(
        "\nDay 4 memory flow completed successfully."
    )


if __name__ == "__main__":
    main()