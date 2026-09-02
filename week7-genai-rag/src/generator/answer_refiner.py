import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is missing.")

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3.6-flash"


def refine_answer(
    question,
    context,
    previous_answer,
    evaluation
):
    prompt = f"""
You are a RAG answer refinement system.

Your job is to improve an answer so that it is fully grounded
in the provided context.

USER QUESTION:

{question}

RETRIEVED CONTEXT:

{context}

PREVIOUS ANSWER:

{previous_answer}

EVALUATION:

{evaluation}

RULES:

1. Answer only using the provided context.
2. Remove unsupported or hallucinated claims.
3. Do not invent facts.
4. If the context does not contain enough information,
   clearly say that the available context is insufficient.
5. Keep the answer concise and directly relevant.
6. Return only the improved answer.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    if not response.text:
        raise ValueError(
            "Gemini returned an empty refined answer."
        )

    return response.text.strip()