from streamlit.testing.v1 import AppTest
from services import remark_ai_service


def test_suggestion_edits_survive_reruns_and_regeneration(monkeypatch):
    replies = iter(['The water container is damaged.', 'The container holding the water is damaged.'])
    monkeypatch.setattr(remark_ai_service, 'improve_remark',
                        lambda *args, **kwargs: dict(text=next(replies), source='ai', error=''))
    app = AppTest.from_string('''
import streamlit as st
from components.remark_editor import render
render(st.session_state.setdefault('draft', {}))
st.button('Unrelated action')
''').run()
    def field(kind, label):
        return next(w for w in getattr(app, kind) if w.label == label)
    field('text_area', 'Technician Remark (raw input)').input('container damaged').run()
    field('button', '✨ Improve with AI').click().run()
    field('text_area', 'Suggested remark (editable)').input('The sample container is damaged.').run()
    field('button', 'Unrelated action').click().run()
    assert field('text_area', 'Suggested remark (editable)').value == 'The sample container is damaged.'
    field('button', '🔄 Regenerate').click().run()
    assert field('text_area', 'Suggested remark (editable)').value == 'The container holding the water is damaged.'
    field('button', '✅ Accept').click().run()
    assert field('text_area', 'Final remark used in report').value == 'The container holding the water is damaged.'
    assert not app.exception
