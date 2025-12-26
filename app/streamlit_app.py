# app/streamlit_app.py
from __future__ import annotations

from pathlib import Path
import streamlit as st


def _apply_global_style() -> None:
    """Optional: light global styling for consistency across pages."""
    st.markdown(
        """
        <style>
          /* Make the sidebar slightly cleaner */
          section[data-testid="stSidebar"] {
            border-right: 1px solid rgba(255,255,255,0.06);
          }

          /* Slightly reduce top padding so headers sit nicer */
          .block-container {
            padding-top: 1.2rem;
          }

          /* Hide the default 'streamlit app' label at the top of sidebar (varies by version) */
          [data-testid="stSidebarNav"] > div:first-child {
            padding-top: 0.75rem;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    # IMPORTANT:
    # - Do not import cv2 or your model pipeline here.
    # - Keep entry file lightweight; let each page import what it needs.

    st.set_page_config(
        page_title="Health Decoder",
        page_icon="💧",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    _apply_global_style()

    # Landing content (optional). Users will still navigate via the Pages sidebar.
    st.markdown(
        """
        <div style="
            padding: 18px 22px;
            border-radius: 14px;
            background: linear-gradient(135deg, rgba(20,30,55,0.55), rgba(10,12,18,0.70));
            border: 1px solid rgba(255,255,255,0.06);
            box-shadow: 0 12px 26px rgba(0,0,0,0.35);
            margin-bottom: 14px;
        ">
          <div style="
              font-size: 34px;
              font-weight: 850;
              letter-spacing: -0.8px;
              color: rgba(255,255,255,0.96);
              line-height: 1.15;
          ">
            Health Decoder
          </div>
          <div style="
              margin-top: 8px;
              font-size: 14px;
              color: rgba(255,255,255,0.78);
          ">
            Wellness insights from a single snapshot • Explainable • Privacy-first
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info("Use the left sidebar to open **Demo**, **How it Works**, or **Privacy & Ethics**.")

    # Optional: quick links hint (works across Streamlit versions)
    st.markdown(
        """
        **Recommended flow (for judges):**
        1. Open **Demo** → try demo buttons → run analysis  
        2. Open **How it Works** → confirm methodology  
        3. Open **Privacy & Ethics** → review responsible-use commitments
        """
    )

    # Sanity checks for repo structure (non-blocking)
    pages_dir = Path(__file__).resolve().parent / "pages"
    if not pages_dir.exists():
        st.warning("Pages folder not found at `app/pages/`. Multipage navigation may not appear.")


if __name__ == "__main__":
    main()
