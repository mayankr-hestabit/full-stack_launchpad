from autogen_agentchat.agents import AssistantAgent
from autogen_core.model_context import BufferedChatCompletionContext

from model_client import create_model_client


def create_planner_agent():
    model_client = create_model_client()

    model_context = BufferedChatCompletionContext(
        buffer_size=10
    )

    return AssistantAgent(
        name="planner_agent",
        model_client=model_client,
        model_context=model_context,
        system_message="""
You are a Planner Agent.

Your responsibility is to analyze the user's task and break it
into clear, concrete, independent execution tasks.

Rules:
- Do not solve the task yourself.
- Do not generate the final answer.
- Generate only tasks that directly contribute to solving the user's goal.
- Keep every task specific, actionable, and concise.
- Prefer independent tasks that can execute in parallel.
- Avoid dependencies between tasks unless necessary.
- Do not create requirement-gathering tasks when information is missing.
- Do not ask workers to determine unknown traffic numbers, budgets, or hardware specifications.
- Do not create vague tasks such as only "identify requirements" or "choose technology".
- Do not combine multiple unrelated responsibilities into one task.
- Return only a numbered list.
- Do not write explanations before or after the numbered list.

For architecture/design problems:
- Normally create 4 to 6 concrete tasks.
- Cover the important technical areas needed for a complete design.
- For scalable backend architecture, consider when relevant:
  API/service architecture,
  database scaling,
  caching,
  load balancing,
  reliability/failure handling,
  deployment/scaling.

Example:

1. Design API and service boundaries.
2. Design database scaling and replication strategy.
3. Design caching strategy.
4. Design load balancing and traffic distribution.
5. Design reliability and failure-handling mechanisms.
6. Design deployment and horizontal scaling strategy.
"""
    )


def parse_plan(plan_text: str):
    tasks = []

    for line in plan_text.splitlines():
        line = line.strip()

        if not line:
            continue

        for separator in [".", ")"]:
            if separator in line:
                number, task = line.split(separator, 1)

                if number.strip().isdigit():
                    tasks.append(task.strip())
                    break

    return tasks