import asyncio

from agents.summarizer_agent import create_summarizer_agent


async def main():
    agent = create_summarizer_agent()

    result = await agent.run(
        task="""
Summarize this research:

Docker is an open platform for packaging and deploying applications and services.
Main benefits include portability, consistency across environments,
faster deployment, and resource efficiency.
"""
    )

    print(result.messages[-1].content)


if __name__ == "__main__":
    asyncio.run(main())