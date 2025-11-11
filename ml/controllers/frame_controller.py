import cv2
import json
import math
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from ml.app.config import get_int, get_str


class FrameController:
    def __init__(self):
        # Lazy import untuk util agar aman dari circular import

        from ml.app.config import get_str

        # Tetapkan root_dir = folder data (ml/data) dan pastikan ada
        self.root_dir = Path(__file__).resolve().parents[1] / get_str(
            "DETECT_SAVE_DIR", "data"
        )

        # Folder penyimpanan gambar: root_dir/detections
        self.detections_dir = self.root_dir / "detections"

        # File dataset tunggal (list of objects): root_dir/dataset.json
        self.dataset_json = self.root_dir / "dataset.json"

        # Versi pipeline untuk tracking
        self.preprocess_version = 1
        self.feature_version = 1

        # Default parameter preprocessing
        self.clahe_clip_limit = 2.0
        self.clahe_tile_grid = (8, 8)
        self.gaussian_kernel = (3, 3)
        self.canny_default = (50, 150)

    def _get_default_roi(self, width: int, height: int) -> Tuple[int, int, int, int]:
        """Ambil ROI default dari .env; jika w/h <= 0 → full frame."""
        x = get_int("ROI_X", 0)
        y = get_int("ROI_Y", 0)
        w = get_int("ROI_W", 0)
        h = get_int("ROI_H", 0)
        if w <= 0 or h <= 0:
            return 0, 0, width, height
        return self._roi_bounds(width, height, (x, y, w, h))

    def _roi_bounds(
        self, width: int, height: int, roi: Optional[Tuple[int, int, int, int]]
    ) -> Tuple[int, int, int, int]:
        """Clamp ROI ke dalam batas frame; jika ROI None atau invalid → full frame."""
        if not roi or len(roi) != 4:
            return 0, 0, width, height
        x, y, w, h = roi
        if w <= 0 or h <= 0:
            return 0, 0, width, height
        x = max(0, min(x, width - 1))
        y = max(0, min(y, height - 1))
        w = max(1, min(w, width - x))
        h = max(1, min(h, height - y))
        return x, y, w, h

    def _sanitize_float(self, val: float, default: float = 0.0) -> float:
        """Pastikan bukan NaN/Inf; jika iya ganti default."""
        if val is None or isinstance(val, (float, int)) is False:
            return default
        if math.isnan(val) or math.isinf(val):
            return default
        return float(val)

    def _hsv_stats(
        self, hsv: np.ndarray, mask: Optional[np.ndarray]
    ) -> Dict[str, float]:
        """Hitung statistik HSV. H dihitung secara circular; S/V linear. H:0–179, S/V:0–255."""
        H, S, V = cv2.split(hsv)

        if mask is None:
            valid = V >= 10
        else:
            valid = (mask.astype(bool)) & (V >= 10)

        if not np.any(valid):
            return {
                "h_mean": 0.0,
                "h_std": 0.0,
                "s_mean": 0.0,
                "s_std": 0.0,
                "v_mean": 0.0,
                "v_std": 0.0,
            }

        # Circular stats untuk H
        h_vals = H[valid].astype(np.float64)
        # Konversi ke radian: 0..179 → 0..2π (tiap unit = 2°)
        theta = h_vals * (np.pi / 90.0)
        c = np.cos(theta)
        s = np.sin(theta)
        c_bar = np.mean(c)
        s_bar = np.mean(s)
        # Mean arah
        mean_theta = float(np.arctan2(s_bar, c_bar))
        if mean_theta < 0:
            mean_theta += 2 * np.pi
        # Resultant length
        R = float(np.sqrt(c_bar**2 + s_bar**2))
        # Circular std (radian)
        std_theta = (
            float(np.sqrt(max(0.0, -2.0 * np.log(max(R, 1e-12))))) if R > 0 else 0.0
        )
        # Konversi kembali ke unit H (0..179)
        h_mean_circ = mean_theta / (np.pi / 90.0)
        h_std_circ = std_theta / (np.pi / 90.0)

        # Linear stats untuk S, V
        s_vals = S[valid].astype(np.float64)
        v_vals = V[valid].astype(np.float64)

        s_mean = float(np.mean(s_vals))
        s_std = float(np.std(s_vals, ddof=1) if s_vals.size > 1 else 0.0)
        v_mean = float(np.mean(v_vals))
        v_std = float(np.std(v_vals, ddof=1) if v_vals.size > 1 else 0.0)

        return {
            "h_mean": float(h_mean_circ),
            "h_std": float(h_std_circ),
            "s_mean": s_mean,
            "s_std": s_std,
            "v_mean": v_mean,
            "v_std": v_std,
        }

    def _laplacian_var(self, gray_roi: np.ndarray) -> float:
        """Gaussian blur 3x3 → Laplacian → varians nilai Laplacian (float64, tanpa normalisasi per piksel)."""
        gray_blur = cv2.GaussianBlur(gray_roi, (3, 3), 0)
        lap = cv2.Laplacian(gray_blur, cv2.CV_64F)
        # Varians mentah; boleh pakai varians nilai absolut
        var = float(np.var(np.abs(lap)))
        return var

    def _canny_thresholds(self, gray_roi: np.ndarray) -> Tuple[int, int]:
        """Ambang Canny berbasis median (metode σ ringan) agar adaptif ke kondisi gelap/terang."""
        med = float(np.median(gray_roi))
        lower = int(max(0, 0.66 * med))
        upper = int(min(255, 1.33 * med))
        # fallback minimal
        if upper < 50:
            lower, upper = 50, 150
        return lower, upper

    def _edge_ratio(self, gray_roi: np.ndarray, auto: bool = True) -> float:
        """Proporsi piksel tepi: E/N dari ROI."""
        # Opsional blur ringan agar noise sensor berkurang
        g = cv2.GaussianBlur(gray_roi, (3, 3), 0)
        if auto:
            t1, t2 = self._canny_thresholds(g)
        else:
            t1, t2 = 50, 150
        edges = cv2.Canny(g, t1, t2)
        E = int(np.count_nonzero(edges == 255))
        N = int(edges.size)
        if N <= 0:
            return 0.0
        return float(E) / float(N)

    def _shape_area_ratio_v(self, hsv_roi: np.ndarray, use_clahe: bool) -> float:
        """Pipeline A berbasis brightness V: CLAHE (opsional) → Otsu → morfologi → kontur terbesar / luas ROI."""
        H, S, V = cv2.split(hsv_roi)
        v_proc = V.copy()
        if use_clahe:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            v_proc = clahe.apply(v_proc)

        # Threshold Otsu pada V
        _, bin_img = cv2.threshold(v_proc, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Jika degenerate (full 0 atau full 1)
        unique_vals = np.unique(bin_img)
        if unique_vals.size == 1:
            return 1.0 if unique_vals[0] == 255 else 0.0

        # Morfologi: close kecil lalu open ringan
        kernel = np.ones((3, 3), np.uint8)
        closed = cv2.morphologyEx(bin_img, cv2.MORPH_CLOSE, kernel, iterations=1)
        opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel, iterations=1)

        # Kontur terbesar
        contours, _ = cv2.findContours(
            opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if not contours:
            return 0.0
        areas = [cv2.contourArea(c) for c in contours]
        largest = float(max(areas)) if areas else 0.0
        ROI_area = float(opened.size)
        if ROI_area <= 0:
            return 0.0
        return largest / ROI_area

    def _append_record_daily(self, record: Dict[str, Any]) -> Path:
        """Append ke file harian JSON list of objects: ml/data/logs/dataset-YYYY-MM-DD.json"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        path = self.logs_dir / f"dataset-{date_str}.json"
        data = []
        if path.exists():
            try:
                with path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    if not isinstance(data, list):
                        data = []
            except Exception:
                # Jika rusak, kita reset ke list baru
                data = []
        data.append(record)
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return path

    def _save_image(
        self, frame: np.ndarray, x: int, y: int, w: int, h: int
    ) -> Tuple[str, Path]:
        """
        Simpan gambar (full frame) ke root_dir/detections dan kembalikan:
        - rel_path: 'data/detections/<filename>.jpg'
        - full_path: Path absolut ke file yang disimpan
        """
        # Lazy import logger saat diperlukan
        from ml.app.services import logger

        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{ts}.jpg"
        full_path = self.detections_dir / filename
        try:
            ok = cv2.imwrite(str(full_path), frame)
            if not ok:
                logger.error(f"Gagal cv2.imwrite ke: {full_path}")
        except Exception as e:
            logger.error(f"Gagal simpan gambar: {e}")
        rel_path = str(Path("data") / "detections" / filename)
        return rel_path, full_path

    def _append_dataset_json(self, record: Dict[str, Any]) -> Path:
        """
        Append ke data/dataset.json (list of object). Jika file belum ada atau rusak, buat list baru.
        """
        data = []
        if self.dataset_json.exists():
            try:
                with self.dataset_json.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    if not isinstance(data, list):
                        data = []
            except Exception:
                data = []
        data.append(record)
        with self.dataset_json.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return self.dataset_json

    def capture_features(
        self,
        label: str = "UNKNOW",
        return_image: bool = False,
    ) -> Dict[str, Any]:
        # Lazy import camera_controller & logger agar aman dari circular import
        from ml.app.services import camera_controller, logger
        from ml.app.config import get_int, get_bool

        # Ambil konfigurasi dari .env (bukan dari argumen)
        warmup_frames = max(3, int(get_int("WARMUP_FRAMES", 4)))
        apply_blur_hsv = bool(get_bool("APPLY_BLUR_HSV", False))
        apply_clahe_v = bool(get_bool("APPLY_CLAHE_V", False))
        canny_auto = bool(get_bool("CANNY_AUTO", True))

        cap = camera_controller.get_cap()
        if cap is None:
            camera_controller.start()
            cap = camera_controller.get_cap()
        if cap is None:
            reason = "Kamera gagal start. Periksa izin/availability."
            logger.error(reason)
            return {"ok": False, "reason": reason, "features": None}

        # Warm-up: buang beberapa frame awal
        for _ in range(warmup_frames):
            ok, _ = camera_controller.read_frame()
            if not ok:
                continue

        # Ambil 1 frame terbaru
        ok, frame = camera_controller.read_frame()
        if not ok or frame is None:
            reason = "Gagal membaca frame dari kamera."
            logger.error(reason)
            return {"ok": False, "reason": reason, "features": None}

        height, width = frame.shape[:2]

        # ROI: selalu ambil dari .env (hilangkan argumen ROI)
        x, y, w, h = self._get_default_roi(width, height)

        roi_frame = frame[y : y + h, x : x + w]

        if roi_frame.size == 0:
            logger.warning("ROI keluar batas, fallback ke full frame.")
            x, y, w, h = 0, 0, width, height
            roi_frame = frame

        # Normalisasi & representasi warna
        bgr_roi = roi_frame
        hsv_roi = cv2.cvtColor(bgr_roi, cv2.COLOR_BGR2HSV)
        if apply_blur_hsv:
            hsv_roi = cv2.GaussianBlur(hsv_roi, self.gaussian_kernel, 0)

        hsv_stats = self._hsv_stats(hsv_roi, mask=None)

        # Grayscale untuk Laplacian (proses di float64, var pada |lap|)
        gray_roi_u8 = cv2.cvtColor(bgr_roi, cv2.COLOR_BGR2GRAY)
        gray_roi = gray_roi_u8.astype(np.float64)
        gray_blur = cv2.GaussianBlur(gray_roi, self.gaussian_kernel, 0)
        lap = cv2.Laplacian(gray_blur, cv2.CV_64F)
        lap_var = float(np.var(np.abs(lap)))

        # Edge ratio dan ambang Canny (rekam T1/T2)
        g = cv2.GaussianBlur(gray_roi_u8, self.gaussian_kernel, 0)
        if canny_auto:
            t1, t2 = self._canny_thresholds(g)
        else:
            t1, t2 = self.canny_default
        edges = cv2.Canny(g, t1, t2)
        E = int(np.count_nonzero(edges == 255))
        N = int(edges.size)
        e_ratio = float(E) / float(N) if N > 0 else 0.0

        # Shape area ratio via Otsu di V + morfologi
        s_area_ratio = self._shape_area_ratio_v(hsv_roi, use_clahe=apply_clahe_v)

        def sanitize(v: float, default: float = 0.0) -> float:
            try:
                vv = float(v)
                if math.isnan(vv) or math.isinf(vv):
                    return default
                return vv
            except Exception:
                return default

        def clamp_and_log(name: str, v: float, lo: float, hi: float) -> float:
            vv = sanitize(v)
            clamped = float(min(max(vv, lo), hi))
            if clamped != vv:
                logger.warning(
                    f"Clamp {name}: {vv} -> {clamped} dalam rentang [{lo}, {hi}]"
                )
            return clamped

        # Clamp sesuai rentang
        h_mean = clamp_and_log("h_mean", hsv_stats["h_mean"], 0.0, 179.0)
        h_std = clamp_and_log("h_std", hsv_stats["h_std"], 0.0, 179.0)
        s_mean = clamp_and_log("s_mean", hsv_stats["s_mean"], 0.0, 255.0)
        s_std = clamp_and_log("s_std", hsv_stats["s_std"], 0.0, 255.0)
        v_mean = clamp_and_log("v_mean", hsv_stats["v_mean"], 0.0, 255.0)
        v_std = clamp_and_log("v_std", hsv_stats["v_std"], 0.0, 255.0)
        laplacian_var = sanitize(lap_var)
        edge_ratio = clamp_and_log("edge_ratio", e_ratio, 0.0, 1.0)
        shape_area_ratio = clamp_and_log("shape_area_ratio", s_area_ratio, 0.0, 1.0)

        # Fitur KNN (tanpa width/height)
        features = {
            "h_mean": round(h_mean, 4),
            "h_std": round(h_std, 4),
            "s_mean": round(s_mean, 4),
            "s_std": round(s_std, 4),
            "v_mean": round(v_mean, 4),
            "v_std": round(v_std, 4),
            "laplacian_var": round(laplacian_var, 4),
            "edge_ratio": round(edge_ratio, 4),
            "shape_area_ratio": round(shape_area_ratio, 4),
        }

        if get_bool("DATASET_SAVE_LOG"):
            from ml.app.utils import ensure_dir

            # Pastikan direktori tersedia hanya saat akan dipakai
            ensure_dir(self.root_dir)
            ensure_dir(self.detections_dir)

            # Simpan gambar ke data/detections
            self._save_image(frame, x, y, w, h)
            # Append ke data/dataset.json (list of objects)
            record_dataset = {
                "label": label,
                "frame": {"width": width, "height": height},
                "roi": {"x": x, "y": y, "w": w, "h": h},
                "features": features,
            }
            self._append_dataset_json(record_dataset)
            logger.info(f"Append record dataset ke: {self.dataset_json}")

        result = {
            "ok": True,
            "reason": None,
            "label": label,
            "frame": {"width": width, "height": height},
            "roi": {"x": x, "y": y, "w": w, "h": h},
            "features": features,
        }

        # Opsi kembalikan image (encoded JPEG) jika dibutuhkan internal
        if return_image:
            ok2, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            if ok2:
                result["image_bytes"] = bytes(buf.tobytes())

        return result
