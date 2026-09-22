import asyncio

from agents.memory_agent import create_memory_agent

from memory.session_memory import SessionMemory
from memory.long_term_memory import LongTermMemory
from memory.vector_store import VectorMemory


async def main():

    print("\n================================")
    print(" DAY 4 - MEMORY AWARE AGENT")
    print("================================")

    session_memory = SessionMemory(
        max_messages=10
    )

    long_term_memory = LongTermMemory()

    vector_memory = VectorMemory()

    # ---------------------------------------------
    # User query
    # ---------------------------------------------

    user_query = input(
        "\nAsk something: "
    )

    # Store current user message in session memory
    session_memory.add_message(
        "user",
        user_query
    )

    # ---------------------------------------------
    # Retrieve relevant semantic memories
    # ---------------------------------------------

    relevant_memories = (
        vector_memory.search(
            user_query,
            top_k=3,
        )
    )

    memory_context = "\n".join(
        f"- [{memory['memory_type']}] "
        f"{memory['content']}"
        for memory in relevant_memories
    )

    print(
        "\n--- Retrieved Memory Context ---"
    )

    if memory_context:
        print(memory_context)
    else:
        print("No relevant memories found.")

    # ---------------------------------------------
    # Create memory-aware agent
    # ---------------------------------------------

    agent = create_memory_agent()

    result = await agent.run(
        task=f"""
User question:

{user_query}


Relevant memory context:

{memory_context}


Answer the user's question using the relevant
memory context when appropriate.
"""
    )

    answer = (
        result.messages[-1].content
    )

    # ---------------------------------------------
    # Store assistant reply in session memory
    # ---------------------------------------------

    session_memory.add_message(
        "assistant",
        answer
    )

    print(
        "\n--- Memory-Aware Agent Response ---"
    )

    print(answer)

    # ---------------------------------------------
    # Show session memory
    # ---------------------------------------------

    print(
        "\n--- Current Session Memory ---"
    )

    for message in (
        session_memory.get_messages()
    ):
        print(message)


if __name__ == "__main__":
    asyncio.run(
        main()
    )