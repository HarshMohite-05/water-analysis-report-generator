from datetime import date

import streamlit as st

from components import (client_form, office_selector, parameter_table, remark_editor,
                        report_preview, sample_form)
from components.authentication import require_login
from components.ui_components import page_setup
from config.constants import DEFAULT_SELECTED
from services import report_service, template_service

page_setup("Create Report")
user = require_login()
template_service.ensure_templates()


def new_draft() -> dict:
    return dict(
        report_id=None, third_party_sample=False, office=user.get("default_office", "Mumbai Office"),
        collection_date=date.today(), analysis_date=date.today(),
        client_name="", client_address="", contact_person="", client_email="", assigned_technician="", assigned_employee_id=None, technician=user["full_name"],
        sample_cols=[{"id": 1, "name": "RO Feed Water"}, {"id": 2, "name": "RO 3rd Stage Reject Water"}],
        next_col_id=2, selected_params=list(DEFAULT_SELECTED), custom_params=[], units={}, values={},
        include_remarks=True, remark_raw="", remark_suggestion="", remark_final="",
    )


def draft_from_report(rep: dict) -> dict:
    """Rebuild UI state from a saved payload."""
    d, data = new_draft(), rep["data"]
    d.update(include_remarks=data.get("include_remarks", True), third_party_sample=data.get("third_party_sample", False), report_id=rep["id"], office=data["office"], collection_date=data["collection_date"],
             analysis_date=data["analysis_date"], client_name=data["client_name"],
             client_address=data.get("client_address", ""), contact_person=data.get("contact_person", ""),
             client_email=data.get("client_email", ""), assigned_technician=data.get("assigned_technician", ""),
             assigned_employee_id=data.get("assigned_employee_id"), remark_raw=data.get("remark_raw", ""), remark_final=data.get("remark_final", ""))
    names = data["sample_columns"]
    d["sample_cols"] = [{"id": i + 1, "name": n} for i, n in enumerate(names)]
    d["next_col_id"] = len(names)
    d["selected_params"] = [p["name"] for p in data["parameters"]]
    d["custom_params"] = [{"name": p["name"], "unit": p["unit"]} for p in data["parameters"]]
    d["units"] = {p["name"]: p["unit"] for p in data["parameters"]}
    d["values"] = {p["name"]: {str(i + 1): p["values"].get(n, "") for i, n in enumerate(names)}
                   for p in data["parameters"]}
    return d


def build_payload(d: dict) -> dict:
    cols = [c for c in d["sample_cols"] if c["name"].strip()]
    params = [dict(name=p, unit=d["units"].get(p, ""),
                   values={c["name"].strip(): d["values"].get(p, {}).get(str(c["id"]), "") for c in cols})
              for p in d["selected_params"]]
    return report_service.normalize_report_payload(dict(third_party_sample=d.get("third_party_sample", False), office=d["office"], client_name=d["client_name"], client_address=d["client_address"],
                contact_person=d["contact_person"], client_email=d.get("client_email", ""),
                assigned_technician=d.get("assigned_technician", ""), assigned_employee_id=d.get("assigned_employee_id"),
                generated_by_employee_id=user["employee_id"], collection_date=d["collection_date"],
                analysis_date=d["analysis_date"], technician=d["technician"], technician_email=user["email"],
                sample_columns=[c["name"].strip() for c in cols], parameters=params,
                include_remarks=d.get("include_remarks", True), remark_raw=d["remark_raw"], remark_final=d["remark_final"] or d["remark_raw"]))


# load a report chosen on the history page, otherwise start (or keep) a draft
if "open_report_id" in st.session_state:
    rep = report_service.get_report(st.session_state.pop("open_report_id"))
    if rep:
        st.session_state["draft"] = draft_from_report(rep)
if "draft" not in st.session_state:
    st.session_state["draft"] = new_draft()
draft = st.session_state["draft"]

st.title("Create New Report")
top = st.columns([1, 5])
if top[0].button("New blank report"):
    st.session_state["draft"] = new_draft()
    st.session_state.pop("preview_pages", None)
    st.rerun()

client_form.render(draft, user["full_name"])
office_selector.render(draft)
sample_form.render(draft)
parameter_table.render_selector(draft)
parameter_table.render_results(draft)
remark_editor.render(draft)

payload = build_payload(draft)
st.divider()
errors = report_service.validate(payload)
for e in errors:
    st.error(e)

if st.button("💾 Save draft", disabled=bool(errors)):
    draft["report_id"] = report_service.save_report(payload, user["id"], draft["report_id"], "draft")
    st.success("Draft saved.")

if not errors:
    report_preview.render_preview(payload)

    def _final(pdf_path: str) -> None:
        draft["report_id"] = report_service.save_report(
            payload, user["id"], draft["report_id"], "final", pdf_path)

    report_preview.render_generate(payload, _final)