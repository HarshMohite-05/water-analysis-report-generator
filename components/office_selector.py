from __future__ import annotations

import streamlit as st

from config.settings import OFFICES
from components.form_state import field_key
from components.ui_components import step_header


def render(draft: dict) -> None:
    step_header(3, "Select Office (Template)",
                "Same report layout for every office; only footer address and seal change.")
    offices = list(OFFICES)
    draft["office"] = st.selectbox(
        "Office / Location", offices,
        key=field_key(draft, "office", draft.get("office", offices[0])),
    )
    for line in OFFICES[draft["office"]]["footer_lines"][1:2]:
        st.caption(f"Footer address: {line}")