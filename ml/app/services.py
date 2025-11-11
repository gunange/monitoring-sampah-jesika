from ml.controllers.frame_controller import FrameController
from ml.controllers.dataset_controller import DatasetController

from .camera import CameraController




# Singleton Service
camera_service = CameraController()
frame_controller = FrameController()
dataset_controller = DatasetController()