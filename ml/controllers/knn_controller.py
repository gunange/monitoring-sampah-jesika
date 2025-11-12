from ml.app.logging import logger


class KNNController:
    def __init__(self):
        self.api_path = "machine-learning/alert"

    def send_to_api(self, pred, result) -> None:
        from ml.lib.api_request_lib import post
        post(self.api_path, {"pred": pred, "result": result})
