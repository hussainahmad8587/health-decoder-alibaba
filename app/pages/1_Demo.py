from __future__ import annotations

import base64
import sys
from dataclasses import asdict
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image, UnidentifiedImageError
import streamlit.components.v1 as components


# ----------------------------
# Path setup (src-layout)
# ----------------------------
ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from health_decoder.pipeline.pipeline import analyze_image  # noqa: E402


# ----------------------------
# Assets
# ----------------------------
LOGO_PATH = ROOT / "assets" / "brand" / "logo.png"
WATERMARK_PATH = ROOT / "assets" / "brand" / "watermark.png"
DEMO_DIR = ROOT / "assets" / "demo_images"

DEMO_FILES = {
    "Hydrated / Good": "hydrated_good_01.jpg",
    "Likely Dehydrated": "dehydrated_low_01.jpg",
    "Office / Tired": "tired_medium_01.jpg",
}

DISCLAIMER = "Wellness guidance only. Not a medical diagnosis."
CONTEXT_OPTIONS = ["Athlete", "Traveler", "Office", "Parent"]

CONTEXT_TIPS = {
    "Athlete": {
        "Low": ["Drink water + consider electrolytes after heavy sweating."],
        "Medium": ["Hydrate steadily during training; sip every 10–15 minutes."],
        "Good": ["Maintain hydration before and after workouts."],
    },
    "Traveler": {
        "Low": ["Air travel can be dehydrating—hydrate and rest."],
        "Medium": ["Drink water regularly; avoid too much caffeine."],
        "Good": ["Keep water accessible throughout the day."],
    },
    "Office": {
        "Low": ["Take a 5-minute break from screens and drink water."],
        "Medium": ["Small sips + short screen breaks help."],
        "Good": ["Keep a water bottle nearby and stay consistent."],
    },
    "Parent": {
        "Low": ["Encourage water intake and monitor comfort."],
        "Medium": ["Offer water and a short rest."],
        "Good": ["Maintain regular hydration habits."],
    },
}

BASE_TIPS = {
    "Low": [
        "Drink 300–500ml water now.",
        "Avoid caffeine for the next 1–2 hours.",
        "Re-check in 30 minutes.",
    ],
    "Medium": [
        "Drink a glass of water.",
        "Take a short break and rest your eyes.",
        "Re-check later today.",
    ],
    "Good": [
        "You look well hydrated—keep your routine.",
        "Maintain steady water intake through the day.",
    ],
}


