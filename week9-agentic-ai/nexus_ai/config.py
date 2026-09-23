from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = PROJECT_ROOT / "logs"
DATA_DIR = PROJECT_ROOT / "data"
MEMORY_DIR = PROJECT_ROOT / "memory"

LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

MAX_AGENT_RETRIES = 3
MAX_IMPROVEMENT_LOOPS = 2
SESSION_MEMORY_SIZE = 10
MEMORY_TOP_K = 3
MEMORY_RELEVANCE_THRESHOLD = 0.65