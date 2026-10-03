"""Entry point: streamlit run app.py"""
import streamlit as st

from components.authentication import current_user, render_login
from components.ui_components import page_setup
from database.seed import seed
from services.dataset_service import DatasetError


@st.cache_resource
def _bootstrap():
    seed()
    return True


page_setup("Login")
try:
    _bootstrap()
except DatasetError as exc:
    st.error(str(exc))
    st.stop()
if current_user():
    st.switch_page("pages/02_Dashboard.py")
render_login()