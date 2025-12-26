from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class QualityResult:
    brightness_mean: float
    blur_laplacian_var: float
    notes: List[str]

@dataclass
class ScoreResult:
    score: int                      # 0..100 higher=better
    category: str                   # Low/Medium/Good
    confidence: str                 # Low/Medium/High
    reasons: List[str]
    risk_components: Dict[str, float]  # 0..1 higher=worse (eyes/lips/skin)

@dataclass
class ExplainResult:
    overlay_bgr: Optional[object]   # np.ndarray, but keep generic here

@dataclass
class AnalysisResult:
    ok: bool
    message: str
    quality: QualityResult
    score: Optional[ScoreResult] = None
    explain: Optional[ExplainResult] = None
