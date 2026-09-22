import asyncio

from agents.memory_agent import create_memory_agent
from memory.long_term_memory import LongTermMemory
from memory.vector_store import VectorMemory


async def main():
    print("\n================================")
    print(" PERSISTENT MEMORY CHAT DEMO")
    print("================================")

    long_term_memory = LongTermMemory()
    vector_memory = VectorMemory()

    agent = create_memory_agent()

    while True:
        print("\nChoose:")
        print("1. Store a memory")
        print("2. Ask using stored memory")
        print("3. Show SQLite memories")
        print("4. Exit")

        choice = input("\nEnter choice: ").strip()

        # -------------------------------------------------
        # STORE MEMORY
        # -------------------------------------------------

        if choice == "1":
            memory_text = input(
                "\nEnter memory to store: "
            ).strip()

            memory_type = input(
                "Memory type (semantic/episodic): "
            ).strip().lower()

            if memory_type not in {
                "semantic",
                "episodic",
            }:
                memory_type = "semantic"

            memory_id = long_term_memory.add_memory(
                memory_text,
                memory_type=memory_type,
            )

            vector_memory.add_memory(
                memory_text,
                memory_type=memory_type,
            )

            print(
                f"\nMemory stored successfully. "
                f"SQLite ID: {memory_id}"
            )

        # -------------------------------------------------
        # ASK QUESTION
        # -------------------------------------------------

        elif choice == "2":
            query = input(
                "\nAsk something: "
            ).strip()

            relevant_memories = (
                vector_memory.search(
                    query,
                    top_k=3,
                )
            )

            if not relevant_memories:
                print(
                    "\nNo relevant stored memory found."
                )
                continue

            print(
                "\n--- Retrieved Persistent Memories ---"
            )

            memory_context_lines = []

            for memory in relevant_memories:
                print(
                    f"[{memory['memory_type']}] "
                    f"{memory['content']} "
                    f"(score={memory['score']:.4f})"
                )

                memory_context_lines.append(
                    f"- [{memory['memory_type']}] "
                    f"{memory['content']}"
                )

            memory_context = "\n".join(
                memory_context_lines
            )

            result = await agent.run(
                task=f"""
User question:

{query}

Persistent memory retrieved from storage:

{memory_context}

Answer the user's question using only relevant
stored memory when applicable.
"""
            )

            answer = (
                result.messages[-1].content
            )

            print(
                "\n--- Agent Response ---"
            )

            print(answer)

        # -------------------------------------------------
        # SHOW SQLITE MEMORY
        # -------------------------------------------------

        elif choice == "3":
            memories = (
                long_term_memory.get_all_memories()
            )

            print(
                "\n--- Persistent SQLite Memories ---"
            )

            if not memories:
                print(
                    "No memories stored."
                )

            for memory in memories:
                print(memory)

        # -------------------------------------------------
        # EXIT
        # -------------------------------------------------

        elif choice == "4":
            print(
                "\nClosing program."
            )
            break

        else:
            print(
                "\nInvalid choice."
            )


if __name__ == "__main__":
    asyncio.run(
        main()
    )