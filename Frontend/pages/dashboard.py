"""Dashboard page for AI Study Buddy."""

from __future__ import annotations
import time
import streamlit as st


def _process(file_name: str, study_days: int, goal: str) -> dict:
    from mock_data import MOCK_QUIZ_STATE, MOCK_STUDY_PLAN_STATE
    state = dict(MOCK_QUIZ_STATE if goal == "quiz" else MOCK_STUDY_PLAN_STATE)
    state["file_name"]  = file_name
    state["study_days"] = study_days
    state["goal"]       = goal
    return state


def render() -> None:
    # ── Navbar ──────────────────────────────────────────────────
    st.markdown("""
    <div class="vw-section app-nav">
        <div class="app-nav-inner">
            <span class="app-nav-brand">AI Study Buddy</span>
            <span class="app-nav-file">Dashboard</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Page header ─────────────────────────────────────────────
    st.markdown("""
    <div class="vw-section dash-hero">
        <h1>Process a Study Document</h1>
        <p>Upload your material, choose your goal, and let the AI agents
        generate exactly what you need.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Body ────────────────────────────────────────────────────
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

    left_col, right_col = st.columns([1.55, 1], gap="large")

    # ── Left: Upload ─────────────────────────────────────────────
    with left_col:
        st.markdown('<div class="dash-card">', unsafe_allow_html=True)
        st.markdown('<span class="card-eyebrow">Study Document</span>', unsafe_allow_html=True)
        st.markdown('<span class="card-hint">PDF format · max 200 MB</span>', unsafe_allow_html=True)

        uploaded = st.file_uploader(
            label="pdf_label",
            type=["pdf"],
            label_visibility="collapsed",
            key="pdf_upload",
        )

        if uploaded:
            st.markdown(f"""
            <div class="file-chip">
                <span class="file-chip-name">{uploaded.name}</span>
                <span class="file-chip-size">{uploaded.size / 1024:.1f} KB</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Right: Config ────────────────────────────────────────────
    with right_col:
        st.markdown('<div class="dash-card">', unsafe_allow_html=True)
        st.markdown('<span class="card-eyebrow">Session Configuration</span>', unsafe_allow_html=True)

        st.markdown('<span class="field-label">Output Goal</span>', unsafe_allow_html=True)
        st.markdown('<span class="field-hint">The AI generates only the selected output.</span>', unsafe_allow_html=True)

        goal_label = st.radio(
            "goal",
            ["Generate Quiz", "Generate Study Plan"],
            label_visibility="collapsed",
            key="goal_radio",
        )

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        is_plan = goal_label == "Generate Study Plan"
        st.markdown('<span class="field-label">Study Days</span>', unsafe_allow_html=True)
        st.markdown('<span class="field-hint">Days available for your plan (1–30). Applies to Study Plan only.</span>', unsafe_allow_html=True)

        study_days = st.number_input(
            "days",
            min_value=1, max_value=30, value=5, step=1,
            label_visibility="collapsed",
            disabled=not is_plan,
            key="study_days_input",
        )

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Process button ───────────────────────────────────────────
    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
    _, btn, _ = st.columns([1.5, 1, 1.5])
    with btn:
        clicked = st.button(
            "Process Document",
            key="process_btn",
            use_container_width=True,
            disabled=uploaded is None,
        )

    if not uploaded:
        st.markdown(
            "<p style='text-align:center;color:#94A3B8;font-size:14px;margin-top:8px;'>"
            "Upload a PDF file to enable processing.</p>",
            unsafe_allow_html=True,
        )

    if clicked and uploaded:
        goal_val = "quiz" if goal_label == "Generate Quiz" else "study_plan"
        with st.spinner("Analyzing document with AI agents..."):
            time.sleep(1.4)
            st.session_state.app_state = _process(uploaded.name, int(study_days), goal_val)
        st.session_state.page = "results"
        st.rerun()

    # ── Sign out ─────────────────────────────────────────────────
    st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)
    _, so, _ = st.columns([3, 0.7, 3])
    with so:
        if st.button("Sign Out", key="dash_out", use_container_width=True):
            st.session_state.page = "landing"
            st.rerun()

    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