# ----------------------------
# Helpers
# ----------------------------
def safe_image(path: Path) -> Optional[Image.Image]:
    try:
        if path.exists() and path.stat().st_size > 0:
            with Image.open(path) as im:
                return im.convert("RGBA").copy()
    except (UnidentifiedImageError, OSError):
        return None
    return None


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

          [data-testid="stFileUploader"] section{
            border-radius: 14px !important;
            border: 1px dashed rgba(255,255,255,0.18) !important;
            background: rgba(255,255,255,0.02) !important;
          }

          [data-testid="stMetric"]{
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 14px;
            padding: 10px 12px;
          }

          [data-testid="stExpander"]{
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,0.08);
            overflow: hidden;
          }

          [data-testid="stAlert"]{
            border-radius: 14px !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
          }

          hr { border-color: rgba(255,255,255,0.08); }

          /* Sidebar brand block */
          .hd-side-title{
            text-align:center;
            font-weight:800;
            font-size: 18px;
            margin: 6px 0 10px 0;
            opacity: 0.95;
          }
          .hd-side-logo{
            display:block;
            margin: 0 auto;
            max-width: 170px;
            width: 100%;
            height: auto;
          }
          .hd-side-divider{
            height:1px;
            background: rgba(255,255,255,0.12);
            margin: 14px 0 12px 0;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _decode_uploaded_image(file_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(file_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode uploaded image.")
    return img


def _bgr_to_rgb(img_bgr: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)


def _load_demo_image(filename: str) -> np.ndarray:
    demo_dir = DEMO_DIR.resolve()
    path = (demo_dir / filename).resolve()

    if not path.exists():
        stem = Path(filename).stem
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            p = demo_dir / f"{stem}{ext}"
            if p.exists():
                path = p
                break

    if not path.exists() or path.stat().st_size == 0:
        available = sorted(p.name for p in demo_dir.glob("*") if p.is_file())
        raise FileNotFoundError(
            f"Demo image missing or empty: {path}\nAvailable demo files: {available}"
        )

    data = path.read_bytes()
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is not None:
        return img

    with Image.open(path) as im:
        im = im.convert("RGB")
        rgb = np.array(im)
        return rgb[:, :, ::-1]


def _tips_for(category: str, context: str) -> list[str]:
    tips = list(BASE_TIPS.get(category, []))
    tips.extend(CONTEXT_TIPS.get(context, {}).get(category, []))
    return tips[:3]


def _quality_label_brightness(mean_val: float) -> tuple[str, str]:
    if mean_val < 55:
        return "Bad", "Too dark — move to brighter front-facing light."
    if mean_val < 85:
        return "OK", "Acceptable lighting — brighter light may improve reliability."
    return "Good", "Lighting looks good."


def _quality_label_blur(lap_var: float) -> tuple[str, str]:
    if lap_var < 25:
        return "Bad", "Very blurry — hold steady and refocus (analysis may be blocked)."
    if lap_var < 45:
        return "Bad", "Blurry — hold steady and refocus."
    if lap_var < 80:
        return "OK", "Slight blur — try a steadier capture."
    return "Good", "Sharpness looks good."


def _init_state() -> None:
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("baseline", None)
    st.session_state.setdefault("selected_demo_label", None)
    st.session_state.setdefault("selected_demo_file", None)
    st.session_state.setdefault("run_requested", False)


def _select_demo(label: str) -> None:
    st.session_state["selected_demo_label"] = label
    st.session_state["selected_demo_file"] = DEMO_FILES[label]
    st.session_state["run_requested"] = True


def _push_history(res, context: str) -> None:
    if not res.ok or res.score is None:
        return
    st.session_state["history"].append(
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "score": int(res.score.score),
            "category": res.score.category,
            "confidence": res.score.confidence,
            "context": context,
            "brightness_mean": float(res.quality.brightness_mean),
            "blur_laplacian_var": float(res.quality.blur_laplacian_var),
        }
    )
    st.session_state["history"] = st.session_state["history"][-50:]


def _history_df() -> pd.DataFrame:
    hist = st.session_state.get("history", [])
    if not hist:
        return pd.DataFrame(
            columns=[
                "timestamp",
                "score",
                "category",
                "confidence",
                "context",
                "brightness_mean",
                "blur_laplacian_var",
            ]
        )
    return pd.DataFrame(hist)


def _render_header() -> None:
    wm_b64 = image_to_base64_safe(WATERMARK_PATH)
    logo_b64 = image_to_base64_safe(LOGO_PATH)

    status = st.session_state.get("pipeline_status", "idle")
    if status == "running":
        dot_class, status_text = "hd-dot--busy", "Analyzing…"
    elif status == "error":
        dot_class, status_text = "hd-dot--err", "Error"
    else:
        dot_class, status_text = "hd-dot--live", "Ready"

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

      .hd-right {{
        display:flex;
        flex-direction:column;
        align-items:flex-end;
        gap:10px;
      }}

      .hd-status {{
        display:inline-flex;
        align-items:center;
        gap:8px;
        padding:6px 10px;
        border-radius:999px;
        border:1px solid rgba(255,255,255,0.12);
        background: rgba(17,24,39,0.55);
        color: rgba(229,231,235,0.92);
        font-size: 12px;
        font-weight: 800;
      }}

      .hd-dot {{
        width: 9px;
        height: 9px;
        border-radius: 50%;
        box-shadow: 0 0 0 3px rgba(255,255,255,0.06);
      }}
      .hd-dot--live {{ background: #2ecc71; }}
      .hd-dot--busy {{ background: #f39c12; }}
      .hd-dot--err  {{ background: #e74c3c; }}

      .hd-badges {{
        display:flex;
        flex-wrap:wrap;
        justify-content:flex-end;
        gap:8px;
      }}
      .hd-badge {{
        display:inline-flex;
        align-items:center;
        padding:6px 10px;
        border-radius:999px;
        border:1px solid rgba(255,255,255,0.12);
        background: rgba(17,24,39,0.55);
        color: rgba(229,231,235,0.92);
        font-size: 11px;
        font-weight: 750;
      }}

      @media (max-width: 720px) {{
        .hd-header {{ flex-direction: column; align-items: flex-start; }}
        .hd-right {{ width:100%; align-items:flex-start; }}
        .hd-badges {{ justify-content:flex-start; }}
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

        <div class="hd-right">
          <div class="hd-status">
            <span class="hd-dot {dot_class}"></span>
            <span>{status_text}</span>
          </div>

          <div class="hd-badges">
            <span class="hd-badge">Explainable</span>
            <span class="hd-badge">Privacy-first</span>
            <span class="hd-badge">Alibaba Cloud</span>
          </div>
        </div>
      </div>
    </div>
    """

    components.html(css + html, height=140)
    st.info(DISCLAIMER)


def _friendly_fail(message: str, quality_mean: float, quality_blur: float) -> None:
    st.warning(
        "We couldn’t confidently analyze this image.\n\n"
        f"**Reason:** {message}\n\n"
        "Try again with a clear, front-facing photo."
    )
    with st.expander("Capture tips (recommended)"):
        st.markdown(
            "- Ensure **eyes, nose, and mouth** are visible\n"
            "- Use **front-facing light**\n"
            "- Avoid motion blur (hold steady)\n"
            "- Avoid extreme close-ups"
        )
        qb, qb_msg = _quality_label_brightness(quality_mean)
        ql, ql_msg = _quality_label_blur(quality_blur)
        st.write(f"**Lighting:** {qb} — {qb_msg}")
        st.write(f"**Sharpness:** {ql} — {ql_msg}")


# ----------------------------
# Page init
# ----------------------------
st.set_page_config(page_title="Health Decoder — Demo", page_icon="💧", layout="wide")
_init_state()
inject_global_ui_css()
_render_header()


# ----------------------------
# Sidebar (clean + professional)
# ----------------------------
logo_b64 = image_to_base64_safe(LOGO_PATH)

st.sidebar.markdown(
    f"""
    <div class="hd-side-title">Demo Controls</div>
    <img class="hd-side-logo" src="data:image/png;base64,{logo_b64}" alt="logo" />
    <div class="hd-side-divider"></div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("### User scenario")
st.sidebar.caption("Used to personalize suggested next steps.")
context = st.sidebar.selectbox("", options=CONTEXT_OPTIONS, index=2, label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.markdown("### Curated demo images")
st.sidebar.caption("Preloaded examples for judging. Files must exist in `assets/demo_images/`.")
st.sidebar.code("\n".join(DEMO_FILES.values()), language="text")

st.sidebar.markdown("---")
with st.sidebar.expander("⚙️ Session actions", expanded=False):
    if st.button("Clear session history", width="stretch"):
        st.session_state["history"] = []
        st.success("History cleared.")
    if st.button("Clear baseline", width="stretch"):
        st.session_state["baseline"] = None
        st.info("Baseline cleared.")


# ----------------------------
# Main layout (cards)
# ----------------------------
left, right = st.columns([0.95, 1.05], gap="large")

with left:
    st.markdown('<div class="hd-card">', unsafe_allow_html=True)

    st.subheader("1️⃣ Upload a Snapshot")

    uploaded = st.file_uploader(
        "Upload a clear selfie image (JPG/PNG)",
        type=["jpg", "jpeg", "png"],
        help="For best results, ensure your full face is visible and the photo is not blurry.",
    )

    st.caption("Tips: front-facing light, steady camera, full face visible.")
    with st.expander("Capture tips"):
        st.markdown(
            "- Ensure **eyes, nose, and mouth** are visible\n"
            "- Use **front-facing light**\n"
            "- Avoid motion blur (hold steady)\n"
            "- Avoid extreme close-ups"
        )

    st.markdown("**Or use demo examples (recommended for judging):**")
    bcols = st.columns(3)
    if bcols[0].button("Likely Dehydrated", width="stretch"):
        _select_demo("Likely Dehydrated")
    if bcols[1].button("Office / Tired", width="stretch"):
        _select_demo("Office / Tired")
    if bcols[2].button("Hydrated / Good", width="stretch"):
        _select_demo("Hydrated / Good")

    st.markdown("---")

    has_demo = st.session_state.get("selected_demo_file") is not None
    has_upload = uploaded is not None
    can_run = has_demo or has_upload

    st.subheader("Run analysis")
    run_clicked = st.button(
        "Analyze Snapshot",
        type="primary",
        width="stretch",
        disabled=not can_run,
    )
    if not can_run:
        st.caption("Upload an image or pick a demo case to enable analysis.")

    run = run_clicked or st.session_state.get("run_requested", False)

    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="hd-card">', unsafe_allow_html=True)

    st.subheader("2️⃣ Results")
    st.caption("Upload an image or select a demo case, then click Analyze Snapshot.")

    selected_img: Optional[np.ndarray] = None
    selected_label = "Input snapshot"

    demo_file = st.session_state.get("selected_demo_file")
    demo_label = st.session_state.get("selected_demo_label")

    if demo_file:
        try:
            selected_img = _load_demo_image(demo_file)
            selected_label = f"Demo: {demo_label}"
        except Exception as e:
            st.error(f"Demo image load failed: {e}")
            selected_img = None

    if run:
        st.session_state["run_requested"] = False

        if selected_img is None:
            if uploaded is None:
                st.warning("Upload an image or select a demo case to start.")
                st.stop()
            selected_img = _decode_uploaded_image(uploaded.getvalue())
            selected_label = "Uploaded snapshot"

        st.image(_bgr_to_rgb(selected_img), caption=selected_label, use_container_width=True)

        with st.spinner("Analyzing..."):
            res = analyze_image(selected_img)

        # Quality first (always)
        st.markdown("### Capture quality")
        b_mean = float(res.quality.brightness_mean)
        b_blur = float(res.quality.blur_laplacian_var)
        qb, qb_msg = _quality_label_brightness(b_mean)
        ql, ql_msg = _quality_label_blur(b_blur)

        q1, q2 = st.columns(2)
        q1.metric("Lighting", qb)
        q2.metric("Sharpness", ql)

        with st.expander("Capture quality details"):
            st.write(f"Brightness mean: **{b_mean:.1f}**")
            st.write(f"Blur (Laplacian variance): **{b_blur:.1f}**")
            st.caption(qb_msg)
            st.caption(ql_msg)

        if not res.ok:
            _friendly_fail(res.message, b_mean, b_blur)
            st.stop()

        assert res.score is not None
        s = res.score

        st.markdown("### Summary")
        c1, c2, c3 = st.columns(3)
        c1.metric("Score", f"{s.score}/100")
        c2.metric("Category", s.category)
        c3.metric("Confidence", s.confidence)

        a, b = st.columns([1, 1])
        with a:
            st.markdown("### What we noticed")
            for r in s.reasons:
                st.write(f"• {r}")
        with b:
            st.markdown("### Suggested next steps")
            for t in _tips_for(s.category, context):
                st.write(f"• {t}")

        baseline = st.session_state.get("baseline")
        if baseline is not None:
            delta = int(s.score) - int(baseline["score"])
            sign = "+" if delta >= 0 else ""
            st.markdown("### Compared to your baseline")
            st.write(f"Baseline: **{baseline['score']}/100** → Change: **{sign}{delta}** points")

        with st.expander("Explainability"):
            st.caption("The system focuses on face sub-regions (eyes, lips, skin). It does not identify you.")
            if res.explain is not None and getattr(res.explain, "overlay_bgr", None) is not None:
                st.image(_bgr_to_rgb(res.explain.overlay_bgr), use_container_width=True)
            else:
                st.info("Explainability overlay not available for this run.")

        with st.expander("Personalization (optional)"):
            cA, cB = st.columns(2)
            with cA:
                if st.button("Set baseline from this snapshot", type="primary", width="stretch"):
                    st.session_state["baseline"] = {
                        "score": int(s.score),
                        "category": s.category,
                        "confidence": s.confidence,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    st.success("Baseline saved.")
            with cB:
                if st.button("Clear baseline", width="stretch"):
                    st.session_state["baseline"] = None
                    st.info("Baseline cleared.")

        _push_history(res, context=context)
        df = _history_df()

        st.markdown("### Trend (this session)")
        if len(df) >= 2:
            st.line_chart(df["score"], height=170)
        else:
            st.caption("Run at least 2 checks to see a trend chart.")

        with st.expander("View session history table"):
            st.dataframe(df, use_container_width=True)

        csv_buf = StringIO()
        df.to_csv(csv_buf, index=False)
        st.download_button(
            "Download results as CSV",
            csv_buf.getvalue(),
            file_name="health_decoder_session_results.csv",
            mime="text/csv",
            width="stretch",
        )

        with st.expander("Technical details (for judges)"):
            st.write("Risk components (0..1; higher indicates stronger visual signal):")
            st.write(s.risk_components)
            st.write("Full result object (debug):")
            st.json(
                {
                    "ok": res.ok,
                    "message": res.message,
                    "quality": asdict(res.quality),
                    "score": asdict(res.score),
                }
            )
    else:
        # Optional preview if demo chosen
        if selected_img is not None:
            st.image(_bgr_to_rgb(selected_img), caption=selected_label, use_container_width=True)
            st.caption("Click **Analyze Snapshot** to run analysis.")

    st.markdown("</div>", unsafe_allow_html=True)
