import logging as log
from pathlib import Path

def get_logger():
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