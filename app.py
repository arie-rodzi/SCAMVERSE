import streamlit as st
from modules.ui import load_css, sidebar, hero, kpi
from modules.engine import analyze_text, theme_df, risk_df, codes_df, active_dimensions, active_indicators
from modules.graphs import dimension_bar, risk_radar, ecosystem_network, sunburst
from config import APP_NAME, APP_SUBTITLE, APP_VERSION

st.set_page_config(page_title=APP_NAME, page_icon='🛡️', layout='wide')
load_css(); sidebar(); hero()

SAMPLE = '''Investment scam cases often involve Telegram, Facebook and WhatsApp recruitment. Scammers promise guaranteed profit, high return and fast dividends. Victims are asked to transfer money to bank accounts or mule accounts. Police, BNM, SSM, SKMM, NSRC and banks need to coordinate prevention. Awareness campaigns and scam alerts are important.'''

if 'analysis' in st.session_state:
    analysis = st.session_state.analysis
else:
    # Display-only preview; nothing is written to the session, so reports are never
    # generated from the sample by accident.
    analysis = analyze_text(SAMPLE)
    st.info('No corpus analysed yet. The dashboard below shows a built-in sample sentence set. '
            'Use Upload and Analyse to analyse your own transcripts.')
tdf = theme_df(analysis); rdf = risk_df(analysis); cdf = codes_df(analysis)

st.markdown("### Executive Dashboard")
c1,c2,c3,c4 = st.columns(4)
with c1: kpi('Warning-signal index', f"{analysis['risk_score']}/100", analysis['risk_level'] + ' band')
with c2: kpi('Active Dimensions', f"{active_dimensions(analysis)}/{len(tdf)}", 'ecosystem dimensions')
with c3: kpi('Active Indicators', f"{active_indicators(analysis)}/{len(rdf)}", 'warning signals')
with c4: kpi('Words Analysed', f"{len(analysis['text'].split()):,}", 'current corpus')

left,right = st.columns([1.15,1])
with left:
    st.markdown('### Ecosystem Dimension Strength')
    st.plotly_chart(dimension_bar(tdf), use_container_width=True)
with right:
    st.markdown('### Risk Indicator Radar')
    st.plotly_chart(risk_radar(rdf), use_container_width=True)

st.markdown('### System Overview')
st.markdown(f"""
<div class='card'>
<h2>{APP_NAME} {APP_VERSION}</h2>
<p>{APP_SUBTITLE} converts interview transcripts into coding evidence, scam-risk indicators, stakeholder matrices, ecosystem maps and HTML/PDF reports.</p>
<span class='success-pill'>Thematic Coding</span><span class='success-pill'>Risk Index</span><span class='success-pill'>HTML Report</span><span class='success-pill'>PDF Report</span>
</div>
""", unsafe_allow_html=True)
