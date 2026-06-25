import streamlit as st
from modules.ui import load_css, sidebar, hero, kpi
from modules.engine import analyze_text, theme_df, risk_df, codes_df
from modules.graphs import dimension_bar, risk_radar, ecosystem_network, sunburst
from config import APP_NAME, APP_SUBTITLE, APP_VERSION

st.set_page_config(page_title=APP_NAME, page_icon='🛡️', layout='wide')
load_css(); sidebar(); hero()

if 'analysis' not in st.session_state:
    sample = '''Investment scam cases often involve Telegram, Facebook and WhatsApp recruitment. Scammers promise guaranteed profit, high return and fast dividends. Victims are asked to transfer money to bank accounts or mule accounts. Police, BNM, SSM, SKMM, NSRC and banks need to coordinate prevention. Awareness campaigns and scam alerts are important.'''
    st.session_state.analysis = analyze_text(sample)

analysis = st.session_state.analysis
tdf = theme_df(analysis); rdf = risk_df(analysis); cdf = codes_df(analysis)

st.markdown("### Executive Dashboard")
c1,c2,c3,c4 = st.columns(4)
with c1: kpi('Risk Score', f"{analysis['risk_score']}/100", analysis['risk_level']+' risk level')
with c2: kpi('Dimensions', len(tdf), 'ecosystem dimensions')
with c3: kpi('Active Indicators', len(rdf[rdf['Detected Evidence']>0]), 'warning signals')
with c4: kpi('Words Analysed', f"{len(analysis['text'].split()):,}", 'current corpus')

left,right = st.columns([1.15,1])
with left:
    st.markdown('### Ecosystem Dimension Strength')
    st.plotly_chart(dimension_bar(tdf), use_container_width=True)
with right:
    st.markdown('### Risk Indicator Radar')
    st.plotly_chart(risk_radar(rdf), use_container_width=True)

st.markdown('### Premium System Overview')
st.markdown(f"""
<div class='card'>
<h2 style='color:white;margin-top:0;'>🛡️ {APP_NAME} {APP_VERSION}</h2>
<p style='color:#dbeafe;font-size:16px;'>{APP_SUBTITLE} converts interview transcripts into coding evidence, scam-risk indicators, stakeholder matrices, ecosystem maps and premium HTML/PDF reports.</p>
<span class='success-pill'>Q1 Paper 1 Engine</span><span class='success-pill'>SoftwareX Ready</span><span class='success-pill'>HTML Report</span><span class='success-pill'>PDF Report</span>
</div>
""", unsafe_allow_html=True)
