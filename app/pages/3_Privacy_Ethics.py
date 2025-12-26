# app/pages/3_Privacy_Ethics.py
from __future__ import annotations

import streamlit as st


def _page_header() -> None:
    st.set_page_config(
        page_title="Privacy & Ethics — Health Decoder",
        page_icon="🔒",
        layout="wide",
    )

    st.markdown(
        """
        <style>
          .hd-hero{
            padding: 18px 22px;
            border-radius: 14px;
            background: linear-gradient(135deg, rgba(25,55,45,0.55), rgba(10,12,18,0.68));
            border: 1px solid rgba(255,255,255,0.06);
            box-shadow: 0 12px 26px rgba(0,0,0,0.35);
            margin-bottom: 14px;
          }
          .hd-hero h1{
            margin: 0;
            font-size: 34px;
            font-weight: 850;
            letter-spacing: -0.8px;
            color: rgba(255,255,255,0.96);
            line-height: 1.15;
          }
          .hd-hero p{
            margin: 8px 0 0 0;
            font-size: 14px;
            color: rgba(255,255,255,0.78);
          }
          .hd-grid{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px;
            margin-top: 14px;
          }
          .hd-card{
            padding: 14px;
            border-radius: 12px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
          }
          .hd-card .t{
            font-weight: 800;
            color: rgba(255,255,255,0.92);
            margin-bottom: 6px;
          }
          .hd-card .b{
            font-size: 13px;
            color: rgba(255,255,255,0.78);
            line-height: 1.55;
          }
          @media (max-width: 900px){
            .hd-grid{ grid-template-columns: 1fr; }
            .hd-hero h1{ font-size: 28px; }
          }
        </style>

        <div class="hd-hero">
          <h1>Privacy & Ethics</h1>
          <p>
            Clear, judge-friendly commitments about data handling, transparency, and responsible use.
          </p>

          <div class="hd-grid">
            <div class="hd-card">
              <div class="t">No Identity Recognition</div>
              <div class="b">The app does not attempt to identify, verify, or match a person.</div>
            </div>
            <div class="hd-card">
              <div class="t">Minimal Data</div>
              <div class="b">Process only what is needed to generate a wellness score and guidance.</div>
            </div>
            <div class="hd-card">
              <div class="t">Not a Diagnosis</div>
              <div class="b">Results are wellness guidance, not medical or clinical decisions.</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _content() -> None:
    st.info("Wellness guidance only. Not a medical diagnosis.")

    st.markdown("## Core principles")
    st.markdown(
        """
- **Privacy-first by design:** avoid storing raw images unless explicitly required.
- **Transparency:** explain what the model uses (visual cues) and what it does not do (identity).
- **User control:** users can clear session history and reset baseline within the app.
- **Safety framing:** the app is not intended for emergencies or medical decision-making.
        """
    )

    left, right = st.columns([1.05, 0.95], gap="large")

    with left:
        st.markdown("## Data handling (recommended)")
        st.markdown(
            """
### Default behavior (best for demo + public hosting)
- Do **not** persist uploaded images.
- Keep only **session-level** metrics in memory (score, category, brightness, blur) for trend visualization.
- Allow users to download their results as CSV (client-controlled export).

### If persistence is required (enterprise scenario)
- Store only what’s needed and define retention.
- Prefer:
  - **Aggregated metrics** over raw images
  - **Short retention windows**
  - **Access controls** and audit logs
            """
        )

        with st.expander("What gets logged (suggested minimal fields)"):
            st.markdown(
                """
- Timestamp
- Wellness score (0–100)
- Category (Low/Medium/Good)
- Confidence
- Capture quality metrics (brightness mean, blur variance)
- Scenario selection (Office/Athlete/Traveler/Parent)

Avoid: names, emails, face embeddings, or raw image bytes.
                """
            )

    with right:
        st.markdown("## Responsible use")
        st.markdown(
            """
- **Not for diagnosis**: should not replace clinical evaluation.
- **Not for emergency**: direct users to professional services when necessary.
- **Model limitations**:
  - lighting and blur impact reliability
  - camera quality varies by device
  - cosmetic filters and heavy makeup can distort cues
            """
        )

        st.markdown("## Bias & fairness considerations")
        st.markdown(
            """
- Validate across diverse lighting conditions and skin tones.
- Measure performance stability across demographic slices where ethically permissible.
- Provide clear UX fallbacks when capture quality is poor (block analysis + guidance).
            """
        )

        st.markdown("## Explainability")
        st.markdown(
            """
When available, show an **overlay** to indicate which regions contributed more strongly.
This is useful for trust and judging, and reinforces that the system focuses on *signals* not identity.
            """
        )

    st.markdown("---")
    st.markdown("## Plain-language promise (for users)")
    st.success(
        "We analyze your photo to provide wellness guidance. "
        "We do not identify you. "
        "We recommend not storing images, and we only keep minimal session data to show trends."
    )


def main() -> None:
    _page_header()
    _content()


if __name__ == "__main__":
    main()
