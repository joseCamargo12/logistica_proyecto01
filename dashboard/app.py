# dashboard/app.py
import streamlit as st
import pandas as pd
from supabase import create_client, Client
import streamlit_authenticator as stauth
from streamlit_lottie import st_lottie
from core.processing import analizar_archivo_cargado, insertar_nuevos_datos, registrar_log_de_carga, to_excel
import os

# --- NUEVOS IMPORTS ---
from core.database import cargar_datos_desde_bd
from core.processing import analizar_archivo_cargado, insertar_nuevos_datos, registrar_log_de_carga, to_excel
from ui.pages import filtros, resumen, clasificacion, soporte, asignacion, analisis_tiempos, analisis_general, pronosticos, glosario
from ui.styles import inyectar_estilos_compactos, load_lottie_url, inyectar_iconos_en_tabs, mostrar_footer
from config import LOGO_URL, LOTTIE_URL

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="FAM Logística | BI", page_icon=LOGO_URL, layout="wide")
st.markdown("""<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">""", unsafe_allow_html=True)

# --- CONEXIÓN Y AUTENTICACIÓN (Tu código original) ---
try:
    # Intenta leer desde st.secrets (para local o Streamlit Cloud)
    # Si falla, el bloque except se encargará de las variables de entorno.
    supabase_url = st.secrets["supabase_url"]
    supabase_key = st.secrets["supabase_key"]
    auth_admin_name = st.secrets["auth_admin_name"]
    auth_admin_password_hash = st.secrets["auth_admin_password_hash"]
    auth_user_name = st.secrets["auth_user_name"]
    auth_user_password_hash = st.secrets["auth_user_password_hash"]

except FileNotFoundError:
    # Si secrets.toml no se encuentra, lee desde las variables de entorno de Railway
    st.info("secrets.toml no encontrado. Usando variables de entorno.")
    supabase_url = os.environ.get("supabase_url")
    supabase_key = os.environ.get("supabase_key")
    auth_admin_name = os.environ.get("auth_admin_name")
    auth_admin_password_hash = os.environ.get("auth_admin_password_hash")
    auth_user_name = os.environ.get("auth_user_name")
    auth_user_password_hash = os.environ.get("auth_user_password_hash")

# --- Una vez cargadas las variables, el resto del código es el mismo ---
try:
    # Verificación de que las variables se cargaron correctamente
    if not all([supabase_url, supabase_key, auth_admin_name, auth_admin_password_hash, auth_user_name, auth_user_password_hash]):
        st.error("Error: Faltan una o más credenciales. Revisa tus secretos o variables de entorno en Railway.")
        st.stop()
        
    supabase = create_client(supabase_url, supabase_key)
    credentials = {
        "usernames": {
            "estrategia.dev": {"name": auth_admin_name, "password": auth_admin_password_hash},
            "fam.team": {"name": auth_user_name, "password": auth_user_password_hash}
        }
    }
    authenticator = stauth.Authenticate(credentials, "cookie_logistica_final", "key_logistica_final", cookie_expiry_days=30)
except Exception as e:
    st.error(f"Error fatal de inicialización: {e}")
    st.stop()

# --- LÓGICA DE LOGIN CON FEEDBACK AL USUARIO (Reemplaza tu authenticator.login() y el if) ---
# En lugar de poner el login dentro del try, lo ponemos aquí y capturamos su estado.
name, authentication_status, username = authenticator.login()

# 1. Si el usuario ha introducido datos y son INCORRECTOS
if authentication_status is False:
    st.error("❌ Usuario o contraseña incorrectos. Por favor, intente de nuevo.")
    st.stop() # Detenemos la ejecución

# 2. Si el usuario AÚN NO ha intentado iniciar sesión
elif authentication_status is None:
    st.info("👋 Por favor, ingrese su usuario y contraseña para acceder.")
    st.stop() # Detenemos la ejecución

# --- LLAMADA A ESTILOS ---
inyectar_estilos_compactos()

