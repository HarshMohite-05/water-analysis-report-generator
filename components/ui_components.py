from __future__ import annotations

import streamlit as st


def page_setup(title: str, icon: str = "💧") -> None:
    st.set_page_config(page_title=f"{title} | Nirmaan WaterTech", page_icon=icon, layout="wide")
    from config.settings import DATABASE_CONFIG_WARNING
    if DATABASE_CONFIG_WARNING:
        st.warning(DATABASE_CONFIG_WARNING)


def step_header(n: int, title: str, hint: str = "") -> None:
    st.markdown(f"### {n}. {title}")
    if hint:
        st.caption(hint)