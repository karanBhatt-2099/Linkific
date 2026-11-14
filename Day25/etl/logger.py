import logging
import sys

from etl import config


def get_logger(name):
    """Logger that writes to the console and to logs/etl.log."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    logger.addHandler(console)

    try:
        config.LOG_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(config.LOG_DIR / "etl.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError:
        logger.warning("Could not open log file, logging to console only")

    return logger
