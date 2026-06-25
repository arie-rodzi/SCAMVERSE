import streamlit as st
from modules.ui import load_css, sidebar, hero
from modules.engine import theme_df, risk_df, codes_df
from modules.reporting import html_report, pdf_report

st.set_page_config(page_title='Premium Report | SCAMVERSE', page_icon='📑', layout='wide')
load_css(); sidebar(); hero('Premium Report', 'Generate formal HTML and PDF intelligence reports')

if 'analysis' not in st.session_state:
    st.warning('Please analyse transcripts first in Upload & Analyse.')
    st.stop()
a = st.session_state.analysis
tdf = theme_df(a); rdf = risk_df(a); cdf = codes_df(a)
html = html_report(tdf, rdf, cdf, a)
pdf = pdf_report(tdf, rdf, cdf, a)

col1,col2 = st.columns(2)
with col1:
    st.download_button('⬇️ Download Premium PDF Report', data=pdf, file_name='SCAMVERSE_Intelligence_Report.pdf', mime='application/pdf')
with col2:
    st.download_button('⬇️ Download HTML Report', data=html, file_name='SCAMVERSE_Intelligence_Report.html', mime='text/html')

st.markdown('### HTML Report Preview')
st.markdown(html, unsafe_allow_html=True)
