from __future__ import annotations
from ui.theme import page_container_open, page_container_close, brand_header

page_container_open()

brand_header(
    title="Health Decoder",
    subtitle="Decode health text into structured, readable insights for demo and discussion.",
    badges=["Hackathon Demo", "Privacy-first", "Explainable Output"],
)

import streamlit as st

st.set_page_config(page_title="Health Decoder — How it Works", page_icon="🧠", layout="wide")

st.markdown(
    """
    <style>
      .block-container { max-width: 1100px; padding-top: 1.1rem; }
      .hd-card{
        border: 1px solid rgba(255,255,255,0.08);
        background: rgba(255,255,255,0.03);
        border-radius: 16px;
        padding: 16px 16px;
        box-shadow: 0 14px 30px rgba(0,0,0,0.35);
      }
      hr { border-color: rgba(255,255,255,0.08); }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="hd-card">', unsafe_allow_html=True)
st.title("How it Works")
st.caption("A high-level, judge-friendly explanation of the pipeline.")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("")

st.markdown('<div class="hd-card">', unsafe_allow_html=True)
st.markdown("### Overview")
st.markdown(
    """
Health Decoder takes a **single selfie snapshot** and produces:

- a **wellness score** (0–100),
- a **category** (Low / Medium / Good),
- **reasons** behind the result, and
- optional **visual explainability** overlays.

This is **wellness guidance only** (not a medical diagnosis).
"""
)

st.markdown("---")

st.markdown("### Processing steps (conceptual)")
st.markdown(
    """
1. **Input validation**  
   Checks if the image is readable and contains enough signal for analysis.

2. **Capture quality checks**  
   Measures:
   - Lighting (brightness mean)
   - Sharpness (blur via Laplacian variance)

3. **Face-region analysis**  
   The system focuses on face sub-regions (e.g., eyes/lips/skin patterns) to extract signals.

4. **Scoring & confidence**  
   The model outputs:
   - score
   - category
   - confidence

5. **Explainability (optional)**  
   When available, an overlay highlights areas most influential in the decision.
"""
)

st.markdown("---")

st.markdown("### Why the quality checks matter")
st.markdown(
    """
If the image is **too dark** or **too blurry**, the model may be unreliable.
So the app surfaces quality indicators first and may **block** analysis when confidence is too low.
"""
)

st.markdown("</div>", unsafe_allow_html=True)
page_container_close()