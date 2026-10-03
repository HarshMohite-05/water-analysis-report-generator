import json

from streamlit.testing.v1 import AppTest

SOURCE = '''
import streamlit as st
from components import parameter_table
if "draft" not in st.session_state:
    st.session_state.draft = dict(custom_params=[], selected_params=["pH"], units={}, values={},
                                 sample_cols=[{"id": 1, "name": "Feed"}])
parameter_table.render_selector(st.session_state.draft)
parameter_table.render_results(st.session_state.draft)
'''


def test_first_edit_persists_across_reruns_and_selection_changes(monkeypatch):
    from services import parameter_service
    monkeypatch.setattr(parameter_service, "list_parameters", lambda: [
        {"name": "pH", "unit": "-"}, {"name": "TDS", "unit": "Mg/L"}])
    app = AppTest.from_string(SOURCE).run()
    assert not app.exception
    assert [c.label for c in app.checkbox] == ['pH', 'TDS']
    assert len(app.multiselect) == 0
    def rerun_with_edits(edits):
        # AppTest has no data-editor wrapper; send the same JSON widget state
        # as the browser, alongside the supported checkbox widget states.
        states = app._tree.get_widget_states()
        state = states.widgets.add()
        state.id = app.get('arrow_data_frame')[0].proto.id
        state.string_value = json.dumps({'edited_rows': edits, 'added_rows': [], 'deleted_rows': []})
        app._run(states)

    rerun_with_edits({0: {'Feed': '7.2'}})
    assert app.session_state['draft']['values']['pH']['1'] == '7.2'
    rerun_with_edits({0: {'Feed': '7.2'}})
    assert app.session_state['draft']['values']['pH']['1'] == '7.2'
    assert app.session_state['draft']['_results_editor']['source'].iloc[0]['Feed'] == ''
    app.checkbox[1].check()
    rerun_with_edits({0: {'Feed': '7.2'}})
    assert app.session_state['draft']['values']['pH']['1'] == '7.2'
    assert app.session_state['draft']['selected_params'] == ['pH', 'TDS']
    rerun_with_edits({1: {'Feed': '125'}})
    assert app.session_state['draft']['values']['TDS']['1'] == '125'
    rerun_with_edits({1: {'Feed': '125'}})
    assert app.session_state['draft']['values']['TDS']['1'] == '125'
    assert not app.exception
