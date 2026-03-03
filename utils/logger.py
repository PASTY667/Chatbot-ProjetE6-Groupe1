import logging as log
from pathlib import Path

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

    log.basicConfig(
        filename=log_file,
        level=log.INFO,
        filemode="w",
        format="%(asctime)s - %(levelname)s - %(message)s",
        force=True
    )

    log.info("logging started")
