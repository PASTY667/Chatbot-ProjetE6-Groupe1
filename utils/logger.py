import logging as log
from pathlib import Path
import os

def get_logger():
    """
    Initialize application logging to the shared logs directory.

    This helper creates the `logs/` folder at the project root if missing
    and configures the Python logger to write the main log file used by the
    API, ingestion pipeline, and vector store components.

    :return: None
    :rtype: None
    """
    BASE_DIR = Path(__file__).resolve().parents[1]
    LOG_DIR = BASE_DIR / "logs"
    LOG_DIR.mkdir(exist_ok=True)

    log_file = LOG_DIR / "mainLog.log"

    root = log.getLogger()
    if root.handlers:
        return

    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(log, level_name, log.INFO)

    log.basicConfig(
        filename=log_file,
        level=level,
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    log.info("logging started")
