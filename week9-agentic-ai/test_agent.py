import asyncio

from autogen_agentchat.agents import AssistantAgent

from model_client import create_model_client


async def main():
    model_client = create_model_client()

    agent = AssistantAgent(
        name="test_agent",
        model_client=model_client,
        system_message="You are a helpful AI assistant.",
    )

    result = await agent.run(
        task="Explain Docker in one short sentence."
    )

    print(result.messages[-1].content)

    await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())