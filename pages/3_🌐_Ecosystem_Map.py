import streamlit as st
from modules.ui import load_css, sidebar, hero, full_width
from modules.graphs import ecosystem_network
from modules.engine import stakeholder_df

st.set_page_config(page_title='Ecosystem Map | SCAMVERSE', page_icon='🌐', layout='wide')
load_css(); sidebar(); hero('Ecosystem Map', 'Reference map of ecosystem actors and stakeholder roles')

st.markdown('### Ecosystem Actor Map')
st.plotly_chart(ecosystem_network(), **full_width(st.plotly_chart))

st.markdown('### Stakeholder Prevention Matrix')
st.dataframe(stakeholder_df(), **full_width(st.dataframe), hide_index=True)
