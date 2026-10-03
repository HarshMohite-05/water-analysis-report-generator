from pathlib import Path

import streamlit as st

from components.authentication import require_login
from components.ui_components import page_setup
from services import report_service
from services.dataset_service import ADMIN_ROLES

page_setup("Report History")
user = require_login()
st.title("Previous Reports")

reports = report_service.list_reports(None if user["role"] in ADMIN_ROLES else user["id"])
if not reports:
    st.info("No reports yet.")
for r in reports:
    c = st.columns([2, 3, 2, 1, 1, 1])
    c[0].write(r["report_no"])
    c[1].write(r["client"])
    c[2].write(f"{r['office']} · {r['created_at']:%d-%m-%Y}")
    c[3].write(r["status"].title())
    if c[4].button("Open", key=f"open_{r['id']}"):
        st.session_state["open_report_id"] = r["id"]
        st.switch_page("pages/03_Create_Report.py")
    p = Path(r["pdf_path"]) if r["pdf_path"] else None
    if p and p.exists():
        c[5].download_button("PDF", p.read_bytes(), file_name=p.name, key=f"dl_{r['id']}")