from __future__ import annotations

import streamlit as st


def page_setup(title: str, icon: str = "💧") -> None:
    st.set_page_config(page_title=f"{title} | Nirmaan WaterTech", page_icon=icon, layout="wide")


def step_header(n: int, title: str, hint: str = "") -> None:
    st.markdown(f"### {n}. {title}")
    if hint:
        st.caption(hint)