import json
import subprocess
import time

import httpx

from deploy.config import (
    GGUF_MODEL_PATH,
    LLAMA_SERVER_BIN,
    LLAMA_HOST,
    LLAMA_PORT,
    LLAMA_BASE_URL,
    CONTEXT_SIZE,
    GPU_LAYERS,
)


_llama_process = None


# ---------------------------------------------------------
# CHECK LLAMA SERVER HEALTH
# ---------------------------------------------------------

def is_server_running():
    try:
        response = httpx.get(
            f"{LLAMA_BASE_URL}/health",
            timeout=2.0,
        )

        return response.status_code == 200

    except Exception:
        return False


# ---------------------------------------------------------
# START LLAMA SERVER
# ---------------------------------------------------------

def start_llama_server():
    global _llama_process

    if is_server_running():
        print("llama-server is already running.")
        return

    if not GGUF_MODEL_PATH.exists():
        raise FileNotFoundError(
            f"GGUF model not found: {GGUF_MODEL_PATH}"
        )

    if not LLAMA_SERVER_BIN.exists():
        raise FileNotFoundError(
            f"llama-server not found: {LLAMA_SERVER_BIN}"
        )

    print("GGUF model found:")
    print(GGUF_MODEL_PATH)

    print("llama-server binary found:")
    print(LLAMA_SERVER_BIN)

    command = [
        str(LLAMA_SERVER_BIN),

        "-m",
        str(GGUF_MODEL_PATH),

        "-c",
        str(CONTEXT_SIZE),

        "-ngl",
        str(GPU_LAYERS),

        "--host",
        LLAMA_HOST,

        "--port",
        str(LLAMA_PORT),
    ]

    print("\nStarting llama-server...")
    print("Waiting for model to load...\n")

    # Do NOT hide llama.cpp logs.
    # They are useful for debugging inside Docker.
    _llama_process = subprocess.Popen(command)

    # Give model up to 5 minutes to load.
    for second in range(300):

        # Detect if llama-server crashed.
        if _llama_process.poll() is not None:
            raise RuntimeError(
                "llama-server stopped unexpectedly while loading the model."
            )

        if is_server_running():
            print(
                f"\nllama-server ready after approximately "
                f"{second + 1} seconds."
            )
            return

        if (second + 1) % 10 == 0:
            print(
                f"Still loading model... "
                f"{second + 1} seconds"
            )

        time.sleep(1)

    raise RuntimeError(
        "llama-server failed to become ready within 300 seconds."
    )


# ---------------------------------------------------------
# STOP LLAMA SERVER
# ---------------------------------------------------------

def stop_llama_server():
    global _llama_process

    if _llama_process is not None:

        print("Stopping llama-server...")

        _llama_process.terminate()

        try:
            _llama_process.wait(timeout=10)

        except subprocess.TimeoutExpired:
            _llama_process.kill()

        _llama_process = None


# ---------------------------------------------------------
# NORMAL CHAT COMPLETION
# ---------------------------------------------------------

def chat_completion(
    messages,
    temperature=0.7,
    top_p=0.9,
    top_k=40,
    max_tokens=256,
):

    payload = {
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "max_tokens": max_tokens,
        "stream": False,
    }

    response = httpx.post(
        f"{LLAMA_BASE_URL}/v1/chat/completions",
        json=payload,
        timeout=300.0,
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]


# ---------------------------------------------------------
# STREAMING CHAT COMPLETION
# ---------------------------------------------------------

def stream_chat_completion(
    messages,
    temperature=0.7,
    top_p=0.9,
    top_k=40,
    max_tokens=256,
):

    payload = {
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "max_tokens": max_tokens,
        "stream": True,
    }

    with httpx.stream(
        "POST",
        f"{LLAMA_BASE_URL}/v1/chat/completions",
        json=payload,
        timeout=None,
    ) as response:

        response.raise_for_status()

        for line in response.iter_lines():

            if not line:
                continue

            if not line.startswith("data:"):
                continue

            data = line[5:].strip()

            if data == "[DONE]":
                break

            try:
                event = json.loads(data)

                delta = (
                    event
                    .get("choices", [{}])[0]
                    .get("delta", {})
                    .get("content", "")
                )

                if delta:
                    yield delta

            except json.JSONDecodeError:
                continue