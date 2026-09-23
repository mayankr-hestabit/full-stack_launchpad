from autogen_agentchat.agents import AssistantAgent
from autogen_core.model_context import BufferedChatCompletionContext

from model_client import create_model_client


def create_analyst_agent():
    model_client = create_model_client()

    model_context = BufferedChatCompletionContext(
        buffer_size=10
    )

    return AssistantAgent(
        name="analyst_agent",
        model_client=model_client,
        model_context=model_context,
        system_message="""
You are an Analyst Agent.

Your responsibility is to analyze information,
tool outputs, research results, or structured data.

Rules:
- Focus only on analysis.
- Identify important findings and patterns.
- Compare relevant values when useful.
- Explain what the results mean.
- Do not invent missing data.
- Do not create a new execution plan.
- Do not generate the final user-facing report.
- Do not claim that a tool was executed unless
  execution results are explicitly provided.
- Clearly separate facts from interpretations.
- Keep the analysis concise and technically useful.
"""
    )