from pathlib import Path

from .config import get_int, get_str
from .utils import get_logger
from .camera import CameraController




# Singleton Service
logger = get_logger("ml-service", Path(get_str("LOGGING_SERVICE", "ml/logs/ml_service.log" )))
camera_service = CameraController()