import os
from pathlib import Path
from typing import Optional

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"

def load_env(env_path: Path = ENV_PATH) -> None:
    if not env_path.exists():
        return
    with env_path.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            os.environ.setdefault(key, value)

load_env()

def get_str(name: str, default: Optional[str] = None) -> str:
    return os.getenv(name, default or "")

def get_int(name: str, default: int = 0) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default

def get_bool(name: str, default: bool = False) -> bool:
    """
    Baca boolean dari .env: true/false, 1/0, yes/no (case-insensitive).
    """
    val = os.getenv(name, None)
    if val is None:
        return default
    s = str(val).strip().lower()
    if s in ("1", "true", "yes", "y", "on"):
        return True
    if s in ("0", "false", "no", "n", "off"):
        return False
    return default