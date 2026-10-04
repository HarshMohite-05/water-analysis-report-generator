from config.database_url import resolve_database_url


def test_default_and_relative_paths(tmp_path):
    expected = 'sqlite:///' + str(tmp_path / 'storage/app.db')
    for value in (None, '', ' ', 'storage/app.db', ' sqlite:///storage/app.db '):
        assert resolve_database_url(value, tmp_path) == (expected, '')


def test_invalid_url_uses_explicit_local_fallback(tmp_path):
    url, warning = resolve_database_url('invalid-secret-value', tmp_path)
    assert url.endswith('/storage/app.db')
    assert warning and 'invalid-secret-value' not in warning


def test_memory_absolute_and_remote_preserved(tmp_path):
    for value in ('sqlite:///:memory:', 'sqlite:////tmp/example.db', 'postgresql://user:password@host/db'):
        assert resolve_database_url(value, tmp_path) == (value, '')
