import streamlit as st
from modules.ui import load_css, sidebar, hero, full_width
from modules.engine import codes_df, theme_df
from modules.graphs import sunburst

st.set_page_config(page_title='Thematic Evidence | SCAMVERSE', page_icon='🧠', layout='wide')
load_css(); sidebar(); hero('Thematic Evidence', 'Lexicon-coded evidence extracts by dimension')

if 'analysis' not in st.session_state:
    st.warning('Please analyse transcripts first in Upload & Analyse.')
    st.stop()
a = st.session_state.analysis
cdf = codes_df(a); tdf = theme_df(a)

st.markdown('### Coding Evidence Table')
st.dataframe(cdf, **full_width(st.dataframe), hide_index=True)

st.markdown('### Dimension Sunburst')
st.plotly_chart(sunburst(tdf), **full_width(st.plotly_chart))

st.markdown('### Evidence Extracts by Dimension')
for theme, evs in a['evidence'].items():
    with st.expander(theme, expanded=False):
        for e in evs:
            st.write('• ' + e)
