# archivo: dashboard/app.py

import streamlit as st
import pandas as pd
from supabase import create_client, Client
import streamlit_authenticator as stauth

# Importaciones de tus módulos locales
from components import filtros, resumen, clasificacion, soporte, asignacion, analisis_tiempos
from utils import limpiar_y_preparar_dataframe, actualizar_bd_con_nuevos_datos

st.set_page_config(page_title="Dashboard Logístico v2.0", layout="wide")

# --- 1. CONEXIÓN A LA BASE DE DATOS ---
@st.cache_resource
def init_supabase_connection():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_supabase_connection()

# --- 2. AUTENTICACIÓN ---
authenticator = stauth.Authenticate(
    st.secrets["auth"],
    "some_cookie_name",
    "some_signature_key",
    cookie_expiry_days=30
)
authenticator.login()

if not st.session_state.get("authentication_status"):
    st.stop()

# --- 3. CUERPO DE LA APP (SI EL LOGIN ES EXITOSO) ---
st.sidebar.title(f"Bienvenido, *{st.session_state['name']}* 👋")
authenticator.logout("Cerrar Sesión", "sidebar")

# --- 4. WIDGET DE CARGA DE ARCHIVOS ---
st.sidebar.divider()
st.sidebar.header("📤 Actualizar Datos")
uploaded_file = st.sidebar.file_uploader(
    "Sube un archivo Excel o CSV",
    type=['csv', 'xls', 'xlsx'],
    key="file_uploader"
)

if uploaded_file:
    if st.sidebar.button("Procesar y Actualizar Base de Datos", type="primary"):
        try:
            df_crudo = pd.read_excel(uploaded_file) if uploaded_file.name.endswith(('xls', 'xlsx')) else pd.read_csv(uploaded_file)
            df_limpio = limpiar_y_preparar_dataframe(df_crudo)
            num_nuevos = actualizar_bd_con_nuevos_datos(df_limpio, supabase)

            if num_nuevos > 0:
                st.cache_data.clear() # Limpia la caché para forzar recarga
                st.rerun() # Refresca la página para mostrar los nuevos datos
        except Exception as e:
            st.sidebar.error(f"Error en el proceso: {e}")

# --- 5. CARGA DE DATOS DESDE LA BASE DE DATOS ---
@st.cache_data(ttl=600) # Cache por 10 minutos
def cargar_datos_desde_bd():
    response = supabase.table('operaciones').select("*").execute()
    df = pd.DataFrame(response.data)
    if df.empty: return df
    df['fecha_file'] = pd.to_datetime(df['fecha_file'])
    df['fecha_cierre'] = pd.to_datetime(df['fecha_cierre'])
    return df

st.title("📊 Dashboard Logístico - Análisis de Operaciones")
df_operaciones = cargar_datos_desde_bd()

if df_operaciones.empty:
    st.warning("Aún no hay datos. Sube un archivo para comenzar.")
else:
    # --- 6. VISUALIZACIÓN DEL DASHBOARD ---
    df_filtrado = filtros.mostrar_filtros(df_operaciones)

    if not df_filtrado.empty:
        st.info(f"Mostrando {len(df_filtrado)} de {len(df_operaciones)} operaciones totales.")
        df_fechas_validas = df_filtrado.dropna(subset=['fecha_file'])
        num_meses = len(pd.to_datetime(df_fechas_validas['fecha_file']).dt.to_period('M').unique())
        num_meses = max(1, num_meses)
    else:
        st.warning("No hay datos que coincidan con los filtros seleccionados.")
        num_meses = 1

    tabs = st.tabs([
        "🚦 Asignación Sugerida", "🧮 Capacidad de Carga", "📊 Clasificación de Flujo",
        "📈 Resumen", "⏱️ Análisis de Tiempos"
    ])
    with tabs[0]: asignacion.mostrar_asignacion(df_filtrado)
    with tabs[1]: soporte.mostrar_soporte(df_filtrado)
    with tabs[2]: clasificacion.mostrar_clasificacion(df_filtrado, num_meses)
    with tabs[3]: resumen.mostrar_resumen(df_filtrado)
    with tabs[4]: analisis_tiempos.mostrar_analisis_tiempos(df_filtrado)