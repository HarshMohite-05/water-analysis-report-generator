from __future__ import annotations

from datetime import date, datetime

from config.constants import DATE_FMT


def fmt_date(d) -> str:
    if isinstance(d, (date, datetime)):
        return d.strftime(DATE_FMT)
    return str(d or "")


def parse_date(s: str) -> date:
    return datetime.strptime(s, DATE_FMT).date()