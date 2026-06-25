import io
from datetime import datetime
from html import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    KeepTogether, HRFlowable
)
from config import APP_NAME, APP_SUBTITLE, FRAMEWORK_NAME
from modules.engine import STAKEHOLDERS

NAVY = '#07111F'
BLUE = '#2563EB'
CYAN = '#06B6D4'
PURPLE = '#7C3AED'
PINK = '#DB2777'
SLATE = '#334155'
LIGHT = '#F8FAFC'
BORDER = '#D7E3F1'
GOLD = '#F59E0B'
RED = '#DC2626'
GREEN = '#16A34A'


def _pct(x):
    try:
        return f"{float(x) * 100:.1f}%"
    except Exception:
        return str(x)


def _short(text, n=260):
    text = ' '.join(str(text).split())
    return text if len(text) <= n else text[:n-1].rstrip() + '...'


def html_report(theme_df, risk_df, codes_df, analysis):
    """Premium self-contained HTML report preview."""
    max_freq = max(theme_df['Evidence Frequency'].max(), 1) if not theme_df.empty else 1
    dim_cards = ''
    palette = [BLUE, CYAN, PURPLE, PINK, GOLD, GREEN, '#0EA5E9', '#64748B']
    for i, r in theme_df.iterrows():
        color = palette[len(dim_cards) % len(palette)] if False else palette[list(theme_df.index).index(i) % len(palette)]
        width = max(8, int(r['Evidence Frequency'] / max_freq * 100))
        dim_cards += f"""
        <div class='dim-card'>
          <div class='dim-top'><b>{escape(str(r['Dimension']))}</b><span>{r['Evidence Frequency']}</span></div>
          <div class='bar-track'><div class='bar-fill' style='width:{width}%;background:{color};'></div></div>
          <small>Relative weight: {_pct(r['Relative Weight'])}</small>
        </div>"""

    risk_cards = ''
    for _, r in risk_df.iterrows():
        sev = 'risk-high' if r['Interpretation'] == 'Strong signal' else 'risk-med' if r['Interpretation'] == 'Present' else 'risk-low'
        risk_cards += f"""
        <div class='risk-card {sev}'>
          <div><b>{escape(str(r['Risk Indicator']))}</b></div>
          <span>{r['Detected Evidence']} evidence hits</span>
          <small>{escape(str(r['Interpretation']))}</small>
        </div>"""

    evidence_html = ''
    for theme, evs in analysis.get('evidence', {}).items():
        if evs:
            bullets = ''.join([f"<li>{escape(_short(e, 330))}</li>" for e in evs[:3]])
            evidence_html += f"<div class='evidence-box'><h3>{escape(theme)}</h3><ul>{bullets}</ul></div>"

    stakeholder_html = ''.join([
        f"<div class='stake'><b>{escape(s)}</b><p>{escape(a)}</p></div>"
        for s, a in STAKEHOLDERS.items()
    ])

    terms = ', '.join([f"{escape(t)} <b>{c}</b>" for t, c in analysis.get('top_terms', [])[:18]])
    risk_level_class = 'level-high' if analysis.get('risk_level') == 'High' else 'level-med' if analysis.get('risk_level') == 'Moderate' else 'level-low'

    return f"""
    <style>
    .lux-report{{background:#fff;color:#0f172a;border-radius:28px;overflow:hidden;box-shadow:0 25px 80px rgba(0,0,0,.30);font-family:Inter,Arial,sans-serif;}}
    .lux-cover{{padding:46px 44px;background:linear-gradient(135deg,#06132e 0%,#102a69 45%,#7c3aed 100%);color:white;position:relative;}}
    .lux-cover:after{{content:'';position:absolute;right:-90px;top:-90px;width:260px;height:260px;border-radius:50%;background:rgba(255,255,255,.16);}}
    .eyebrow{{letter-spacing:.16em;text-transform:uppercase;font-size:12px;color:#bae6fd;font-weight:900;}}
    .lux-cover h1{{font-size:50px;line-height:1.02;margin:12px 0 8px;font-weight:950;letter-spacing:-1.6px;color:white;}}
    .lux-cover p{{font-size:17px;color:#e0f2fe;max-width:780px;}}
    .lux-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:28px;}}
    .lux-kpi{{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.24);border-radius:20px;padding:18px;backdrop-filter:blur(8px);}}
    .lux-kpi small{{display:block;color:#cbd5e1;font-weight:800;text-transform:uppercase;font-size:11px;}}
    .lux-kpi b{{font-size:30px;color:white;}}
    .lux-body{{padding:34px 42px;}}
    .section-title{{font-size:25px;color:#0f172a;font-weight:950;margin:34px 0 14px;border-left:6px solid #2563eb;padding-left:12px;}}
    .summary-box{{background:linear-gradient(135deg,#eff6ff,#f5f3ff);border:1px solid #dbeafe;border-radius:22px;padding:22px;font-size:15px;}}
    .level-high{{color:#991b1b;background:#fee2e2;border:1px solid #fecaca;padding:4px 10px;border-radius:999px;font-weight:900;}}
    .level-med{{color:#92400e;background:#fef3c7;border:1px solid #fde68a;padding:4px 10px;border-radius:999px;font-weight:900;}}
    .level-low{{color:#166534;background:#dcfce7;border:1px solid #bbf7d0;padding:4px 10px;border-radius:999px;font-weight:900;}}
    .dim-wrap{{display:grid;grid-template-columns:1fr 1fr;gap:14px;}}
    .dim-card{{border:1px solid #e2e8f0;background:#f8fafc;border-radius:18px;padding:16px;}}
    .dim-top{{display:flex;justify-content:space-between;gap:10px;align-items:center;}}
    .dim-top span{{background:#0f172a;color:white;border-radius:999px;padding:3px 9px;font-size:12px;font-weight:900;}}
    .bar-track{{height:9px;background:#e2e8f0;border-radius:999px;overflow:hidden;margin:10px 0;}}
    .bar-fill{{height:9px;border-radius:999px;}}
    .risk-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;}}
    .risk-card{{border-radius:18px;padding:15px;border:1px solid #e2e8f0;min-height:105px;}}
    .risk-card b{{font-size:14px;}}
    .risk-card span{{display:block;font-size:22px;font-weight:950;margin-top:8px;}}
    .risk-card small{{font-weight:800;}}
    .risk-high{{background:#fff1f2;border-color:#fecdd3;}}
    .risk-med{{background:#fffbeb;border-color:#fde68a;}}
    .risk-low{{background:#f0fdf4;border-color:#bbf7d0;}}
    .framework{{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin:16px 0;}}
    .fw-step{{background:#0f172a;color:white;border-radius:16px;padding:14px;text-align:center;font-weight:900;font-size:13px;}}
    .evidence-box{{border:1px solid #e2e8f0;border-radius:18px;padding:16px;margin-bottom:12px;background:white;}}
    .evidence-box h3{{margin:0 0 8px;color:#1d4ed8;}}
    .evidence-box li{{margin-bottom:8px;line-height:1.45;}}
    .stake-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;}}
    .stake{{border:1px solid #e2e8f0;background:#f8fafc;border-radius:18px;padding:16px;}}
    .stake b{{color:#0f172a;}}
    .stake p{{margin:6px 0 0;color:#475569;}}
    .terms{{background:#0f172a;color:#e2e8f0;border-radius:18px;padding:18px;line-height:1.8;}}
    </style>
    <div class='lux-report'>
      <div class='lux-cover'>
        <div class='eyebrow'>Strategic Intelligence Output</div>
        <h1>{APP_NAME}<br/>Intelligence Report</h1>
        <p>{APP_SUBTITLE}. Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')}.</p>
        <div class='lux-grid'>
          <div class='lux-kpi'><small>Risk Score</small><b>{analysis['risk_score']}/100</b></div>
          <div class='lux-kpi'><small>Risk Level</small><b>{analysis['risk_level']}</b></div>
          <div class='lux-kpi'><small>Dimensions</small><b>{len(theme_df)}</b></div>
          <div class='lux-kpi'><small>Words Analysed</small><b>{len(analysis.get('text','').split()):,}</b></div>
        </div>
      </div>
      <div class='lux-body'>
        <div class='section-title'>Executive Summary</div>
        <div class='summary-box'>The analysed corpus indicates a <span class='{risk_level_class}'>{analysis['risk_level']} risk profile</span> with a score of <b>{analysis['risk_score']}/100</b>. The report translates interview evidence into a multi-layer ecosystem interpretation covering digital recruitment, psychological manipulation, victim vulnerability, financial movement, institutional response, and prevention capacity.</div>
        <div class='section-title'>Ecosystem Dimension Strength</div>
        <div class='dim-wrap'>{dim_cards}</div>
        <div class='section-title'>Risk Indicator Heatmap</div>
        <div class='risk-grid'>{risk_cards}</div>
        <div class='section-title'>{FRAMEWORK_NAME}</div>
        <div class='framework'><div class='fw-step'>Digital Recruitment</div><div class='fw-step'>Manipulation</div><div class='fw-step'>Victim Decision</div><div class='fw-step'>Financial Chain</div><div class='fw-step'>Institutional Response</div><div class='fw-step'>Prevention Capacity</div></div>
        <p>The framework positions scam prevention as a connected ecosystem rather than an isolated enforcement problem.</p>
        <div class='section-title'>Selected Qualitative Evidence</div>{evidence_html}
        <div class='section-title'>Stakeholder Prevention Matrix</div><div class='stake-grid'>{stakeholder_html}</div>
        <div class='section-title'>Analytical Terms</div><div class='terms'>{terms}</div>
      </div>
    </div>"""


