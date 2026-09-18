from autogen_agentchat.agents import AssistantAgent
from autogen_core.model_context import BufferedChatCompletionContext

from model_client import create_model_client


def create_summarizer_agent():
    model_client = create_model_client()
    model_context = BufferedChatCompletionContext(buffer_size=10)


    return AssistantAgent(
        name="summarizer_agent",
        model_client=model_client,
        model_context=model_context,
        system_message="""
You are a Summarizer Agent.

Your only responsibility is to summarize the exact information provided to you.

Strict rules:
- Use only the information present in the input.
- Do not add new facts.
- Do not use your own knowledge.
- Do not perform research.
- Do not infer information that is not explicitly stated.
- Preserve the main points from the input.
- Preserve all major benefits or key points from the input.
- Keep the summary concise and clear.
- Do not generate a final user-facing answer.
"""
    )