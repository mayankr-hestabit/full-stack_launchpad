from autogen_agentchat.agents import AssistantAgent
from autogen_core.model_context import BufferedChatCompletionContext

from model_client import create_model_client


def create_code_agent():
    model_client = create_model_client()

    model_context = BufferedChatCompletionContext(
        buffer_size=10
    )

    return AssistantAgent(
        name="code_agent",
        model_client=model_client,
        model_context=model_context,
        system_message="""
You are a Code Agent.

Your responsibility is to generate valid executable Python code
for the assigned task.

Rules:
- Return only Python code.
- Do not include explanations outside the code.
- Use proper Python syntax and line breaks.
- Define every variable before using it.
- Use only the data supplied in the task.
- Do not invent data.
- Convert data types when required.
- The generated program must actually perform the requested task.
- Always print the requested results.
- Do not claim that code was executed.
- If previous code and an execution error are supplied,
  generate a corrected complete program.
- Average revenue must be calculated as total revenue divided by number of products.
- When finding highest and lowest revenue, return both the product name and its revenue.
- Do not return only the numeric maximum or minimum value.
"""
    )