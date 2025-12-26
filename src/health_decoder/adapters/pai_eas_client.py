from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict
import requests

@dataclass
class PaiEasConfig:
    endpoint: str
    token: str

class PaiEasClient:
    """
    Call PAI EAS online inference (optional).
    Docs: EAS quick start. :contentReference[oaicite:11]{index=11}
    """
    def __init__(self, cfg: PaiEasConfig):
        self.cfg = cfg

    def predict(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.cfg.token,  # adjust depending on your EAS auth mode
        }
        r = requests.post(self.cfg.endpoint, json=payload, headers=headers, timeout=30)
        r.raise_for_status()
        return r.json()
