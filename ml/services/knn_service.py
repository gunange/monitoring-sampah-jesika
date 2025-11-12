# ml/app/services/knn_service.py
# module imports
from typing import List, Dict, Any, Optional, Callable
import asyncio
from ml.app.logging import logger
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
import joblib


class KNNService:
    def __init__(self):
        from ml.app.config import get_int

        self.k = get_int("KNN_NEIGHBORS", 5)
        self.pipeline: Optional[Pipeline] = None
        self.encoder: Optional[LabelEncoder] = None
        self.last_pred: Optional[str] = None

        # Tambahan untuk loop prediksi realtime
        self._running = False
        self._task: Optional["asyncio.Task"] = None
        self._interval = get_int("MACHINE_INTERVAL", 3)
        self._on_result: Optional[Callable[[str, Dict[str, Any]], None]] = None

    def fit_from_records(self, records: List[Dict[str, Any]]):
        from .main_service import FEATURE_COLS

        if not records:
            raise ValueError("Dataset kosong.")

        df = pd.DataFrame(records)
        X = df[FEATURE_COLS].values
        y_raw = df["label"].astype(str).values

        self.encoder = LabelEncoder().fit(y_raw)
        y = self.encoder.transform(y_raw)

        self.pipeline = Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                (
                    "knn",
                    KNeighborsClassifier(
                        n_neighbors=self.k,
                        weights="distance",  # biasanya lebih stabil utk data real
                        metric="euclidean",
                    ),
                ),
            ]
        )
        self.pipeline.fit(X, y)

    def predict_from_feature_map(self, features: Dict[str, float]) -> str:
        from .main_service import FEATURE_COLS
        if self.pipeline is None or self.encoder is None:
            raise RuntimeError("Model belum dilatih.")
        x = np.array([[features[c] for c in FEATURE_COLS]], dtype=float)
        y_pred = self.pipeline.predict(x)[0]
        label = self.encoder.inverse_transform([y_pred])[0]
        self.last_pred = label
        return label

    def save(self, path_model: str, path_encoder: str):
        if self.pipeline is None or self.encoder is None:
            raise RuntimeError("Belum ada model/encoder.")
        joblib.dump(self.pipeline, path_model)
        joblib.dump(self.encoder, path_encoder)

    def load(self, path_model: str, path_encoder: str):
        self.pipeline = joblib.load(path_model)
        self.encoder = joblib.load(path_encoder)

    async def _loop(self):
        from ml.services.main_service import frame_controller, knn_controller

        while self._running:
            try:
                result = frame_controller.capture_features(
                    label=None, return_image=False
                )
                if result.get("ok"):
                    features = result["features"]
                    pred = self.predict_from_feature_map(features)
                    self.last_pred = pred
                    knn_controller.send_info_to_api(pred, result)
                    if self._on_result:
                        self._on_result(pred, result)
                else:
                    logger.warning("Capture not ok: %s", result.get("reason"))
            except Exception as e:
                logger.error("KNN loop error: %s", e)
            await asyncio.sleep(self._interval)

    def start(self, on_result: Optional[Callable[[str, Dict[str, Any]], None]] = None):
        from ml.app.config import get_int

        if self.pipeline is None:
            raise RuntimeError("Model belum dilatih. Panggil fit_from_records() dulu.")
        if self._running:
            logger.info("KNN service already running; start ignored")
            return
        self._interval = get_int("MACHINE_INTERVAL", 2)
        self._on_result = on_result
        self._running = True
        self._task = asyncio.create_task(self._loop())

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except:
                pass
            self._task = None
            logger.info("KNN service stopped")


