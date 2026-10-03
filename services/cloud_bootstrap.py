"""Restore private deployment datasets without committing them to GitHub."""
import base64
import binascii
import io
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import ZipFile, BadZipFile


def _secret(name):
    if os.getenv(name):
        return os.environ[name]
    import streamlit as st
    try:
        return st.secrets.get(name, '')
    except FileNotFoundError:
        return ''


def restore_datasets():
    from services.dataset_service import EMPLOYEE_FILE, CLIENT_FILE, DatasetError
    for path, name in ((EMPLOYEE_FILE, 'EMPLOYEE_DATA_BASE64'), (CLIENT_FILE, 'CLIENT_DATA_BASE64')):
        path = Path(path)
        if path.exists():
            continue  # Preserve local source files and in-session admin edits.
        encoded = _secret(name)
        if not encoded:
            raise DatasetError(f'{path.name} is missing. Configure {name} in Streamlit Secrets.')
        try:
            content = base64.b64decode(encoded, validate=True)
            with ZipFile(io.BytesIO(content)) as archive:
                if 'xl/workbook.xml' not in archive.namelist():
                    raise ValueError('Not an Excel workbook')
        except (ValueError, binascii.Error, BadZipFile):
            raise DatasetError(f'{name} does not contain a valid encoded Excel workbook.') from None
        path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(dir=path.parent, delete=False) as temp:
            temp.write(content)
            temp_path = Path(temp.name)
        os.replace(temp_path, path)
