import streamlit as st

from components.authentication import require_login
from components.ui_components import page_setup
from services import report_service
from services.dataset_service import ADMIN_ROLES

page_setup("Dashboard")
user = require_login()

st.title(f"Welcome, {user['full_name']}")
reports = report_service.list_reports(None if user["role"] in ADMIN_ROLES else user["id"])
c1, c2, c3 = st.columns(3)
c1.metric("Reports", len(reports))
c2.metric("Final", sum(r["status"] == "final" for r in reports))
c3.metric("Drafts", sum(r["status"] == "draft" for r in reports))

st.divider()
a, b, c = st.columns(3)
a.page_link("pages/03_Create_Report.py", label="➕ Create New Report")
b.page_link("pages/04_Report_History.py", label="🕘 Previous Reports")
if user["role"] in ADMIN_ROLES:
    c.page_link("pages/05_Admin_Panel.py", label="⚙️ Admin (Clients / Parameters / Users)")