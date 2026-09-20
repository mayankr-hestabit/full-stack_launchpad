from autogen_agentchat.agents import AssistantAgent
from autogen_core.model_context import BufferedChatCompletionContext

from model_client import create_model_client


def create_reflection_agent():
    model_client = create_model_client()

    model_context = BufferedChatCompletionContext(
        buffer_size=10
    )

    return AssistantAgent(
        name="reflection_agent",
        model_client=model_client,
        model_context=model_context,
        system_message="""
You are a Reflection Agent.

Your responsibility is to review and improve the combined
outputs produced by Worker Agents.

Rules:
- Do not create a new execution plan.
- Do not perform unrelated work.
- Combine useful information from all worker outputs.
- Remove repetition.
- Improve clarity and organization.
- Identify weak or incomplete explanations and make them clearer.
- Preserve the meaning of useful worker results.
- Do not invent precise numbers or unsupported facts.
- Do not introduce unrelated information.
- Ensure the improved result addresses the original user task.
- Return one coherent improved result.
"""
    )