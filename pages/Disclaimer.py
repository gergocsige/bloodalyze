import streamlit as st
from translations import translations

# Fetch the language from the session state, fallback to English
lang = st.session_state.get('persistent_lang', 'English')
t = translations[lang]

st.set_page_config(page_title=t["disclaimer_page_title"], page_icon="⚖️", layout="wide")

st.title(t["disclaimer_page_title"])

st.markdown(t["disclaimer_text"])

st.page_link("app.py", label=t["return_analyzer"], icon="⬅️")
