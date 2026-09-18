import asyncio

from agents.research_agent import create_research_agent
from agents.summarizer_agent import create_summarizer_agent
from agents.answer_agent import create_answer_agent


async def main():
    research_agent = create_research_agent()
    summarizer_agent = create_summarizer_agent()
    answer_agent = create_answer_agent()

    while True:
        user_query = input("\nEnter your question (or type 'exit'): ")

        if user_query.lower() == "exit":
            break

        research_result = await research_agent.run(task=user_query)
        research_output = research_result.messages[-1].content

        summary_result = await summarizer_agent.run(
            task=f"Summarize this research:\n\n{research_output}"
        )
        summary_output = summary_result.messages[-1].content

        answer_result = await answer_agent.run(
            task=f"Create the final answer using this summary:\n\n{summary_output}"
        )
        final_answer = answer_result.messages[-1].content

        print("\n--- Final Answer ---")
        print(final_answer)

        # Check Research Agent memory after every turn
        research_messages = await research_agent.model_context.get_messages()

        print("\n--- Research Agent Context ---")
        print("Total messages in context:", len(research_messages))

        for message in research_messages:
            print(type(message).__name__, "->", message.content)


if __name__ == "__main__":
    asyncio.run(main())