import logging
from pathlib import Path


LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "purchase_assistant.log"


def get_logger(name="purchase_assistant"):
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.FileHandler(LOG_FILE)
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        )
        logger.addHandler(handler)

    return logger
