import json

import pandas as pd
import streamlit as st

from config import APP_NAME, APP_VERSION
from modules.engine import RISK_CAP, default_lexicon
from modules.ui import full_width, hero, load_css, sidebar

st.set_page_config(page_title='About | SCAMVERSE', page_icon='⚙️', layout='wide')
load_css(); sidebar(); hero('About SCAMVERSE', 'System description, lexicons and documentation')

st.markdown(f"""
<div class='card'>
<h2>{APP_NAME} {APP_VERSION}</h2>
<p>SCAMVERSE is an open-source Streamlit application for transparent, lexicon-based coding of online
investment-scam transcripts. It produces coded evidence sentences, a bounded warning-signal index with
indicator densities, a reference map of ecosystem actors, a stakeholder matrix and HTML/PDF reports.
Source code: https://github.com/arie-rodzi/SCAMVERSE (BSD 3-Clause License).</p>
</div>
""", unsafe_allow_html=True)

st.markdown('### Method in brief')
st.markdown(f"""
- Terms are matched case-insensitively as whole terms, with an optional inflectional suffix (-s, -es, -d, -ed, -ing).
- Each dimension keeps up to five evidence sentences; each sentence is coded with the first lexicon term it contains.
- Warning-signal index: floor(100 × Σ min(matches, {RISK_CAP}) / ({RISK_CAP} × number of indicators)); bands High ≥ 70, Moderate ≥ 35, otherwise Low. The bands are descriptive and uncalibrated.
- Indicator density: matches per 1,000 words (uncapped).
- Results describe the text; they are not a judgement about any individual case.
""")

lex = default_lexicon()
st.markdown('### Default lexicon: ecosystem dimensions')
st.dataframe(pd.DataFrame({'Dimension': list(lex['dimensions']),
                           'Terms': [', '.join(v) for v in lex['dimensions'].values()]}),
             **full_width(st.dataframe), hide_index=True)
st.markdown('### Default lexicon: warning indicators')
st.dataframe(pd.DataFrame({'Warning indicator': list(lex['indicators']),
                           'Terms': [', '.join(v) for v in lex['indicators'].values()]}),
             **full_width(st.dataframe), hide_index=True)

st.download_button('Download default lexicon (JSON)', data=json.dumps(lex, indent=2, ensure_ascii=False),
                   file_name='scamverse_lexicon.json', mime='application/json')
st.caption('A custom lexicon with the same structure, {"dimensions": {name: [terms]}, "indicators": {name: [terms]}}, '
           'can be supplied on the Upload and Analyse page.')
