import cv2
import numpy as np
from pathlib import Path
from ml.app.utils import get_logger

logger = get_logger("image-features", Path("ml/logs/ml_service.log"))

def extract_features_bgr(img):
    try:
        h, w = img.shape[:2]
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        hist_h = cv2.calcHist([hsv], [0], None, [16], [0, 180]).flatten()
        hist_s = cv2.calcHist([hsv], [1], None, [16], [0, 256]).flatten()
        hist_v = cv2.calcHist([hsv], [2], None, [16], [0, 256]).flatten()
        for hist in (hist_h, hist_s, hist_v):
            s = float(hist.sum()) or 1.0
            hist /= s

        h_mean = float(hsv[:, :, 0].mean()); h_std = float(hsv[:, :, 0].std())
        s_mean = float(hsv[:, :, 1].mean()); s_std = float(hsv[:, :, 1].std())
        v_mean = float(hsv[:, :, 2].mean()); v_std = float(hsv[:, :, 2].std())

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        lap = cv2.Laplacian(gray, cv2.CV_64F)
        lap_var = float(lap.var())

        edges = cv2.Canny(img, 100, 200)
        edge_ratio = float(np.count_nonzero(edges)) / float(h * w) if (h * w) > 0 else 0.0

        _, thr = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        cnts = cv2.findContours(thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = cnts[0] if len(cnts) == 2 else cnts[1]
        max_area = float(max((cv2.contourArea(c) for c in contours), default=0.0))
        shape_area_ratio = (max_area / float(h * w)) if (h * w) > 0 else 0.0

        return {
            "width": int(w),
            "height": int(h),
            "color_hist_h": hist_h.tolist(),
            "color_hist_s": hist_s.tolist(),
            "color_hist_v": hist_v.tolist(),
            "h_mean": h_mean, "h_std": h_std,
            "s_mean": s_mean, "s_std": s_std,
            "v_mean": v_mean, "v_std": v_std,
            "laplacian_var": lap_var,
            "edge_ratio": edge_ratio,
            "shape_area_ratio": shape_area_ratio,
        }
    except Exception as e:
        logger.error(f"extract_features_bgr error: {e}")
        return None