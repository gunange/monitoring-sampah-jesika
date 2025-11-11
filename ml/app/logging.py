import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Optional

from ml.app.config import get_bool
from ml.app.utils import ensure_dir

BASE_DIR = Path(__file__).resolve().parents[1]
LOG_DIR = BASE_DIR / "logs"

def _level_from_env() -> int:
    level_name = (get_str("LOG_LEVEL", "INFO") or "INFO").upper()
    if get_bool("LOG_ERROR", False):
        level_name = "ERROR"
    return getattr(logging, level_name, logging.INFO)

def _app_level_from_env() -> int:
    level_name = (get_str("LOG_LEVEL", "INFO") or "INFO").upper()
    return getattr(logging, level_name, logging.INFO)

def get_logger(name: Optional[str] = "ml") -> logging.Logger:
    ensure_dir(LOG_DIR)

    logger = logging.getLogger(name or "ml")
    # Izinkan semua level; routing ke file dikontrol oleh handler/filter
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # Selalu siapkan formatter
    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(module)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Filter level eksak
    class ExactLevelFilter(logging.Filter):
        def __init__(self, level: int):
            super().__init__()
            self.level = level
        def filter(self, record: logging.LogRecord) -> bool:
            return record.levelno == self.level

    # Baca flag dari env
    use_error = get_bool("LOG_ERROR", False)
    use_info = get_bool("LOG_INFO", False)
    use_debug = get_bool("LOG_DEBUG", False)

    # --- error.log: hanya ERROR/CRITICAL jika diaktifkan ---
    has_error_file = any(
        isinstance(h, TimedRotatingFileHandler) and getattr(h, "baseFilename", "").endswith("error.log")
        for h in logger.handlers
    )
    if use_error and not has_error_file:
        err_handler = TimedRotatingFileHandler(
            (LOG_DIR / "error.log"),
            when="midnight",
            backupCount=14,
            encoding="utf-8",
            utc=False,
        )
        err_handler.setLevel(logging.ERROR)  # tangkap ERROR+
        err_handler.setFormatter(fmt)
        logger.addHandler(err_handler)

    # --- app.log: hanya INFO jika diaktifkan ---
    has_info_file = any(
        isinstance(h, TimedRotatingFileHandler) and getattr(h, "baseFilename", "").endswith("app.log")
        for h in logger.handlers
    )
    if use_info and not has_info_file:
        info_handler = TimedRotatingFileHandler(
            (LOG_DIR / "app.log"),
            when="midnight",
            backupCount=14,
            encoding="utf-8",
            utc=False,
        )
        info_handler.setLevel(logging.INFO)
        info_handler.addFilter(ExactLevelFilter(logging.INFO))  # hanya level INFO
        info_handler.setFormatter(fmt)
        logger.addHandler(info_handler)

    # --- debug.log: hanya DEBUG jika diaktifkan ---
    has_debug_file = any(
        isinstance(h, TimedRotatingFileHandler) and getattr(h, "baseFilename", "").endswith("debug.log")
        for h in logger.handlers
    )
    if use_debug and not has_debug_file:
        dbg_handler = TimedRotatingFileHandler(
            (LOG_DIR / "debug.log"),
            when="midnight",
            backupCount=14,
            encoding="utf-8",
            utc=False,
        )
        dbg_handler.setLevel(logging.DEBUG)
        dbg_handler.addFilter(ExactLevelFilter(logging.DEBUG))  # hanya level DEBUG
        dbg_handler.setFormatter(fmt)
        logger.addHandler(dbg_handler)

    # Tidak ada console handler; semuanya dikendalikan oleh flag di atas
    return logger

# Instance siap pakai
logger = get_logger("ml")

def log_config_summary() -> None:
    # Tulis ringkasan konfigurasi jika ada handler aktif
    try:
        handler_info = []
        for h in logger.handlers:
            handler_info.append({
                "type": type(h).__name__,
                "level": logging.getLevelName(h.level),
                "file": getattr(h, "baseFilename", None),
            })
        # Catat sebagai INFO jika LOG_INFO aktif, jika tidak maka tidak akan keluar.
        logger.info(
            "Logger configured: level=%s, handlers=%s",
            logging.getLevelName(logger.level),
            handler_info,
        )
    except Exception:
        pass