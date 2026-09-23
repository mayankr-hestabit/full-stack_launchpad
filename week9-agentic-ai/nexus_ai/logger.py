import logging
from datetime import datetime

from nexus_ai.config import LOG_DIR


def create_logger():
    """
    Create a logger for NEXUS AI execution tracing.
    """

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    log_file = (
        LOG_DIR
        / f"nexus_{timestamp}.log"
    )

    logger = logging.getLogger(
        "nexus_ai"
    )

    logger.setLevel(
        logging.INFO
    )

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    file_handler = logging.FileHandler(
        log_file,
        encoding="utf-8",
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler.setFormatter(
        formatter
    )

    logger.addHandler(
        file_handler
    )

    return logger