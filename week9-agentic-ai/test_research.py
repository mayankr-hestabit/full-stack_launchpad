import asyncio

from agents.research_agent import create_research_agent


async def main():
    agent = create_research_agent()

    for i in range(1, 7):
        result = await agent.run(
            task=f"Remember this message number: {i}"
        )
        print(f"Turn {i}: {result.messages[-1].content}")

    print("\nMessages currently inside model context:")

    messages = await agent.model_context.get_messages()

    for message in messages:
        print(type(message).__name__, "->", message.content)


if __name__ == "__main__":
    asyncio.run(main())