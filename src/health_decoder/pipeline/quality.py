from __future__ import annotations
import cv2
import numpy as np
from ..domain.models import QualityResult

def compute_quality(img_bgr: np.ndarray) -> QualityResult:
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    brightness = float(gray.mean())
    lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

    notes = []
    if brightness < 55:
        notes.append("Too dark (low lighting).")
    if lap_var < 45:
        notes.append("Blurry image (low sharpness).")
    if not notes:
        notes.append("Capture quality looks acceptable.")

    return QualityResult(
        brightness_mean=brightness,
        blur_laplacian_var=lap_var,
        notes=notes,
    )
