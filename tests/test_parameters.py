from datetime import date

from utils.validators import validate_report_payload


def _ok():
    return dict(office="Mumbai Office", client_name="X", collection_date=date(2026, 6, 9),
                analysis_date=date(2026, 6, 12), sample_columns=["A", "B"], parameters=[{"name": "pH"}])


def test_valid():
    assert validate_report_payload(_ok()) == []


def test_bad_dates_and_dupe_columns():
    d = _ok()
    d["analysis_date"] = date(2026, 6, 1)
    d["sample_columns"] = ["A", "a"]
    assert len(validate_report_payload(d)) == 2