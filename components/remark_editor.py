from __future__ import annotations

import streamlit as st

from components.form_state import field_key
from components.ui_components import step_header
from services import remark_ai_service


def render(draft: dict) -> None:
    step_header(8, "Technician Remarks", "Write a rough note in your own words, then refine with AI.")
    draft["remark_raw"] = st.text_area("Technician Remark (raw input)", key=field_key(draft, "remark_raw", draft.get("remark_raw", "")), height=80)

    st.markdown("**AI-refined remark**")
    c1, c2 = st.columns([1, 1])
    if c1.button("✨ Improve with AI", disabled=not draft["remark_raw"].strip()):
        res = remark_ai_service.improve_remark(draft["remark_raw"])
        draft["remark_suggestion"] = res["text"]
        draft["remark_source"] = res["source"]
        if res["source"] == "fallback":
            st.warning(f"AI unavailable, basic clean-up applied. ({res['error']})")
    if c2.button("🔄 Regenerate", disabled=not draft.get("remark_suggestion")):
        res = remark_ai_service.improve_remark(draft["remark_raw"], previous=draft["remark_suggestion"])
        draft["remark_suggestion"] = res["text"]
        draft["remark_source"] = res["source"]
        if res["source"] == "fallback":
            st.warning(f"AI unavailable, basic clean-up applied. ({res['error']})")

    if draft.get("remark_suggestion"):
        draft["remark_suggestion"] = st.text_area("Suggested remark (editable)", draft["remark_suggestion"], height=90)
        if st.button("✅ Accept"):
            draft["remark_final"] = draft["remark_suggestion"]
            st.session_state[field_key(draft, "remark_final")] = draft["remark_suggestion"]
    draft["remark_final"] = st.text_area(
        "Final remark used in report", key=field_key(draft, "remark_final", draft.get("remark_final", "")), height=80,
        help="Write each remark on a separate line for separate bullet points. If left empty, the raw remark is used.")
