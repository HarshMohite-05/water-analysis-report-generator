from __future__ import annotations

from uuid import uuid4

import pandas as pd
import streamlit as st

from components.ui_components import step_header
from services import parameter_service


def render_selector(draft: dict) -> None:
    step_header(6, "Select Analysis Parameters")
    master = parameter_service.list_parameters()
    units = {p["name"]: p["unit"] for p in master}
    for p in draft["custom_params"]:
        units.setdefault(p["name"], p["unit"])
    units.update(draft.get("units", {}))
    scope = draft.setdefault("_parameter_scope", uuid4().hex)
    options = list(units)
    selected = []
    checkbox_cols = st.columns(3)
    for i, name in enumerate(options):
        key = f"parameter_{scope}_{name}"
        if key not in st.session_state:
            st.session_state[key] = name in draft["selected_params"]
        if checkbox_cols[i % 3].checkbox(name, key=key):
            selected.append(name)
    draft["selected_params"] = selected
    with st.expander("Add custom parameter"):
        c1, c2 = st.columns(2)
        n, u = c1.text_input("Name", key="cp_name"), c2.text_input("Unit", key="cp_unit")
        if st.button("Add custom parameter") and n.strip():
            st.session_state[f"parameter_{scope}_{n.strip()}"] = True
            draft["custom_params"].append({"name": n.strip(), "unit": u.strip()})
            draft["selected_params"].append(n.strip())
            st.rerun()
    draft["units"] = units


def render_results(draft: dict) -> None:
    step_header(7, "Enter Analysis Results", "Enter measured values; units come from the Parameter Master.")
    cols = [c for c in draft["sample_cols"] if c["name"].strip()]
    if not cols or not draft["selected_params"]:
        st.info("Add at least one named sample column and one parameter above.")
        return
    rows = []
    for p in draft["selected_params"]:
        row = {"Parameter": p, "Unit": draft["units"].get(p, "")}
        for c in cols:
            row[c["name"]] = draft["values"].get(p, {}).get(str(c["id"]), "")
        rows.append(row)
    signature = (tuple(draft["selected_params"]), tuple((c["id"], c["name"]) for c in cols))
    editor = draft.get("_results_editor")
    if editor is None or editor["signature"] != signature:
        editor = {"signature": signature, "key": f"results_{uuid4().hex}",
                  "source": pd.DataFrame(rows)}
        draft["_results_editor"] = editor
    # Streamlit applies edits relative to this source. Feeding the edited result
    # back as next run's source resets the widget and loses alternate edits.
    df, key = editor["source"], editor["key"]
    edited = st.data_editor(
        df, key=key, hide_index=True, use_container_width=True,
        disabled=["Parameter"],
        column_config={c["name"]: st.column_config.TextColumn(c["name"]) for c in cols},
    )
    for _, r in edited.iterrows():
        p = r["Parameter"]
        draft["units"][p] = r["Unit"]
        draft["values"].setdefault(p, {})
        for c in cols:
            draft["values"][p][str(c["id"])] = "" if pd.isna(r[c["name"]]) else str(r[c["name"]])