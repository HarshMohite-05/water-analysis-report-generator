from unittest.mock import Mock

from docx import Document
from streamlit.testing.v1 import AppTest

from components import report_preview


def test_docx_download_survives_pdf_failure_and_rerun(tmp_path, monkeypatch):
    path = tmp_path / 'report.docx'
    document = Document()
    document.add_paragraph('The water container is damaged.')
    document.save(path)
    monkeypatch.setattr(report_preview, 'build_docx', lambda *args: path)
    monkeypatch.setattr(report_preview.pdf_converter, 'docx_to_pdf',
                        Mock(side_effect=report_preview.pdf_converter.PdfConversionError('Converter unavailable')))
    app = AppTest.from_string('''
import streamlit as st
from components.report_preview import render_generate
client = st.text_input('Client', 'Test client')
render_generate({'client_name': client, 'office': 'Mumbai Office'},
                lambda path: st.session_state.update(finalized=True))
''').run()
    app.button[0].click().run()
    assert not app.exception
    assert [w.label for w in app.get('download_button')] == ['Download DOCX (Word)']
    assert 'finalized' not in app.session_state
    app.run()
    assert [w.label for w in app.get('download_button')] == ['Download DOCX (Word)']
    app.text_input[0].input('Changed client').run()
    assert not app.get('download_button')
