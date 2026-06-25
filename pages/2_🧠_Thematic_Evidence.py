import streamlit as st
from modules.ui import load_css, sidebar, hero
from modules.engine import codes_df, theme_df
from modules.graphs import sunburst

st.set_page_config(page_title='Coding Evidence | SCAMVERSE', page_icon='🧠', layout='wide')
load_css(); sidebar(); hero('Thematic Evidence', 'Open coding, axial coding and dimension-level evidence synthesis')

if 'analysis' not in st.session_state:
    st.warning('Please analyse transcripts first in Upload & Analyse.')
    st.stop()
a = st.session_state.analysis
cdf = codes_df(a); tdf = theme_df(a)

st.markdown('### Coding Evidence Table')
st.dataframe(cdf, use_container_width=True, hide_index=True)

st.markdown('### Coding-to-Dimension Sunburst')
st.plotly_chart(sunburst(tdf), use_container_width=True)

st.markdown('### Evidence Extracts by Dimension')
for theme, evs in a['evidence'].items():
    with st.expander(theme, expanded=False):
        for e in evs:
            st.write('• ' + e)
