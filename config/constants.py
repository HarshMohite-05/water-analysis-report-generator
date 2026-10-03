"""Static constants: roles, default master parameters, pagination limits."""
from __future__ import annotations

ROLE_ADMIN = "admin"
ROLE_TECHNICIAN = "technician"

DATE_FMT = "%d-%m-%Y"

# (name, unit)
DEFAULT_PARAMETERS = [
    ("pH", "-"),
    ("TDS", "Mg/L"),
    ("Total Hardness as CaCO3", "Mg/L"),
    ("T Alkalinity as CaCO3", "Mg/L"),
    ("Chloride as Cl", "Mg/L"),
    ("Sulphate", "Mg/L"),
    ("Phosphate as PO4", "Mg/L"),
    ("Calcium", "Mg/L"),
    ("Magnesium", "Mg/L"),
    ("Turbidity", "NTU"),
    ("Colour", "Pt-Co"),
]
DEFAULT_SELECTED = [p[0] for p in DEFAULT_PARAMETERS[:9]]

# Pagination (table rows per page; remark+seal block is kept together)
ROWS_FIRST_PAGE = 16
ROWS_OTHER_PAGES = 26
REMARK_BLOCK_ROWS = 9   # approx. row-equivalents the remarks + signature block need
MAX_SAMPLE_COLUMNS = 6