from __future__ import annotations

import streamlit as st

from services.dataset_service import ADMIN_ROLES, DatasetError
from services import auth_service


def current_user():
    user = st.session_state.get("user")
    if user:
        try:
            user = auth_service.refresh_user(user["id"])
        except DatasetError as exc:
            st.error(str(exc))
            user = None
        if user:
            st.session_state["user"] = user
        else:
            logout()
    return user


def logout() -> None:
    for k in list(st.session_state.keys()):
        del st.session_state[k]


def require_login(admin_only: bool = False) -> dict:
    user = current_user()
    if not user:
        st.warning("Please log in to continue.")
        st.page_link("pages/01_Login.py", label="Go to Login")
        st.stop()
    if admin_only and user["role"] not in ADMIN_ROLES:
        st.error("Admin or Director access required.")
        st.stop()
    sidebar_user(user)
    return user


def sidebar_user(user: dict) -> None:
    with st.sidebar:
        st.markdown(f"**{user['full_name']}**  \n{user['role'].title()}")
        if st.button("Logout", key="logout_btn"):
            logout()
            st.switch_page("pages/01_Login.py")


def render_login() -> None:
    st.title("Nirmaan WaterTech Solutions")
    st.caption("Water Analysis Report Generator")
    with st.form("login_form"):
        ident = st.text_input("Employee ID / Email")
        pw = st.text_input("Password", type="password")
        ok = st.form_submit_button("Login", type="primary")
    if ok:
        try:
            user = auth_service.authenticate(ident, pw)
        except DatasetError as exc:
            st.error(str(exc))
            return
        if user:
            st.session_state["user"] = user
            st.switch_page("pages/02_Dashboard.py")
        else:
            st.error("Invalid credentials.")