import os
from pathlib import Path


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

GGUF_MODEL_PATH = Path(
    os.getenv(
        "GGUF_MODEL_PATH",
        PROJECT_ROOT / "quantized" / "model.gguf"
    )
)

LLAMA_SERVER_BIN = Path(
    os.getenv(
        "LLAMA_SERVER_BIN",
        Path.home() / "llama.cpp" / "build" / "bin" / "llama-server"
    )
)


# ---------------------------------------------------------
# LLAMA.CPP SERVER CONFIG
# ---------------------------------------------------------

LLAMA_HOST = "127.0.0.1"
LLAMA_PORT = 8081

LLAMA_BASE_URL = f"http://{LLAMA_HOST}:{LLAMA_PORT}"

CONTEXT_SIZE = 2048

GPU_LAYERS = 0


# ---------------------------------------------------------
# FASTAPI CONFIG
# ---------------------------------------------------------

API_HOST = "0.0.0.0"
API_PORT = 8000


# ---------------------------------------------------------
# DEFAULT GENERATION SETTINGS
# ---------------------------------------------------------

DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.9
DEFAULT_TOP_K = 40
DEFAULT_MAX_TOKENS = 256