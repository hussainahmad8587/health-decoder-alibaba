from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np

@dataclass
class ImmConfig:
    endpoint: str
    project: str
    access_key_id: str
    access_key_secret: str
    region: str

class AlibabaImmVisionAdapter:
    """
    IMM Face Detection adapter.
    Uses Alibaba Cloud IMM face detection feature (cloud).
    Docs: IMM Face detection. :contentReference[oaicite:7]{index=7}
    """
    def __init__(self, cfg: ImmConfig):
        self.cfg = cfg

    def detect_face(self, img_bgr: np.ndarray) -> Optional[Tuple[int,int,int,int]]:
        # TODO:
        # 1) encode image (jpg bytes)
        # 2) call IMM face detection API (signed request)
        # 3) parse face rectangle
        #
        # Return (x1,y1,x2,y2) in image pixel coords
        raise NotImplementedError("Configure IMM call + auth signing here.")
