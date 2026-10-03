from __future__ import annotations

from pathlib import Path

from docx.shared import Cm


def make_placeholder_seal(path: Path, label: str) -> None:
    """Draw a simple circular seal. Replace seal.png with the real one in production."""
    from PIL import Image, ImageDraw, ImageFont

    size = 400
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    blue = (20, 60, 150, 255)
    d.ellipse((6, 6, size - 6, size - 6), outline=blue, width=8)
    d.ellipse((40, 40, size - 40, size - 40), outline=blue, width=3)
    try:
        font = ImageFont.truetype("Arial.ttf", 34)
    except Exception:
        font = ImageFont.load_default()
    for y, text in ((150, "NIRMAAN"), (200, "WATERTECH"), (250, label.upper())):
        w = d.textlength(text, font=font)
        d.text(((size - w) / 2, y), text, fill=blue, font=font)
    img.save(path)


def insert_seal(paragraph, seal_path: Path, width_cm: float = 2.624) -> None:
    run = paragraph.add_run()
    run.add_picture(str(seal_path), width=Cm(width_cm))