"""Programmatic report typography and table spacing."""
import re

from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt

REPORT_FONT = 'Times New Roman'
CONTENT_PT = 12  # body text size; only the two report headings are larger

_PLAIN_NUMBER = re.compile(r'([+-]?)(\d+)(\.\d+)?')


def format_number(value) -> str:
    """Add thousands separators to plain numbers (10000.5 -> 10,000.5).

    Decimals are kept exactly as typed; text such as 'BDL', '<0.1' or '6.5-8.5' is unchanged.
    """
    text = str(value).strip()
    match = _PLAIN_NUMBER.fullmatch(text)
    if not match:
        return text
    sign, whole, decimals = match.groups()
    return f'{sign}{int(whole):,}{decimals or ""}'


def cell_padding(cell, vertical=30, horizontal=80):
    props = cell._tc.get_or_add_tcPr()
    margins = props.find(qn('w:tcMar'))
    if margins is None:
        margins = OxmlElement('w:tcMar')
        props.append(margins)
    for edge, value in [('top', vertical), ('bottom', vertical),
                        ('left', horizontal), ('right', horizontal)]:
        element = OxmlElement(f'w:{edge}')
        element.set(qn('w:w'), str(value))
        element.set(qn('w:type'), 'dxa')
        margins.append(element)


def apply_report_font(doc):
    """Set explicit font slots, including hyperlinks and editable header/footer text.

    Image-based branding is preserved; it contains no editable text runs.
    """
    doc.styles['Normal'].font.name = REPORT_FONT
    doc.styles['Normal'].font.size = Pt(CONTENT_PT)
    roots = [doc.element]
    for section in doc.sections:
        for story in (section.header, section.first_page_header, section.even_page_header,
                      section.footer, section.first_page_footer, section.even_page_footer):
            if not story.is_linked_to_previous:
                roots.append(story._element)
    for root in roots:
        for run in root.iter(qn('w:r')):
            props = run.get_or_add_rPr()
            fonts = props.find(qn('w:rFonts'))
            if fonts is None:
                fonts = OxmlElement('w:rFonts')
                props.insert(0, fonts)
            fonts.attrib.clear()
            for slot in ('ascii', 'hAnsi', 'eastAsia', 'cs'):
                fonts.set(qn(f'w:{slot}'), REPORT_FONT)
