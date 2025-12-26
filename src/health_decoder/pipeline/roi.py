from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass
class ROIBoxes:
    face: tuple[int,int,int,int]
    eyes: tuple[int,int,int,int]
    lips: tuple[int,int,int,int]
    skin: tuple[int,int,int,int]

def clamp_box(x1,y1,x2,y2,w,h):
    x1 = max(0, min(x1, w-1)); x2 = max(0, min(x2, w-1))
    y1 = max(0, min(y1, h-1)); y2 = max(0, min(y2, h-1))
    if x2 <= x1: x2 = min(w-1, x1+1)
    if y2 <= y1: y2 = min(h-1, y1+1)
    return (x1,y1,x2,y2)

def derive_rois(img_bgr: np.ndarray, face_box: tuple[int,int,int,int]) -> ROIBoxes:
    h, w = img_bgr.shape[:2]
    x1,y1,x2,y2 = face_box
    fw, fh = (x2-x1), (y2-y1)

    # Heuristic ROIs proportional to face box (lightweight + explainable)
    eyes_box = clamp_box(x1 + int(0.15*fw), y1 + int(0.20*fh),
                         x1 + int(0.85*fw), y1 + int(0.48*fh), w, h)
    lips_box = clamp_box(x1 + int(0.25*fw), y1 + int(0.62*fh),
                         x1 + int(0.75*fw), y1 + int(0.82*fh), w, h)
    skin_box = clamp_box(x1 + int(0.18*fw), y1 + int(0.48*fh),
                         x1 + int(0.82*fw), y1 + int(0.70*fh), w, h)

    return ROIBoxes(
        face=clamp_box(x1,y1,x2,y2,w,h),
        eyes=eyes_box,
        lips=lips_box,
        skin=skin_box,
    )
