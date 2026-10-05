from __future__ import annotations

from pathlib import Path
from copy import deepcopy

import streamlit as st

from components.ui_components import step_header
from config.settings import GENERATED_DIR, TEMP_DIR
from report_engine import docx_generator, pdf_converter
from services import template_service
from utils.file_utils import unique_path

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

def build_docx(payload: dict, out_dir: Path, stem: str) -> Path:
    tpl, seal = template_service.template_paths(payload["office"])
    return docx_generator.generate_docx(payload, tpl, seal, unique_path(out_dir, stem, ".docx"))


def render_preview(payload: dict) -> None:
    step_header(10, "Preview Report", "Exact template used for the final PDF.")
    if st.session_state.get("preview_payload") != payload:
        st.session_state.pop("preview_pages", None)
    if st.button("🔍 Preview Full Report"):
        try:
            docx_path = build_docx(payload, TEMP_DIR, "preview")
            pdf = pdf_converter.docx_to_pdf(docx_path, TEMP_DIR)
            st.session_state["preview_pages"] = pdf_converter.render_pages(pdf)
            st.session_state["preview_payload"] = deepcopy(payload)
        except pdf_converter.PdfConversionError as e:
            st.session_state.pop("preview_pages", None)
            st.error(str(e))
    pages = st.session_state.get("preview_pages")
    if pages:
        st.caption(f"{len(pages)} page(s). Check that the remarks and seal block is not split.")
        cols = st.columns(min(len(pages), 3))
        for i, png in enumerate(pages):
            cols[i % len(cols)].image(png, caption=f"Page {i + 1}", use_container_width=True)


def render_generate(payload: dict, on_final) -> None:
    step_header(11, "Generate PDF and Word Report")
    if st.button("📄 Generate PDF & DOCX", type="primary"):
        name = "Third_Party_Sample" if payload.get("third_party_sample") else payload["client_name"]
        stem = f"{name}_{payload['office']}"
        docx_path = build_docx(payload, GENERATED_DIR, stem)
        generated = {"payload": deepcopy(payload), "docx_path": str(docx_path), "path": ""}
        st.session_state["generated_report"] = generated
        try:
            pdf = pdf_converter.docx_to_pdf(docx_path, GENERATED_DIR)
        except pdf_converter.PdfConversionError as e:
            st.error(str(e))
            st.info("The Word report is ready. You can download DOCX below even though PDF conversion failed.")
        else:
            on_final(str(pdf))
            generated["path"] = str(pdf)
            st.success("Report generated. Download PDF or editable Word below.")
    generated = st.session_state.get("generated_report")
    if generated and generated["payload"] == payload:
        if generated.get("path"):
            pdf = Path(generated["path"])
            if pdf.is_file():
                st.download_button("Download PDF", pdf.read_bytes(), file_name=pdf.name, mime="application/pdf")
        if generated.get("docx_path"):
            docx = Path(generated["docx_path"])
            if docx.is_file():
                st.download_button("Download DOCX (Word)", docx.read_bytes(), file_name=docx.name, mime=DOCX_MIME)
