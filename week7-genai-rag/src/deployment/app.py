from fastapi import FastAPI
from pydantic import BaseModel
from google import genai
import os
import time
import json
from datetime import datetime
from pathlib import Path
from google.genai.errors import ServerError
from dotenv import load_dotenv
from retriever.hybrid_retriever import HybridRetriever
from evaluation.rag_eval import (
    evaluate_rag,
    needs_refinement
)
from generator.answer_refiner import refine_answer
from memory.memory_store import (
    add_message,
    get_recent_messages
)
from retriever.image_search import ImageSearchEngine
from pipelines.sql_pipeline import run_sql_qa

app = FastAPI()
retriever = HybridRetriever()
image_search = ImageSearchEngine()

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
BASE_DIR = Path(__file__).resolve().parent.parent
CHAT_LOG_FILE = BASE_DIR / "CHAT-LOGS.json"

class AskRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {
        "message": "Enterprise Knowledge Intelligence API"
    }


def log_chat(endpoint, question, answer, evaluation=None):
    if CHAT_LOG_FILE.exists():
        with open(CHAT_LOG_FILE, "r", encoding="utf-8") as file:
            try:
                logs = json.load(file)
            except json.JSONDecodeError:
                logs = []
    else:
        logs = []

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "endpoint": endpoint,
        "question": question,
        "answer": answer,
        "evaluation": evaluation
    }

    logs.append(log_entry)

    with open(CHAT_LOG_FILE, "w", encoding="utf-8") as file:
        json.dump(
            logs,
            file,
            indent=4,
            ensure_ascii=False
        )

@app.post("/ask")
def ask(request: AskRequest):

    # 1. Load recent conversation memory
    recent_messages = get_recent_messages()

    memory_text = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in recent_messages
    )

    # 2. Retrieve relevant chunks
    results = retriever.hybrid_search(
        request.question,
        top_k=3
    )

    # 3. Build context from retrieved chunks
    context = "\n\n".join(
        result["chunk"]["text"]
        for result in results
    )

    # 4. Create grounded RAG prompt
    prompt = f"""
Answer the user's question using only the provided context.

RECENT CONVERSATION:
{memory_text}

QUESTION:
{request.question}

CONTEXT:
{context}

If the answer is not supported by the context,
say that the available context is insufficient.
"""

    # 5. Generate answer with retry
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )
            break

        except ServerError:
            if attempt == 2:
                raise

            print("Gemini busy. Retrying...")
            time.sleep(2)

    answer = response.text

    # 6. Evaluate generated answer
    evaluation = evaluate_rag(
        request.question,
        answer,
        context
    )

    # 7. Refine if quality is poor
    if needs_refinement(evaluation):

        answer = refine_answer(
            request.question,
            context,
            answer,
            evaluation
        )

        evaluation = evaluate_rag(
            request.question,
            answer,
            context
        )

    # 8. Save latest conversation to memory
    add_message("user", request.question)
    add_message("assistant", answer)


    log_chat(
        endpoint="/ask",
        question=request.question,
        answer=answer,
        evaluation=evaluation
    )
    # 9. Return final response
    return {
        "question": request.question,
        "answer": answer,
        "evaluation": evaluation
    }

@app.post("/ask-image")
def ask_image(request: AskRequest):

    # 1. Search relevant images using the question
    results = image_search.search_by_text(
        request.question,
        top_k=3
    )

    # 2. Build context using image captions + OCR
    context = image_search.build_image_context(
        results
    )

    # 3. Ask Gemini using retrieved image context
    prompt = f"""
Answer the user's question using only the provided image context.

QUESTION:
{request.question}

IMAGE CONTEXT:
{context}

If the answer is not supported by the image context,
say that the available image context is insufficient.
"""

    # 4. Generate answer
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )
            break

        except ServerError:
            if attempt == 2:
                raise

            print("Gemini busy. Retrying...")
            time.sleep(2)

    answer = response.text

    evaluation = evaluate_rag(
        request.question,
        answer,
        context
    )

    log_chat(
        endpoint="/ask-image",
        question=request.question,
        answer=answer,
        evaluation=evaluation
    )
    # 5. Return result
    return {
        "question": request.question,
        "answer": answer,
        "evaluation": evaluation,
        "images": [
            {
                "source": result["image"]["source"],
                "score": result["score"]
            }
            for result in results
        ]
    }

@app.post("/ask-sql")
def ask_sql(request: AskRequest):

    result = run_sql_qa(
        request.question
    )

    log_chat(
        endpoint="/ask-sql",
        question=request.question,
        answer=result["answer"]
    )

    return result