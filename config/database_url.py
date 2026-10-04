"""Normalize database settings without displaying credentials."""
from pathlib import Path
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


def resolve_database_url(value, base_dir):
    default = 'sqlite:///' + str(Path(base_dir) / 'storage' / 'app.db')
    value = (value or '').strip()
    if not value:
        return default, ''
    if '://' not in value and value.endswith(('.db', '.sqlite', '.sqlite3')):
        value = 'sqlite:///' + value
    try:
        url = make_url(value)
    except ArgumentError:
        return default, ('DATABASE_URL is invalid. Using the local storage/app.db database. '
                         'For this app, set DATABASE_URL=sqlite:///storage/app.db and restart.')
    if url.get_backend_name() == 'sqlite' and url.database and url.database != ':memory:':
        path = Path(url.database)
        if not path.is_absolute() and not url.database.startswith('file:'):
            url = url.set(database=str(Path(base_dir) / path))
    return url.render_as_string(hide_password=False), ''
