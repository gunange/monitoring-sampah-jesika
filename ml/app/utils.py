import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def timestamp_str() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")
