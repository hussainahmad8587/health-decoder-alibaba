# app/pages/2_How_it_Works.py
from __future__ import annotations

import streamlit as st


def _page_header() -> None:
    st.set_page_config(
        page_title="How it Works — Health Decoder",
        page_icon="ℹ️",
        layout="wide",
    )

    st.markdown(
        """
        <style>
          .hd-page-wrap{
            padding: 18px 22px;
            border-radius: 14px;
            background: linear-gradient(135deg, rgba(20,30,55,0.65), rgba(10,12,18,0.65));
            border: 1px solid rgba(255,255,255,0.06);
            box-shadow: 0 12px 26px rgba(0,0,0,0.35);
            margin-bottom: 14px;
          }
          .hd-page-title{
            margin: 0;
            font-size: 34px;
            font-weight: 800;
            letter-spacing: -0.8px;
            color: rgba(255,255,255,0.96);
            line-height: 1.15;
          }
          .hd-page-sub{
            margin: 8px 0 0 0;
            font-size: 14px;
            color: rgba(255,255,255,0.78);
          }
          .hd-kpi{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 10px;
            margin-top: 14px;
          }
          .hd-kpi .card{
            padding: 12px 12px;
            border-radius: 12px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
          }
          .hd-kpi .label{
            font-size: 11px;
            letter-spacing: 0.35px;
            text-transform: uppercase;
            color: rgba(255,255,255,0.62);
            margin-bottom: 6px;
          }
          .hd-kpi .value{
            font-size: 16px;
            font-weight: 800;
            color: rgba(255,255,255,0.92);
            line-height: 1.2;
          }

          @media (max-width: 900px){
            .hd-kpi{ grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .hd-page-title{ font-size: 28px; }
          }
        </style>

        <div class="hd-page-wrap">
          <div class="hd-page-title">How it Works</div>
          <div class="hd-page-sub">
            A clear overview of the Health Decoder flow for users and judges.
          </div>

          <div class="hd-kpi">
            <div class="card">
              <div class="label">Input</div>
              <div class="value">Single selfie (JPG/PNG)</div>
            </div>
            <div class="card">
              <div class="label">Output</div>
              <div class="value">Score • Category • Confidence</div>
            </div>
            <div class="card">
              <div class="label">Explainability</div>
              <div class="value">Optional overlay</div>
            </div>
            <div class="card">
              <div class="label">Privacy</div>
              <div class="value">No identity recognition</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _content() -> None:
    st.info("Wellness guidance only. Not a medical diagnosis.")

    left, right = st.columns([1.05, 0.95], gap="large")

    with left:
        st.markdown("## End-to-end flow")
        st.markdown(
            """
1. **Capture / Upload**
   - User uploads a clear selfie image (front-facing, good lighting).
2. **Quality checks**
   - The system evaluates **lighting** and **sharpness**.
   - If quality is too poor, it blocks analysis and provides capture guidance.
3. **Region-focused analysis**
   - The system focuses on facial sub-regions (e.g., eyes/lips/skin areas) to extract visual cues.
4. **Scoring**
   - Extracted signals are converted into:
     - **Wellness score (0–100)**
     - **Category** (e.g., Low / Medium / Good)
     - **Confidence**
5. **User guidance**
   - Suggestions are generated based on the category and the chosen user scenario
     (Office, Athlete, Traveler, Parent).
            """
        )

        st.markdown("## What we show to the user")
        c1, c2, c3 = st.columns(3)
        c1.metric("Wellness Score", "0–100")
        c2.metric("Category", "Low / Medium / Good")
        c3.metric("Confidence", "Low / Medium / High")

        with st.expander("Optional: Explainability overlay"):
            st.markdown(
                """
When available, an overlay can highlight which regions influenced the score more strongly.
This improves transparency for judging and helps users understand that the system is
**not performing identity recognition**.
                """
            )

    with right:
        st.markdown("## Capture tips (recommended)")
        st.markdown(
            """
- Use **front-facing light** (avoid strong backlight)
- Keep the camera **steady** (reduce blur)
- Ensure **eyes, nose, and mouth** are visible
- Avoid extreme close-ups
            """
        )

        st.markdown("## Reliability notes")
        st.markdown(
            """
- Scores are most consistent when users keep **similar lighting + distance** across checks.
- Heavy makeup, strong filters, and motion blur can reduce reliability.
- The system is designed for **wellness guidance**, not clinical use.
            """
        )

        st.markdown("## For judges (demo expectations)")
        st.markdown(
            """
- Demo buttons load curated cases for consistent evaluation.
- CSV export provides session-level results for inspection.
- Technical details panel shows risk components and debug fields.
            """
        )


def main() -> None:
    _page_header()
    _content()


if __name__ == "__main__":
    main()
