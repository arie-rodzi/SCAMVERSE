from __future__ import annotations

import io
from pathlib import Path

import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.scam_engine import (
    analyze_texts,
    build_interaction_edges,
    read_text_from_file,
    stakeholder_matrix,
)

APP_DIR = Path(__file__).parent
SAMPLE_DIR = APP_DIR / "data" / "sample_transcripts"

st.set_page_config(
    page_title="ScamShield Analytics",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
.stApp {
    background: radial-gradient(circle at top left, #1e3a8a 0, #0f172a 34%, #020617 100%);
    color: #f8fafc;
}
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
.hero {
    padding: 28px 32px;
    border-radius: 28px;
    background: linear-gradient(135deg, rgba(59,130,246,.35), rgba(168,85,247,.22), rgba(20,184,166,.18));
    border: 1px solid rgba(255,255,255,.16);
    box-shadow: 0 24px 80px rgba(0,0,0,.25);
    margin-bottom: 18px;
}
.hero h1 {font-size: 44px; font-weight: 800; margin: 0; letter-spacing: -1.2px;}
.hero p {font-size: 16px; color: #dbeafe; max-width: 950px;}
.metric-card {
    padding: 20px;
    border-radius: 24px;
    background: rgba(15,23,42,.72);
    border: 1px solid rgba(255,255,255,.12);
    box-shadow: 0 18px 50px rgba(0,0,0,.18);
}
.metric-label {font-size: 13px; color: #bae6fd; text-transform: uppercase; letter-spacing: .08em;}
.metric-value {font-size: 34px; font-weight: 800; color: #ffffff;}
.gradient-title {
    font-weight: 800;
    background: linear-gradient(90deg, #93c5fd, #f0abfc, #5eead4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.note-box {
    padding: 16px 18px;
    border-radius: 18px;
    background: rgba(255,255,255,.08);
    border-left: 5px solid #38bdf8;
    color: #e0f2fe;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #111827);
}
.stDataFrame, .stTable {background: rgba(255,255,255,.95); border-radius: 16px;}
hr {border-color: rgba(255,255,255,.16);}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="hero">
  <h1>🛡️ ScamShield Analytics</h1>
  <p><b>Premium decision-support dashboard</b> for deconstructing online investment scam ecosystems from interview transcripts and translating qualitative evidence into an integrated multi-stakeholder prevention framework.</p>
</div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### 🧭 Navigation")
    page = st.radio(
        "Select module",
        [
            "1. Data Upload",
            "2. Executive Dashboard",
            "3. Qualitative Coding",
            "4. Scam Ecosystem Network",
            "5. Risk & Warning Signals",
            "6. Stakeholder Prevention Framework",
            "7. Export Results",
        ],
    )
    st.markdown("---")
    use_sample = st.toggle("Use included IV1–IV7 sample transcripts", value=True)
    st.caption("Upload your own DOCX/TXT files or use the bundled interview transcripts.")

uploaded_files = st.file_uploader(
    "Upload interview transcripts (.docx or .txt)",
    type=["docx", "txt"],
    accept_multiple_files=True,
)

@st.cache_data(show_spinner=False)
def load_sample_texts() -> dict[str, str]:
    texts = {}
    for path in sorted(SAMPLE_DIR.glob("*.docx")):
        with open(path, "rb") as f:
            texts[path.name] = read_text_from_file(f)
    return texts

texts: dict[str, str] = {}
if use_sample:
    texts.update(load_sample_texts())
if uploaded_files:
    for f in uploaded_files:
        try:
            texts[f.name] = read_text_from_file(f)
        except Exception as e:
            st.error(f"Could not read {f.name}: {e}")

if not texts:
    st.info("Upload transcripts or enable sample transcripts in the sidebar.")
    st.stop()

results = analyze_texts(texts)
dim_df = results["dimensions"]
summary_df = results["dimension_summary"]
warn_df = results["warnings"]
risk_df = results["risk"]
quotes_df = results["quotes"]

n_docs = len(texts)
total_words = sum(len(t.split()) for t in texts.values())
total_evidence = int(dim_df["Evidence_Count"].sum())
top_dim = summary_df.iloc[0]["Dimension"] if not summary_df.empty else "-"

if page == "1. Data Upload":
    st.markdown("## <span class='gradient-title'>1. Data Upload</span>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    for col, label, value in [
        (c1, "Transcripts loaded", n_docs),
        (c2, "Approx. word count", f"{total_words:,}"),
        (c3, "Evidence signals", f"{total_evidence:,}"),
    ]:
        col.markdown(f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div></div>", unsafe_allow_html=True)
    st.markdown("### Loaded files")
    st.dataframe(pd.DataFrame({"Transcript": list(texts.keys()), "Words": [len(v.split()) for v in texts.values()]}), use_container_width=True)
    st.markdown("<div class='note-box'>This MVP uses a transparent dictionary-based coding engine. For the final SoftwareX version, this can be extended with validated human coding, LLM-assisted coding, or supervised text classification.</div>", unsafe_allow_html=True)

elif page == "2. Executive Dashboard":
    st.markdown("## <span class='gradient-title'>2. Executive Dashboard</span>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    metrics = [("Transcripts", n_docs), ("Words", f"{total_words:,}"), ("Dominant Dimension", top_dim), ("Total Signals", f"{total_evidence:,}")]
    for col, (label, value) in zip([c1, c2, c3, c4], metrics):
        col.markdown(f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value' style='font-size:24px'>{value}</div></div>", unsafe_allow_html=True)
    st.markdown("### Ecosystem dimension intensity")
    fig = px.bar(summary_df, x="Evidence_Count", y="Dimension", orientation="h", text="Evidence_Count", title="Evidence signals by framework dimension")
    fig.update_layout(height=480, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.03)", font_color="#e5e7eb")
    st.plotly_chart(fig, use_container_width=True)

elif page == "3. Qualitative Coding":
    st.markdown("## <span class='gradient-title'>3. Qualitative Coding</span>", unsafe_allow_html=True)
    st.markdown("### Dimension × transcript evidence matrix")
    pivot = dim_df.pivot_table(index="Transcript", columns="Dimension", values="Evidence_Count", fill_value=0)
    st.dataframe(pivot, use_container_width=True)
    fig = px.imshow(pivot, text_auto=True, aspect="auto", title="Qualitative coding heatmap")
    fig.update_layout(height=520, paper_bgcolor="rgba(0,0,0,0)", font_color="#e5e7eb")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("### Indicative qualitative evidence")
    st.dataframe(quotes_df, use_container_width=True)

elif page == "4. Scam Ecosystem Network":
    st.markdown("## <span class='gradient-title'>4. Scam Ecosystem Network</span>", unsafe_allow_html=True)
    edges = build_interaction_edges()
    G = nx.from_pandas_edgelist(edges, "Source", "Target", edge_attr="Weight", create_using=nx.DiGraph())
    pos = nx.spring_layout(G, seed=42, k=0.9)
    edge_x, edge_y = [], []
    for src, tgt in G.edges():
        x0, y0 = pos[src]
        x1, y1 = pos[tgt]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=1.5, color="rgba(147,197,253,.65)"), hoverinfo="none", mode="lines")
    node_x, node_y, node_text, node_size = [], [], [], []
    degrees = dict(G.degree())
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x); node_y.append(y); node_text.append(node); node_size.append(18 + degrees[node] * 4)
    node_trace = go.Scatter(
        x=node_x, y=node_y, mode="markers+text", text=node_text, textposition="top center",
        marker=dict(size=node_size, line=dict(width=1, color="#fff"), color=node_size, colorscale="Viridis", showscale=False),
        hovertext=node_text, hoverinfo="text",
    )
    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(title="Directed ecosystem map of online investment scam prevention", showlegend=False, height=700, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.02)", font_color="#e5e7eb", xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(edges, use_container_width=True)

elif page == "5. Risk & Warning Signals":
    st.markdown("## <span class='gradient-title'>5. Risk & Warning Signals</span>", unsafe_allow_html=True)
    st.markdown("### Transcript-level risk signal index")
    fig = px.bar(risk_df.sort_values("Risk_Index_0_100", ascending=False), x="Transcript", y="Risk_Index_0_100", text="Risk_Index_0_100", title="Risk index derived from warning-sign signals")
    fig.update_layout(height=470, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.03)", font_color="#e5e7eb")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("### Warning sign evidence")
    warn_pivot = warn_df.pivot_table(index="Transcript", columns="Warning_Sign", values="Signal_Count", fill_value=0)
    st.dataframe(warn_pivot, use_container_width=True)

elif page == "6. Stakeholder Prevention Framework":
    st.markdown("## <span class='gradient-title'>6. Stakeholder Prevention Framework</span>", unsafe_allow_html=True)
    st.markdown("<div class='note-box'><b>Integrated Multi-Stakeholder Prevention Framework (IMSPF):</b> prevention requires coordinated action across enforcement, financial institutions, regulators, telcos, digital platforms and public awareness.</div>", unsafe_allow_html=True)
    matrix = stakeholder_matrix()
    st.dataframe(matrix, use_container_width=True)
    fig = px.treemap(matrix, path=["Priority", "Stakeholder"], values=[3 if x == "High" else 2 for x in matrix["Priority"]], title="Prevention responsibility map")
    fig.update_layout(height=560, paper_bgcolor="rgba(0,0,0,0)", font_color="#e5e7eb")
    st.plotly_chart(fig, use_container_width=True)

elif page == "7. Export Results":
    st.markdown("## <span class='gradient-title'>7. Export Results</span>", unsafe_allow_html=True)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        summary_df.to_excel(writer, sheet_name="Dimension_Summary", index=False)
        dim_df.to_excel(writer, sheet_name="Dimension_By_Transcript", index=False)
        warn_df.to_excel(writer, sheet_name="Warning_Signs", index=False)
        risk_df.to_excel(writer, sheet_name="Risk_Index", index=False)
        quotes_df.to_excel(writer, sheet_name="Indicative_Evidence", index=False)
        stakeholder_matrix().to_excel(writer, sheet_name="Stakeholder_Matrix", index=False)
        build_interaction_edges().to_excel(writer, sheet_name="Network_Edges", index=False)
    st.download_button(
        "⬇️ Download analysis workbook",
        data=output.getvalue(),
        file_name="scamshield_analysis_results.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    st.markdown("### Tables available for manuscript writing")
    st.write("Dimension summary, evidence matrix, warning signs, risk index, stakeholder matrix and ecosystem network edges.")
