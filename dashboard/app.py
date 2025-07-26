# ================================================
# ARCHIVO A MODIFICAR: dashboard/app.py (REMASTERIZADO)
# ================================================
import streamlit as st
import pandas as pd
from supabase import create_client, Client
import streamlit_authenticator as stauth
import sys
import os

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Dashboard Logístico v3.0", layout="wide", initial_sidebar_state="expanded")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- 2. IMPORTACIÓN DE COMPONENTES ---
from components import filtros, resumen, clasificacion, soporte, asignacion, analisis_tiempos, analisis_general
from utils import procesar_y_validar_dataframe, actualizar_bd_con_nuevos_datos, registrar_log_de_carga, to_excel

# --- 3. CONEXIÓN A LA BASE DE DATOS ---
try:
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    supabase = create_client(url, key)
except Exception as e:
    st.error(f"Error fatal: No se pudo conectar a Supabase. Revisa tus secretos. Error: {e}")
    st.stop()

# --- 4. AUTENTICACIÓN ---
try:
    credentials = {"usernames": {"admin": {"name": st.secrets["auth_admin_name"], "password": st.secrets["auth_admin_password_hash"]}}}
    authenticator = stauth.Authenticate(credentials, "cookie_logistica_v3", "key_logistica_v3", cookie_expiry_days=30)
    authenticator.login()
except Exception as e:
    st.error(f"Error fatal: No se pudo configurar la autenticación. Revisa tus secretos. Error: {e}")
    st.stop()

if not st.session_state.get("authentication_status"):
    st.stop()

# --- 5. SIDEBAR Y LÓGICA DE CARGA DE DATOS ---
st.sidebar.title(f"Bienvenido, *{st.session_state['name']}* 👋")
authenticator.logout("Cerrar Sesión", "sidebar")
st.sidebar.divider()
st.sidebar.header("📤 Actualizar Datos")

uploaded_file = st.sidebar.file_uploader("Sube el archivo de operaciones", type=['xls', 'xlsx'], key="file_uploader")

if 'df_limpio' not in st.session_state:
    st.session_state.df_limpio = pd.DataFrame()
    st.session_state.df_duplicados = pd.DataFrame()
    st.session_state.resumen_calidad = pd.DataFrame()

if uploaded_file:
    if st.sidebar.button("1. Analizar Archivo", type="secondary"):
        with st.spinner("Analizando archivo..."):
            try:
                df_crudo = pd.read_excel(uploaded_file, engine=None)
                df_limpio, df_duplicados, resumen_calidad = procesar_y_validar_dataframe(df_crudo)
                st.session_state.df_limpio = df_limpio
                st.session_state.df_duplicados = df_duplicados
                st.session_state.resumen_calidad = resumen_calidad
            except Exception as e:
                st.sidebar.error(f"Error en el análisis: {e}")
                st.session_state.df_limpio, st.session_state.df_duplicados, st.session_state.resumen_calidad = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

if not st.session_state.df_limpio.empty or not st.session_state.df_duplicados.empty:
    st.sidebar.divider()
    st.sidebar.subheader("Resultados del Análisis")
    st.sidebar.success(f"**{len(st.session_state.df_limpio)}** registros limpios y únicos.")
    if not st.session_state.df_duplicados.empty:
        st.sidebar.warning(f"**{len(st.session_state.df_duplicados)}** registros duplicados encontrados.")
        st.sidebar.download_button(label="📥 Descargar Reporte de Duplicados", data=to_excel(st.session_state.df_duplicados), file_name="reporte_duplicados.xlsx")
    if not st.session_state.resumen_calidad.empty:
        st.sidebar.subheader("Reporte de Calidad de Datos")
        st.sidebar.dataframe(st.session_state.resumen_calidad, use_container_width=True)
    if st.sidebar.button("2. Cargar Datos Limpios a la BD", type="primary"):
        num_nuevos = actualizar_bd_con_nuevos_datos(st.session_state.df_limpio, supabase)
        if num_nuevos != -1:
            registrar_log_de_carga(supabase, len(st.session_state.df_limpio), len(st.session_state.df_duplicados), st.session_state.resumen_calidad)
            st.cache_data.clear()
            st.session_state.df_limpio, st.session_state.df_duplicados, st.session_state.resumen_calidad = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
            st.rerun()

# --- 6. LÓGICA PRINCIPAL DEL DASHBOARD ---
@st.cache_data(ttl=300)
def cargar_datos_desde_bd():
    response = supabase.table('operaciones').select("*").execute()
    df = pd.DataFrame(response.data)
    if df.empty: return df
    columnas_fecha = ['fecha_file', 'fecha_cierre', 'fecha_primera_factura', 'fecha_arribo', 'fecha_zarpe', 'fecha_de_factura', 'fecha_envio_cierre']
    for col in columnas_fecha:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

st.title("📊 Análisis de Operaciones")
df_operaciones = cargar_datos_desde_bd()

if df_operaciones.empty:
    st.warning("Aún no hay datos. Sube un archivo para comenzar.")
else:
    # --- PESTAÑA DE ANÁLISIS GENERAL CON KPIs ---
    analisis_general.mostrar_kpis_calidad(supabase)
    
    df_filtrado = filtros.mostrar_filtros(df_operaciones)
    if not df_filtrado.empty:
        df_fechas_validas = df_filtrado.dropna(subset=['fecha_file'])
        num_meses = len(df_fechas_validas['fecha_file'].dt.to_period('M').unique()) if not df_fechas_validas.empty else 1
        num_meses = max(1, num_meses)
    else:
        st.warning("No hay datos que coincidan con los filtros seleccionados.")
        num_meses = 1

    # --- NUEVAS PESTAÑAS REMASTERIZADAS ---
    tabs = st.tabs(["🔬 Análisis General", "🚦 Asignación", "🧮 Capacidad", "📊 Clasificación", "📈 Resumen", "⏱️ Tiempos"])
    with tabs[0]: analisis_general.mostrar_analisis_general(df_filtrado)
    with tabs[1]: asignacion.mostrar_asignacion(df_filtrado)
    with tabs[2]: soporte.mostrar_soporte(df_filtrado)
    with tabs[3]: clasificacion.mostrar_clasificacion(df_filtrado, num_meses)
    with tabs[4]: resumen.mostrar_resumen(df_filtrado)
    with tabs[5]: analisis_tiempos.mostrar_analisis_tiempos(df_filtrado)