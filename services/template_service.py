"""Office-wise template resolution.

Both offices share one institutional layout. Only the footer address and the seal
image differ. Each office folder holds a .docx (letterhead header + office footer)
and seal.png. `ensure_templates()` (re)creates them when missing so a fresh checkout
works; drop in your real files with the same names to override.
"""
from __future__ import annotations

from pathlib import Path
from typing import Tuple

from config.settings import OFFICES, TEMPLATES_DIR
from report_engine import docx_generator, seal_inserter


def office_key(office: str) -> str:
    if office not in OFFICES:
        raise ValueError(f"Unknown office: {office}")
    return OFFICES[office]["key"]


def template_paths(office: str) -> Tuple[Path, Path]:
    key = office_key(office)
    d = TEMPLATES_DIR / key
    return d / "water_analysis_template.docx", d / "seal.png"


def ensure_templates() -> None:
    for office, cfg in OFFICES.items():
        tpl, seal = template_paths(office)
        tpl.parent.mkdir(parents=True, exist_ok=True)
        if not seal.exists():
            seal_inserter.make_placeholder_seal(seal, cfg["key"].title())
        if not tpl.exists():
            docx_generator.build_template(tpl, cfg["footer_lines"])