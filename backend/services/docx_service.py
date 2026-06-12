"""
DOCX Export Service – Converts a FinalReport markdown string into a
professionally structured Microsoft Word (.docx) document using python-docx.

Heading levels are inferred from the markdown `#` prefix.
"""

from __future__ import annotations

import io
import re
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import FinalReport

logger = logging.getLogger(__name__)


def generate_report_docx(report: "FinalReport") -> bytes:
    """
    Returns raw DOCX bytes ready for streaming to the browser.
    Falls back gracefully if python-docx is not installed.
    """
    try:
        from docx import Document
        from docx.shared import Pt, RGBColor, Inches
        from docx.enum.text import WD_ALIGN_PARAGRAPH
    except ImportError as exc:
        raise RuntimeError(
            "python-docx is not installed. Run: pip install python-docx"
        ) from exc

    doc = Document()

    # ── Global Styles ────────────────────────────────────────────────────────
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    # ── Cover / Title Page ───────────────────────────────────────────────────
    title_para = doc.add_paragraph()
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_para.add_run(report.title or report.topic)
    run.bold = True
    run.font.size = Pt(20)
    run.font.color.rgb = RGBColor(0x1E, 0x40, 0xAF)   # deep blue

    doc.add_paragraph()  # spacer

    meta_para = doc.add_paragraph()
    meta_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta_run = meta_para.add_run(
        f"Topic: {report.topic}\n"
        f"Template: {report.template_type or 'Research Report'}\n"
        f"Generated: {report.created_at.strftime('%B %d, %Y') if report.created_at else 'N/A'}"
    )
    meta_run.font.size = Pt(10)
    meta_run.font.color.rgb = RGBColor(0x6B, 0x72, 0x80)

    doc.add_page_break()

    # ── Parse Markdown → DOCX ────────────────────────────────────────────────
    markdown = report.report_markdown or report.content or "(No content available)"
    lines = markdown.splitlines()

    for line in lines:
        stripped = line.strip()

        # Headings
        if stripped.startswith("#### "):
            doc.add_heading(stripped[5:], level=4)
        elif stripped.startswith("### "):
            doc.add_heading(stripped[4:], level=3)
        elif stripped.startswith("## "):
            doc.add_heading(stripped[3:], level=2)
        elif stripped.startswith("# "):
            doc.add_heading(stripped[2:], level=1)

        # Bullet lists
        elif stripped.startswith("- ") or stripped.startswith("* "):
            para = doc.add_paragraph(style="List Bullet")
            _add_inline_markdown(para, stripped[2:])

        # Numbered lists
        elif re.match(r"^\d+\.\s", stripped):
            para = doc.add_paragraph(style="List Number")
            _add_inline_markdown(para, re.sub(r"^\d+\.\s", "", stripped))

        # Horizontal rule → page break
        elif stripped in ("---", "___", "***"):
            doc.add_page_break()

        # Blank line → spacing
        elif stripped == "":
            doc.add_paragraph()

        # Normal paragraph
        else:
            para = doc.add_paragraph()
            _add_inline_markdown(para, stripped)

    # ── Serialise ────────────────────────────────────────────────────────────
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.read()


def _add_inline_markdown(para, text: str):
    """
    Handles **bold** and *italic* inline markers inside a paragraph.
    """
    from docx.shared import Pt

    # Split on bold/italic markers using regex
    segments = re.split(r"(\*\*.*?\*\*|\*.*?\*)", text)
    for seg in segments:
        if seg.startswith("**") and seg.endswith("**"):
            run = para.add_run(seg[2:-2])
            run.bold = True
        elif seg.startswith("*") and seg.endswith("*"):
            run = para.add_run(seg[1:-1])
            run.italic = True
        elif seg:
            para.add_run(seg)
