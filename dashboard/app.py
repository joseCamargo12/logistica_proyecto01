# ================================================
# ARCHIVO A MODIFICAR: dashboard/app.py (VERSIÓN TRANSPARENTE)
# ================================================
import streamlit as st
import pandas as pd
from supabase import create_client, Client
import streamlit_authenticator as stauth
import sys
import os

st.set_page_config(page_title="FAM analisis de datos", layout="wide", initial_sidebar_state="expanded")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components import filtros, resumen, clasificacion, soporte, asignacion, analisis_tiempos, analisis_general
from utils import analizar_archivo_cargado, insertar_nuevos_datos, registrar_log_de_carga, to_excel

try:
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    supabase = create_client(url, key)
except Exception as e:
    st.error(f"Error fatal: No se pudo conectar a Supabase. Revisa tus secretos. Error: {e}")
    st.stop()

try:
    credentials = {"usernames": {"admin": {"name": st.secrets["auth_admin_name"], "password": st.secrets["auth_admin_password_hash"]}}}
    authenticator = stauth.Authenticate(credentials, "cookie_logistica_v4", "key_logistica_v4", cookie_expiry_days=30)
    authenticator.login()
except Exception as e:
    st.error(f"Error fatal: No se pudo configurar la autenticación. Revisa tus secretos. Error: {e}")
    st.stop()

if not st.session_state.get("authentication_status"):
    st.stop()

# --- SIDEBAR Y LÓGICA DE CARGA DE DATOS ---
st.sidebar.title(f"Bienvenido, *{st.session_state['name']}* 👋")
authenticator.logout("Cerrar Sesión", "sidebar")
st.sidebar.divider()
st.sidebar.header("📤 Actualizar Datos")

uploaded_file = st.sidebar.file_uploader("Sube el archivo de operaciones", type=['xls', 'xlsx'], key="file_uploader")

# Inicializar el estado de la sesión para los nuevos DataFrames
if 'df_nuevos' not in st.session_state:
    st.session_state.df_nuevos = pd.DataFrame()
    st.session_state.df_existentes = pd.DataFrame()
    st.session_state.df_duplicados_internos = pd.DataFrame()
    st.session_state.resumen_calidad = pd.DataFrame()

if uploaded_file:
    if st.sidebar.button("1. Analizar Archivo", type="secondary"):
        with st.spinner("Realizando análisis completo del archivo..."):
            try:
                df_crudo = pd.read_excel(uploaded_file, engine=None)
                # La nueva función devuelve 4 DataFrames
                df_nuevos, df_existentes, df_duplicados_internos, resumen_calidad = analizar_archivo_cargado(df_crudo, supabase)
                
                st.session_state.df_nuevos = df_nuevos
                st.session_state.df_existentes = df_existentes
                st.session_state.df_duplicados_internos = df_duplicados_internos
                st.session_state.resumen_calidad = resumen_calidad

            except Exception as e:
                st.sidebar.error(f"Error en el análisis: {e}")
                # Limpiar el estado en caso de error
                st.session_state.df_nuevos, st.session_state.df_existentes, st.session_state.df_duplicados_internos, st.session_state.resumen_calidad = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Mostrar los resultados del análisis de forma transparente
if not st.session_state.df_nuevos.empty or not st.session_state.df_existentes.empty or not st.session_state.df_duplicados_internos.empty:
    st.sidebar.divider()
    st.sidebar.subheader("Resultados del Análisis")
    
    st.sidebar.success(f"**{len(st.session_state.df_nuevos)}** registros nuevos para cargar.")
    st.sidebar.info(f"**{len(st.session_state.df_existentes)}** registros ya existentes en la BD.")
    
    if not st.session_state.df_duplicados_internos.empty:
        st.sidebar.warning(f"**{len(st.session_state.df_duplicados_internos)}** filas duplicadas en el archivo (descartadas).")
        st.sidebar.download_button(label="📥 Descargar Reporte de Duplicados", data=to_excel(st.session_state.df_duplicados_internos), file_name="reporte_duplicados.xlsx")
    
    if not st.session_state.resumen_calidad.empty:
        st.sidebar.subheader("Calidad de los Datos Nuevos")
        st.sidebar.dataframe(st.session_state.resumen_calidad, use_container_width=True)

    # El botón ahora refleja la acción real
    if st.sidebar.button(f"2. Cargar {len(st.session_state.df_nuevos)} Registros Nuevos a la BD", type="primary"):
        num_insertados = insertar_nuevos_datos(st.session_state.df_nuevos, supabase)
        if num_insertados != -1:
            registrar_log_de_carga(supabase, num_insertados, len(st.session_state.df_existentes), len(st.session_state.df_duplicados_internos), st.session_state.resumen_calidad)
            st.cache_data.clear()
            # Limpiar estado para la próxima carga
            st.session_state.df_nuevos, st.session_state.df_existentes, st.session_state.df_duplicados_internos, st.session_state.resumen_calidad = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
            st.rerun()

# --- LÓGICA PRINCIPAL DEL DASHBOARD ---
@st.cache_data(ttl=300)
def cargar_datos_desde_bd():
    # Esta función ya es correcta (con paginación)
    all_data = []
    page = 0
    while True:
        response = supabase.table('operaciones').select("*").range(page * 1000, (page + 1) * 1000 - 1).execute()
        data = response.data
        if not data: break
        all_data.extend(data)
        page += 1

    df = pd.DataFrame(all_data)
    if df.empty: return df
    
    columnas_fecha = ['fecha_file', 'fecha_cierre', 'fecha_primera_factura', 'fecha_arribo', 'fecha_zarpe', 'fecha_de_factura', 'fecha_envio_cierre']
    for col in columnas_fecha:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    df.dropna(subset=['fecha_file'], inplace=True)
    return df

st.title("📊 Análisis de Operaciones")
df_operaciones = cargar_datos_desde_bd()

if df_operaciones.empty:
    st.warning("Aún no hay datos. Sube un archivo para comenzar.")
else:
    analisis_general.mostrar_kpis_calidad(supabase)
    
    df_filtrado = filtros.mostrar_filtros(df_operaciones)
    
    if not df_filtrado.empty:
        num_meses = len(df_filtrado['fecha_file'].dt.to_period('M').unique())
        num_meses = max(1, num_meses)
    else:
        st.warning("No hay datos que coincidan con los filtros seleccionados.")
        num_meses = 1

    tabs = st.tabs(["🔬 Análisis General", "🚦 Asignación", "🧮 Capacidad", "📊 Clasificación", "📈 Resumen", "⏱️ Tiempos"])
    with tabs[0]: analisis_general.mostrar_analisis_general(df_filtrado)
    with tabs[1]: asignacion.mostrar_asignacion(df_filtrado)
    with tabs[2]: soporte.mostrar_soporte(df_filtrado)
    with tabs[3]: clasificacion.mostrar_clasificacion(df_filtrado, num_meses)
    with tabs[4]: resumen.mostrar_resumen(df_filtrado)
    with tabs[5]: analisis_tiempos.mostrar_analisis_tiempos(df_filtrado)