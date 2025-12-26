# app/pages/1_Demo.py
# Refactored, professional Streamlit UI for Health Decoder (Alibaba-ready)
# - Clean header + single disclaimer
# - Clear 2-step flow (Upload → Results)
# - Friendly error handling
# - Capture tips + demo images (one-click demo runs)
# - Expanders for details (quality / explainability / session / technical)
# - Session trend + CSV export
#
# Run:
#   streamlit run app/streamlit_app.py
# or:
#   streamlit run app/pages/1_Demo.py

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
    """Return a PIL image if readable, otherwise None (never crash UI)."""
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


def _decode_uploaded_image(file_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(file_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode uploaded image.")
    return img


def _bgr_to_rgb(img_bgr: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)


def _load_demo_image(filename: str) -> np.ndarray:
    """
    Robust demo-image loader:
    - Extension-flexible (tries jpg/jpeg/png/webp)
    - Windows-safe (byte decode via cv2.imdecode)
    - PIL fallback for weird encodings
    """
    demo_dir = DEMO_DIR.resolve()
    path = (demo_dir / filename).resolve()

    # Try alternate extensions automatically if exact file doesn't exist
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
            f"Demo image missing or empty: {path}\n"
            f"Available demo files: {available}"
        )

    data = path.read_bytes()
    if not data:
        raise RuntimeError(f"Demo image is empty: {path}")

    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is not None:
        return img

    # Fallback: PIL (robust)
    try:
        with Image.open(path) as im:
            im = im.convert("RGB")
            rgb = np.array(im)
            return rgb[:, :, ::-1]  # RGB -> BGR
    except Exception as e:
        raise RuntimeError(f"Failed to decode demo image via OpenCV and PIL: {path}") from e


def _tips_for(category: str, context: str) -> list[str]:
    tips = list(BASE_TIPS.get(category, []))
    tips.extend(CONTEXT_TIPS.get(context, {}).get(category, []))
    return tips[:3]


def _quality_label_brightness(mean_val: float) -> tuple[str, str]:
    # Align with your core threshold ranges; adjust if needed.
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
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if "baseline" not in st.session_state:
        st.session_state["baseline"] = None  # dict

    # Demo selection + one-click run
    if "selected_demo_label" not in st.session_state:
        st.session_state["selected_demo_label"] = None
    if "selected_demo_file" not in st.session_state:
        st.session_state["selected_demo_file"] = None
    if "run_requested" not in st.session_state:
        st.session_state["run_requested"] = False


def _select_demo(label: str) -> None:
    """Select a demo case and request an immediate run."""
    st.session_state["selected_demo_label"] = label
    st.session_state["selected_demo_file"] = DEMO_FILES[label]
    st.session_state["run_requested"] = True


def _push_history(res, context: str) -> None:
    # res is AnalysisResult
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
    watermark_path = ROOT / "assets" / "brand" / "watermark.png"
    logo_path = ROOT / "assets" / "brand" / "logo.png"

    wm_b64 = image_to_base64_safe(watermark_path)
    logo_b64 = image_to_base64_safe(logo_path)

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
        padding: 24px 30px;
        border-radius: 18px;
        background:
          radial-gradient(1200px 420px at 25% 25%, rgba(60,130,255,0.16), rgba(0,0,0,0) 55%),
          linear-gradient(135deg, #0b1220 0%, #0f1c2e 52%, #0b1220 100%);
        overflow: hidden;
        margin-bottom: 14px;
        border: 1px solid rgba(255,255,255,0.06);
        box-shadow: 0 16px 36px rgba(0,0,0,0.45);
      }}

      .hd-header-wrap::before {{
        content: "";
        position: absolute;
        inset: 0;
        border-radius: 18px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.06);
        pointer-events: none;
        z-index: 1;
      }}

      .hd-header-wrap::after {{
        content: "";
        position: absolute;
        inset: 0;
        background-image: url("data:image/png;base64,{wm_b64}");
        background-repeat: no-repeat;
        background-position: right 22px center;
        background-size: 260px auto;
        opacity: 0.055;
        filter: grayscale(100%);
        pointer-events: none;
        z-index: 1;
      }}

      .hd-header {{
        position: relative;
        display: flex;
        align-items: center;
        gap: 18px;
        z-index: 2;
      }}

      .hd-logo img {{
        height: 110px;
        width: auto;
        display: block;
        border-radius: 14px;
      }}

      .hd-title {{
        flex: 1 1 auto;
        min-width: 0;
        display: flex;
        flex-direction: column;
        gap: 6px;
      }}

      .hd-title h1 {{
        margin: 0;
        font-size: 40px;
        font-weight: 800;
        letter-spacing: -1.5px;
        line-height: 2.05;
        color: rgba(255,255,255,0.98);
      }}

      .hd-title p {{
        margin: 0;
        font-size: 14px;
        opacity: 0.86;
        color: rgba(255,255,255,0.86);
      }}

      .hd-right {{
        flex: 0 0 auto;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 10px;
        min-width: 240px;
      }}

      .hd-status {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 10px;
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.12);
        background: rgba(255,255,255,0.04);
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
        font-size: 12px;
        font-weight: 700;
        color: rgba(255,255,255,0.92);
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

      .hd-pills {{
        display: flex;
        flex-wrap: wrap;
        justify-content: flex-end;
        gap: 8px;
      }}

      .hd-pill {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 7px 10px;
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.12);
        background: rgba(255,255,255,0.03);
        color: rgba(255,255,255,0.86);
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.25px;
        line-height: 1;
        user-select: none;
      }}

      @media (max-width: 980px) {{
        .hd-header-wrap {{ padding: 20px 22px; }}
        .hd-logo img {{ height: 66px; }}
        .hd-title h1 {{ font-size: 32px; }}
        .hd-right {{ min-width: 210px; }}
        .hd-header-wrap::after {{ background-size: 210px auto; opacity: 0.05; }}
      }}

      @media (max-width: 720px) {{
        .hd-header {{
          flex-direction: column;
          align-items: flex-start;
          gap: 14px;
        }}
        
        .hd-right {{
          width: 100%;
          min-width: 0;
          align-items: flex-start;
        }}
        .hd-pills {{
          justify-content: flex-start;
        }}
        .hd-header-wrap::after {{
          background-position: center bottom;
          background-size: 180px auto;
          opacity: 0.045;
        }}
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

          <div class="hd-pills">
            <span class="hd-pill">🧠 Explainable</span>
            <span class="hd-pill">🔒 Privacy-first</span>
            <span class="hd-pill">☁️ Alibaba Cloud</span>
          </div>
        </div>
      </div>
    </div>
    """

    # CRITICAL: must be markdown with unsafe_allow_html=True
    components.html(css + html, height=170)


    st.info("Wellness guidance only. Not a medical diagnosis.")

def _friendly_fail(message: str, quality_mean: float, quality_blur: float) -> None:
    st.warning(
        "We couldn’t confidently analyze this image.\n\n"
        f"**Reason:** {message}\n\n"
        "Try again with a clear, front-facing photo."
    )
    with st.expander("📷 Capture tips (recommended)"):
        st.markdown(
            "- Ensure **eyes, nose, and mouth** are fully visible\n"
            "- Hold the camera steady (avoid motion blur)\n"
            "- Avoid extreme close-ups\n"
            "- Use natural front-facing light"
        )
        qb, qb_msg = _quality_label_brightness(quality_mean)
        ql, ql_msg = _quality_label_blur(quality_blur)
        st.write(f"**Lighting:** {qb} — {qb_msg}")
        st.write(f"**Sharpness:** {ql} — {ql_msg}")


# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="Health Decoder — Demo", page_icon="💧", layout="wide")
_init_state()
_render_header()

# ----------------------------
# Sidebar: Brand block (refined)
# ----------------------------
st.sidebar.markdown(
    """
    <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 12px;
        margin-top: 6px;
        margin-bottom: 12px;
        text-align: center;
    ">
        <div style="
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: 0.4px;
            opacity: 0.95;
        ">
            Demo Controls
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

logo_img = safe_image(LOGO_PATH)
if logo_img is not None:
    st.sidebar.image(logo_img, width="stretch")
else:
    st.sidebar.caption(
        "Logo not found or invalid.\nAdd a valid PNG at `assets/brand/logo.png`."
    )

st.sidebar.markdown(
    """
    <div style="
        height: 1px;
        background: rgba(255,255,255,0.12);
        margin: 14px 0 10px 0;
    "></div>
    """,
    unsafe_allow_html=True,
)

# Section: User context
st.sidebar.markdown("### User scenario")
st.sidebar.caption("Used to personalize suggested next steps.")

context = st.sidebar.selectbox(
    label="",
    options=CONTEXT_OPTIONS,
    index=2,
    label_visibility="collapsed",
)

st.sidebar.markdown("---")

# Section: Demo images
st.sidebar.markdown("### Curated demo images")
st.sidebar.caption(
    "Preloaded examples for judging.\n"
    "Files must exist in `assets/demo_images/`."
)

st.sidebar.code(
    "\n".join(DEMO_FILES.values()),
    language="text",
)

demo_pick = st.sidebar.radio(
    label="Choose a demo case",
    options=["None (use upload)"] + list(DEMO_FILES.keys()),
    index=0,
)

# Keep sidebar selection in session state (no auto-run from radio)
if demo_pick != "None (use upload)":
    st.session_state["selected_demo_label"] = demo_pick
    st.session_state["selected_demo_file"] = DEMO_FILES[demo_pick]
else:
    st.session_state["selected_demo_label"] = None
    st.session_state["selected_demo_file"] = None

st.sidebar.markdown("---")

# Section: Session actions
with st.sidebar.expander("⚙️ Session actions", expanded=False):
    if st.button("Clear session history", width="stretch"):
        st.session_state["history"] = []
        st.success("History cleared.")

    if st.button("Clear baseline", width="stretch"):
        st.session_state["baseline"] = None
        st.info("Baseline cleared.")

# ----------------------------
# Main layout
# ----------------------------
left, right = st.columns([0.95, 1.05], gap="large")


# ----------------------------
# Left: Input
# ----------------------------
with left:
    st.subheader("1️⃣ Upload a Snapshot")

    uploaded = st.file_uploader(
        "Upload a clear selfie image (JPG/PNG)",
        type=["jpg", "jpeg", "png"],
        help="For best results, ensure your full face is visible and the photo is not blurry.",
    )

    st.caption(
        "For best results:\n"
        "• Ensure eyes, nose, and mouth are fully visible\n"
        "• Hold the camera steady\n"
        "• Avoid extreme close-ups\n"
        "• Use natural front-facing light"
    )

    st.markdown("**Or use demo examples (recommended for judging):**")
    bcols = st.columns(3)
    b_dehydrated = bcols[0].button("Likely Dehydrated", width="stretch")
    b_tired = bcols[1].button("Office / Tired", width="stretch")
    b_hydrated = bcols[2].button("Hydrated / Good", width="stretch")

    # One-click demo runs
    if b_dehydrated:
        _select_demo("Likely Dehydrated")
    if b_tired:
        _select_demo("Office / Tired")
    if b_hydrated:
        _select_demo("Hydrated / Good")

    st.markdown("---")
    st.subheader("Run analysis")
    run_clicked = st.button("Analyze Snapshot", type="primary", width="stretch")
    run = run_clicked or st.session_state.get("run_requested", False)


# ----------------------------
# Right: Results
# ----------------------------
with right:
    st.subheader("2️⃣ Results")

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
        # Reset run request so it doesn't rerun forever
        st.session_state["run_requested"] = False

        if selected_img is None:
            if uploaded is None:
                st.warning("Upload an image or select a demo case to start.")
                st.stop()
            try:
                selected_img = _decode_uploaded_image(uploaded.getvalue())
                selected_label = "Uploaded snapshot"
            except Exception as e:
                st.error(f"Image load failed: {e}")
                st.stop()

        st.image(_bgr_to_rgb(selected_img), caption=selected_label, width="stretch")

        with st.spinner("Analyzing..."):
            res = analyze_image(selected_img)

        # Capture quality (always show)
        st.markdown("### Capture quality")
        b_mean = float(res.quality.brightness_mean)
        b_blur = float(res.quality.blur_laplacian_var)
        qb, qb_msg = _quality_label_brightness(b_mean)
        ql, ql_msg = _quality_label_blur(b_blur)

        q1, q2 = st.columns(2)
        q1.metric("Lighting", qb)
        q2.metric("Sharpness", ql)

        with st.expander("📷 Capture quality details"):
            st.write(f"Brightness mean: **{b_mean:.1f}**")
            st.write(f"Blur (Laplacian variance): **{b_blur:.1f}**")
            st.write("Notes:")
            for n in res.quality.notes:
                st.write(f"• {n}")
            st.caption("Tip: Use steady hands and front-facing light for best reliability.")
            st.write(f"Lighting hint: {qb_msg}")
            st.write(f"Sharpness hint: {ql_msg}")

        if not res.ok:
            _friendly_fail(res.message, b_mean, b_blur)
            st.stop()

        assert res.score is not None
        s = res.score

        st.markdown("### Your wellness result")
        c1, c2, c3 = st.columns(3)
        c1.metric("Wellness Score", f"{s.score}/100")
        c2.metric("Category", s.category)
        c3.metric("Confidence", s.confidence)

        baseline = st.session_state.get("baseline")
        if baseline is not None:
            delta = int(s.score) - int(baseline["score"])
            sign = "+" if delta >= 0 else ""
            st.markdown("### Compared to your baseline")
            st.write(
                f"Baseline: **{baseline['score']}/100**  →  Current change: **{sign}{delta}** points"
            )
            if delta >= 5:
                st.success("Compared to your baseline, this looks improved.")
            elif delta <= -5:
                st.warning(
                    "Compared to your baseline, this looks worse (could be wellness or capture conditions)."
                )
            else:
                st.info("Compared to your baseline, this looks similar.")

        st.markdown("### What we noticed")
        for r in s.reasons:
            st.write(f"• {r}")

        st.markdown("### Suggested next steps")
        for t in _tips_for(s.category, context):
            st.write(f"• {t}")

        with st.expander("🧠 How the AI looked at your image (Explainability)"):
            st.caption("The system focuses on face sub-regions (eyes, lips, skin). It does not identify you.")
            if res.explain is not None and getattr(res.explain, "overlay_bgr", None) is not None:
                st.image(_bgr_to_rgb(res.explain.overlay_bgr), width="stretch")
            else:
                st.info("Explainability overlay not available for this run.")

        with st.expander("👤 Personalization (optional)"):
            cA, cB = st.columns(2)
            with cA:
                if st.button("Set baseline from this snapshot", type="primary", width="stretch"):
                    st.session_state["baseline"] = {
                        "score": int(s.score),
                        "category": s.category,
                        "confidence": s.confidence,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    st.success("Baseline saved. Future checks will show changes vs baseline.")
            with cB:
                if st.button("Clear baseline", width="stretch"):
                    st.session_state["baseline"] = None
                    st.info("Baseline cleared.")

        _push_history(res, context=context)
        df = _history_df()

        st.markdown("### Trend (this session)")
        st.caption("For meaningful trends, use consistent lighting and distance between checks.")
        if len(df) >= 2:
            st.line_chart(df["score"], height=170)
        else:
            st.caption("Run at least 2 checks to see a trend chart.")

        with st.expander("📈 View session history table"):
            st.dataframe(df, width="stretch")

        csv_buf = StringIO()
        df.to_csv(csv_buf, index=False)
        st.download_button(
            "Download results as CSV",
            csv_buf.getvalue(),
            file_name="health_decoder_session_results.csv",
            mime="text/csv",
            width="stretch",
        )

        with st.expander("🔧 Technical details (for judges)"):
            st.write("Risk components (0..1; higher indicates stronger visual signal):")
            st.write(s.risk_components)
            st.write("Full result object (debug):")
            try:
                st.json(
                    {
                        "ok": res.ok,
                        "message": res.message,
                        "quality": asdict(res.quality),
                        "score": asdict(res.score),
                    }
                )
            except Exception:
                st.write(res)

    else:
        # If demo is selected but user hasn't clicked analyze, show a preview (optional)
        if selected_img is not None:
            st.image(_bgr_to_rgb(selected_img), caption=selected_label, width="stretch")
            st.caption("Click **Analyze Snapshot** to run analysis, or click another demo for one-click run.")
        else:
            st.caption("Upload an image or select a demo case, then click **Analyze Snapshot**.")
