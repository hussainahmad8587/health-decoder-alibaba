from __future__ import annotations
import numpy as np

def _roi_stat(gray_roi: np.ndarray) -> tuple[float,float]:
    # mean, std (simple, explainable)
    return float(gray_roi.mean()), float(gray_roi.std())

def risk_from_rois(eyes_gray: np.ndarray, lips_gray: np.ndarray, skin_gray: np.ndarray) -> dict:
    e_mean, e_std = _roi_stat(eyes_gray)
    l_mean, l_std = _roi_stat(lips_gray)
    s_mean, s_std = _roi_stat(skin_gray)

    # Heuristic “risk” in 0..1 (higher worse), for demo only
    eyes_risk = np.clip((110 - e_mean) / 110, 0, 1) * 0.6 + np.clip((25 - e_std)/25, 0, 1)*0.4
    lips_risk = np.clip((115 - l_mean) / 115, 0, 1) * 0.7 + np.clip((22 - l_std)/22, 0, 1)*0.3
    skin_risk = np.clip((120 - s_mean) / 120, 0, 1) * 0.6 + np.clip((20 - s_std)/20, 0, 1)*0.4

    return {"eyes": float(eyes_risk), "lips": float(lips_risk), "skin": float(skin_risk)}

def wellness_score(risk: dict) -> tuple[int,str,str,list[str]]:
    # Aggregate risk → wellness score
    agg = 0.4*risk["eyes"] + 0.35*risk["lips"] + 0.25*risk["skin"]
    score = int(round(100 * (1.0 - agg)))

    if score < 45:
        cat = "Low"
    elif score < 70:
        cat = "Medium"
    else:
        cat = "Good"

    # Confidence heuristic (demo)
    if score < 40 or score > 80:
        conf = "High"
    else:
        conf = "Medium"

    reasons = []
    if risk["lips"] > 0.55: reasons.append("Lip region suggests dryness-like cues.")
    if risk["eyes"] > 0.55: reasons.append("Eye region suggests fatigue-like cues.")
    if risk["skin"] > 0.55: reasons.append("Skin region suggests lower vitality-like cues.")
    if not reasons: reasons.append("Overall signals look balanced under current capture conditions.")

    return score, cat, conf, reasons
