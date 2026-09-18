import asyncio

from agents.answer_agent import create_answer_agent


async def main():
    agent = create_answer_agent()

    result = await agent.run(
        task="""
Create the final answer using this summary:

Docker packages applications and services while providing
portability, consistent environment setup,
faster deployments, and reduced resource usage.
"""
    )

    print(result.messages[-1].content)


if __name__ == "__main__":
    asyncio.run(main())