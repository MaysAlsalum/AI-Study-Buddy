"""Sign Up page for AI Study Buddy."""

from __future__ import annotations
import streamlit as st

_NAV = """
<div class="vw-section auth-nav">
    <span class="auth-nav-brand">AI Study Buddy</span>
</div>
"""

_HEAD = """
<div class="auth-head">
    <h1>Create Account</h1>
    <p>Start your personalized academic learning experience</p>
</div>
"""

_DIVIDER = """<div class="auth-divider">Already have an account?</div>"""


def _validate(name, email, pw, pw2):
    errs = []
    if not name or not name.strip():       errs.append("Full name is required.")
    if not email or "@" not in email:      errs.append("A valid email address is required.")
    if not pw or len(pw) < 8:             errs.append("Password must be at least 8 characters.")
    if pw != pw2:                          errs.append("Passwords do not match.")
    return errs


def render() -> None:
    st.markdown(_NAV, unsafe_allow_html=True)
    st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown(_HEAD, unsafe_allow_html=True)

        with st.form("signup_form"):
            name  = st.text_input("Full Name",        placeholder="Your full name",      key="s_name")
            email = st.text_input("Email Address",     placeholder="you@university.edu",  key="s_email")
            pw    = st.text_input("Password",          placeholder="Minimum 8 characters",key="s_pw",  type="password")
            pw2   = st.text_input("Confirm Password",  placeholder="Repeat your password",key="s_pw2", type="password")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Create Account", use_container_width=True)

        if submitted:
            errs = _validate(name, email, pw, pw2)
            if errs:
                for e in errs:
                    st.error(e)
            else:
                st.success("Account created. Redirecting to sign in...")
                st.session_state.page = "login"
                st.rerun()

        st.markdown(_DIVIDER, unsafe_allow_html=True)
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        if st.button("Sign In to Existing Account", key="go_login", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        _, bc, _ = st.columns([1, 2, 1])
        with bc:
            if st.button("Back to Home", key="s_back", use_container_width=True):
                st.session_state.page = "landing"
                st.rerun()
