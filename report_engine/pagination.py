"""Row pagination for the parameter table.

Rules: table rows never split across pages; the header row repeats on every page;
the remarks + signature/seal block is never separated from itself and, if it does not
fit under the last table chunk, moves whole to a new page.
"""
from __future__ import annotations

from typing import List, Tuple

from config.constants import REMARK_BLOCK_ROWS, ROWS_FIRST_PAGE, ROWS_OTHER_PAGES


def paginate(n_rows: int, first: int = ROWS_FIRST_PAGE, other: int = ROWS_OTHER_PAGES,
             remark_rows: int = REMARK_BLOCK_ROWS) -> Tuple[List[Tuple[int, int]], bool]:
    """Return ([(start, end), ...] row slices, remark_on_new_page)."""
    if n_rows <= 0:
        return [(0, 0)], False
    chunks: List[Tuple[int, int]] = []
    start, cap = 0, first
    while start < n_rows:
        end = min(start + cap, n_rows)
        chunks.append((start, end))
        start, cap = end, other
    last_cap = first if len(chunks) == 1 else other
    used = chunks[-1][1] - chunks[-1][0]
    remark_on_new_page = used + remark_rows > last_cap
    return chunks, remark_on_new_page