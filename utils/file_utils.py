from __future__ import annotations

import re
from pathlib import Path


def safe_filename(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_") or "file"


def unique_path(directory: Path, stem: str, suffix: str) -> Path:
    p = directory / f"{safe_filename(stem)}{suffix}"
    i = 1
    while p.exists():
        p = directory / f"{safe_filename(stem)}_{i}{suffix}"
        i += 1
    return p