def _make_styles():
    styles = getSampleStyleSheet()
    for name in ['TitleX','SubTitleX','H1X','H2X','BodyX','SmallX','TinyX','WhiteTitle','WhiteBody','CardTitle','CardValue']:
        if name in styles:
            del styles[name]
    styles.add(ParagraphStyle('WhiteTitle', parent=styles['Title'], textColor=colors.white, fontSize=30, leading=34, alignment=TA_LEFT, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle('WhiteBody', parent=styles['BodyText'], textColor=colors.HexColor('#E0F2FE'), fontSize=10.5, leading=14))
    styles.add(ParagraphStyle('TitleX', parent=styles['Title'], textColor=colors.HexColor(NAVY), fontSize=24, leading=28, alignment=TA_LEFT, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle('SubTitleX', parent=styles['BodyText'], textColor=colors.HexColor(SLATE), fontSize=10.5, leading=14))
    styles.add(ParagraphStyle('H1X', parent=styles['Heading1'], textColor=colors.HexColor(NAVY), fontSize=17, leading=20, spaceBefore=8, spaceAfter=8, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle('H2X', parent=styles['Heading2'], textColor=colors.HexColor(BLUE), fontSize=13, leading=16, spaceBefore=8, spaceAfter=6, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle('BodyX', parent=styles['BodyText'], fontSize=9.3, leading=13.2, textColor=colors.HexColor('#1E293B')))
    styles.add(ParagraphStyle('SmallX', parent=styles['BodyText'], fontSize=7.8, leading=10.5, textColor=colors.HexColor('#334155')))
    styles.add(ParagraphStyle('TinyX', parent=styles['BodyText'], fontSize=6.7, leading=8.5, textColor=colors.HexColor('#475569')))
    styles.add(ParagraphStyle('CardTitle', parent=styles['BodyText'], fontSize=7.2, leading=9, textColor=colors.HexColor('#CBD5E1'), fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle('CardValue', parent=styles['BodyText'], fontSize=18, leading=21, textColor=colors.white, fontName='Helvetica-Bold'))
    return styles


def _p(text, style):
    return Paragraph(escape(str(text)).replace('\n', '<br/>'), style)


def _header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(colors.HexColor(NAVY))
    canvas.rect(0, height-1.05*cm, width, 1.05*cm, stroke=0, fill=1)
    canvas.setFillColor(colors.white)
    canvas.setFont('Helvetica-Bold', 8)
    canvas.drawString(1.35*cm, height-0.65*cm, f'{APP_NAME} Intelligence Report')
    canvas.setFont('Helvetica', 7)
    canvas.drawRightString(width-1.35*cm, height-0.65*cm, f'Page {doc.page}')
    canvas.setFillColor(colors.HexColor('#94A3B8'))
    canvas.setFont('Helvetica', 7)
    canvas.drawString(1.35*cm, 0.85*cm, 'Generated by SCAMVERSE - Online Investment Scam Ecosystem Intelligence Platform')
    canvas.restoreState()


def _cover(canvas, doc, analysis):
    canvas.saveState()
    width, height = A4
    # dark background with block gradient feel
    colors_list = [NAVY, '#0B1F4D', '#1D4ED8', PURPLE]
    band_h = height / len(colors_list)
    for i, c in enumerate(colors_list):
        canvas.setFillColor(colors.HexColor(c))
        canvas.rect(0, height-(i+1)*band_h, width, band_h+1, stroke=0, fill=1)
    # decorative circles
    canvas.setFillColor(colors.Color(1,1,1, alpha=0.10))
    canvas.circle(width-1.2*cm, height-1.4*cm, 3.2*cm, stroke=0, fill=1)
    canvas.circle(width-5.0*cm, 2.2*cm, 2.4*cm, stroke=0, fill=1)
    canvas.setFillColor(colors.HexColor(CYAN))
    canvas.rect(1.35*cm, height-2.7*cm, 2.4*cm, 0.12*cm, stroke=0, fill=1)
    canvas.setFillColor(colors.white)
    canvas.setFont('Helvetica-Bold', 12)
    canvas.drawString(1.35*cm, height-3.35*cm, 'STRATEGIC INTELLIGENCE OUTPUT')
    canvas.setFont('Helvetica-Bold', 34)
    canvas.drawString(1.35*cm, height-4.55*cm, APP_NAME)
    canvas.drawString(1.35*cm, height-5.75*cm, 'Intelligence Report')
    canvas.setFont('Helvetica', 11)
    canvas.setFillColor(colors.HexColor('#E0F2FE'))
    canvas.drawString(1.35*cm, height-6.55*cm, APP_SUBTITLE)
    canvas.drawString(1.35*cm, height-7.10*cm, f"Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')}")
    # KPI cards
    card_y = height-10.1*cm
    card_w = 4.15*cm
    gap = 0.35*cm
    kpis = [('Risk Score', f"{analysis['risk_score']}/100"), ('Risk Level', analysis['risk_level']), ('Dimensions', '8'), ('Corpus Words', f"{len(analysis.get('text','').split()):,}")]
    for i,(lab,val) in enumerate(kpis):
        x = 1.35*cm + i*(card_w+gap)
        canvas.setFillColor(colors.Color(1,1,1, alpha=0.14))
        canvas.roundRect(x, card_y, card_w, 2.25*cm, 12, stroke=0, fill=1)
        canvas.setFillColor(colors.HexColor('#BAE6FD'))
        canvas.setFont('Helvetica-Bold', 7.5)
        canvas.drawString(x+0.32*cm, card_y+1.48*cm, lab.upper())
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica-Bold', 17)
        canvas.drawString(x+0.32*cm, card_y+0.65*cm, str(val)[:18])
    canvas.setFillColor(colors.white)
    canvas.setFont('Helvetica-Bold', 13)
    canvas.drawString(1.35*cm, 3.25*cm, FRAMEWORK_NAME)
    canvas.setFillColor(colors.HexColor('#DBEAFE'))
    canvas.setFont('Helvetica', 9.5)
    canvas.drawString(1.35*cm, 2.75*cm, 'Digital recruitment - manipulation - victim decision - financial chain - institutional response - prevention capacity')
    canvas.restoreState()


def _section_label(text, styles):
    return KeepTogether([
        Spacer(1, 0.08*cm),
        Table([[Paragraph(text, styles['H1X'])]], colWidths=[16.2*cm], style=TableStyle([
            ('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#EFF6FF')),
            ('BOX',(0,0),(-1,-1),0.5,colors.HexColor('#BFDBFE')),
            ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
        ]))
    ])


def _card_table(items, styles, columns=2):
    rows = []
    row = []
    for title, value, note, color in items:
        cell = Table([[Paragraph(title, styles['CardTitle'])],[Paragraph(value, styles['CardValue'])],[Paragraph(note, styles['TinyX'])]], colWidths=[7.75*cm if columns==2 else 3.82*cm])
        cell.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,-1),colors.HexColor(color)),
            ('BOX',(0,0),(-1,-1),0.4,colors.HexColor(color)),
            ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
        ]))
        row.append(cell)
        if len(row) == columns:
            rows.append(row); row=[]
    if row:
        while len(row)<columns: row.append('')
        rows.append(row)
    t = Table(rows, colWidths=[8.05*cm]*columns if columns==2 else [4.05*cm]*columns, hAlign='LEFT')
    t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
    return t


