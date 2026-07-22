"""Login page for AI Study Buddy."""

from __future__ import annotations
import streamlit as st

_NAV = """
<div class="vw-section auth-nav">
    <span class="auth-nav-brand">AI Study Buddy</span>
</div>
"""

_HEAD = """
<div class="auth-head">
    <h1>Sign In</h1>
    <p>Continue your academic learning journey</p>
</div>
"""

_DIVIDER = """<div class="auth-divider">Don't have an account?</div>"""


def render() -> None:
    st.markdown(_NAV, unsafe_allow_html=True)
    st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown(_HEAD, unsafe_allow_html=True)

        with st.form("login_form"):
            email    = st.text_input("Email Address",  placeholder="you@university.edu", key="l_email")
            password = st.text_input("Password",        placeholder="Your password",       key="l_pass", type="password")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Sign In", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("Please enter your email and password.")
            else:
                st.session_state.user = {"email": email}
                st.session_state.page = "dashboard"
                st.rerun()

        st.markdown(_DIVIDER, unsafe_allow_html=True)
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        if st.button("Create an Account", key="go_signup", use_container_width=True):
            st.session_state.page = "signup"
            st.rerun()

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        _, bc, _ = st.columns([1, 2, 1])
        with bc:
            if st.button("Back to Home", key="l_back", use_container_width=True):
                st.session_state.page = "landing"
                st.rerun()
