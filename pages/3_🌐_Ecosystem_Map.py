import streamlit as st
from modules.ui import load_css, sidebar, hero
from modules.graphs import ecosystem_network
from modules.engine import stakeholder_df

st.set_page_config(page_title='Ecosystem Map | SCAMVERSE', page_icon='🌐', layout='wide')
load_css(); sidebar(); hero('Ecosystem Map', 'Network view of the online investment scam ecosystem')

st.markdown('### Interactive Ecosystem Network')
st.plotly_chart(ecosystem_network(), use_container_width=True)

st.markdown('### Stakeholder Action Matrix')
st.dataframe(stakeholder_df(), use_container_width=True, hide_index=True)
