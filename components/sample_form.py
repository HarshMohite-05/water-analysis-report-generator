from __future__ import annotations

import streamlit as st

from components.form_state import field_key
from components.ui_components import step_header
from config.constants import MAX_SAMPLE_COLUMNS


def render(draft: dict) -> None:
    """draft['sample_cols'] = [{'id': int, 'name': str}] (stable ids keep values on rename)."""
    step_header(5, "Sample / Source Columns", "e.g. Raw Water, Treated Water, RO Feed Water")
    cols = draft["sample_cols"]
    remove = None
    for c in cols:
        a, b = st.columns([6, 1])
        c["name"] = a.text_input("Column name", key=field_key(draft, f"colname_{c['id']}", c["name"]),
                                 label_visibility="collapsed")
        if b.button("🗑", key=f"coldel_{c['id']}", help="Remove column") and len(cols) > 1:
            remove = c
    if remove:
        cols.remove(remove)
        st.rerun()
    if len(cols) < MAX_SAMPLE_COLUMNS and st.button("＋ Add Sample Column"):
        draft["next_col_id"] += 1
        cols.append({"id": draft["next_col_id"], "name": ""})
        st.rerun()