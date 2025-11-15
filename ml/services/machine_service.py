class MachineService:
    def __init__(self):
        self.name = "Machine Learning"
        self.running = False
        self.camera = None
        self.knn = None
        self.dataset = 0
        self.camera_list = []
        self.knn_neighbors = None
        self.machine_interval = None

        pass

    def startup(self):
        from ml.services.main_service import (
            camera_controller,
            knn_service,
            dataset_controller,
        )
        from ml.lib.camera import get_camera_list



        dataset_controller.initSetDataFromDb()

        self.dataset = len(dataset_controller.dataset)
        self.camera_list = get_camera_list()
        self.knn = knn_service._running
        self.camera = camera_controller.get_cap() is not None
        self.knn_neighbors = knn_service.k
        self.machine_interval = knn_service._interval


    @property
    def status(self):
        self.running = bool(self.camera) and bool(self.knn)

        return {
            "name": "Machine Learning",
            "running": self.running,
            "detail": {
                "camera": self.camera,
                "knn": self.knn,
                "knn-k-value": self.knn_neighbors,
                "machine-interval": self.machine_interval,
                "dataset": self.dataset,
                "camera-list": self.camera_list,
            },
        }
    def load_status(self):
        from ml.services.main_service import (
            camera_controller,
            knn_service,
            dataset_controller,
        )
        self.knn = knn_service._running
        self.camera = camera_controller.get_cap() is not None
        self.dataset = len(dataset_controller.dataset)