from ml.controllers.frame_controller import FrameController
from ml.controllers.dataset_controller import DatasetController
from ml.controllers.mahine_learning_controller import MachineLearningController

from ml.controllers.camera_controller import CameraController
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
machine_learning_controller = MachineLearningController()

# Singleton Controller
knn_service = KNNService()