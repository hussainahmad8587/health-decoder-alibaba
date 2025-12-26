from __future__ import annotations
import cv2
import numpy as np
from .roi import ROIBoxes

def draw_overlay(img_bgr: np.ndarray, rois: ROIBoxes) -> np.ndarray:
    out = img_bgr.copy()
    def box(b, color, label):
        x1,y1,x2,y2 = b
        cv2.rectangle(out, (x1,y1), (x2,y2), color, 2)
        cv2.putText(out, label, (x1, max(18,y1-6)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    box(rois.face, (0,255,255), "Face")
    box(rois.eyes, (255,0,0), "Eyes")
    box(rois.lips, (0,0,255), "Lips")
    box(rois.skin, (0,255,0), "Skin")
    return out
