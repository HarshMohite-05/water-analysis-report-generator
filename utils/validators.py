from __future__ import annotations

from datetime import date
from typing import Dict, List

from config.constants import MAX_SAMPLE_COLUMNS


def validate_report_payload(data: Dict) -> List[str]:
    """Return a list of human-readable problems (empty list == valid)."""
    errors: List[str] = []
    if not data.get("office"):
        errors.append("Select an office.")
    if not data.get("third_party_sample") and not data.get("client_name"):
        errors.append("Select a client.")
    cd, ad = data.get("collection_date"), data.get("analysis_date")
    if isinstance(cd, date) and isinstance(ad, date) and ad < cd:
        errors.append("Analysis date cannot be before collection date.")
    cols = [c.strip() for c in data.get("sample_columns", []) if c and c.strip()]
    if not cols:
        errors.append("Add at least one sample column.")
    if len(cols) != len(set(c.lower() for c in cols)):
        errors.append("Sample column names must be unique.")
    if len(cols) > MAX_SAMPLE_COLUMNS:
        errors.append(f"At most {MAX_SAMPLE_COLUMNS} sample columns are supported.")
    if not data.get("parameters"):
        errors.append("Select at least one analysis parameter.")
    return errors