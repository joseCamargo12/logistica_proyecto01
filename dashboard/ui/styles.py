# dashboard/ui/styles.py
import streamlit as st
import requests

# Tu función 'inyectar_estilos_compactos' original
def inyectar_estilos_compactos():
    st.markdown("""
    <style>
    .st-emotion-cache-183lzff { padding-bottom: 0rem; }
    .st-emotion-cache-1gulkj5 { padding-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# Tu función 'load_lottie_url' original
@st.cache_resource
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Tu función 'inyectar_iconos_en_tabs' original
def inyectar_iconos_en_tabs():
    st.markdown("""
    <style>
    button[data-baseweb="tab"] { display: flex; align-items: center; gap: 8px; }
    button[data-baseweb="tab"]:nth-child(1)::before { font-family: "bootstrap-icons"; content: "\\f428"; }
    button[data-baseweb="tab"]:nth-child(2)::before { font-family: "bootstrap-icons"; content: "\\f54d"; }
    button[data-baseweb="tab"]:nth-child(3)::before { font-family: "bootstrap-icons"; content: "\\f1c8"; }
    button[data-baseweb="tab"]:nth-child(4)::before { font-family: "bootstrap-icons"; content: "\\f551"; }
    button[data-baseweb="tab"]:nth-child(5)::before { font-family: "bootstrap-icons"; content: "\\f223"; }
    button[data-baseweb="tab"]:nth-child(6)::before { font-family: "bootstrap-icons"; content: "\\f28c"; }
    button[data-baseweb="tab"]:nth-child(7)::before { font-family: "bootstrap-icons"; content: "\\f1f3"; }
    button[data-baseweb="tab"]:nth-child(8)::before { font-family: "bootstrap-icons"; content: "\\f4f6"; }
    </style>
    """, unsafe_allow_html=True)

# Tu función 'mostrar_footer' original
def mostrar_footer(logo_url): # Le pasamos el logo_url
    st.divider()
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown(
            f"""
            <div style="text-align: center; color: gray; font-size: 0.9rem;">
                <img src="{logo_url}" width="40" style="vertical-align: middle; margin-right: 10px;">
                Desarrollado por <a href='https://estrategiaempresarial.com.co' style='text-decoration: none; color: #1E90FF; font-weight: bold;'>Estrategia Empresarial</a>
            </div>
            """,
            unsafe_allow_html=True
        )