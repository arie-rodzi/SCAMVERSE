import re
import io
from datetime import datetime
from collections import Counter, defaultdict

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

st.set_page_config(page_title="SCAMVERSE", page_icon="🛡️", layout="wide")

APP_NAME = "SCAMVERSE"
APP_SUBTITLE = "Online Investment Scam Ecosystem Intelligence Platform"

THEME_KEYWORDS = {
    "Digital Recruitment": ["telegram", "facebook", "whatsapp", "wechat", "social media", "group", "link", "ads"],
    "Psychological Manipulation": ["guarantee", "profit", "return", "dividend", "testimonial", "receipt", "urgent", "bonus"],
    "Victim Vulnerability": ["victim", "retiree", "teacher", "student", "professional", "nurse", "lecturer", "greed"],
    "Financial Transaction Chain": ["bank", "account", "mule", "atm", "transfer", "tac", "crypto", "wallet", "money"],
    "Institutional Response": ["police", "pdrm", "bnm", "bank negara", "ssm", "skmm", "sc", "nsrc", "bukit aman", "ipk", "ipd"],
    "Evidence and Investigation": ["evidence", "receipt", "report", "statement", "investigation", "section 420", "court", "arrest"],
    "Prevention and Awareness": ["awareness", "campaign", "education", "prevent", "hotline", "mule check", "alert", "seminar"],
}

RISK_RULES = {
    "Unrealistic high return": ["high return", "30%", "300%", "profit", "return", "dividend", "bonus"],
    "Guaranteed profit": ["guarantee", "guaranteed", "confirm", "no risk", "risk-free"],
    "Telegram / social media recruitment": ["telegram", "facebook", "whatsapp", "wechat", "social media"],
    "Mule account / layered transfer": ["mule", "account", "atm", "transfer", "bank", "layer"],
    "Fake testimonial evidence": ["testimonial", "receipt", "screenshot", "proof", "dividend received"],
    "Unlicensed or unclear company": ["no license", "unlicensed", "ssm", "bank negara", "bnm", "not listed"],
    "Crypto or cross-border laundering": ["crypto", "cryptocurrency", "bitcoin", "overseas", "out of the country"],
    "Urgency pressure": ["urgent", "immediate", "short period", "limited", "act now"],
}

STAKEHOLDERS = {
    "PDRM / CCID": "Investigation, evidence gathering, arrest, prosecution support, public warnings.",
    "BNM": "Financial licensing, consumer alert list, transaction monitoring coordination.",
    "Banks": "Real-time suspicious transaction monitoring, mule-account detection, freezing mechanism.",
    "SSM": "Company registration verification, fraud-risk flagging, entity legitimacy checks.",
    "SKMM / Telcos": "SIM-card governance, platform cooperation, scam-number monitoring.",
    "NSRC": "Rapid reporting, transaction blocking coordination, victim response support.",
    "Social Media Platforms": "Scam advertisement takedown, group monitoring, fake testimonial detection.",
    "Public / Victims": "Due diligence, financial literacy, scam reporting, account protection.",
}

