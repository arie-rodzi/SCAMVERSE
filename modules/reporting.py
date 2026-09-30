"""HTML and PDF intelligence reports.

Both reports carry the same sections, built from the shared analysis object:
summary, dimension profile, risk-indicator profile, IMSPF framework, qualitative
evidence, coding snapshot, stakeholder matrix, recommendations and top terms.
The layout is deliberately formal: black text, one accent colour, ruled tables.
"""
import io
from datetime import datetime
from html import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.platypus import (HRFlowable, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

from config import APP_NAME, APP_SUBTITLE, APP_VERSION, FRAMEWORK_NAME
from modules.engine import RISK_CAP, STAKEHOLDERS

INK = '#1B1F24'
INK_2 = '#545B66'
RULE = '#C9CDD3'
FAINT = '#F4F5F7'
ACCENT = '#1F5FA8'

PREVENTION_LAYERS = [
    'Digital-platform intelligence',
    'Victim vulnerability reduction',
    'Scam operational disruption',
    'Financial-chain monitoring',
    'Multi-agency enforcement coordination',
    'Public resilience and rapid reporting',
]

RECOMMENDATIONS = [
    'Prioritise early-warning indicators involving unrealistic returns, social-media recruitment, '
    'fake testimonials and mule-account transfers.',
    'Strengthen operational data-sharing between PDRM/CCID, BNM, banks, SSM, SKMM, NSRC and platform operators.',
    'Convert repeated coding evidence into a prevention taxonomy for public education, investigation triage '
    'and policy design.',
    'Re-run the analysis on new transcript batches to track how dimension and indicator profiles shift over '
    'time and across case types.',
]


def action_priority(hits: int) -> str:
    """Action priority used in both reports (based on raw lexicon matches)."""
    return 'Critical' if hits >= 10 else 'High' if hits >= 3 else 'Monitor' if hits > 0 else 'Low'


def _pct(x):
    try:
        return f"{float(x) * 100:.1f}%"
    except (TypeError, ValueError):
        return str(x)


def _short(text, n=260):
    text = ' '.join(str(text).split())
    return text if len(text) <= n else text[:n - 1].rstrip() + '...'


def _summary_sentence(analysis, theme_df, risk_df):
    active = int((theme_df['Evidence Frequency'] > 0).sum())
    lead_dim = theme_df.iloc[0]['Dimension'] if not theme_df.empty and theme_df.iloc[0]['Evidence Frequency'] > 0 else None
    top_ind = risk_df.sort_values('Matches', ascending=False, kind='stable')
    lead_ind = top_ind.iloc[0]['Warning Indicator'] if not top_ind.empty and top_ind.iloc[0]['Matches'] > 0 else None
    s = (f"The corpus of {len(analysis.get('text', '').split()):,} words returns a bounded warning-signal index of "
         f"{analysis['risk_score']}/100 ({analysis['risk_level']} band), with evidence in {active} of "
         f"{len(theme_df)} ecosystem dimensions.")
    if lead_dim:
        s += f" The strongest dimension is {lead_dim}"
        s += f" and the most frequent indicator is {lead_ind.lower()}." if lead_ind else "."
    return s


def _provenance(analysis):
    """Reproducibility record: software version, lexicon and corpus fingerprints."""
    lex = analysis.get('lexicon_name', 'default')
    return (f"Reproducibility: {APP_NAME} v{APP_VERSION}; {lex} lexicon SHA-256 "
            f"{analysis.get('lexicon_sha256', 'n/a')[:16]}; corpus SHA-256 {analysis.get('corpus_sha256', 'n/a')[:16]}.")


# ----------------------------------------------------------------------------- HTML

def html_report(theme_df, risk_df, codes_df, analysis):
    """HTML report fragment (styled block); wrap with html_document() for a standalone file."""
    generated = datetime.now().strftime('%d %B %Y, %H:%M')
    max_freq = max(int(theme_df['Evidence Frequency'].max()), 1) if not theme_df.empty else 1

    dim_rows = ''.join(
        f"<tr><td>{escape(str(r['Dimension']))}</td><td class='num'>{r['Evidence Frequency']}</td>"
        f"<td class='num'>{_pct(r['Relative Weight'])}</td>"
        f"<td><div class='bar'><span style='width:{int(r['Evidence Frequency'] / max_freq * 100)}%'></span></div></td></tr>"
        for _, r in theme_df.iterrows())

    risk_rows = ''.join(
        f"<tr><td>{escape(str(r['Warning Indicator']))}</td><td class='num'>{r['Matches']}</td>"
        f"<td class='num'>{r['Index Contribution']}/{RISK_CAP}</td><td class='num'>{r['Per 1,000 Words']:.2f}</td>"
        f"<td>{escape(str(r['Interpretation']))}</td><td>{action_priority(int(r['Matches']))}</td></tr>"
        for _, r in risk_df.iterrows())

    evidence_html = ''
    for theme, evs in analysis.get('evidence', {}).items():
        if evs:
            items = ''.join(f"<li>{escape(_short(e, 330))}</li>" for e in evs[:3])
            evidence_html += f"<h3>{escape(theme)}</h3><ul>{items}</ul>"

    code_rows = ''.join(
        f"<tr><td>{escape(str(r['Dimension']))}</td><td>{escape(str(r['Indicative Code']))}</td>"
        f"<td>{escape(_short(r['Evidence Extract'], 220))}</td></tr>"
        for _, r in codes_df.head(24).iterrows()) if not codes_df.empty else ''

    stake_rows = ''.join(f"<tr><td>{escape(s)}</td><td>{escape(a)}</td></tr>" for s, a in STAKEHOLDERS.items())
    layers = ''.join(f"<li>{escape(x)}</li>" for x in PREVENTION_LAYERS)
    recs = ''.join(f"<li>{escape(x)}</li>" for x in RECOMMENDATIONS)
    terms = ', '.join(f"{escape(t)} ({c})" for t, c in analysis.get('top_terms', [])[:30])

    return f"""
<style>
.sv-report{{max-width:920px;margin:0 auto;background:#fff;color:{INK};font-family:"Source Sans Pro","Segoe UI",Arial,sans-serif;font-size:15px;line-height:1.5;padding:36px 44px;border:1px solid {RULE};}}
.sv-report header{{border-bottom:2px solid {ACCENT};padding-bottom:12px;margin-bottom:18px;}}
.sv-report header h1{{font-size:28px;margin:0;font-weight:700;}}
.sv-report header p{{margin:4px 0 0;color:{INK_2};}}
.sv-report h2{{font-size:19px;margin:28px 0 8px;padding-bottom:4px;border-bottom:1px solid {RULE};}}
.sv-report h3{{font-size:15px;margin:14px 0 4px;}}
.sv-report table{{width:100%;border-collapse:collapse;margin:6px 0 4px;font-size:14px;}}
.sv-report th{{text-align:left;font-weight:600;border-top:1.5px solid {INK};border-bottom:1px solid {INK};padding:5px 6px;}}
.sv-report td{{border-bottom:1px solid #E3E6EA;padding:5px 6px;vertical-align:top;}}
.sv-report tr:last-child td{{border-bottom:1.5px solid {INK};}}
.sv-report .num{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap;}}
.sv-report .bar{{background:{FAINT};height:9px;min-width:120px;}}
.sv-report .bar span{{display:block;height:9px;background:{ACCENT};}}
.sv-report .kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:0;border:1px solid {RULE};margin:10px 0;}}
.sv-report .kpis div{{padding:10px 12px;border-right:1px solid {RULE};}}
.sv-report .kpis div:last-child{{border-right:0;}}
.sv-report .kpis small{{display:block;color:{INK_2};font-size:12px;text-transform:uppercase;letter-spacing:.05em;}}
.sv-report .kpis b{{font-size:22px;font-variant-numeric:tabular-nums;}}
.sv-report .muted{{color:{INK_2};font-size:13px;}}
</style>
<div class='sv-report'>
  <header><h1>{APP_NAME} Intelligence Report</h1>
  <p>{APP_SUBTITLE} &middot; v{APP_VERSION} &middot; generated {generated}</p></header>
  <h2>1. Summary</h2>
  <div class='kpis'>
    <div><small>Warning-signal index</small><b>{analysis['risk_score']}/100</b></div>
    <div><small>Band</small><b>{analysis['risk_level']}</b></div>
    <div><small>Active dimensions</small><b>{int((theme_df['Evidence Frequency'] > 0).sum())}/{len(theme_df)}</b></div>
    <div><small>Words analysed</small><b>{len(analysis.get('text', '').split()):,}</b></div>
  </div>
  <p>{escape(_summary_sentence(analysis, theme_df, risk_df))}</p>
  <p class='muted'>{escape(_provenance(analysis))}</p>
  <h2>2. Ecosystem dimension profile</h2>
  <table><tr><th>Dimension</th><th class='num'>Matches</th><th class='num'>Share</th><th>Relative strength</th></tr>{dim_rows}</table>
  <h2>3. Warning-indicator profile</h2>
  <table><tr><th>Indicator</th><th class='num'>Matches</th><th class='num'>Index contribution</th><th class='num'>Per 1,000 words</th><th>Signal</th><th>Priority</th></tr>{risk_rows}</table>
  <p class='muted'>Index = floor(100 &times; &Sigma; min(matches, {RISK_CAP}) / ({RISK_CAP} &times; {len(risk_df)})). Bands: High &ge; 70, Moderate &ge; 35, otherwise Low. Bands, signal and priority (raw matches: Critical &ge; 10, High &ge; 3, Monitor &ge; 1) are descriptive and uncalibrated.</p>
  <h2>4. {escape(FRAMEWORK_NAME)}</h2>
  <p>Ecosystem risk is represented as S = f(D, M, V, O, F, I, P): digital recruitment, manipulation intensity, victim vulnerability, operational sophistication, financial-chain complexity, institutional coordination gap and preventive capacity. The prevention index PI = &Sigma; w<sub>i</sub>C<sub>i</sub> &minus; &Sigma; &lambda;<sub>j</sub>R<sub>j</sub> balances stakeholder capabilities against residual risk indicators. Prevention layers:</p>
  <ol>{layers}</ol>
  <h2>5. Qualitative evidence by dimension</h2>{evidence_html}
  <h2>6. Coding evidence (first 24 codes)</h2>
  <table><tr><th>Dimension</th><th>Code</th><th>Evidence extract</th></tr>{code_rows}</table>
  <h2>7. Stakeholder prevention matrix</h2>
  <table><tr><th>Stakeholder</th><th>Prevention role</th></tr>{stake_rows}</table>
  <h2>8. Recommendations</h2><ol>{recs}</ol>
  <p class='muted'><b>Most frequent terms:</b> {terms}</p>
</div>"""


def html_document(fragment: str) -> str:
    """Wrap the report fragment in a complete, standalone UTF-8 HTML document for download."""
    return ("<!DOCTYPE html>\n<html lang='en'>\n<head>\n<meta charset='utf-8'>\n"
            "<meta name='viewport' content='width=device-width, initial-scale=1'>\n"
            f"<title>{escape(APP_NAME)} Intelligence Report</title>\n"
            "<style>body{margin:0;padding:24px;background:#F4F5F7;}</style>\n"
            f"</head>\n<body>\n{fragment}\n</body>\n</html>\n")


# ----------------------------------------------------------------------------- PDF

def _styles():
    ss = getSampleStyleSheet()
    base = dict(fontName='Helvetica', textColor=colors.HexColor(INK))
    return {
        'title': ParagraphStyle('t', parent=ss['Title'], fontName='Helvetica-Bold', fontSize=20, leading=24,
                                alignment=TA_LEFT, textColor=colors.HexColor(INK), spaceAfter=2),
        'sub': ParagraphStyle('s', parent=ss['BodyText'], fontSize=9.5, leading=13, textColor=colors.HexColor(INK_2)),
        'h1': ParagraphStyle('h1', parent=ss['Heading2'], fontName='Helvetica-Bold', fontSize=12.5, leading=16,
                             spaceBefore=12, spaceAfter=5, textColor=colors.HexColor(INK)),
        'h2': ParagraphStyle('h2', parent=ss['Heading3'], fontName='Helvetica-Bold', fontSize=10, leading=13,
                             spaceBefore=6, spaceAfter=2, textColor=colors.HexColor(INK)),
        'body': ParagraphStyle('b', parent=ss['BodyText'], fontSize=9.2, leading=13, **base),
        'cell': ParagraphStyle('c', parent=ss['BodyText'], fontSize=8.2, leading=10.4, **base),
        'cellb': ParagraphStyle('cb', parent=ss['BodyText'], fontSize=8.2, leading=10.4, fontName='Helvetica-Bold',
                                textColor=colors.HexColor(INK)),
        'small': ParagraphStyle('sm', parent=ss['BodyText'], fontSize=7.8, leading=10.2,
                                textColor=colors.HexColor(INK_2)),
        'kpil': ParagraphStyle('kl', parent=ss['BodyText'], fontSize=7, leading=9, textColor=colors.HexColor(INK_2)),
        'kpiv': ParagraphStyle('kv', parent=ss['BodyText'], fontSize=15, leading=18, fontName='Helvetica-Bold',
                               textColor=colors.HexColor(INK)),
    }


def _booktabs(rows, widths, st, num_cols=()):
    """Ruled table: heavy top/bottom rules, light rule under the header, no fills."""
    data = []
    for i, row in enumerate(rows):
        out = []
        for j, v in enumerate(row):
            if hasattr(v, 'wrap'):
                out.append(v)
            else:
                style = st['cellb'] if i == 0 else st['cell']
                if j in num_cols:
                    style = ParagraphStyle('n', parent=style, alignment=2)
                out.append(Paragraph(escape(str(v)), style))
        data.append(out)
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 1.0, colors.HexColor(INK)),
        ('LINEBELOW', (0, 0), (-1, 0), 0.6, colors.HexColor(INK)),
        ('LINEBELOW', (0, -1), (-1, -1), 1.0, colors.HexColor(INK)),
        ('LINEBELOW', (0, 1), (-1, -2), 0.25, colors.HexColor('#E3E6EA')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4), ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    return t


