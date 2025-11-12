from ml.app.logging import logger


class KNNController:
    def __init__(self):
        self.api_path = "machine-learning"

    def send_info_to_api(self, pred, result) -> None:
        from ml.lib.api_request_lib import post
        post(self.api_path + "/info", {"pred": pred, "result": result})

    def send_alert_to_api(self, pred, result) -> None:
        from ml.lib.api_request_lib import post
        post(self.api_path + "/alert", {"pred": pred, "result": result})
