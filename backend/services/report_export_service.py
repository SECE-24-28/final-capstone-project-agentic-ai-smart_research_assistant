"""
PDF Export Service – Converts a FinalReport into a professional PDF using
reportlab.platypus (flowable document engine).

Uses Paragraph, Heading, Spacer, HRFlowable and a two-column TOC-style
layout to produce a polished academic PDF output.
"""

from __future__ import annotations

import io
import re
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import FinalReport

logger = logging.getLogger(__name__)


def generate_report_pdf(report: "FinalReport") -> bytes:
    """
    Returns raw PDF bytes ready for streaming to the browser.
    Raises RuntimeError if reportlab is not installed.
    """
    try:
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer,
            HRFlowable, PageBreak, ListFlowable, ListItem,
        )
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    except ImportError as exc:
        raise RuntimeError(
            "reportlab is not installed. Run: pip install reportlab"
        ) from exc

    buf = io.BytesIO()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=2.5 * cm,
        leftMargin=2.5 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
        title=report.title or report.topic,
        author="Smart Research Assistant",
    )

    # ── Style Palette ────────────────────────────────────────────────────────
    base = getSampleStyleSheet()

    cover_title_style = ParagraphStyle(
        "CoverTitle",
        parent=base["Title"],
        fontSize=24,
        textColor=colors.HexColor("#1E40AF"),
        spaceAfter=12,
        alignment=TA_CENTER,
    )
    cover_meta_style = ParagraphStyle(
        "CoverMeta",
        parent=base["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#6B7280"),
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    h1_style = ParagraphStyle(
        "H1",
        parent=base["Heading1"],
        fontSize=16,
        textColor=colors.HexColor("#1E40AF"),
        spaceBefore=18,
        spaceAfter=6,
        borderPad=4,
    )
    h2_style = ParagraphStyle(
        "H2",
        parent=base["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#1D4ED8"),
        spaceBefore=14,
        spaceAfter=4,
    )
    h3_style = ParagraphStyle(
        "H3",
        parent=base["Heading3"],
        fontSize=11,
        textColor=colors.HexColor("#374151"),
        spaceBefore=10,
        spaceAfter=4,
        fontName="Helvetica-Bold",
    )
    body_style = ParagraphStyle(
        "Body",
        parent=base["Normal"],
        fontSize=10,
        leading=15,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
    )
    bullet_style = ParagraphStyle(
        "Bullet",
        parent=body_style,
        leftIndent=18,
        bulletIndent=6,
        spaceAfter=3,
    )

    # ── Build Flowables ──────────────────────────────────────────────────────
    story = []

    # Cover page
    story.append(Spacer(1, 3 * cm))
    story.append(Paragraph(report.title or report.topic, cover_title_style))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(f"Topic: {report.topic}", cover_meta_style))
    story.append(Paragraph(
        f"Template: {report.template_type or 'Research Report'}", cover_meta_style
    ))
    if report.created_at:
        story.append(Paragraph(
            f"Generated: {report.created_at.strftime('%B %d, %Y')}", cover_meta_style
        ))
    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="80%", thickness=1,
                             color=colors.HexColor("#1E40AF"),
                             spaceAfter=6))
    story.append(PageBreak())

    # Parse markdown → flowables
    markdown = report.report_markdown or report.content or "(No content)"
    lines = markdown.splitlines()
    bullet_items: list = []

    def _flush_bullets():
        nonlocal bullet_items
        if bullet_items:
            story.append(ListFlowable(
                [ListItem(Paragraph(item, bullet_style), bulletColor=colors.HexColor("#1E40AF"))
                 for item in bullet_items],
                bulletType="bullet",
                leftIndent=18,
            ))
            bullet_items = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("#### "):
            _flush_bullets()
            story.append(Paragraph(_md_inline(stripped[5:]), h3_style))

        elif stripped.startswith("### "):
            _flush_bullets()
            story.append(Paragraph(_md_inline(stripped[4:]), h3_style))

        elif stripped.startswith("## "):
            _flush_bullets()
            story.append(HRFlowable(width="100%", thickness=0.5,
                                    color=colors.HexColor("#E5E7EB"),
                                    spaceBefore=4, spaceAfter=2))
            story.append(Paragraph(_md_inline(stripped[3:]), h2_style))

        elif stripped.startswith("# "):
            _flush_bullets()
            story.append(Paragraph(_md_inline(stripped[2:]), h1_style))

        elif stripped.startswith("- ") or stripped.startswith("* "):
            bullet_items.append(_md_inline(stripped[2:]))

        elif re.match(r"^\d+\.\s", stripped):
            _flush_bullets()
            cleaned_text = re.sub(r"^\d+\.\s", "", stripped)
            story.append(Paragraph(
                f"• {_md_inline(cleaned_text)}",
                bullet_style,
            ))

        elif stripped in ("---", "___"):
            _flush_bullets()
            story.append(HRFlowable(width="100%", thickness=0.5,
                                    color=colors.HexColor("#D1D5DB"),
                                    spaceBefore=6, spaceAfter=6))

        elif stripped == "":
            _flush_bullets()
            story.append(Spacer(1, 6))

        else:
            _flush_bullets()
            story.append(Paragraph(_md_inline(stripped), body_style))

    _flush_bullets()

    doc.build(story)
    buf.seek(0)
    return buf.read()


def _md_inline(text: str) -> str:
    """Convert inline **bold** and *italic* to ReportLab XML tags."""
    # Bold: **text**
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # Italic: *text*
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    # Escape any bare & that aren't already entities
    text = re.sub(r"&(?!amp;|lt;|gt;|quot;|#)", "&amp;", text)
    return text
