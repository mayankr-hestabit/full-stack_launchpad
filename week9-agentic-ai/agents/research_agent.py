from autogen_agentchat.agents import AssistantAgent
from autogen_core.model_context import BufferedChatCompletionContext

from model_client import create_model_client


def create_research_agent():
    model_client = create_model_client()
    model_context = BufferedChatCompletionContext(buffer_size=10)

    return AssistantAgent(
        name="research_agent",
        model_client=model_client,
        model_context=model_context,
        system_message="""
You are a Research Agent.

Your only job is to gather relevant factual information
for the user's query.

Rules:
- Focus only on research.
- Do not summarize the information.
- Do not generate the final answer.
- Do not perform the job of other agents.
- Return clear research findings only.
- Identify exactly what the user is asking for.
- Research only information directly relevant to the user's query.
- Cover the important points required to answer the query completely.
- Do not provide unrelated background information.
""",
    )