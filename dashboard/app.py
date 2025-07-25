import streamlit as st
import pandas as pd
from supabase import create_client
import streamlit_authenticator as stauth
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components import filtros, resumen, clasificacion, soporte, asignacion, analisis_tiempos
from utils import limpiar_y_preparar_dataframe, actualizar_bd_con_nuevos_datos

st.set_page_config(page_title="Dashboard Logístico v2.0", layout="wide", initial_sidebar_state="expanded")

# --- 1. CONEXIÓN A LA BASE DE DATOS (VERSIÓN DIRECTA) ---
try:
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    supabase = create_client(url, key)
except Exception as e:
    st.error(f"Error fatal: No se pudo conectar a Supabase. Revisa tus secretos. Error: {e}")
    st.stop()

# --- 2. AUTENTICACIÓN ---
try:
    credentials = {
        "usernames": {
            "admin": {
                "name": st.secrets["auth_admin_name"],
                "password": st.secrets["auth_admin_password_hash"]
            }
        }
    }
    authenticator = stauth.Authenticate(
        credentials,
        "some_cookie_name",
        "some_signature_key",
        cookie_expiry_days=30
    )
    authenticator.login()
except Exception as e:
    st.error(f"Error fatal: No se pudo configurar la autenticación. Revisa tus secretos. Error: {e}")
    st.stop()

# --- EL RESTO DEL ARCHIVO SE QUEDA IGUAL ---
# (El código de if not st.session_state... en adelante no necesita cambios)
if not st.session_state.get("authentication_status"):
    st.stop()
authenticator.login()

if not st.session_state.get("authentication_status"):
    st.stop()

st.sidebar.title(f"Bienvenido, *{st.session_state['name']}* 👋")
authenticator.logout("Cerrar Sesión", "sidebar")
st.sidebar.divider()

st.sidebar.header("📤 Actualizar Datos")
uploaded_file = st.sidebar.file_uploader(
    "Sube el archivo Excel o CSV",
    type=['csv', 'xls', 'xlsx'],
    key="file_uploader"
)

if uploaded_file:
    if st.sidebar.button("Procesar y Actualizar", type="primary"):
        try:
            df_crudo = pd.read_excel(uploaded_file)
            df_limpio = limpiar_y_preparar_dataframe(df_crudo)
            num_nuevos = actualizar_bd_con_nuevos_datos(df_limpio, supabase)
            if num_nuevos > 0:
                st.cache_data.clear()
                st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error en el proceso: {e}")

@st.cache_data(ttl=300)
def cargar_datos_desde_bd():
    response = supabase.table('operaciones').select("*").execute()
    df = pd.DataFrame(response.data)
    if df.empty: return df
    for col in ['fecha_file', 'fecha_cierre', 'fecha_arribo', 'fecha_zarpe', 'fecha_de_factura', 'fecha_envio_cierre']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

st.title("📊Análisis de Operaciones")
df_operaciones = cargar_datos_desde_bd()

if df_operaciones.empty:
    st.warning("Aún no hay datos. Sube un archivo para comenzar.")
else:
    df_filtrado = filtros.mostrar_filtros(df_operaciones)
    if not df_filtrado.empty:
        num_meses = len(pd.to_datetime(df_filtrado.dropna(subset=['fecha_file'])['fecha_file']).dt.to_period('M').unique())
        num_meses = max(1, num_meses)
    else:
        st.warning("No hay datos que coincidan con los filtros seleccionados.")
        num_meses = 1

    tabs = st.tabs(["🚦 Asignación", "🧮 Capacidad", "📊 Clasificación", "📈 Resumen", "⏱️ Tiempos"])
    with tabs[0]: asignacion.mostrar_asignacion(df_filtrado)
    with tabs[1]: soporte.mostrar_soporte(df_filtrado)
    with tabs[2]: clasificacion.mostrar_clasificacion(df_filtrado, num_meses)
    with tabs[3]: resumen.mostrar_resumen(df_filtrado)
    with tabs[4]: analisis_tiempos.mostrar_analisis_tiempos(df_filtrado)