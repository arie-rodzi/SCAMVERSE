from pathlib import Path
import streamlit as st
from config import APP_NAME, APP_SUBTITLE, APP_VERSION

ROOT = Path(__file__).resolve().parents[1]

def load_css():
    css_path = ROOT / 'assets' / 'styles.css'
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

def sidebar():
    st.sidebar.markdown(f"# 🛡️ {APP_NAME}")
    st.sidebar.markdown("**Premium scam ecosystem analytics**")
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Version:** {APP_VERSION}")
    st.sidebar.markdown("**Outputs:** HTML + PDF + analysis tables")
    st.sidebar.markdown("---")
    st.sidebar.info("Use the Upload page first, then open Dashboard, Coding, Ecosystem, Framework or Report.")

def hero(title=APP_NAME, subtitle=APP_SUBTITLE):
    st.markdown(f"<div class='hero'><h1>{title}</h1><p>{subtitle}</p></div>", unsafe_allow_html=True)

def kpi(label, value, note):
    st.markdown(f"<div class='kpi'><div class='label'>{label}</div><div class='value'>{value}</div><div class='note'>{note}</div></div>", unsafe_allow_html=True)
