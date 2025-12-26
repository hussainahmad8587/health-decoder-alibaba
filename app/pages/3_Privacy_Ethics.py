from __future__ import annotations
from ui.theme import page_container_open, page_container_close, brand_header

page_container_open()

brand_header(
    title="Health Decoder",
    subtitle="Decode health text into structured, readable insights for demo and discussion.",
    badges=["Hackathon Demo", "Privacy-first", "Explainable Output"],
)
import streamlit as st

st.set_page_config(page_title="Health Decoder — Privacy & Ethics", page_icon="🔒", layout="wide")

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
st.title("Privacy & Ethics")
st.caption("A clear, responsible-use policy suitable for demos and judging.")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("")

st.markdown('<div class="hd-card">', unsafe_allow_html=True)
st.markdown("### Privacy principles")
st.markdown(
    """
- **No identity recognition**: the app is not designed to identify a person.
- **Minimal data**: only the image provided for analysis is used for the session.
- **No hidden tracking**: no behavioral profiling or ad tracking.
- **User control**: users can clear session history at any time.
"""
)

st.markdown("---")

st.markdown("### Responsible-use commitments")
st.markdown(
    """
- This app provides **wellness guidance**, not a medical diagnosis.
- Outputs should not be used to make clinical decisions.
- If the user has health concerns, they should consult a qualified professional.
"""
)

st.markdown("---")

st.markdown("### Bias & limitations")
st.markdown(
    """
Like all computer vision systems, performance can vary based on:
- lighting conditions,
- camera quality,
- image blur and angle,
- and individual differences.

To reduce risk, the app includes **quality checks** and warns/blocks analysis when reliability is low.
"""
)

st.markdown("---")

st.markdown("### Transparency")
st.markdown(
    """
The app provides:
- **confidence estimates**
- **reasons** for decisions
- optional **explainability overlays** (when available)

This is intended to make results more understandable and auditable during evaluation.
"""
)

st.markdown("</div>", unsafe_allow_html=True)
page_container_close()