from __future__ import annotations
import cv2
import numpy as np

from ..config import get_settings
from ..domain.models import AnalysisResult, ExplainResult, ScoreResult
from ..pipeline.quality import compute_quality
from ..pipeline.roi import derive_rois
from ..pipeline.explain import draw_overlay
from ..services.vision_service import VisionService

from ..domain.scoring import risk_from_rois, wellness_score

def analyze_image(img_bgr: np.ndarray) -> AnalysisResult:
    quality = compute_quality(img_bgr)
    # 🚫 Hard stop for very blurry images
    if quality.blur_laplacian_var < 25:
        return AnalysisResult(
            ok=False,
            message="Image is too blurry for reliable analysis. Please hold the camera steady.",
            quality=quality,
        )

    settings = get_settings()
    vision = VisionService.from_settings(settings)

    face_box = vision.detect_face(img_bgr)
    partial_face = False

    if face_box is None:
        h, w = img_bgr.shape[:2]

        # Fallback: assume partial face if image is reasonably sized
        if h > 200 and w > 200:
            face_box = (
                int(0.25 * w),
                int(0.15 * h),
                int(0.75 * w),
                int(0.85 * h),
            )
            partial_face = True
        else:
            return AnalysisResult(
                ok=False,
                message=(
                    "No full face detected. "
                    "Please ensure your eyes, nose, and mouth are fully visible."
                ),
                quality=quality,
            )

    rois = derive_rois(img_bgr, face_box)

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    def crop(b): 
        x1,y1,x2,y2 = b
        return gray[y1:y2, x1:x2]

    risk = risk_from_rois(crop(rois.eyes), crop(rois.lips), crop(rois.skin))
    score, cat, conf, reasons = wellness_score(risk)
    if partial_face:
        reasons.append(
            "Analysis is based on a partial face. Results may be less reliable."
        )

    overlay = draw_overlay(img_bgr, rois)

    return AnalysisResult(
        ok=True,
        message="OK",
        quality=quality,
        score=ScoreResult(
            score=score,
            category=cat,
            confidence=conf,
            reasons=reasons,
            risk_components=risk,
        ),
        explain=ExplainResult(overlay_bgr=overlay),
    )
