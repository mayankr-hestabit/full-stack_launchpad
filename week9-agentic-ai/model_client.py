from autogen_ext.models.openai import OpenAIChatCompletionClient


def create_model_client():
    return OpenAIChatCompletionClient(
        model="/home/mayank/full-stack_launchpad/week8-llm-fine-tuning/quantized/model.gguf",
        base_url="http://127.0.0.1:8080/v1",
        api_key="not-required",
        model_info={
            "vision": False,
            "function_calling": False,
            "json_output": False,
            "family": "unknown",
            "structured_output": False,
        },
    )