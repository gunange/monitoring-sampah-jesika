import cv2
import numpy as np
from pathlib import Path
from ml.app.utils import get_logger

logger = get_logger("image-features", Path("ml/logs/ml_service.log"))

def extract_features_bgr(img):
    try:
        h, w = img.shape[:2]
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)     

        h_mean = float(hsv[:, :, 0].mean()); h_std = float(hsv[:, :, 0].std())
        s_mean = float(hsv[:, :, 1].mean()); s_std = float(hsv[:, :, 1].std())
        v_mean = float(hsv[:, :, 2].mean()); v_std = float(hsv[:, :, 2].std())

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        lap = cv2.Laplacian(gray, cv2.CV_64F)
        lap_var = float(lap.var())

        # SELARASKAN DENGAN KNN: gunakan Canny pada grayscale
        edges = cv2.Canny(gray, 100, 200)
        edge_ratio = float(np.count_nonzero(edges)) / float(h * w) if (h * w) > 0 else 0.0

        _, thr = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        cnts = cv2.findContours(thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = cnts[0] if len(cnts) == 2 else cnts[1]
        max_area = float(max((cv2.contourArea(c) for c in contours), default=0.0))
        shape_area_ratio = (max_area / float(h * w)) if (h * w) > 0 else 0.0

        return {
            "width": int(w),
            "height": int(h),
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

def hsv_hist_and_stats_bgr(img_bgr):
    try:
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        # Histogram: H=32, S=16, V=8
        h_hist = cv2.calcHist([hsv], [0], None, [32], [0, 180]).flatten().astype(np.float32)
        s_hist = cv2.calcHist([hsv], [1], None, [16], [0, 256]).flatten().astype(np.float32)
        v_hist = cv2.calcHist([hsv], [2], None, [8],  [0, 256]).flatten().astype(np.float32)
        # L1 normalization
        for hist in (h_hist, s_hist, v_hist):
            s = float(hist.sum()) or 1.0
            hist /= s
        # Stats (mean/std)
        h_mean = float(hsv[:, :, 0].mean()); h_std = float(hsv[:, :, 0].std())
        s_mean = float(hsv[:, :, 1].mean()); s_std = float(hsv[:, :, 1].std())
        v_mean = float(hsv[:, :, 2].mean()); v_std = float(hsv[:, :, 2].std())
        return {
            "histH32": h_hist.tolist(),
            "histS16": s_hist.tolist(),
            "histV8": v_hist.tolist(),
            "H_mean": h_mean, "H_std": h_std,
            "S_mean": s_mean, "S_std": s_std,
            "V_mean": v_mean, "V_std": v_std,
        }
    except Exception as e:
        logger.error(f"hsv_hist_and_stats_bgr error: {e}")
        return None

def lbp_uniform_hist(gray, P=8, R=1):
    # Implementasi LBP uniform (8,1) menghasilkan 59 bin
    try:
        gray = gray.astype(np.uint8)
        h, w = gray.shape
        # padding radius
        pad = R
        g = np.pad(gray, pad_width=pad, mode="edge")
        # sampling koordinat tetangga
        offsets = [(0, R), (R/np.sqrt(2), R/np.sqrt(2)), (R, 0), (R/np.sqrt(2), -R/np.sqrt(2)),
                   (0, -R), (-R/np.sqrt(2), -R/np.sqrt(2)), (-R, 0), (-R/np.sqrt(2), R/np.sqrt(2))]
        offsets = [(int(round(dy)), int(round(dx))) for dy, dx in offsets]
        center = g[pad:pad+h, pad:pad+w].astype(np.float32)
        codes = np.zeros((h, w), dtype=np.uint8)
        # bangun kode LBP
        for i, (dy, dx) in enumerate(offsets):
            nb = g[pad+dy:pad+dy+h, pad+dx:pad+dx+w].astype(np.float32)
            bit = (nb >= center).astype(np.uint8)
            codes |= (bit << i)
        # cek uniform: jumlah transisi 0->1 pada pola melingkar <= 2
        def transitions(x):
            # 8-bit circular
            b = [(x >> i) & 1 for i in range(P)]
            b.append(b[0])
            return sum(b[i] != b[i+1] for i in range(P))
        # map code ke bin uniform (0..58), non-uniform -> bin 58
        bins = np.zeros(59, dtype=np.float32)
        # precompute lookup untuk semua 0..255
        lookup = np.empty(256, dtype=np.uint8)
        uni_idx = {}
        idx = 0
        for code in range(256):
            t = transitions(code)
            ones = bin(code).count("1")
            if t <= 2:
                key = ones  # untuk P=8, bin ditentukan oleh jumlah 1
                if key not in uni_idx:
                    uni_idx[key] = idx
                    idx += 1
                lookup[code] = uni_idx[key]
            else:
                lookup[code] = 58  # non-uniform bin terakhir
        flat_codes = codes.flatten()
        for c in flat_codes:
            bins[lookup[int(c)]] += 1.0
        # L1 normalize
        s = float(bins.sum()) or 1.0
        bins /= s
        return bins.tolist()
    except Exception as e:
        logger.error(f"lbp_uniform_hist error: {e}")
        return None

def edge_density(gray):
    try:
        edges = cv2.Canny(gray, 100, 200)
        return float(np.count_nonzero(edges)) / float(edges.size)
    except Exception as e:
        logger.error(f"edge_density error: {e}")
        return 0.0

def contour_features_from_mask(mask):
    try:
        cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = cnts[0] if len(cnts) == 2 else cnts[1]
        if not contours:
            return {"area_ratio": 0.0, "solidity": 0.0, "hu7": [0.0]*7}
        # ambil kontur terbesar
        c = max(contours, key=cv2.contourArea)
        area = float(cv2.contourArea(c))
        hull = cv2.convexHull(c)
        hull_area = float(cv2.contourArea(hull)) or 1.0
        solidity = float(area / hull_area)
        h, w = mask.shape[:2]
        roi_area = float(h * w) or 1.0
        area_ratio = float(area / roi_area)
        hu = cv2.HuMoments(cv2.moments(c)).flatten().tolist()
        return {"area_ratio": area_ratio, "solidity": solidity, "hu7": [float(x) for x in hu[:7]]}
    except Exception as e:
        logger.error(f"contour_features_from_mask error: {e}")
        return {"area_ratio": 0.0, "solidity": 0.0, "hu7": [0.0]*7}