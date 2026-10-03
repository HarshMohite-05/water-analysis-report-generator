import base64
from services import cloud_bootstrap, dataset_service


def test_restore_private_cloud_workbooks_without_overwriting_edits(isolated_reports, monkeypatch):
    paths = {'EMPLOYEE_DATA_BASE64': dataset_service.EMPLOYEE_FILE,
             'CLIENT_DATA_BASE64': dataset_service.CLIENT_FILE}
    snapshots = {key: path.read_bytes() for key, path in paths.items()}
    monkeypatch.setattr(cloud_bootstrap, '_secret', lambda name: base64.b64encode(snapshots[name]).decode())
    for path in paths.values():
        path.unlink()
    cloud_bootstrap.restore_datasets()
    assert all(path.read_bytes() == snapshots[key] for key, path in paths.items())
    dataset_service.CLIENT_FILE.write_bytes(b'local edits')
    cloud_bootstrap.restore_datasets()
    assert dataset_service.CLIENT_FILE.read_bytes() == b'local edits'
