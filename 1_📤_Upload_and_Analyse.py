import streamlit as st
from modules.ui import load_css, sidebar, hero
from modules.parser import extract_text
from modules.engine import analyze_text, theme_df, risk_df, codes_df

st.set_page_config(page_title='Upload & Analyse | SCAMVERSE', page_icon='📤', layout='wide')
load_css(); sidebar(); hero('Upload & Analyse', 'Upload transcript files or paste text for automated scam ecosystem analysis')

uploaded_files = st.file_uploader('Upload TXT or DOCX transcripts', type=['txt','docx'], accept_multiple_files=True)
pasted = st.text_area('Or paste transcript text here', height=260)

if st.button('🚀 Analyse Corpus'):
    corpus = ''
    if uploaded_files:
        for f in uploaded_files:
            corpus += f"\n\n===== {f.name} =====\n" + extract_text(f)
    if pasted.strip():
        corpus += '\n\n===== PASTED TEXT =====\n' + pasted
    if not corpus.strip():
        st.warning('Please upload or paste transcript text first.')
    else:
        st.session_state.analysis = analyze_text(corpus)
        st.success('Analysis completed. Open Dashboard, Coding Evidence, Ecosystem Map, Framework or Premium Report.')

if 'analysis' in st.session_state:
    a = st.session_state.analysis
    c1,c2,c3 = st.columns(3)
    c1.metric('Risk Score', f"{a['risk_score']}/100")
    c2.metric('Risk Level', a['risk_level'])
    c3.metric('Words', f"{len(a['text'].split()):,}")
    st.markdown('### Detected Dimensions')
    st.dataframe(theme_df(a), use_container_width=True, hide_index=True)
    st.markdown('### Risk Indicators')
    st.dataframe(risk_df(a), use_container_width=True, hide_index=True)
    st.markdown('### Coding Evidence Preview')
    st.dataframe(codes_df(a).head(20), use_container_width=True, hide_index=True)
