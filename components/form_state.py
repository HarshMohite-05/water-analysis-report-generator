"""Stable widget identities scoped to one report draft."""
from uuid import uuid4

import streamlit as st


def field_key(draft: dict, field: str, value=None) -> str:
    scope = draft.setdefault('_form_scope', uuid4().hex)
    key = f'draft_{scope}_{field}'
    if key not in st.session_state:
        st.session_state[key] = value
    return key
