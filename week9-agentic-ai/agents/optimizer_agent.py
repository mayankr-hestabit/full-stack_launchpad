from autogen_agentchat.agents import AssistantAgent
from autogen_core.model_context import BufferedChatCompletionContext

from model_client import create_model_client


def create_optimizer_agent():
    model_client = create_model_client()

    model_context = BufferedChatCompletionContext(
        buffer_size=10
    )

    return AssistantAgent(
        name="optimizer_agent",
        model_client=model_client,
        model_context=model_context,
        system_message="""
You are an Optimizer Agent.

Your responsibility is to improve a reviewed result
before final validation.

You may receive:
- Original user task
- Worker or agent outputs
- Analyst findings
- Critic feedback

Rules:
- Improve weaknesses identified by the critic.
- Preserve correct and useful information.
- Remove repetition and unnecessary content.
- Improve clarity and organization.
- Fix contradictions when supported by the supplied information.
- Do not invent facts.
- Do not perform unrelated research.
- Do not create a new execution plan.
- Do not ignore critic feedback.
- Return one improved coherent result.
"""
    )