import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from config import APP_NAME, APP_SUBTITLE, FRAMEWORK_NAME
from modules.engine import STAKEHOLDERS

def html_report(theme_df, risk_df, codes_df, analysis):
    dims = ''.join([f"<span class='badge'>{r.Dimension}: {r['Evidence Frequency']}</span>" for _,r in theme_df.iterrows()])
    risk_rows = ''.join([f"<tr><td>{r['Risk Indicator']}</td><td>{r['Detected Evidence']}</td><td>{r['Interpretation']}</td></tr>" for _,r in risk_df.iterrows()])
    codes_rows = ''.join([f"<tr><td>{r['Dimension']}</td><td>{r['Indicative Code']}</td><td>{r['Evidence Extract']}</td></tr>" for _,r in codes_df.head(25).iterrows()])
    ev_html = ''
    for theme, evs in analysis['evidence'].items():
        if evs:
            ev_html += f"<h3>{theme}</h3><ul>" + ''.join([f"<li>{e}</li>" for e in evs[:3]]) + '</ul>'
    terms = ', '.join([f"{t} ({c})" for t,c in analysis['top_terms'][:18]])
    stakeholder = ''.join([f"<tr><td>{s}</td><td>{a}</td></tr>" for s,a in STAKEHOLDERS.items()])
    return f"""
    <div class='report-card'>
      <h1>{APP_NAME} Intelligence Report</h1>
      <p><b>{APP_SUBTITLE}</b></p>
      <p>Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')}</p>
      <h2>Executive Summary</h2>
      <p>This premium report converts qualitative interview evidence into a structured ecosystem analysis for online investment scam prevention. The current evidence indicates a <b>{analysis['risk_level']}</b> risk profile with a score of <b>{analysis['risk_score']}/100</b>.</p>
      <p>{dims}</p>
      <h2>Detected Risk Indicators</h2>
      <table style='width:100%; border-collapse:collapse;'><tr style='background:#1d4ed8;color:white;'><th style='padding:10px;'>Indicator</th><th>Evidence</th><th>Interpretation</th></tr>{risk_rows}</table>
      <h2>Qualitative Coding Evidence</h2>
      <table style='width:100%; border-collapse:collapse;'><tr style='background:#7c3aed;color:white;'><th style='padding:10px;'>Dimension</th><th>Code</th><th>Evidence Extract</th></tr>{codes_rows}</table>
      <h2>Evidence Extracts by Dimension</h2>{ev_html}
      <h2>{FRAMEWORK_NAME}</h2>
      <p>The framework integrates digital recruitment, manipulation mechanisms, victim vulnerability, operational architecture, financial laundering chain, institutional response and prevention intelligence.</p>
      <h2>Stakeholder Prevention Matrix</h2>
      <table style='width:100%; border-collapse:collapse;'><tr style='background:#0f172a;color:white;'><th style='padding:10px;'>Stakeholder</th><th>Prevention Role</th></tr>{stakeholder}</table>
      <h2>Analytical Terms</h2><p>{terms}</p>
      <h2>Recommended Actions</h2><ol><li>Prioritise early warnings involving guaranteed returns, Telegram recruitment and mule-account transfers.</li><li>Strengthen data-sharing between PDRM/CCID, BNM, banks, SSM, SKMM, NSRC and platform operators.</li><li>Develop targeted public awareness campaigns for professionals, retirees, new workers and social-media-active groups.</li><li>Use this system output as the empirical engine for the Q1 conceptual paper and the SoftwareX article.</li></ol>
    </div>
    """

def _table(data, widths, header='#1D4ED8'):
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor(header)),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#CBD5E1')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#F8FAFC'),colors.white]),('FONTSIZE',(0,0),(-1,-1),7.2),('VALIGN',(0,0),(-1,-1),'TOP')]))
    return t

def pdf_report(theme_df, risk_df, codes_df, analysis):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=1.45*cm, leftMargin=1.45*cm, topMargin=1.4*cm, bottomMargin=1.4*cm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='TitleX', parent=styles['Title'], textColor=colors.HexColor('#0F172A'), fontSize=24, leading=28))
    styles.add(ParagraphStyle(name='H2X', parent=styles['Heading2'], textColor=colors.HexColor('#1D4ED8'), fontSize=14, leading=17))
    styles.add(ParagraphStyle(name='BodyX', parent=styles['BodyText'], fontSize=9.5, leading=13))
    styles.add(ParagraphStyle(name='SmallX', parent=styles['BodyText'], fontSize=7.4, leading=9.5))
    story=[]
    story.append(Paragraph(f'{APP_NAME} Intelligence Report', styles['TitleX']))
    story.append(Paragraph(APP_SUBTITLE, styles['BodyX']))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')}", styles['SmallX']))
    story.append(Spacer(1,10))
    story.append(Paragraph('1. Executive Summary', styles['H2X']))
    story.append(Paragraph(f"The system analysed the uploaded transcript corpus and detected a <b>{analysis['risk_level']}</b> risk profile with a score of <b>{analysis['risk_score']}/100</b>. The results are organised around the Integrated Multi-Stakeholder Prevention Framework.", styles['BodyX']))
    story.append(Paragraph('2. Ecosystem Dimensions', styles['H2X']))
    story.append(_table([['Dimension','Evidence Frequency','Relative Weight']] + theme_df.values.tolist(), [8*cm,4*cm,4*cm]))
    story.append(Spacer(1,8))
    story.append(Paragraph('3. Risk Indicators', styles['H2X']))
    story.append(_table([['Risk Indicator','Evidence','Interpretation']] + risk_df.values.tolist(), [7*cm,3*cm,5*cm], '#7C3AED'))
    story.append(PageBreak())
    story.append(Paragraph('4. Qualitative Coding Evidence', styles['H2X']))
    code_data = [['Dimension','Code','Evidence Extract']] + codes_df.head(35).values.tolist()
    story.append(_table(code_data, [4.8*cm,3.5*cm,8.2*cm], '#0F766E'))
    story.append(Paragraph('5. Evidence Extracts by Dimension', styles['H2X']))
    for theme, evs in analysis['evidence'].items():
        story.append(Paragraph(f'<b>{theme}</b>', styles['BodyX']))
        for e in evs[:3]:
            story.append(Paragraph('• '+e.replace('&','&amp;'), styles['SmallX']))
        story.append(Spacer(1,4))
    story.append(Paragraph('6. Stakeholder Prevention Matrix', styles['H2X']))
    st_data = [['Stakeholder','Prevention Role']] + [[s,a] for s,a in STAKEHOLDERS.items()]
    story.append(_table(st_data, [4.5*cm,11.5*cm], '#0F172A'))
    story.append(Paragraph('7. Analytical Terms', styles['H2X']))
    story.append(Paragraph(', '.join([f'{t} ({c})' for t,c in analysis['top_terms'][:25]]), styles['BodyX']))
    doc.build(story)
    buf.seek(0)
    return buf.getvalue()