def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
    html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
    .stApp {
        background: radial-gradient(circle at top left, #183b8f 0%, #07111f 28%, #020617 70%);
        color: #eef5ff;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #061b3a 0%, #07111f 52%, #020617 100%) !important;
        border-right: 1px solid rgba(125, 211, 252, .35);
    }
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
        opacity: 1 !important;
        font-weight: 650 !important;
    }
    .hero {
        padding: 34px;
        border-radius: 28px;
        background: linear-gradient(135deg, rgba(14,165,233,.95), rgba(99,102,241,.84), rgba(217,70,239,.62));
        box-shadow: 0 20px 60px rgba(0,0,0,.38);
        border: 1px solid rgba(255,255,255,.25);
        margin-bottom: 22px;
    }
    .hero h1 {font-size: 58px; margin: 0; font-weight: 950; color: white;}
    .hero p {font-size: 19px; color: #f7fbff; font-weight: 650;}
    .kpi {
        padding: 20px;
        border-radius: 22px;
        background: linear-gradient(145deg, rgba(15,23,42,.92), rgba(30,64,175,.50));
        border: 1px solid rgba(125,211,252,.35);
        min-height: 126px;
    }
    .kpi .label {color:#cbd5e1; font-size: 13px; font-weight: 700; text-transform: uppercase;}
    .kpi .value {font-size: 34px; font-weight: 950; color:#ffffff;}
    .kpi .note {font-size: 12px; color:#bfdbfe;}
    .glass {
        background: rgba(15, 23, 42, .78);
        border: 1px solid rgba(148, 163, 184, .28);
        border-radius: 22px;
        padding: 22px;
    }
    .report-card {
        background: white;
        color: #0f172a;
        border-radius: 26px;
        padding: 30px;
        box-shadow: 0 18px 50px rgba(0,0,0,.25);
        border-top: 10px solid #2563eb;
    }
    .report-card h1 {font-size: 38px; color:#0f172a;}
    .report-card h2 {color:#1d4ed8; border-bottom: 2px solid #dbeafe; padding-bottom: 6px;}
    .badge {display:inline-block; padding: 6px 12px; border-radius:999px; background:#dbeafe; color:#1e40af; font-weight:800; margin: 4px;}
    div[data-testid="stDownloadButton"] button, div[data-testid="stButton"] button {
        background: linear-gradient(135deg, #2563eb, #9333ea) !important;
        color: white !important;
        border: 0 !important;
        border-radius: 14px !important;
        font-weight: 800 !important;
    }
    </style>
    """, unsafe_allow_html=True)

def clean_text(text):
    return re.sub(r"\s+", " ", text or "").strip()

def extract_text_from_upload(file):
    if file is None:
        return ""
    name = file.name.lower()
    raw = file.read()
    if name.endswith(".txt"):
        return raw.decode("utf-8", errors="ignore")
    if name.endswith(".docx"):
        from docx import Document
        doc = Document(io.BytesIO(raw))
        return "\n".join([p.text for p in doc.paragraphs])
    return raw.decode("utf-8", errors="ignore")

def analyze_text(text):
    lower = text.lower()
    theme_counts = {}
    evidence = defaultdict(list)
    sentences = re.split(r"(?<=[.!?])\s+", clean_text(text))

    for theme, keys in THEME_KEYWORDS.items():
        count = sum(lower.count(key) for key in keys)
        theme_counts[theme] = count
        for sent in sentences:
            if any(k in sent.lower() for k in keys):
                evidence[theme].append(sent[:280])
                if len(evidence[theme]) >= 3:
                    break

    risk_hits = {rule: sum(lower.count(k) for k in keys) for rule, keys in RISK_RULES.items()}
    raw_score = sum(min(v, 4) for v in risk_hits.values())
    risk_score = min(100, int(raw_score / (len(RISK_RULES) * 4) * 100))
    risk_level = "High" if risk_score >= 70 else "Moderate" if risk_score >= 35 else "Low"

    words = re.findall(r"[A-Za-z]{4,}", lower)
    stop = set("this that with from they them were have been will into when what where which there their about because under above after before also only most more some such case cases scam scams scammer scammers victim victims police investment investments".split())
    top_terms = Counter([w for w in words if w not in stop]).most_common(20)
    return theme_counts, evidence, risk_hits, risk_score, risk_level, top_terms

def make_theme_df(theme_counts):
    total = sum(theme_counts.values()) or 1
    return pd.DataFrame({
        "Dimension": list(theme_counts.keys()),
        "Evidence Frequency": list(theme_counts.values()),
        "Relative Weight": [round(v / total, 3) for v in theme_counts.values()],
    }).sort_values("Evidence Frequency", ascending=False)

def make_risk_df(risk_hits):
    return pd.DataFrame({
        "Risk Indicator": list(risk_hits.keys()),
        "Detected Evidence": list(risk_hits.values()),
        "Interpretation": ["Strong signal" if v >= 3 else "Present" if v > 0 else "Not detected" for v in risk_hits.values()]
    })

def ecosystem_graph():
    nodes = ["Victim", "Scammer", "Telegram/Facebook", "Mule Account", "Bank", "BNM", "SSM", "SKMM/Telco", "NSRC", "PDRM/CCID", "Public Awareness"]
    edges = [
        ("Scammer", "Telegram/Facebook"), ("Telegram/Facebook", "Victim"), ("Scammer", "Victim"),
        ("Victim", "Mule Account"), ("Mule Account", "Bank"), ("Bank", "BNM"),
        ("Victim", "PDRM/CCID"), ("PDRM/CCID", "NSRC"), ("PDRM/CCID", "SSM"),
        ("PDRM/CCID", "BNM"), ("NSRC", "Bank"), ("Public Awareness", "Victim")
    ]
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    pos = nx.spring_layout(G, seed=8, k=0.8)

    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    node_x, node_y, labels = [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        labels.append(node)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines", line=dict(width=1.8, color="rgba(148,163,184,.65)"), hoverinfo="none"))
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y, mode="markers+text", text=labels, textposition="top center",
        marker=dict(size=28, color=list(range(len(labels))), colorscale="Turbo", line=dict(width=2, color="white")),
        textfont=dict(color="white", size=12), hoverinfo="text"
    ))
    fig.update_layout(height=620, margin=dict(l=10,r=10,t=20,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(visible=False), yaxis=dict(visible=False), showlegend=False)
    return fig

def generate_html_report(theme_df, risk_df, evidence, risk_score, risk_level, top_terms):
    dims_html = "".join([f"<span class='badge'>{row.Dimension}: {row['Evidence Frequency']}</span>" for _, row in theme_df.iterrows()])
    risk_rows = "".join([f"<tr><td>{r['Risk Indicator']}</td><td>{r['Detected Evidence']}</td><td>{r['Interpretation']}</td></tr>" for _, r in risk_df.iterrows()])
    evidence_html = ""
    for theme, evs in evidence.items():
        if evs:
            evidence_html += f"<h3>{theme}</h3><ul>" + "".join([f"<li>{e}</li>" for e in evs]) + "</ul>"
    terms = ", ".join([f"{t} ({c})" for t, c in top_terms[:12]])

    return f"""
    <div class='report-card'>
      <h1>SCAMVERSE Intelligence Report</h1>
      <p><b>{APP_SUBTITLE}</b></p>
      <p>Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')}</p>

      <h2>Executive Summary</h2>
      <p>This report analyses the uploaded transcript using the SCAMVERSE ecosystem model. The detected scam-risk level is <b>{risk_level}</b> with a risk score of <b>{risk_score}/100</b>.</p>
      <p>{dims_html}</p>

      <h2>Detected Risk Indicators</h2>
      <table style='width:100%; border-collapse:collapse;'>
        <tr style='background:#1d4ed8;color:white;'>
          <th style='padding:10px;'>Indicator</th><th>Evidence</th><th>Interpretation</th>
        </tr>
        {risk_rows}
      </table>

      <h2>Qualitative Evidence Extracts</h2>
      {evidence_html}

      <h2>Integrated Multi-Stakeholder Prevention Framework</h2>
      <p>The findings support a layered prevention logic: digital-platform monitoring, victim vulnerability reduction, financial-chain disruption, institutional coordination, and public-warning dissemination.</p>

      <h2>Top Analytical Terms</h2>
      <p>{terms}</p>

      <h2>Recommended Actions</h2>
      <ol>
        <li>Prioritise early warning indicators involving guaranteed returns, Telegram recruitment and mule-account transfers.</li>
        <li>Strengthen data-sharing between PDRM/CCID, BNM, banks, SSM, SKMM, NSRC and platform operators.</li>
        <li>Develop targeted public awareness campaigns for professionals, retirees, new workers and social-media-active groups.</li>
        <li>Use this analysis as evidence for the Q1 conceptual paper and SoftwareX article.</li>
      </ol>
    </div>
    """

def generate_pdf_report(theme_df, risk_df, evidence, risk_score, risk_level, top_terms):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleBlue", parent=styles["Title"], textColor=colors.HexColor("#0F172A"), fontSize=24, leading=28))
    styles.add(ParagraphStyle(name="HeaderBlue", parent=styles["Heading2"], textColor=colors.HexColor("#1D4ED8"), fontSize=15))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8.5, leading=11))
    styles.add(ParagraphStyle(name="Body", parent=styles["BodyText"], fontSize=10, leading=14))

    story = []
    story.append(Paragraph("SCAMVERSE Intelligence Report", styles["TitleBlue"]))
    story.append(Paragraph(APP_SUBTITLE, styles["Body"]))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%d %B %Y, %I:%M %p')}", styles["Small"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("1. Executive Summary", styles["HeaderBlue"]))
    story.append(Paragraph(f"The detected scam-risk level is <b>{risk_level}</b> with a risk score of <b>{risk_score}/100</b>.", styles["Body"]))

    story.append(Paragraph("2. Ecosystem Dimensions", styles["HeaderBlue"]))
    data = [["Dimension", "Evidence Frequency", "Relative Weight"]] + theme_df.values.tolist()
    table = Table(data, colWidths=[8*cm, 4*cm, 4*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1D4ED8")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), .35, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#F8FAFC"), colors.white]),
        ("FONTSIZE", (0,0), (-1,-1), 8),
    ]))
    story.append(table)

    story.append(Paragraph("3. Risk Indicators", styles["HeaderBlue"]))
    rdata = [["Risk Indicator", "Evidence", "Interpretation"]] + risk_df.values.tolist()
    rtable = Table(rdata, colWidths=[7*cm, 3*cm, 5*cm])
    rtable.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#7C3AED")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), .35, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#F8FAFC"), colors.white]),
        ("FONTSIZE", (0,0), (-1,-1), 8),
    ]))
    story.append(rtable)

    story.append(Paragraph("4. Qualitative Evidence Extracts", styles["HeaderBlue"]))
    for theme, evs in evidence.items():
        if evs:
            story.append(Paragraph(f"<b>{theme}</b>", styles["Body"]))
            for e in evs[:2]:
                story.append(Paragraph("- " + e.replace("&", "&amp;"), styles["Small"]))
            story.append(Spacer(1, 4))

    story.append(Paragraph("5. Multi-Stakeholder Prevention Recommendations", styles["HeaderBlue"]))
    for s, action in STAKEHOLDERS.items():
        story.append(Paragraph(f"<b>{s}:</b> {action}", styles["Small"]))

    story.append(Paragraph("6. Analytical Terms", styles["HeaderBlue"]))
    story.append(Paragraph(", ".join([f"{t} ({c})" for t, c in top_terms[:20]]), styles["Body"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def kpi(label, value, note):
    st.markdown(f"<div class='kpi'><div class='label'>{label}</div><div class='value'>{value}</div><div class='note'>{note}</div></div>", unsafe_allow_html=True)

inject_css()

with st.sidebar:
    st.markdown("# 🛡️ SCAMVERSE")
    st.markdown("**Premium scam ecosystem analytics**")
    page = st.radio("Navigation", ["Dashboard", "Upload & Analyse", "Ecosystem Map", "Premium Report", "Framework"])
    st.markdown("---")
    st.markdown("**Version:** 2.0 PDF Report Edition")
    st.markdown("**Output:** HTML + PDF report")

st.markdown(f"<div class='hero'><h1>{APP_NAME}</h1><p>{APP_SUBTITLE}</p></div>", unsafe_allow_html=True)

if "analysis" not in st.session_state:
    sample = """
    Investment scam cases often involve Telegram, Facebook and WhatsApp recruitment.
    Scammers promise guaranteed profit, high return and fast dividends.
    Victims are asked to transfer money to bank accounts or mule accounts.
    Police, BNM, SSM, SKMM, NSRC and banks need to coordinate prevention.
    Awareness campaigns and scam alerts are important.
    """
    tc, ev, rh, rs, rl, tt = analyze_text(sample)
    st.session_state.analysis = (sample, tc, ev, rh, rs, rl, tt)

text, theme_counts, evidence, risk_hits, risk_score, risk_level, top_terms = st.session_state.analysis
theme_df = make_theme_df(theme_counts)
risk_df = make_risk_df(risk_hits)

if page == "Dashboard":
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Risk Score", f"{risk_score}/100", f"{risk_level} risk level")
    with c2: kpi("Dimensions", len(theme_df), "ecosystem dimensions")
    with c3: kpi("Indicators", len(risk_df[risk_df["Detected Evidence"] > 0]), "active warning signals")
    with c4: kpi("Words Analysed", f"{len(text.split()):,}", "uploaded transcript corpus")

    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("### Ecosystem Dimension Strength")
        fig = px.bar(theme_df, x="Evidence Frequency", y="Dimension", orientation="h", text="Evidence Frequency", color="Relative Weight", color_continuous_scale="Turbo")
        fig.update_layout(height=430, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown("### Risk Indicator Radar")
        radar = go.Figure(data=go.Scatterpolar(r=risk_df["Detected Evidence"].clip(upper=6), theta=risk_df["Risk Indicator"], fill="toself"))
        radar.update_layout(height=430, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", polar=dict(bgcolor="rgba(15,23,42,.4)"))
        st.plotly_chart(radar, use_container_width=True)

elif page == "Upload & Analyse":
    st.markdown("### Upload Transcript")
    uploaded = st.file_uploader("Upload TXT or DOCX transcript", type=["txt", "docx"])
    pasted = st.text_area("Or paste transcript text here", height=260)

    if st.button("Analyse Transcript"):
        new_text = extract_text_from_upload(uploaded) if uploaded else pasted
        if not clean_text(new_text):
            st.warning("Please upload or paste transcript text first.")
        else:
            tc, ev, rh, rs, rl, tt = analyze_text(new_text)
            st.session_state.analysis = (new_text, tc, ev, rh, rs, rl, tt)
            st.success("Analysis completed. Open Dashboard or Premium Report.")

    st.markdown("### Current Theme Table")
    st.dataframe(theme_df, use_container_width=True)

elif page == "Ecosystem Map":
    st.markdown("### Online Investment Scam Ecosystem Network")
    st.plotly_chart(ecosystem_graph(), use_container_width=True)

    st.markdown("### Stakeholder Action Matrix")
    sdf = pd.DataFrame({"Stakeholder": list(STAKEHOLDERS.keys()), "Prevention Role": list(STAKEHOLDERS.values())})
    st.dataframe(sdf, use_container_width=True, hide_index=True)

elif page == "Premium Report":
    st.markdown("### HTML Report Preview")
    html = generate_html_report(theme_df, risk_df, evidence, risk_score, risk_level, top_terms)
    st.markdown(html, unsafe_allow_html=True)

    pdf = generate_pdf_report(theme_df, risk_df, evidence, risk_score, risk_level, top_terms)
    st.download_button("⬇️ Download Premium PDF Report", data=pdf, file_name="SCAMVERSE_Intelligence_Report.pdf", mime="application/pdf")
    st.download_button("⬇️ Download HTML Report", data=html, file_name="SCAMVERSE_Intelligence_Report.html", mime="text/html")

elif page == "Framework":
    st.markdown("### Integrated Multi-Stakeholder Prevention Framework")
    st.markdown("""
    <div class='glass'>
    <h2 style='color:white;'>SCAMVERSE Framework Logic</h2>
    <p style='color:#dbeafe;font-size:16px;'>The system transforms qualitative interview evidence into six integrated layers: digital recruitment, psychological manipulation, victim vulnerability, financial transaction chain, institutional response, and prevention intelligence.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Mathematical Representation")
    st.latex(r"S = f(D, M, V, F, I, P)")
    st.markdown("Where S is ecosystem scam risk, D is digital recruitment, M is manipulation intensity, V is victim vulnerability, F is financial-chain complexity, I is institutional coordination gap, and P is preventive capacity.")

    st.latex(r"PI = \sum_{i=1}^{n} w_i C_i - \sum_{j=1}^{m} \lambda_j R_j")
    st.markdown("PI represents a prevention index balancing stakeholder capabilities and residual risk indicators.")
