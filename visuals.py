from pathlib import Path
import streamlit as st


def _load_css(path: Path):
    if path.exists():
        return path.read_text()
    return ""


def render_holographic():
    base = Path(__file__).parent / "templates"
    css = _load_css(base / "holographic.css")
    html = _load_css(base / "holographic.html")

    if css:
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

    if html:
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.write("[Holographic preview placeholder]")
