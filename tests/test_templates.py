from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT

from config.settings import OFFICES
from services import template_service


def test_templates_exist_and_footers_differ():
    template_service.ensure_templates()
    footers = []
    for office in OFFICES:
        tpl, seal = template_service.template_paths(office)
        assert tpl.exists() and seal.exists()
        footer = Document(str(tpl)).sections[0].footer
        # Supplied letterheads can carry their office address in an image.
        text = "\n".join(p.text for p in footer.paragraphs).strip()
        images = tuple(rel.target_part.blob for rel in footer.part.rels.values()
                       if rel.reltype == RT.IMAGE)
        assert text or images, f"Missing footer content for {office}"
        footers.append((text, images))
    assert footers[0] != footers[1]
