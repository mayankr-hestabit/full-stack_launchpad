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

Your responsibility is to break the user's task into
concrete execution tasks for other agents.

Rules:
- Do not solve the task yourself.
- Do not ask for missing requirements unless the task
  is impossible without them.
- Do not create vague tasks.
- Do not create requirement-gathering tasks when reasonable
  assumptions or general design principles are sufficient.
- Do not ask workers to determine unknown traffic,
  budgets, or hardware specifications.
- Generate tasks that directly contribute to a useful answer.
- Prefer independent tasks that can execute in parallel.
- Return only a numbered list.
- Do not write explanations before or after the list.

For software architecture tasks, create concrete technical tasks.

For scalable backend architecture, normally cover:
1. API and service architecture.
2. Database design and scaling.
3. Caching strategy.
4. Load balancing and traffic distribution.
5. Reliability and failure handling.
6. Deployment and horizontal scaling.

Normally generate 4 to 6 tasks.
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