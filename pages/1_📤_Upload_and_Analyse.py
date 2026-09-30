import streamlit as st
from modules.ui import load_css, sidebar, hero, full_width
from modules.parser import extract_text
from modules.engine import analyze_text, theme_df, risk_df, codes_df, prepare_text, load_lexicon

st.set_page_config(page_title='Upload and Analyse | SCAMVERSE', page_icon='📤', layout='wide')
load_css(); sidebar(); hero('Upload and Analyse', 'Upload transcript files or paste text for lexicon-based analysis')

st.caption('Confidential transcripts should be analysed with a local installation (streamlit run app.py). '
           'Text uploaded to a hosted instance is processed on that host.')

uploaded_files = st.file_uploader('Upload TXT or DOCX transcripts', type=['txt','docx'], accept_multiple_files=True)
pasted = st.text_area('Or paste transcript text here', height=260)

with st.expander('Options'):
    strip_labels = st.checkbox('Remove speaker labels such as "Officer A:" before analysis', value=True)
    exclude = st.text_input('Exclude turns by these speakers (comma-separated label prefixes)', value='Interviewer')
    lex_file = st.file_uploader('Custom lexicon (JSON, optional; see About page for the format)', type=['json'])

if st.button('🚀 Analyse Corpus'):
    # Documents are joined with blank lines only; file names are never added to the
    # analysed text, so they cannot contribute lexicon matches or word counts.
    parts = [extract_text(f) for f in uploaded_files or []]
    if pasted.strip():
        parts.append(pasted)
    corpus = '\n\n'.join(p for p in parts if p.strip())
    corpus = prepare_text(corpus, strip_labels=strip_labels,
                          exclude_speakers=[x for x in exclude.split(',') if x.strip()])
    lexicon = None
    if lex_file is not None:
        try:
            lexicon = load_lexicon(lex_file.read().decode('utf-8'))
        except (ValueError, UnicodeDecodeError) as exc:
            st.error(f'Custom lexicon not used: {exc}')
    if not corpus.strip():
        st.warning('Please upload or paste transcript text first.')
    else:
        st.session_state.analysis = analyze_text(corpus, lexicon)
        st.success('Analysis completed. Open Dashboard, Thematic Evidence, Ecosystem Map, Framework Model or Report.')

if 'analysis' in st.session_state:
    a = st.session_state.analysis
    c1,c2,c3 = st.columns(3)
    c1.metric('Warning-signal index', f"{a['risk_score']}/100")
    c2.metric('Band', a['risk_level'])
    c3.metric('Words', f"{len(a['text'].split()):,}")
    st.markdown('### Detected Dimensions')
    st.dataframe(theme_df(a), **full_width(st.dataframe), hide_index=True)
    st.markdown('### Warning Indicators')
    st.dataframe(risk_df(a), **full_width(st.dataframe), hide_index=True)
    st.markdown('### Coding Evidence Preview')
    st.dataframe(codes_df(a).head(20), **full_width(st.dataframe), hide_index=True)
