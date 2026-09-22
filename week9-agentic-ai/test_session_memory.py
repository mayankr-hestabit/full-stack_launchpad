from memory.session_memory import SessionMemory


memory = SessionMemory(max_messages=3)

memory.add_message(
    "user",
    "My name is Mayank."
)

memory.add_message(
    "assistant",
    "Hello Mayank."
)

memory.add_message(
    "user",
    "I am learning Agentic AI."
)


print("\n--- Current Memory ---")

for message in memory.get_messages():
    print(message)


print("\n--- Adding One More Message ---")

memory.add_message(
    "assistant",
    "Agentic AI uses agents, tools and memory."
)


print("\n--- Updated Memory ---")

for message in memory.get_messages():
    print(message)


print(
    "\nMemory Size:",
    memory.size()
)