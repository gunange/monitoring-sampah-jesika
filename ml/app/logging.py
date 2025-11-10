import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Optional

from ml.app.config import get_bool, get_str
from ml.app.utils import ensure_dir

BASE_DIR = Path(__file__).resolve().parents[1]
LOG_DIR = BASE_DIR / "logs"

def _level_from_env() -> int:
    level_name = (get_str("LOG_LEVEL", "INFO") or "INFO").upper()
    if get_bool("LOG_ERROR", False):
        level_name = "ERROR"
    return getattr(logging, level_name, logging.INFO)

def get_logger(name: Optional[str] = "ml") -> logging.Logger:
    ensure_dir(LOG_DIR)

    logger = logging.getLogger(name or "ml")
    logger.setLevel(_level_from_env())
    logger.propagate = False

    # Selalu siapkan formatter
    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(module)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Pastikan hanya ada file handler untuk error.log
    has_error_file = any(
        isinstance(h, TimedRotatingFileHandler) and getattr(h, "baseFilename", "").endswith("error.log")
        for h in logger.handlers
    )
    if not has_error_file:
        err_handler = TimedRotatingFileHandler(
            (LOG_DIR / "error.log"),
            when="midnight",
            backupCount=14,
            encoding="utf-8",
            utc=False,
        )
        err_handler.setLevel(logging.ERROR)
        err_handler.setFormatter(fmt)
        logger.addHandler(err_handler)

    # Hilangkan seluruh StreamHandler jika LOG_CONSOLE=false
    if not get_bool("LOG_CONSOLE", False):
        for h in list(logger.handlers):
            if isinstance(h, logging.StreamHandler) and not isinstance(h, TimedRotatingFileHandler):
                logger.removeHandler(h)
    else:
        # Jika ingin console dan belum ada, tambahkan
        has_console = any(isinstance(h, logging.StreamHandler) and not isinstance(h, TimedRotatingFileHandler)
                          for h in logger.handlers)
        if not has_console:
            console = logging.StreamHandler()
            console.setLevel(_level_from_env())
            console.setFormatter(fmt)
            logger.addHandler(console)

    return logger

# Instance siap pakai
logger = get_logger("ml")