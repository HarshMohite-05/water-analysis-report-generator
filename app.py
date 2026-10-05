"""Entry point: streamlit run app.py"""
import logging

import streamlit as st

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("water_reports.startup")
logger.info("Loading application modules")

from components.authentication import current_user, render_login
from components.ui_components import page_setup
from database.seed import seed
from services.dataset_service import DatasetError


@st.cache_resource
def _bootstrap():
    logger.info("Initializing application data")
    seed()
    logger.info("Application data ready")
    return True


page_setup("Login")
try:
    _bootstrap()
except DatasetError as exc:
    st.error(str(exc))
    st.stop()
if current_user():
    st.switch_page("pages/02_Dashboard.py")
logger.info("Rendering login page")
render_login()