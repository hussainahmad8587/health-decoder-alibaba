from __future__ import annotations
from typing import Optional, Tuple
import numpy as np
from ..config import Settings
from ..adapters.vision_local import LocalVisionAdapter
from ..adapters.vision_alibaba_imm import AlibabaImmVisionAdapter, ImmConfig

class VisionService:
    def __init__(self, adapter):
        self.adapter = adapter

    @staticmethod
    def from_settings(s: Settings) -> "VisionService":
        if s.vision_backend == "alibaba_imm":
            cfg = ImmConfig(
                endpoint=s.imm_endpoint,
                project=s.imm_project,
                access_key_id=s.access_key_id,
                access_key_secret=s.access_key_secret,
                region=s.region,
            )
            return VisionService(AlibabaImmVisionAdapter(cfg))
        return VisionService(LocalVisionAdapter())

    def detect_face(self, img_bgr: np.ndarray) -> Optional[Tuple[int,int,int,int]]:
        return self.adapter.detect_face(img_bgr)
