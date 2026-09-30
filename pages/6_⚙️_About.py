import streamlit as st
from modules.ui import load_css, sidebar, hero
from config import APP_NAME, APP_VERSION

st.set_page_config(page_title='About | SCAMVERSE', page_icon='⚙️', layout='wide')
load_css(); sidebar(); hero('About SCAMVERSE', 'System description and documentation')

st.markdown(f"""
<div class='card'>
<h2>{APP_NAME} {APP_VERSION}</h2>
<p>SCAMVERSE is a modular Streamlit-based decision support system for mapping and preventing online investment scam ecosystems. It is the software companion to the Integrated Multi-Stakeholder Prevention Framework (IMSPF). Source code: https://github.com/arie-rodzi/SCAMVERSE (BSD 3-Clause License).</p>
</div>
""", unsafe_allow_html=True)

st.markdown('### Main Modules')
st.write('- Transcript upload and parsing')
st.write('- Automated qualitative coding evidence')
st.write('- Risk indicator scoring')
st.write('- Ecosystem network map')
st.write('- Stakeholder prevention matrix')
st.write('- Mathematical framework representation')
st.write('- HTML and PDF report generation')