# --- SIDEBAR (Tu código original, con las llamadas a funciones de UI) ---
with st.sidebar:
    # --- INICIO DEL BLOQUE A REEMPLAZAR ---

    # Usaremos CSS Flexbox dentro de un solo st.markdown para tener control total
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 15px;">
            <a href="https://www.estrategiaempresarial.com" target="_blank">
                <img src="{LOGO_URL}" width="60" style="border-radius: 8px;" />
            </a>
            <div style="line-height: 1.3;">
                <span style="font-size: 18px; font-weight: 700; color: #222;">
                    Estrategia Empresarial
                </span><br>
                <span style="font-size: 16px; color: #444;">
                    te da la bienvenida <b>FAM TEAM</b>
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
    authenticator.logout("Cerrar Sesión", "sidebar")
    st.sidebar.divider()

    # Panel de Administrador (Tu código 100% original, solo con imports cambiados)
    if st.session_state.get("username") == "estrategia.dev":
        st.sidebar.markdown("""<span style="font-size:18px;"><i class="bi bi-person-gear"></i> <strong>Panel de Administrador</strong></span>""", unsafe_allow_html=True)
        with st.sidebar.expander("Opciones", expanded=True):
            st.markdown('<h2><i class="bi bi-cloud-arrow-up"></i> Actualizar Datos</h2>', unsafe_allow_html=True)
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
                st.success(f"{len(st.session_state.df_nuevos)} registros nuevos para cargar.")
                st.info(f"{len(st.session_state.df_existentes)} registros ya existentes en la BD.")
                if not st.session_state.df_duplicados_internos.empty:
                    st.warning(f"{len(st.session_state.df_duplicados_internos)} filas duplicadas en el archivo (descartadas).")
                    st.download_button(label="Descargar Reporte de Duplicados", data=to_excel(st.session_state.df_duplicados_internos), file_name="reporte_duplicados.xlsx", use_container_width=True, key="descargar_duplicados")
                if not st.session_state.resumen_calidad.empty:
                    st.subheader("Calidad de los Datos Nuevos")
                    st.dataframe(st.session_state.resumen_calidad, use_container_width=True)
                if not st.session_state.df_nuevos.empty: # Comprobación extra
                    if st.button(f"2. Cargar {len(st.session_state.df_nuevos)} Registros Nuevos a la BD", type="primary", use_container_width=True):
                        num_insertados = insertar_nuevos_datos(st.session_state.df_nuevos, supabase)
                        if num_insertados != -1:
                            registrar_log_de_carga(supabase, num_insertados, len(st.session_state.df_existentes), len(st.session_state.df_duplicados_internos), st.session_state.resumen_calidad)
                            st.cache_data.clear()
                            st.session_state.df_nuevos, st.session_state.df_existentes, st.session_state.df_duplicados_internos, st.session_state.resumen_calidad = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
                            st.rerun()

# --- LÓGICA PRINCIPAL DEL DASHBOARD (Tu código original) ---
df_operaciones = cargar_datos_desde_bd(supabase)

if df_operaciones.empty:
    lottie_animation = load_lottie_url(LOTTIE_URL)
    with st.container():
        st.write("")
        cols = st.columns([1, 1, 1])
        with cols[1]:
            if lottie_animation:
                st_lottie(lottie_animation, speed=1, height=200, key="loading")
            st.info("Cargando datos por primera vez. Esto puede tardar un momento...")
    # Tu código original tenía una lógica de st.rerun que puede ser simplificada.
    # Si la carga inicial falla o no devuelve datos, el código se detiene aquí con el warning.
    st.warning("Aún no hay datos. Sube un archivo para comenzar.")
else:
    st.markdown("""<style>.st-emotion-cache-183lzff{display:none;}</style><h1><i class="bi bi-graph-up-arrow"></i> FAM | Análisis de Operaciones</h1>""", unsafe_allow_html=True)
    st.title(" ") # Placeholder

    analisis_general.mostrar_kpis_calidad(supabase)
    df_filtrado = filtros.mostrar_filtros(df_operaciones)
    
    if not df_filtrado.empty:
        num_meses = len(df_filtrado['fecha_file'].dt.to_period('M').unique())
        num_meses = max(1, num_meses)
    else:
        st.warning("No hay datos que coincidan con los filtros seleccionados.")
        num_meses = 1

    tabs = st.tabs(["Análisis General", "Asignación", "Capacidad", "Clasificación", "Resumen", "Tiempos", "Pronósticos", "Ayuda"])
    inyectar_iconos_en_tabs()
    
    with tabs[0]: analisis_general.mostrar_analisis_general(df_filtrado)
    with tabs[1]: asignacion.mostrar_asignacion(df_filtrado)
    with tabs[2]: soporte.mostrar_soporte(df_filtrado)
    with tabs[3]: clasificacion.mostrar_clasificacion(df_filtrado, num_meses)
    with tabs[4]: resumen.mostrar_resumen(df_filtrado)
    with tabs[5]: analisis_tiempos.mostrar_analisis_tiempos(df_filtrado)
    with tabs[6]: pronosticos.mostrar_pronosticos(df_operaciones)
    with tabs[7]: glosario.mostrar_glosario_y_soporte()

    mostrar_footer(LOGO_URL)