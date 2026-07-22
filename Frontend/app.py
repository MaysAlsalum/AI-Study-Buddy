"""
AI Study Buddy — Streamlit Application Entry Point.

Responsibilities:
  - Configure the Streamlit page (title, layout, no sidebar).
  - Load the global CSS stylesheet.
  - Inject Google Fonts.
  - Route to the correct page based on st.session_state.page.

Pages:
  landing   → pages/landing.py
  login     → pages/login.py
  signup    → pages/signup.py
  dashboard → pages/dashboard.py
  results   → pages/results.py

Compatible with Docker and Google Cloud Run.
Run with:
    streamlit run Frontend/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------------------
# Path setup — make sure sibling modules resolve correctly
# ---------------------------------------------------------------------------

_FRONTEND_DIR = Path(__file__).parent
if str(_FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(_FRONTEND_DIR))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_css() -> None:
    """Inject the global CSS stylesheet into the Streamlit page."""
    css_path = _FRONTEND_DIR / "styles" / "main.css"
    css = css_path.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def _load_fonts() -> None:
    """Inject the Google Fonts Inter typeface link tag."""
    st.markdown(
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">',
        unsafe_allow_html=True,
    )


def _init_session_state() -> None:
    """Initialise required session state keys with default values."""
    defaults: dict[str, object] = {
        "page":      "landing",
        "user":      None,
        "app_state": {},      # Holds the full backend JSON contract state
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ---------------------------------------------------------------------------
# Page router
# ---------------------------------------------------------------------------

def _route() -> None:
    """Dispatch to the correct page renderer based on session state."""
    page = st.session_state.page

    if page == "landing":
        from pages.landing import render
        render()

    elif page == "login":
        from pages.login import render
        render()

    elif page == "signup":
        from pages.signup import render
        render()

    elif page == "dashboard":
        from pages.dashboard import render
        render()

    elif page == "results":
        from pages.results import render
        render()

    else:
        # Fallback — unknown page → redirect to landing
        st.session_state.page = "landing"
        st.rerun()


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

def main() -> None:
    """Configure and launch the AI Study Buddy Streamlit application."""
    st.set_page_config(
        page_title="AI Study Buddy",
        page_icon=None,
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    _load_fonts()
    _load_css()
    _init_session_state()
    _route()


if __name__ == "__main__":
    main()
