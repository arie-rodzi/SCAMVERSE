import streamlit as st
from modules.ui import load_css, sidebar, hero
from config import APP_NAME, APP_VERSION

st.set_page_config(page_title='About | SCAMVERSE', page_icon='⚙️', layout='wide')
load_css(); sidebar(); hero('About SCAMVERSE', 'System description for research and SoftwareX documentation')

st.markdown(f"""
<div class='card'>
<h2 style='color:white;'>{APP_NAME} {APP_VERSION}</h2>
<p style='color:#dbeafe;'>SCAMVERSE is a modular Streamlit-based decision support system for mapping and preventing online investment scam ecosystems. It is designed as a software artefact for a future SoftwareX paper and as an analytical companion for the Q1 conceptual framework paper.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('### Main Modules')
st.write('- Transcript upload and parsing')
st.write('- Automated qualitative coding evidence')
st.write('- Risk indicator scoring')
st.write('- Ecosystem network map')
st.write('- Stakeholder prevention matrix')
st.write('- Mathematical framework representation')
st.write('- Premium HTML and PDF report generation')
