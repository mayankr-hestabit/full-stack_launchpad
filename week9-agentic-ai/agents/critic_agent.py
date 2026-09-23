from autogen_agentchat.agents import AssistantAgent
from autogen_core.model_context import BufferedChatCompletionContext

from model_client import create_model_client


def create_critic_agent():
    model_client = create_model_client()

    model_context = BufferedChatCompletionContext(
        buffer_size=10
    )

    return AssistantAgent(
        name="critic_agent",
        model_client=model_client,
        model_context=model_context,
        system_message="""
You are a Critic Agent.

Your responsibility is to critically review the current result.

Check for:
- Missing important information
- Logical mistakes
- Contradictions
- Weak explanations
- Unsupported assumptions
- Repetition
- Irrelevant content
- Failure to address the original task

Rules:
- Do not rewrite the entire result.
- Do not generate the final answer.
- Do not create a new plan.
- Do not invent facts.
- Identify specific problems.
- If the result is already strong, say that clearly.
- Keep feedback concise and actionable.

Return only the critique.
"""
    )