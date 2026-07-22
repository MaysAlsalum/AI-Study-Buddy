"""Landing page for AI Study Buddy."""

from __future__ import annotations
import streamlit as st

_NAVBAR = """
<div class="vw-section lp-nav">
    <div class="inner">
        <div class="lp-nav-brand">AI Study Buddy</div>
        <div class="lp-nav-links">
            <span class="lp-nav-link">Features</span>
            <span class="lp-nav-link">How It Works</span>
        </div>
    </div>
</div>
"""

_HERO = """
<div class="vw-section hero">
    <div class="inner">
        <span class="hero-badge">Powered by Multi-Agent AI</span>
        <h1 class="hero-title">
            Your Intelligent<br><em>Academic Study</em><br>Companion
        </h1>
        <p class="hero-subtitle">
            Transform any study material into structured, adaptive learning experiences.
            AI-generated summaries, personalized study plans, and smart assessments
            — all in one academic platform.
        </p>
    </div>
</div>
"""

_FEATURES = """
<div class="vw-section features">
    <div class="inner">
        <div class="features-heading">
            <span class="eyebrow">Capabilities</span>
            <h2>Everything You Need<br>to Study Smarter</h2>
            <p>A complete multi-agent AI system designed to accelerate
               learning and improve academic outcomes.</p>
        </div>
        <div class="feat-grid">
            <div class="feat-card">
                <span class="feat-num">01</span>
                <h3 class="feat-title">Intelligent Summarization</h3>
                <p class="feat-desc">Automatically condenses uploaded documents into
                structured, topic-focused summaries that highlight the most critical
                concepts for efficient review.</p>
            </div>
            <div class="feat-card">
                <span class="feat-num">02</span>
                <h3 class="feat-title">AI-Powered Assessments</h3>
                <p class="feat-desc">Generates adaptive multiple-choice questions
                calibrated to your study material, reinforcing knowledge through
                targeted practice.</p>
            </div>
            <div class="feat-card">
                <span class="feat-num">03</span>
                <h3 class="feat-title">Personalized Study Planning</h3>
                <p class="feat-desc">Produces day-by-day study schedules with spaced
                repetition built in, optimized for your available study time.</p>
            </div>
            <div class="feat-card">
                <span class="feat-num">04</span>
                <h3 class="feat-title">Secure Document Processing</h3>
                <p class="feat-desc">Handles PDF uploads through a validated, sanitized
                pipeline that protects your data before any AI processing takes place.</p>
            </div>
            <div class="feat-card">
                <span class="feat-num">05</span>
                <h3 class="feat-title">Multi-Agent Intelligence</h3>
                <p class="feat-desc">Coordinates specialized AI agents through a LangGraph
                workflow — each with a distinct academic role — for consistent,
                high-quality outputs.</p>
            </div>
            <div class="feat-card">
                <span class="feat-num">06</span>
                <h3 class="feat-title">Progress Tracking</h3>
                <p class="feat-desc">Monitors completed sessions and topic mastery over
                time so you can direct effort precisely where improvement is needed.</p>
            </div>
        </div>
    </div>
</div>
"""

_HOW = """
<div class="vw-section how">
    <div class="inner">
        <span class="eyebrow">Process</span>
        <h2>How It Works</h2>
        <div class="steps">
            <div class="step">
                <div class="step-num">1</div>
                <h3>Upload Study Material</h3>
                <p>Submit your PDF or lecture notes through the secure document portal.
                All content is validated and sanitized before processing.</p>
            </div>
            <div class="step">
                <div class="step-num">2</div>
                <h3>AI Analyzes the Document</h3>
                <p>A coordinated pipeline of specialized agents processes your material —
                extracting key concepts, assessing difficulty, and structuring the content.</p>
            </div>
            <div class="step">
                <div class="step-num">3</div>
                <h3>Receive Your Learning Package</h3>
                <p>Get a structured summary, adaptive practice questions, and a
                personalized multi-day study plan with spaced repetition built in.</p>
            </div>
        </div>
    </div>
</div>
"""

_WHY = """
<div class="vw-section why">
    <div class="inner">
        <div class="why-grid">
            <div class="why-left">
                <span class="eyebrow">Academic Value</span>
                <h2>Designed for Serious Learners</h2>
            </div>
            <div class="why-right">
                <p>AI Study Buddy applies established principles from cognitive science —
                spaced repetition, active recall, and deliberate practice — within a
                modern AI-driven workflow. Rather than replacing the effort of studying,
                it directs that effort more precisely.</p>
                <p>Built on a multi-agent LangGraph architecture with production-grade
                security, the system delivers consistent, reliable academic support at
                scale.</p>
                <div class="why-stats">
                    <div class="stat">
                        <h3>3x</h3>
                        <p>Faster concept review with AI summarization</p>
                    </div>
                    <div class="stat">
                        <h3>5+</h3>
                        <p>Specialized AI agents working in coordination</p>
                    </div>
                    <div class="stat">
                        <h3>100%</h3>
                        <p>Input validated before any LLM invocation</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
"""

_CTA = """
<div class="vw-section cta">
    <div class="inner">
        <h2>Begin Your Learning Journey</h2>
        <p>Join a platform built for academic excellence. Your study materials
        become structured, intelligent learning experiences.</p>
    </div>
</div>
"""

_FOOTER = """
<div class="vw-section lp-footer">
    <div class="inner lp-footer-inner" style="display:flex;align-items:center;justify-content:space-between;">
        <span class="lp-footer-brand">AI Study Buddy</span>
        <span class="lp-footer-copy">Built with LangGraph · LangChain · Gemini 2.5 Flash</span>
    </div>
</div>
"""


def render() -> None:
    st.markdown(_NAVBAR, unsafe_allow_html=True)
    st.markdown(_HERO, unsafe_allow_html=True)

    # Dark zone — extends hero background behind the Streamlit button
    st.markdown('<div class="vw-section hero-btn-zone"></div>', unsafe_allow_html=True)

    # Hero CTA button (Streamlit widget — must be outside HTML block)
    _, c, _ = st.columns([2.5, 1, 2.5])
    with c:
        if st.button("Get Started", key="hero_cta", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()

    # Close dark zone below button
    st.markdown('<div class="vw-section" style="background:#0F172A;height:60px;margin-top:-12px;"></div>',
                unsafe_allow_html=True)

    st.markdown(_FEATURES, unsafe_allow_html=True)
    st.markdown(_HOW, unsafe_allow_html=True)
    st.markdown(_WHY, unsafe_allow_html=True)
    st.markdown(_CTA, unsafe_allow_html=True)

    # CTA button
    _, c, _ = st.columns([2.5, 1, 2.5])
    with c:
        if st.button("Continue to Sign In", key="cta_btn", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()

    st.markdown(_FOOTER, unsafe_allow_html=True)