def _para_table(data, widths, styles, header=BLUE, font_size=7.5):
    converted = []
    for r, row in enumerate(data):
        converted_row = []
        for cell in row:
            style = styles['SmallX'] if r else ParagraphStyle('TblHeadTmp', parent=styles['SmallX'], textColor=colors.white, fontName='Helvetica-Bold', fontSize=font_size, leading=font_size+2)
            converted_row.append(Paragraph(escape(str(cell)), style))
        converted.append(converted_row)
    t = Table(converted, colWidths=widths, repeatRows=1, splitByRow=1)
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor(header)),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('GRID',(0,0),(-1,-1),0.28,colors.HexColor(BORDER)),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#F8FAFC'), colors.white]),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
    ]))
    return t


def pdf_report(theme_df, risk_df, codes_df, analysis):
    """Premium PDF report with cover, KPI cards, cleaner tables and no clipped text."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=1.35*cm, leftMargin=1.35*cm, topMargin=1.55*cm, bottomMargin=1.35*cm)
    styles = _make_styles()
    story = []

    story.append(Spacer(1, 25.5*cm))
    story.append(PageBreak())

    # Executive Summary
    story.append(_section_label('1. Executive Summary', styles))
    summary = (f"The analysed transcript corpus indicates a <b>{analysis['risk_level']}</b> risk profile with a score of "
               f"<b>{analysis['risk_score']}/100</b>. The strongest signals are interpreted through the {FRAMEWORK_NAME}, "
               "which treats online investment scams as a connected ecosystem of digital recruitment, psychological manipulation, "
               "victim decision behaviour, financial transaction chains, institutional response and prevention capacity.")
    story.append(Paragraph(summary, styles['BodyX']))
    story.append(Spacer(1, 0.18*cm))
    story.append(_card_table([
        ('RISK SCORE', f"{analysis['risk_score']}/100", 'Automated warning-signal index', BLUE),
        ('RISK LEVEL', analysis['risk_level'], 'Overall corpus-level profile', RED if analysis['risk_level']=='High' else GOLD),
        ('DIMENSIONS', str(len(theme_df)), 'Integrated ecosystem dimensions', PURPLE),
        ('WORDS ANALYSED', f"{len(analysis.get('text','').split()):,}", 'Transcript corpus size', '#0F766E'),
    ], styles, columns=4))

    # Dimensions as premium cards
    story.append(_section_label('2. Ecosystem Dimension Strength', styles))
    max_freq = max(theme_df['Evidence Frequency'].max(), 1) if not theme_df.empty else 1
    dim_items=[]
    dim_colors=[BLUE, '#0EA5E9', PURPLE, '#0F766E', PINK, GOLD, '#475569', '#1E40AF']
    for idx, (_, r) in enumerate(theme_df.iterrows()):
        val = f"{r['Evidence Frequency']} hits"
        note = f"Relative weight: {_pct(r['Relative Weight'])} | intensity: {int(r['Evidence Frequency']/max_freq*100)}%"
        dim_items.append((str(r['Dimension']).upper(), val, note, dim_colors[idx % len(dim_colors)]))
    story.append(_card_table(dim_items, styles, columns=2))

    # Risk heatmap table
    story.append(_section_label('3. Risk Indicator Heatmap', styles))
    risk_data = [['Risk Indicator', 'Evidence Hits', 'Signal Strength', 'Action Priority']]
    for _, r in risk_df.iterrows():
        hits = int(r['Detected Evidence'])
        priority = 'Critical' if hits >= 10 else 'High' if hits >= 3 else 'Monitor' if hits > 0 else 'Low'
        risk_data.append([r['Risk Indicator'], hits, r['Interpretation'], priority])
    story.append(_para_table(risk_data, [7.2*cm, 2.5*cm, 3.0*cm, 3.2*cm], styles, header=PURPLE))

    # Framework page
    story.append(PageBreak())
    story.append(_section_label(f'4. {FRAMEWORK_NAME}', styles))
    story.append(Paragraph('The framework below translates qualitative evidence into a prevention-oriented ecosystem model. It connects upstream digital exposure to downstream enforcement and prevention response.', styles['BodyX']))
    fw = [['Digital Recruitment', 'Manipulation Cues', 'Victim Decision', 'Financial Chain', 'Institutional Response', 'Prevention Capacity']]
    fw_tbl = Table([[Paragraph(x, ParagraphStyle('fw', parent=styles['SmallX'], textColor=colors.white, alignment=TA_CENTER, fontName='Helvetica-Bold')) for x in fw[0]]], colWidths=[2.65*cm]*6)
    fw_tbl.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(0,0),colors.HexColor(BLUE)),('BACKGROUND',(1,0),(1,0),colors.HexColor(PURPLE)),('BACKGROUND',(2,0),(2,0),colors.HexColor(PINK)),('BACKGROUND',(3,0),(3,0),colors.HexColor(GOLD)),('BACKGROUND',(4,0),(4,0),colors.HexColor('#0F766E')),('BACKGROUND',(5,0),(5,0),colors.HexColor(NAVY)),
        ('BOX',(0,0),(-1,-1),0.5,colors.white),('INNERGRID',(0,0),(-1,-1),1,colors.white),('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10)
    ]))
    story.append(fw_tbl)
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph('<b>Mathematical ecosystem representation</b>', styles['H2X']))
    story.append(Paragraph('Scam ecosystem risk can be represented as <b>S = f(D, M, V, O, F, I, P)</b>, where D is digital recruitment exposure, M is manipulation intensity, V is victim vulnerability, O is operational sophistication, F is financial-chain complexity, I is institutional coordination gap and P is preventive capacity.', styles['BodyX']))
    story.append(Paragraph('The prevention index can be expressed as <b>PI = Σ w_i C_i - Σ λ_j R_j</b>, where stakeholder capability terms reduce residual risk indicators.', styles['BodyX']))

    # Evidence section
    story.append(_section_label('5. Selected Qualitative Evidence by Dimension', styles))
    for theme, evs in analysis.get('evidence', {}).items():
        if not evs:
            continue
        story.append(KeepTogether([
            Paragraph(theme, styles['H2X']),
            _para_table([['Evidence Extract']] + [[_short(e, 430)] for e in evs[:3]], [16.0*cm], styles, header='#0F766E')
        ]))
        story.append(Spacer(1, 0.12*cm))

    # Coding evidence concise appendix
    story.append(PageBreak())
    story.append(_section_label('6. Coding Evidence Snapshot', styles))
    code_rows = [['Dimension', 'Indicative Code', 'Evidence Extract']]
    if not codes_df.empty:
        for _, r in codes_df.head(24).iterrows():
            code_rows.append([r['Dimension'], r['Indicative Code'], _short(r['Evidence Extract'], 210)])
    story.append(_para_table(code_rows, [4.4*cm, 3.0*cm, 8.6*cm], styles, header='#0F766E', font_size=7.2))

    story.append(_section_label('7. Stakeholder Prevention Matrix', styles))
    st_rows = [['Stakeholder', 'Prevention Role']]
    for s, a in STAKEHOLDERS.items():
        st_rows.append([s, a])
    story.append(_para_table(st_rows, [4.1*cm, 11.9*cm], styles, header=NAVY))

    story.append(_section_label('8. Executive Recommendations', styles))
    recs = [
        'Prioritise early-warning indicators involving unrealistic returns, Telegram/social-media recruitment, fake testimonials and mule-account transfers.',
        'Strengthen operational data-sharing between PDRM/CCID, BNM, banks, SSM, SKMM, NSRC and platform operators.',
        'Convert repeated coding evidence into a national prevention taxonomy for public education, investigation triage and policy design.',
        'Use SCAMVERSE outputs as the software artefact for a SoftwareX paper and as empirical evidence support for the Q1 framework paper.'
    ]
    for i, rec in enumerate(recs, 1):
        story.append(Paragraph(f'<b>{i}.</b> {rec}', styles['BodyX']))

    story.append(Spacer(1, 0.2*cm))
    story.append(HRFlowable(width='100%', color=colors.HexColor('#CBD5E1'), thickness=0.5))
    story.append(Paragraph('<b>Analytical Terms:</b> ' + ', '.join([f'{escape(t)} ({c})' for t,c in analysis.get('top_terms', [])[:22]]), styles['SmallX']))

    doc.build(story, onFirstPage=lambda c,d: _cover(c,d,analysis), onLaterPages=_header_footer)
    buf.seek(0)
    return buf.getvalue()
