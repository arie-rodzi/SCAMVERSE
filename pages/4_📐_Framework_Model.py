import streamlit as st
from modules.ui import load_css, sidebar, hero
from config import FRAMEWORK_NAME

st.set_page_config(page_title='Framework | SCAMVERSE', page_icon='📐', layout='wide')
load_css(); sidebar(); hero('Framework Model', FRAMEWORK_NAME)

st.markdown("""
<div class='card'>
<h2 style='color:white;'>Integrated Framework Logic</h2>
<p style='color:#dbeafe;font-size:16px;'>SCAMVERSE models online investment scams as a layered ecosystem involving digital recruitment, manipulation, victim vulnerability, scammer operations, financial laundering, institutional response and prevention capacity.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('### Mathematical Ecosystem Representation')
st.latex(r"S = f(D, M, V, O, F, I, P)")
st.markdown('Where **S** is ecosystem scam risk, **D** digital recruitment, **M** manipulation intensity, **V** victim vulnerability, **O** operational sophistication, **F** financial-chain complexity, **I** institutional coordination gap and **P** preventive capacity.')

st.latex(r"PI = \sum_{i=1}^{n} w_i C_i - \sum_{j=1}^{m} \lambda_j R_j")
st.markdown('The prevention index **PI** balances stakeholder capabilities against residual risk indicators.')

st.markdown('### Six Prevention Layers')
st.markdown("""
1. Digital-platform intelligence  
2. Victim vulnerability reduction  
3. Scam operational disruption  
4. Financial-chain monitoring  
5. Multi-agency enforcement coordination  
6. Public resilience and rapid reporting  
""")
