import requests
from typing import Any, Dict, Optional, Union
from ml.app.config import get_str

# Base URL dibaca dari .env (ml/.env → API_BASE)
_API_BASE: str = get_str("API_BASE", "")

def set_api_base(url: str) -> None:
    """
    Override base URL secara runtime jika diperlukan.
    """
    global _API_BASE
    _API_BASE = url or ""

def get_api_base() -> str:
    """
    Kembalikan base URL saat ini.
    """
    return _API_BASE

def _build_url(path: str) -> str:
    """
    Sambungkan base URL dengan path. Menjaga agar tidak ada double slash.
    """
    base = _API_BASE.strip()
    if not base:
        raise ValueError("API_BASE tidak terdefinisi. Pastikan ml/.env berisi API_BASE.")
    return f"{base.rstrip('/')}/{str(path).lstrip('/')}"

def get(
    path: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: Union[int, float] = 10,
) -> requests.Response:
    """
    GET ke {API_BASE}/{path}
    """
    url = _build_url(path)
    return requests.get(url, params=params, headers=headers, timeout=timeout)

def post(
    path: str,
    json: Optional[Dict[str, Any]] = None,
    data: Optional[Union[Dict[str, Any], str, bytes]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: Union[int, float] = 10,
) -> requests.Response:
    """
    POST ke {API_BASE}/{path}
    - gunakan argumen 'json' untuk body JSON
    - gunakan argumen 'data' untuk form-data atau raw payload
    """
    url = _build_url(path)
    return requests.post(url, json=json, data=data, headers=headers, timeout=timeout)

def delete(
    path: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: Union[int, float] = 10,
) -> requests.Response:
    """
    DELETE ke {API_BASE}/{path}
    """
    url = _build_url(path)
    return requests.delete(url, params=params, headers=headers, timeout=timeout)

def patch(
    path: str,
    json: Optional[Dict[str, Any]] = None,
    data: Optional[Union[Dict[str, Any], str, bytes]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: Union[int, float] = 10,
) -> requests.Response:
    """
    PATCH ke {API_BASE}/{path}
    - gunakan argumen 'json' untuk body JSON
    - gunakan argumen 'data' untuk form-data atau raw payload
    """
    url = _build_url(path)
    return requests.patch(url, json=json, data=data, headers=headers, timeout=timeout)