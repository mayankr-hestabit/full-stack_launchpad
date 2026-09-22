from memory.vector_store import VectorMemory


memory = VectorMemory()


memory.clear()


memory.add_memory(
    "User prefers Python for backend development.",
    memory_type="semantic",
)

memory.add_memory(
    "User likes FastAPI for building APIs.",
    memory_type="semantic",
)

memory.add_memory(
    "User debugged a Docker container issue yesterday.",
    memory_type="episodic",
)

memory.add_memory(
    "User worked on SQLite database integration.",
    memory_type="episodic",
)


query = (
    "Which technology does the user prefer "
    "for creating backend APIs?"
)


print(
    "\n--- Query ---"
)

print(
    query
)


print(
    "\n--- Relevant Memories ---"
)

results = memory.search(
    query,
    top_k=3,
)

for result in results:
    print(result)