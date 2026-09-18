from autogen_agentchat.agents import AssistantAgent
from autogen_core.model_context import BufferedChatCompletionContext


from model_client import create_model_client


def create_answer_agent():
    model_client = create_model_client()
    model_context = BufferedChatCompletionContext(buffer_size=10)

    return AssistantAgent(
        name="answer_agent",
        model_client=model_client,
        model_context=model_context,
        system_message="""
You are an Answer Agent.

Your only responsibility is to convert the provided summary
into a clear final user-facing answer.

Strict rules:
- Use only the information explicitly present in the summary.
- Do not use your own knowledge.
- Do not add new facts, examples, definitions, or explanations.
- Do not infer anything that is not stated.
- Preserve all important points from the summary.
- Rephrase only for clarity and readability.
""",
    )