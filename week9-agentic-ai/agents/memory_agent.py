from autogen_agentchat.agents import AssistantAgent
from autogen_core.model_context import BufferedChatCompletionContext

from model_client import create_model_client


def create_memory_agent():
    model_client = create_model_client()

    model_context = BufferedChatCompletionContext(
        buffer_size=10
    )

    return AssistantAgent(
        name="memory_agent",
        model_client=model_client,
        model_context=model_context,
        system_message="""
You are a Memory-Aware Assistant.

Your responsibility is to answer the user's question
using the memory context supplied to you.

Rules:
- Use relevant memories when they help answer the question.
- Do not invent memories.
- Do not claim that you remember something unless it is
  present in the supplied memory context.
- Prefer relevant semantic memories for facts/preferences.
- Episodic memories may be used for previous events.
- Keep answers concise and clear.
"""
    )