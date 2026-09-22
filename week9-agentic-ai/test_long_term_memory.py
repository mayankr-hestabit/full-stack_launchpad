from memory.long_term_memory import LongTermMemory


memory = LongTermMemory()


memory.clear()


memory.add_memory(
    "User prefers Python for backend development.",
    memory_type="semantic",
)

memory.add_memory(
    "User debugged a Python tool-calling agent today.",
    memory_type="episodic",
)


print(
    "\n--- All Long-Term Memories ---"
)

for item in memory.get_all_memories():
    print(item)


print(
    "\n--- Semantic Memories ---"
)

for item in memory.get_memories_by_type(
    "semantic"
):
    print(item)


print(
    "\n--- Episodic Memories ---"
)

for item in memory.get_memories_by_type(
    "episodic"
):
    print(item)