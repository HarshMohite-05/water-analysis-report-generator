"""Application settings: paths, environment and per-office configuration."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

from config.database_url import resolve_database_url

DATABASE_URL, DATABASE_CONFIG_WARNING = resolve_database_url(os.getenv("DATABASE_URL"), BASE_DIR)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
AI_MODEL = os.getenv("AI_MODEL", "openai/gpt-oss-20b").strip() or "openai/gpt-oss-20b"
LIBREOFFICE_PATH = os.getenv("LIBREOFFICE_PATH", "")

TEMPLATES_DIR = BASE_DIR / "templates"
GENERATED_DIR = BASE_DIR / "storage" / "generated_reports"
DRAFTS_DIR = BASE_DIR / "storage" / "drafts"
TEMP_DIR = BASE_DIR / "storage" / "temporary"

# Only footer address and seal differ between offices; letterhead/layout are shared.
OFFICES = {
    "Mumbai Office": {
        "key": "mumbai",
        "footer_lines": [
            "Nirmaan WaterTech Solutions - Mumbai Office",
            "Unit 12, Industrial Estate, Andheri East, Mumbai - 400093, Maharashtra",
            "www.nirmaanwatertech.com | info@nirmaanwatertech.com | +91 22 0000 0000",
        ],
    },
    "Ahmedabad Office": {
        "key": "ahmedabad",
        "footer_lines": [
            "Nirmaan WaterTech Solutions - Ahmedabad Office",
            "B-204, Corporate Park, Naroda GIDC, Ahmedabad - 382330, Gujarat",
            "www.nirmaanwatertech.com | info@nirmaanwatertech.com | +91 79 0000 0000",
        ],
    },
}

SIGNATORY_COMPANY = "Nirmaan WaterTech Solutions"
SIGNATORY_EMAIL = "info@nirmaanwatertech.com"

for _d in (GENERATED_DIR, DRAFTS_DIR, TEMP_DIR):
    _d.mkdir(parents=True, exist_ok=True)
