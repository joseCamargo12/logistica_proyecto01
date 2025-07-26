# ================================================
# ARCHIVO: dashboard/app.py (VERSIÓN FINAL CON PRONÓSTICOS)
# ================================================
import streamlit as st
import pandas as pd
from supabase import create_client, Client
import streamlit_authenticator as stauth
import sys
import os

st.set_page_config(page_title="FAM analisis de datos", layout="wide", initial_sidebar_state="expanded")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- CAMBIO 1: IMPORTAR EL NUEVO COMPONENTE ---
from components import filtros, resumen, clasificacion, soporte, asignacion, analisis_tiempos, analisis_general, pronosticos, glosario
from utils import analizar_archivo_cargado, insertar_nuevos_datos, registrar_log_de_carga, to_excel

try:
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    supabase = create_client(url, key)
except Exception as e:
    st.error(f"Error fatal: No se pudo conectar a Supabase. Revisa tus secretos. Error: {e}")
    st.stop()

try:
    credentials = {
        "usernames": {
            "estrategia": {
                "name": st.secrets["auth_admin_name"],
                "password": st.secrets["auth_admin_password_hash"]
            },
            "fam.team": {
                "name": st.secrets["auth_user_name"],
                "password": st.secrets["auth_user_password_hash"]
            }
        }
    }
    authenticator = stauth.Authenticate(credentials, "cookie_logistica_final", "key_logistica_final", cookie_expiry_days=30)
    authenticator.login()
except Exception as e:
    st.error(f"Error fatal: No se pudo configurar la autenticación. Revisa tus secretos. Error: {e}")
    st.stop()

if not st.session_state.get("authentication_status"):
    st.stop()

# --- SIDEBAR Y LÓGICA DE CARGA DE DATOS (SIN CAMBIOS) ---
st.sidebar.title(f"Bienvenido, *{st.session_state['name']}* 👋")
authenticator.logout("Cerrar Sesión", "sidebar")
st.sidebar.divider()

if st.session_state.get("username") == "estrategia":
    with st.sidebar.expander("🔑 **Panel de Administrador**", expanded=True):
        # ... (Toda la lógica de carga de datos que ya tienes y funciona bien va aquí)
        st.header("📤 Actualizar Datos")
        uploaded_file = st.file_uploader("Sube el archivo de operaciones", type=['xls', 'xlsx'], key="file_uploader")
        if 'df_nuevos' not in st.session_state:
            st.session_state.df_nuevos, st.session_state.df_existentes, st.session_state.df_duplicados_internos, st.session_state.resumen_calidad = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        if uploaded_file:
            if st.button("1. Analizar Archivo", type="secondary", use_container_width=True):
                with st.spinner("Realizando análisis completo del archivo..."):
                    try:
                        df_crudo = pd.read_excel(uploaded_file, engine=None)
                        df_nuevos, df_existentes, df_duplicados_internos, resumen_calidad = analizar_archivo_cargado(df_crudo, supabase)
                        st.session_state.df_nuevos, st.session_state.df_existentes, st.session_state.df_duplicados_internos, st.session_state.resumen_calidad = df_nuevos, df_existentes, df_duplicados_internos, resumen_calidad
                    except Exception as e:
                        st.sidebar.error(f"Error en el análisis: {e}")
                        st.session_state.df_nuevos, st.session_state.df_existentes, st.session_state.df_duplicados_internos, st.session_state.resumen_calidad = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        if not st.session_state.df_nuevos.empty or not st.session_state.df_existentes.empty or not st.session_state.df_duplicados_internos.empty:
            st.subheader("Resultados del Análisis")
            st.success(f"**{len(st.session_state.df_nuevos)}** registros nuevos para cargar.")
            st.info(f"**{len(st.session_state.df_existentes)}** registros ya existentes en la BD.")
            if not st.session_state.df_duplicados_internos.empty:
                st.warning(f"**{len(st.session_state.df_duplicados_internos)}** filas duplicadas en el archivo (descartadas).")
                st.download_button(label="📥 Descargar Reporte de Duplicados", data=to_excel(st.session_state.df_duplicados_internos), file_name="reporte_duplicados.xlsx", use_container_width=True)
            if not st.session_state.resumen_calidad.empty:
                st.subheader("Calidad de los Datos Nuevos")
                st.dataframe(st.session_state.resumen_calidad, use_container_width=True)
            if st.button(f"2. Cargar {len(st.session_state.df_nuevos)} Registros Nuevos a la BD", type="primary", use_container_width=True):
                num_insertados = insertar_nuevos_datos(st.session_state.df_nuevos, supabase)
                if num_insertados != -1:
                    registrar_log_de_carga(supabase, num_insertados, len(st.session_state.df_existentes), len(st.session_state.df_duplicados_internos), st.session_state.resumen_calidad)
                    st.cache_data.clear()
                    st.session_state.df_nuevos, st.session_state.df_existentes, st.session_state.df_duplicados_internos, st.session_state.resumen_calidad = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
                    st.rerun()

# --- LÓGICA PRINCIPAL DEL DASHBOARD ---
@st.cache_data(ttl=300)
def cargar_datos_desde_bd():
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
        if col in df.columns: df[col] = pd.to_datetime(df[col], errors='coerce')
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

    # --- 2. AÑADIR LA NUEVA PESTAÑA A LA LISTA ---
    tabs = st.tabs([
        "🔬 Análisis General", "🚦 Asignación", "🧮 Capacidad", 
        "📊 Clasificación", "📈 Resumen", "⏱️ Tiempos", "🔮 Pronósticos",
        "📖 Glosario" # <-- NUEVA PESTAÑA
    ])
    
    # --- 3. AÑADIR LA LÓGICA PARA MOSTRAR LA NUEVA PESTAÑA ---
    with tabs[0]: analisis_general.mostrar_analisis_general(df_filtrado)
    with tabs[1]: asignacion.mostrar_asignacion(df_filtrado)
    with tabs[2]: soporte.mostrar_soporte(df_filtrado)
    with tabs[3]: clasificacion.mostrar_clasificacion(df_filtrado, num_meses)
    with tabs[4]: resumen.mostrar_resumen(df_filtrado)
    with tabs[5]: analisis_tiempos.mostrar_analisis_tiempos(df_filtrado)
    with tabs[6]: pronosticos.mostrar_pronosticos(df_operaciones)
    with tabs[7]: glosario.mostrar_glosario() # <-- NUEVA LÓGICA