from ml.controllers.frame_controller import FrameController
from ml.controllers.dataset_controller import DatasetController
from ml.controllers.camera_controller import CameraController
from ml.controllers.knn_controller import KNNController
from ml.services.machine_service import MachineService

from .knn_service import KNNService

FEATURE_COLS = [
    "h_mean",
    "h_std",
    "s_mean",
    "s_std",
    "v_mean",
    "v_std",
    "laplacian_var",
    "edge_ratio",
    "shape_area_ratio",
]

# Singleton Controller
camera_controller = CameraController()
frame_controller = FrameController()
dataset_controller = DatasetController()
knn_controller = KNNController()

# Singleton Service
knn_service = KNNService()
machine_service = MachineService()