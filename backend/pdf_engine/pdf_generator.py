"""
VIDHI — Professional Legal Notice PDF Generator
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# Brand colours
VIDHI_PURPLE = colors.HexColor("#7c3aed")
VIDHI_DARK   = colors.HexColor("#1e1b4b")
GOLD         = colors.HexColor("#f59e0b")
LIGHT_PURPLE = colors.HexColor("#ede9fe")
WHITE        = colors.white
BLACK        = colors.HexColor("#0f0f0f")

def generate_notice_pdf(
    citizen_name:  str,
    opponent_name: str,
    opponent_addr: str,
    situation:     str,
    notice_text:   str,
    act:           str,
    section:       str,
    authority:     str,
    win_prob:      float,
    output_dir:    str = None
) -> str:
    if output_dir is None:
        output_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "outputs", "notices"
        )
    os.makedirs(output_dir, exist_ok=True)

    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_dir, f"VIDHI_Notice_{ts}.pdf")
    doc      = SimpleDocTemplate(
        filename, pagesize=A4,
        leftMargin=2.5*cm, rightMargin=2.5*cm,
        topMargin=2*cm,    bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    story  = []

    # ── Header Banner ────────────────────────────────────────
    header_data = [[
        Paragraph(
            '<font color="#ffffff" size="18"><b>⚖ VIDHI</b></font><br/>'
            '<font color="#c4b5fd" size="8">AI-Powered Legal Rights Platform · Free for All Indians</font>',
            ParagraphStyle("h", fontName="Helvetica-Bold", alignment=TA_LEFT)
        ),
        Paragraph(
            f'<font color="#c4b5fd" size="7">Date: {datetime.now().strftime("%d %B %Y")}<br/>'
            f'Ref: VIDHI/{ts[:8]}<br/>'
            f'Win Probability: <b>{win_prob}%</b></font>',
            ParagraphStyle("hr", fontName="Helvetica", alignment=TA_CENTER)
        )
    ]]
    header_table = Table(header_data, colWidths=[12*cm, 5*cm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,-1), VIDHI_DARK),
        ("TEXTCOLOR",   (0,0), (-1,-1), WHITE),
        ("ROWPADDING",  (0,0), (-1,-1), 14),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ("ROUNDEDCORNERS", [8]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.5*cm))

    # ── LEGAL NOTICE Title ───────────────────────────────────
    story.append(Paragraph(
        "LEGAL NOTICE",
        ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=16,
                        textColor=VIDHI_PURPLE, alignment=TA_CENTER,
                        spaceAfter=4)
    ))
    story.append(Paragraph(
        f"Under: {act} — {section}",
        ParagraphStyle("sub", fontName="Helvetica", fontSize=9,
                        textColor=colors.grey, alignment=TA_CENTER)
    ))
    story.append(Spacer(1, 0.4*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=VIDHI_PURPLE))
    story.append(Spacer(1, 0.4*cm))

    # ── Parties ──────────────────────────────────────────────
    parties_data = [
        ["FROM (Complainant):", citizen_name],
        ["TO (Respondent):",    opponent_name],
        ["Address:",            opponent_addr],
    ]
    parties_table = Table(parties_data, colWidths=[4.5*cm, 12.5*cm])
    parties_table.setStyle(TableStyle([
        ("FONTNAME",    (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME",    (1,0), (1,-1), "Helvetica"),
        ("FONTSIZE",    (0,0), (-1,-1), 9),
        ("TEXTCOLOR",   (0,0), (0,-1), VIDHI_PURPLE),
        ("TEXTCOLOR",   (1,0), (1,-1), BLACK),
        ("ROWPADDING",  (0,0), (-1,-1), 5),
        ("BACKGROUND",  (0,0), (-1,-1), LIGHT_PURPLE),
        ("ROUNDEDCORNERS", [6]),
    ]))
    story.append(parties_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Notice Body ──────────────────────────────────────────
    story.append(Paragraph("Notice:", ParagraphStyle(
        "nl", fontName="Helvetica-Bold", fontSize=10, textColor=VIDHI_DARK)))
    story.append(Spacer(1, 0.2*cm))

    for para in notice_text.split("\n\n"):
        if para.strip():
            story.append(Paragraph(
                para.strip().replace("\n", " "),
                ParagraphStyle("body", fontName="Helvetica", fontSize=9.5,
                                textColor=BLACK, leading=16, alignment=TA_JUSTIFY)
            ))
            story.append(Spacer(1, 0.3*cm))

    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    story.append(Spacer(1, 0.3*cm))

    # ── Authority & Relief ───────────────────────────────────
    auth_data = [
        ["File Complaint At:", authority],
        ["Deadline:",          "30 days from receipt of this notice"],
        ["AI Win Probability:",f"{win_prob}% (based on 100 Monte Carlo simulations)"],
    ]
    auth_table = Table(auth_data, colWidths=[4.5*cm, 12.5*cm])
    auth_table.setStyle(TableStyle([
        ("FONTNAME",   (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 9),
        ("TEXTCOLOR",  (0,0), (0,-1), GOLD),
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#1c1917")),
        ("TEXTCOLOR",  (1,0), (1,-1), WHITE),
        ("ROWPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(auth_table)
    story.append(Spacer(1, 0.6*cm))

    # ── Signature ────────────────────────────────────────────
    sig_data = [[
        Paragraph(
            f'<b>{citizen_name}</b><br/>'
            '<font size="8">Complainant</font>',
            ParagraphStyle("sig", fontName="Helvetica", fontSize=10, alignment=TA_LEFT)
        ),
        Paragraph(
            '<b>VIDHI Legal AI Platform</b><br/>'
            '<font size="8" color="#7c3aed">Powered by LangGraph + Local LLM</font><br/>'
            '<font size="7">vidhi.legal · Free for every Indian citizen</font>',
            ParagraphStyle("sig2", fontName="Helvetica", fontSize=9, alignment=TA_CENTER)
        )
    ]]
    sig_table = Table(sig_data, colWidths=[8*cm, 9*cm])
    sig_table.setStyle(TableStyle([
        ("ROWPADDING",  (0,0), (-1,-1), 8),
        ("VALIGN",      (0,0), (-1,-1), "BOTTOM"),
        ("LINEABOVE",   (0,0), (0,0), 1, VIDHI_PURPLE),
        ("LINEABOVE",   (1,0), (1,0), 1, GOLD),
    ]))
    story.append(sig_table)

    # ── Footer Disclaimer ────────────────────────────────────
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(
        "This notice was auto-generated by VIDHI AI. It is legally formatted under Indian law. "
        "Consult a licensed advocate for court proceedings. VIDHI is a free public service.",
        ParagraphStyle("disc", fontName="Helvetica-Oblique", fontSize=7,
                        textColor=colors.grey, alignment=TA_CENTER)
    ))

    doc.build(story)
    return filename
