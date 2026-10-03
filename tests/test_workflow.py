"""Exercise real pages, authentication, isolated SQL database and PDF converter."""
import json
from datetime import date
from pathlib import Path

import fitz
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from streamlit.testing.v1 import AppTest

from database import database
from database.seed import seed
from components import report_preview
from services import report_service


def run_ui(app, edits=None, download=False):
    states = app._tree.get_widget_states()
    editors = app.get('arrow_data_frame')
    if editors:
        key = app.session_state['draft']['_results_editor']['key']
        value = edits if edits is not None else app.session_state[key]
        state = states.widgets.add()
        state.id = editors[0].proto.id
        state.string_value = json.dumps(value)
    if download:
        state = states.widgets.add()
        state.id = app.get('download_button')[0].proto.id
        state.trigger_value = True
    app._run(states, timeout=60)
    assert not app.exception, [e.message for e in app.exception]
    return app


def widget(app, kind, label):
    return next(w for w in getattr(app, kind) if w.label == label)




@pytest.mark.parametrize('office', ['Mumbai Office', 'Ahmedabad Office'])
@pytest.mark.parametrize('actor', [('ADM001', 'ChangeMe#1', 'Test Administrator', 'admin'),
                                   ('TECH1', 'TechTest!', 'Assigned Technician', 'technician')])
def test_full_office_workflow(isolated_reports, office, actor):
    app = AppTest.from_file(str(Path('app.py').resolve())).run()
    widget(app, 'text_input', 'Employee ID / Email').input(actor[0])
    widget(app, 'text_input', 'Password').input(actor[1])
    widget(app, 'button', 'Login').click().run()
    assert not app.exception
    assert app.session_state['user']['role'] == actor[3]
    app.switch_page('pages/05_Admin_Panel.py').run()
    assert not app.exception
    assert bool(app.error) == (actor[3] != 'admin')
    app.switch_page('pages/03_Create_Report.py').run()
    widget(app, 'selectbox', 'Office / Location').select(office)
    run_ui(app)
    widget(app, 'selectbox', 'Client Name').select('Shree Prakash Textiles' if office == 'Ahmedabad Office' else 'Mumbai Client')
    run_ui(app)
    assert app.session_state['draft']['office'] == office
    assert app.session_state['draft']['assigned_employee_id'] == 'TECH1'
    assert widget(app, 'text_input', 'Client Email').value == 'client@example.test'
    widget(app, 'text_area', 'Address').input('Test address, Industrial Estate')
    widget(app, 'text_input', 'Contact Person').input('Mr. Test')
    for label in ['Sample Collection Date', 'Sample Analysis Date']:
        widget(app, 'date_input', label).set_value(date(2026, 6, 12))
    run_ui(app)
    for checkbox in app.checkbox:
        checkbox.set_value(checkbox.label in ['pH', 'TDS'])
    run_ui(app)
    edits = {'edited_rows': {0: {'RO Feed Water': '7.2', 'RO 3rd Stage Reject Water': '7.6'},
                             1: {'RO Feed Water': '125', 'RO 3rd Stage Reject Water': '350'}},
             'added_rows': [], 'deleted_rows': []}
    run_ui(app, edits)
    widget(app, 'text_area', 'Final remark used in report').input('Water sample was clear.')
    run_ui(app)
    widget(app, 'button', '🔍 Preview Full Report').click()
    run_ui(app)
    assert app.session_state['preview_pages']
    widget(app, 'text_area', 'Final remark used in report').input('Water sample was clear.\n\nTDS was measured at 125 mg/L.\n-')
    run_ui(app)
    assert 'preview_pages' not in app.session_state
    widget(app, 'checkbox', 'TDS').uncheck()
    run_ui(app)
    widget(app, 'checkbox', 'TDS').check()
    run_ui(app)
    assert app.session_state['draft']['values']['TDS']['1'] == '125'
    widget(app, 'button', '🔍 Preview Full Report').click()
    run_ui(app)
    widget(app, 'button', '📄 Generate PDF & DOCX').click()
    run_ui(app)
    assert len(app.get('download_button')) == 2
    run_ui(app, download=True)
    assert len(app.get('download_button')) == 2
    generated = Path(app.session_state['generated_report']['path'])
    assert generated.read_bytes().startswith(b'%PDF')
    from docx import Document
    word_path = Path(app.session_state['generated_report']['docx_path'])
    assert word_path == generated.with_suffix('.docx')
    document = Document(word_path)
    assert any('Water sample was clear.' in p.text for p in document.paragraphs)
    report = report_service.get_report(app.session_state['draft']['report_id'])
    assert report['status'] == 'final'
    assert 'received_date' not in report['data']
    assert report['data']['technician'] == actor[2]
    assert report['data']['technician_email'] == app.session_state['user']['email']
    assert report['data']['assigned_technician'] == 'Assigned Technician'
    assert [p['name'] for p in report['data']['parameters']] == ['pH', 'TDS']
    with fitz.open(generated) as pdf:
        text = ''.join(page.get_text() for page in pdf)
        fonts = {span['font'] for page in pdf for block in page.get_text('dict')['blocks']
                 if 'lines' in block for line in block['lines'] for span in line['spans']
                 if span['text'].strip()}
        assert all('TimesNewRoman' in font for font in fonts), fonts
        assert all(s in text for s in ['WATER REPORT', '7.2', '125', 'Dear Sir,'])
        assert actor[2] in text
        if actor[3] == 'admin':
            assert 'Assigned Technician' not in text
        assert 'Analysed by' not in text and 'Total Hardness' not in text
        assert any(link.get('uri') == 'mailto:' + app.session_state['user']['email'] for page in pdf for link in page.get_links())
    from report_engine.pdf_converter import render_pages
    assert app.session_state['preview_pages'] == render_pages(generated)
    app.switch_page('pages/04_Report_History.py').run()
    assert not app.exception
    assert {w.label for w in app.get('download_button')} == {'PDF', 'DOCX'}
    widget(app, 'button', 'Open').click().run()
    assert not app.exception
    assert app.session_state['draft']['values']['pH']['1'] == '7.2'
    assert widget(app, 'text_input', 'Contact Person').value == 'Mr. Test'
    app.switch_page('pages/03_Create_Report.py').run()
    widget(app, 'button', 'New blank report').click()
    run_ui(app)
    assert all(v == '' for row in app.session_state['draft']['values'].values() for v in row.values())
    assert widget(app, 'text_input', 'Contact Person').value == ''
