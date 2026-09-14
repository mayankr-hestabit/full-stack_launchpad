import logging
import uuid

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from deploy.model_loader import (
    start_llama_server,
    stop_llama_server,
    chat_completion,
    stream_chat_completion,
)


# ---------------------------------------------------------
# LOGGING
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("llm-api")


# ---------------------------------------------------------
# CHAT MEMORY
# ---------------------------------------------------------

chat_sessions = {}


# ---------------------------------------------------------
# FASTAPI STARTUP / SHUTDOWN
# ---------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Starting Local LLM API")

    start_llama_server()

    yield

    logger.info("Stopping Local LLM API")

    stop_llama_server()


app = FastAPI(
    title="Local Fine-Tuned LLM API",
    description="FastAPI service for the quantized Qwen GGUF model.",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------
# REQUEST MODELS
# ---------------------------------------------------------

class GenerateRequest(BaseModel):

    prompt: str

    system_prompt: str = (
        "You are a helpful coding and software engineering assistant."
    )

    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
    )

    top_p: float = Field(
        default=0.9,
        gt=0.0,
        le=1.0,
    )

    top_k: int = Field(
        default=40,
        ge=0,
        le=200,
    )

    max_tokens: int = Field(
        default=256,
        ge=1,
        le=2048,
    )

    stream: bool = False


class ChatRequest(BaseModel):

    message: str

    session_id: str | None = None

    system_prompt: str = (
        "You are a helpful coding and software engineering assistant."
    )

    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
    )

    top_p: float = Field(
        default=0.9,
        gt=0.0,
        le=1.0,
    )

    top_k: int = Field(
        default=40,
        ge=0,
        le=200,
    )

    max_tokens: int = Field(
        default=256,
        ge=1,
        le=2048,
    )

    stream: bool = False


# ---------------------------------------------------------
# ROOT
# ---------------------------------------------------------

@app.get("/")
def root():

    return {
        "status": "running",
        "service": "Local Fine-Tuned LLM API",
        "model": "Qwen2.5-1.5B-Instruct Fine-Tuned GGUF Q4_0",
    }


# ---------------------------------------------------------
# POST /generate
# ---------------------------------------------------------

@app.post("/generate")
def generate(request: GenerateRequest):

    request_id = str(uuid.uuid4())

    logger.info(
        "[%s] /generate request received",
        request_id,
    )

    messages = [
        {
            "role": "system",
            "content": request.system_prompt,
        },
        {
            "role": "user",
            "content": request.prompt,
        },
    ]

    if request.stream:

        generator = stream_chat_completion(
            messages=messages,
            temperature=request.temperature,
            top_p=request.top_p,
            top_k=request.top_k,
            max_tokens=request.max_tokens,
        )

        return StreamingResponse(
            generator,
            media_type="text/plain",
            headers={
                "X-Request-ID": request_id
            },
        )

    output = chat_completion(
        messages=messages,
        temperature=request.temperature,
        top_p=request.top_p,
        top_k=request.top_k,
        max_tokens=request.max_tokens,
    )

    logger.info(
        "[%s] generation completed",
        request_id,
    )

    return {
        "request_id": request_id,
        "response": output,
    }


# ---------------------------------------------------------
# POST /chat
# ---------------------------------------------------------

@app.post("/chat")
def chat(request: ChatRequest):

    request_id = str(uuid.uuid4())

    session_id = (
        request.session_id
        if request.session_id
        else str(uuid.uuid4())
    )

    logger.info(
        "[%s] /chat | session=%s",
        request_id,
        session_id,
    )

    history = chat_sessions.setdefault(
        session_id,
        []
    )

    messages = [
        {
            "role": "system",
            "content": request.system_prompt,
        }
    ]

    messages.extend(history)

    messages.append(
        {
            "role": "user",
            "content": request.message,
        }
    )

    # -----------------------------------------------------
    # STREAMING CHAT
    # -----------------------------------------------------

    if request.stream:

        def generate_stream():

            collected_response = ""

            for token in stream_chat_completion(
                messages=messages,
                temperature=request.temperature,
                top_p=request.top_p,
                top_k=request.top_k,
                max_tokens=request.max_tokens,
            ):

                collected_response += token

                yield token

            history.append(
                {
                    "role": "user",
                    "content": request.message,
                }
            )

            history.append(
                {
                    "role": "assistant",
                    "content": collected_response,
                }
            )

        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "X-Request-ID": request_id,
                "X-Session-ID": session_id,
            },
        )

    # -----------------------------------------------------
    # NORMAL CHAT
    # -----------------------------------------------------

    response = chat_completion(
        messages=messages,
        temperature=request.temperature,
        top_p=request.top_p,
        top_k=request.top_k,
        max_tokens=request.max_tokens,
    )

    history.append(
        {
            "role": "user",
            "content": request.message,
        }
    )

    history.append(
        {
            "role": "assistant",
            "content": response,
        }
    )

    return {
        "request_id": request_id,
        "session_id": session_id,
        "response": response,
    }