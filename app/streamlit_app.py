from __future__ import annotations

import base64
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
from ui.theme import inject_theme_css

inject_theme_css()

ROOT = Path(__file__).resolve().parents[1]


def image_to_base64_safe(path: Path) -> str:
    try:
        if path.exists() and path.stat().st_size > 0:
            return base64.b64encode(path.read_bytes()).decode("utf-8")
    except Exception:
        pass
    return ""


def inject_global_ui_css() -> None:
    st.markdown(
        """
        <style>
          .block-container { padding-top: 1.1rem; padding-bottom: 2rem; max-width: 1200px; }
          [data-testid="stSidebar"] .block-container { padding-top: 0.9rem; }

          h1,h2,h3 { letter-spacing: -0.2px; }
          p,li { color: rgba(229,231,235,0.90); }

          .hd-card{
            border: 1px solid rgba(255,255,255,0.08);
            background: rgba(255,255,255,0.03);
            border-radius: 16px;
            padding: 16px 16px;
            box-shadow: 0 14px 30px rgba(0,0,0,0.35);
          }

          div.stButton > button{
            border-radius: 12px !important;
            padding: 0.70rem 1rem !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
          }
          div.stButton > button:hover{
            border: 1px solid rgba(255,255,255,0.18) !important;
            transform: translateY(-1px);
          }

          [data-testid="stAlert"]{
            border-radius: 14px !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
          }
          hr { border-color: rgba(255,255,255,0.08); }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    watermark_path = ROOT / "assets" / "brand" / "watermark.png"
    logo_path = ROOT / "assets" / "brand" / "logo.png"

    wm_b64 = image_to_base64_safe(watermark_path)
    logo_b64 = image_to_base64_safe(logo_path)

    css = f"""
    <style>
      .hd-header-wrap {{
        position: relative;
        padding: 22px 26px;
        border-radius: 18px;
        background:
          radial-gradient(1000px 360px at 22% 25%, rgba(60,130,255,0.16), rgba(0,0,0,0) 55%),
          linear-gradient(135deg, #0b1220 0%, #0f1c2e 52%, #0b1220 100%);
        overflow: hidden;
        margin-bottom: 14px;
        border: 1px solid rgba(255,255,255,0.06);
        box-shadow: 0 16px 36px rgba(0,0,0,0.45);
      }}

      .hd-header-wrap::after {{
        content: "";
        position: absolute;
        inset: 0;
        background-image: url("data:image/png;base64,{wm_b64}");
        background-repeat: no-repeat;
        background-position: right 20px center;
        background-size: 240px auto;
        opacity: 0.05;
        filter: grayscale(100%);
        pointer-events: none;
      }}

      .hd-header {{
        position: relative;
        display: flex;
        align-items: center;
        gap: 16px;
        z-index: 2;
      }}

      .hd-logo img {{
        height: 74px;
        width: auto;
        display: block;
        border-radius: 14px;
      }}

      .hd-title {{
        flex: 1 1 auto;
        min-width: 0;
      }}

      .hd-title h1 {{
        margin: 0;
        font-size: 34px;
        font-weight: 850;
        letter-spacing: -1px;
        line-height: 1.15;
        color: rgba(255,255,255,0.98);
      }}

      .hd-title p {{
        margin: 6px 0 0 0;
        font-size: 14px;
        opacity: 0.86;
        color: rgba(255,255,255,0.86);
      }}

      .hd-badges {{
        display: flex;
        flex-wrap: wrap;
        justify-content: flex-end;
        gap: 8px;
      }}

      .hd-badge {{
        display: inline-flex;
        align-items: center;
        padding: 6px 10px;
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.12);
        background: rgba(17,24,39,0.55);
        color: rgba(229,231,235,0.92);
        font-size: 11px;
        font-weight: 750;
      }}

      @media (max-width: 720px) {{
        .hd-header {{ flex-direction: column; align-items: flex-start; }}
        .hd-badges {{ justify-content: flex-start; }}
      }}
    </style>
    """

    html = f"""
    <div class="hd-header-wrap">
      <div class="hd-header">
        <div class="hd-logo">
          <img src="data:image/png;base64,{logo_b64}" alt="Health Decoder logo" />
        </div>

        <div class="hd-title">
          <h1>Health Decoder</h1>
          <p>Wellness insights from a single snapshot • Explainable • Privacy-first</p>
        </div>

        <div class="hd-badges">
          <span class="hd-badge">Explainable</span>
          <span class="hd-badge">Privacy-first</span>
          <span class="hd-badge">Alibaba Cloud</span>
        </div>
      </div>
    </div>
    """

    components.html(css + html, height=140)


st.set_page_config(page_title="Health Decoder", page_icon="💧", layout="wide")
inject_global_ui_css()
render_header()

st.info("Use the left sidebar to open **Demo**, **How it Works**, or **Privacy & Ethics**.")

st.markdown('<div class="hd-card">', unsafe_allow_html=True)
st.markdown("### Recommended flow (for judges)")
st.markdown(
    """
1. Open **Demo** → try demo buttons → run analysis  
2. Open **How it Works** → confirm methodology & pipeline  
3. Open **Privacy & Ethics** → review responsible-use commitments
"""
)
st.markdown("</div>", unsafe_allow_html=True)
