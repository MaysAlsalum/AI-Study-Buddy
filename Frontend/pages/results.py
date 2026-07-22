"""Results page for AI Study Buddy."""

from __future__ import annotations
import streamlit as st


def _heading(eyebrow: str, title: str) -> str:
    return f"""
    <div class="res-section">
        <span class="res-eyebrow">{eyebrow}</span>
        <h2 class="res-title">{title}</h2>
    </div>
    """


def _security(sec: dict) -> None:
    warnings = sec.get("warnings", [])
    level    = sec.get("risk_level", "Low")
    if not warnings and level == "Low":
        return
    cls = {"Low": "sec-low", "Medium": "sec-med", "High": "sec-high"}.get(level, "sec-low")
    warns_html = "".join(f'<span class="sec-warn">{w}</span>' for w in warnings)
    st.markdown(f"""
    <div class="sec-banner {cls}">
        <span class="sec-label">Security · {level} Risk</span>
        {warns_html}
    </div>
    """, unsafe_allow_html=True)


def _summary(text: str) -> None:
    st.markdown(_heading("Document Analysis", "Summary"), unsafe_allow_html=True)
    st.markdown(f'<div class="res-card"><p class="summary-body">{text}</p></div>', unsafe_allow_html=True)


def _topics(topics: list[str]) -> None:
    st.markdown(_heading("Extracted Concepts", "Key Topics"), unsafe_allow_html=True)
    pills = "".join(f'<span class="pill">{t}</span>' for t in topics)
    st.markdown(f'<div class="res-card pills" style="padding:28px 36px;">{pills}</div>', unsafe_allow_html=True)


def _definitions(defs: list[dict]) -> None:
    st.markdown(_heading("Glossary", "Definitions"), unsafe_allow_html=True)
    rows = "".join(f"""
    <div class="def-row">
        <div class="def-term">{d["term"]}</div>
        <div class="def-body">{d["definition"]}</div>
    </div>
    """ for d in defs)
    st.markdown(f'<div class="res-card def-table">{rows}</div>', unsafe_allow_html=True)


def _quiz(quiz: list[dict]) -> None:
    st.markdown(_heading("Assessment", "Quiz"), unsafe_allow_html=True)

    for i, q in enumerate(quiz):
        choices_html = "".join(
            f'<div class="choice">'
            f'<span class="choice-letter">{chr(65+j)}</span>'
            f'<span class="choice-text">{c}</span>'
            f'</div>'
            for j, c in enumerate(q["choices"])
        )
        st.markdown(f"""
        <div class="quiz-card">
            <span class="q-num">Question {i+1}</span>
            <p class="q-text">{q["question"]}</p>
            <div class="choices">{choices_html}</div>
        </div>
        """, unsafe_allow_html=True)

        key = f"rev_{i}"
        if key not in st.session_state:
            st.session_state[key] = False

        _, bc, _ = st.columns([0.05, 0.28, 1])
        with bc:
            lbl = "Hide Answer" if st.session_state[key] else "Reveal Answer"
            if st.button(lbl, key=f"rb_{i}", use_container_width=True):
                st.session_state[key] = not st.session_state[key]
                st.rerun()

        if st.session_state[key]:
            st.markdown(f"""
            <div class="answer-reveal">
                <span class="ans-label">Correct Answer</span>
                <p class="ans-text">{q["correct_answer"]}</p>
                <p class="ans-explain">{q["explanation"]}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:8px;border-bottom:1px solid #F1F5F9;margin-bottom:24px'></div>",
                    unsafe_allow_html=True)


def _study_plan(plan: list[dict]) -> None:
    st.markdown(_heading("Learning Schedule", "Study Plan"), unsafe_allow_html=True)

    rows_html = ""
    for entry in plan:
        chips = "".join(
            f'<span class="plan-topic-chip {"review-chip" if t.startswith("Review:") else ""}">{t}</span>'
            for t in entry["topics"]
        )
        rows_html += f"""
        <div class="plan-row">
            <div class="plan-day-col">
                <span class="plan-day-label">Day</span>
                <span class="plan-day-num">{entry["day"]}</span>
            </div>
            <div class="plan-topics-col">{chips}</div>
        </div>
        """

    st.markdown(f'<div class="plan-grid">{rows_html}</div>', unsafe_allow_html=True)


def render() -> None:
    state = st.session_state.get("app_state", {})
    if not state:
        st.session_state.page = "dashboard"
        st.rerun()
        return

    file_name   = state.get("file_name", "Document")
    goal        = state.get("goal", "quiz")
    summary     = state.get("summary", "")
    key_topics  = state.get("key_topics", [])
    definitions = state.get("definitions", [])
    quiz        = state.get("quiz", [])
    study_plan  = state.get("study_plan", [])
    security    = state.get("security", {"is_safe": True, "risk_level": "Low", "warnings": []})

    # ── Navbar ──────────────────────────────────────────────────
    st.markdown(f"""
    <div class="vw-section app-nav">
        <div class="app-nav-inner">
            <span class="app-nav-brand">AI Study Buddy</span>
            <span class="app-nav-file">{file_name}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

    # ── Action bar ──────────────────────────────────────────────
    b1, b2, _ = st.columns([0.55, 0.42, 5])
    with b1:
        if st.button("New Document", key="r_new", use_container_width=True):
            st.session_state.app_state = {}
            st.session_state.page = "dashboard"
            st.rerun()
    with b2:
        if st.button("Sign Out", key="r_out", use_container_width=True):
            st.session_state.app_state = {}
            st.session_state.page = "landing"
            st.rerun()

    # ── Divider ──────────────────────────────────────────────────
    st.markdown("<hr style='border:none;border-top:1px solid #E2E8F0;margin:20px 0 8px'>",
                unsafe_allow_html=True)

    # ── Content sections ─────────────────────────────────────────
    _security(security)
    _summary(summary)
    _topics(key_topics)
    _definitions(definitions)

    if goal == "quiz" and quiz:
        _quiz(quiz)
    elif goal == "study_plan" and study_plan:
        _study_plan(study_plan)

    st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)
