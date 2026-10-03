from __future__ import annotations

import shutil
import subprocess
from tempfile import TemporaryDirectory
from pathlib import Path
from typing import List

from config.settings import LIBREOFFICE_PATH


class PdfConversionError(RuntimeError):
    pass


def _soffice() -> str:
    for cand in (LIBREOFFICE_PATH, shutil.which("soffice"), shutil.which("libreoffice"),
                 "/Applications/LibreOffice.app/Contents/MacOS/soffice"):
        if cand and Path(cand).exists():
            return cand
    return ""


def docx_to_pdf(docx_path: Path, out_dir: Path) -> Path:
    """LibreOffice first (headless servers); falls back to docx2pdf (needs MS Word)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf = out_dir / (docx_path.stem + ".pdf")
    exe = _soffice()
    if exe:
        try:
            # A separate profile avoids conflicts with an open desktop instance.
            with TemporaryDirectory(prefix="water-report-lo-") as profile:
                # Headless macOS LibreOffice can miss Supplemental system fonts.
                # Expose the installed Times New Roman faces to this isolated
                # conversion profile without altering the user's font settings.
                system_fonts = Path("/System/Library/Fonts/Supplemental")
                for font in system_fonts.glob("Times New Roman*.ttf"):
                    font_dir = Path(profile) / "user" / "fonts"
                    font_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(font, font_dir / font.name)
                proc = subprocess.run(
                    [exe, f"-env:UserInstallation={Path(profile).as_uri()}",
                     "--headless", "--convert-to", "pdf", "--outdir",
                     str(out_dir.resolve()), str(docx_path.resolve())],
                    capture_output=True, text=True, timeout=120,
                )
        except (OSError, subprocess.TimeoutExpired) as e:
            raise PdfConversionError(f"LibreOffice could not convert the report: {e}") from e
        if proc.returncode == 0 and pdf.exists() and pdf.stat().st_size:
            return pdf
        raise PdfConversionError(f"LibreOffice failed: {proc.stderr or proc.stdout}")
    try:
        from docx2pdf import convert

        convert(str(docx_path), str(pdf))
        if pdf.exists():
            return pdf
    except Exception as e:
        raise PdfConversionError(
            "No PDF converter available. Install LibreOffice (recommended) or MS Word. "
            f"Detail: {e}"
        )
    raise PdfConversionError("PDF conversion produced no file.")


def pdf_page_count(pdf_path: Path) -> int:
    import fitz

    with fitz.open(str(pdf_path)) as d:
        return d.page_count


def render_pages(pdf_path: Path, zoom: float = 1.4) -> List[bytes]:
    """PNG bytes per page, for in-app preview."""
    import fitz

    out = []
    with fitz.open(str(pdf_path)) as d:
        for page in d:
            out.append(page.get_pixmap(matrix=fitz.Matrix(zoom, zoom)).tobytes("png"))
    return out