def _bar(fraction, width=4.2 * cm, height=0.22 * cm):
    d = Drawing(width, height + 2)
    d.add(Rect(0, 1, width, height, fillColor=colors.HexColor(FAINT), strokeColor=None))
    d.add(Rect(0, 1, max(width * fraction, 0.5), height, fillColor=colors.HexColor(ACCENT), strokeColor=None))
    return d


def _page(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setStrokeColor(colors.HexColor(RULE)); canvas.setLineWidth(0.5)
    canvas.line(2 * cm, h - 1.35 * cm, w - 2 * cm, h - 1.35 * cm)
    canvas.setFont('Helvetica', 7.5); canvas.setFillColor(colors.HexColor(INK_2))
    canvas.drawString(2 * cm, h - 1.15 * cm, f'{APP_NAME} Intelligence Report')
    canvas.drawRightString(w - 2 * cm, h - 1.15 * cm, f'v{APP_VERSION}')
    canvas.line(2 * cm, 1.35 * cm, w - 2 * cm, 1.35 * cm)
    canvas.drawString(2 * cm, 0.95 * cm, 'Generated automatically from the analysed transcript corpus.')
    canvas.drawRightString(w - 2 * cm, 0.95 * cm, f'Page {doc.page}')
    canvas.restoreState()


def pdf_report(theme_df, risk_df, codes_df, analysis):
    """Paginated A4 PDF report; returns the PDF as bytes."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.9 * cm, bottomMargin=1.8 * cm,
                            title=f'{APP_NAME} Intelligence Report', author=APP_NAME)
    st = _styles()
    full = doc.width
    story = []

    story.append(Paragraph(f'{APP_NAME} Intelligence Report', st['title']))
    story.append(Paragraph(f"{APP_SUBTITLE} &middot; generated {datetime.now().strftime('%d %B %Y, %H:%M')}", st['sub']))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width='100%', color=colors.HexColor(ACCENT), thickness=1.6, spaceAfter=8))

    # 1. Summary
    story.append(Paragraph('1. Summary', st['h1']))
    kpis = [('Warning-signal index', f"{analysis['risk_score']}/100"), ('Band', analysis['risk_level']),
            ('Active dimensions', f"{int((theme_df['Evidence Frequency'] > 0).sum())}/{len(theme_df)}"),
            ('Words analysed', f"{len(analysis.get('text', '').split()):,}")]
    kt = Table([[[Paragraph(l.upper(), st['kpil']), Paragraph(v, st['kpiv'])] for l, v in kpis]],
               colWidths=[full / 4] * 4)
    kt.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor(RULE)),
                            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor(RULE)),
                            ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
                            ('LEFTPADDING', (0, 0), (-1, -1), 8)]))
    story.append(kt)
    story.append(Spacer(1, 6))
    story.append(Paragraph(escape(_summary_sentence(analysis, theme_df, risk_df)), st['body']))
    story.append(Spacer(1, 3))
    story.append(Paragraph(escape(_provenance(analysis)), st['small']))

    # 2. Dimensions
    story.append(Paragraph('2. Ecosystem dimension profile', st['h1']))
    max_freq = max(int(theme_df['Evidence Frequency'].max()), 1) if not theme_df.empty else 1
    rows = [['Dimension', 'Matches', 'Share', 'Relative strength']]
    for _, r in theme_df.iterrows():
        rows.append([r['Dimension'], r['Evidence Frequency'], _pct(r['Relative Weight']),
                     _bar(r['Evidence Frequency'] / max_freq)])
    story.append(_booktabs(rows, [7.4 * cm, 1.9 * cm, 1.9 * cm, full - 11.2 * cm], st, num_cols=(1, 2)))

    # 3. Risk indicators
    story.append(Paragraph('3. Warning-indicator profile', st['h1']))
    rows = [['Indicator', 'Matches', f'Contribution (of {RISK_CAP})', 'Per 1,000 words', 'Signal', 'Priority']]
    for _, r in risk_df.iterrows():
        rows.append([r['Warning Indicator'], r['Matches'], r['Index Contribution'],
                     f"{r['Per 1,000 Words']:.2f}", r['Interpretation'], action_priority(int(r['Matches']))])
    story.append(_booktabs(rows, [5.4 * cm, 1.5 * cm, 2.3 * cm, 2.2 * cm, 2.3 * cm, full - 13.7 * cm], st,
                           num_cols=(1, 2, 3)))
    story.append(Spacer(1, 3))
    story.append(Paragraph(f'Index = floor(100 &times; &Sigma; min(matches, {RISK_CAP}) / ({RISK_CAP} &times; '
                           f'{len(risk_df)})). Bands: High &ge; 70, Moderate &ge; 35, otherwise Low. The per-1,000-word '
                           'density is uncapped and comparable across corpora of different size. Bands, signal and priority are '
                           'descriptive heuristics (priority on raw matches: Critical &ge; 10, High &ge; 3, Monitor &ge; 1) and are not calibrated.', st['small']))

    # 4. Framework
    story.append(Paragraph(f'4. {escape(FRAMEWORK_NAME)}', st['h1']))
    story.append(Paragraph('Ecosystem risk is represented as <i>S = f(D, M, V, O, F, I, P)</i>, where D is digital '
                           'recruitment exposure, M manipulation intensity, V victim vulnerability, O operational '
                           'sophistication, F financial-chain complexity, I institutional coordination gap and P '
                           'preventive capacity. The prevention index <i>PI = &Sigma; w<sub>i</sub>C<sub>i</sub> '
                           '&minus; &Sigma; &lambda;<sub>j</sub>R<sub>j</sub></i> balances stakeholder capabilities '
                           'against residual risk indicators.', st['body']))
    story.append(Spacer(1, 3))
    story.append(Paragraph('Prevention layers: ' + '; '.join(f'({i}) {x}' for i, x in enumerate(PREVENTION_LAYERS, 1))
                           + '.', st['body']))

    # 5. Evidence
    story.append(Paragraph('5. Qualitative evidence by dimension', st['h1']))
    for theme, evs in analysis.get('evidence', {}).items():
        if not evs:
            continue
        block = [Paragraph(escape(theme), st['h2'])]
        block += [Paragraph('&bull;&nbsp; ' + escape(_short(e, 430)), st['cell']) for e in evs[:3]]
        story.append(KeepTogether(block))

    # 6. Coding snapshot
    story.append(PageBreak())
    story.append(Paragraph('6. Coding evidence (first 24 codes)', st['h1']))
    rows = [['Dimension', 'Code', 'Evidence extract']]
    if not codes_df.empty:
        for _, r in codes_df.head(24).iterrows():
            rows.append([r['Dimension'], r['Indicative Code'], _short(r['Evidence Extract'], 210)])
    story.append(_booktabs(rows, [4.6 * cm, 2.4 * cm, full - 7.0 * cm], st))

    # 7. Stakeholders
    story.append(Paragraph('7. Stakeholder prevention matrix', st['h1']))
    rows = [['Stakeholder', 'Prevention role']] + [[s, a] for s, a in STAKEHOLDERS.items()]
    story.append(_booktabs(rows, [3.8 * cm, full - 3.8 * cm], st))

    # 8. Recommendations and terms
    story.append(Paragraph('8. Recommendations', st['h1']))
    for i, rec in enumerate(RECOMMENDATIONS, 1):
        story.append(Paragraph(f'{i}. {escape(rec)}', st['body']))
    story.append(Spacer(1, 6))
    story.append(Paragraph('<b>Most frequent terms:</b> ' + ', '.join(
        f'{escape(t)} ({c})' for t, c in analysis.get('top_terms', [])[:30]), st['small']))

    doc.build(story, onFirstPage=_page, onLaterPages=_page)
    return buf.getvalue()
