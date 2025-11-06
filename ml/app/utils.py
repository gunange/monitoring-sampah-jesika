import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def timestamp_str() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")

def get_logger(name: str, log_file: Path) -> logging.Logger:
    ensure_dir(log_file.parent)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    return logger