# ==========================================================
# CÓDIGO CORREGIDO Y A PRUEBA DE BALAS PARA app.py
# ==========================================================
import streamlit as st

# --- PASO 1: CONFIGURACIÓN DE PÁGINA (DEBE SER LO PRIMERO) ---
# La única excepción son los imports y las definiciones de variables simples.
logo_url = "https://res.cloudinary.com/dwqahfw5n/image/upload/v1753630828/copia-removebg-preview_yced1y.png"

st.set_page_config(
    page_title="FAM Logística | BI Dashboard",
    page_icon=logo_url, 
    layout="wide"
)

# --- PASO 2: IMPORTS DEL PROYECTO Y LIBRERÍAS ---
# Ahora que la página ya está configurada, podemos importar todo lo demás.
import pandas as pd
from supabase import create_client, Client
import streamlit_authenticator as stauth
import sys
import os
from streamlit_lottie import st_lottie
import requests

from components import filtros, resumen, clasificacion, soporte, asignacion, analisis_tiempos, analisis_general, pronosticos, glosario
from utils import analizar_archivo_cargado, insertar_nuevos_datos, registrar_log_de_carga, to_excel

# --- PASO 3: COMANDOS DE STREAMLIT ---
# Ahora sí podemos ejecutar st.markdown y cualquier otro comando.
st.markdown("""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
""", unsafe_allow_html=True)


# --- PASO 4: DEFINICIÓN DE FUNCIONES ---
# El resto de tu código (definiciones de funciones, etc.) va aquí.

def inyectar_estilos_compactos():
    """ Inyecta CSS para reducir los márgenes verticales. """
    st.markdown("""
        <style>
            /* Apunta al contenedor del título principal */
            .st-emotion-cache-183lzff {
                padding-bottom: 0rem; /* Reduce el espacio debajo del título */
            }
            /* Apunta al contenedor de las pestañas */
            .st-emotion-cache-1gulkj5 {
                padding-top: 1rem; /* Reduce el espacio encima de las pestañas */
            }
        </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def load_lottie_url(url: str):
    """ Carga una animación Lottie desde una URL. """
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def inyectar_iconos_en_tabs():
    st.markdown("""
        <style>
            button[data-baseweb="tab"] {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            button[data-baseweb="tab"]:nth-child(1)::before { font-family: "bootstrap-icons"; content: "\\f428"; } /* Análisis */
            button[data-baseweb="tab"]:nth-child(2)::before { font-family: "bootstrap-icons"; content: "\\f54d"; } /* Asignación */
            button[data-baseweb="tab"]:nth-child(3)::before { font-family: "bootstrap-icons"; content: "\\f1c8"; } /* Capacidad */
            button[data-baseweb="tab"]:nth-child(4)::before { font-family: "bootstrap-icons"; content: "\\f551"; } /* Clasificación */
            button[data-baseweb="tab"]:nth-child(5)::before { font-family: "bootstrap-icons"; content: "\\f223"; } /* Resumen */
            button[data-baseweb="tab"]:nth-child(6)::before { font-family: "bootstrap-icons"; content: "\\f28c"; } /* Tiempos */
            button[data-baseweb="tab"]:nth-child(7)::before { font-family: "bootstrap-icons"; content: "\\f1f3"; } /* Pronósticos */
            button[data-baseweb="tab"]:nth-child(8)::before { font-family: "bootstrap-icons"; content: "\\f4f6"; } /* Ayuda */
        </style>
    """, unsafe_allow_html=True)

def mostrar_footer():
    st.divider()
    
    # Creamos 3 columnas para centrar el contenido
    _, col_mid, _ = st.columns([1, 2, 1]) # Columnas vacías a los lados para centrar
    
    with col_mid:
        st.markdown(
            f"""
            <div style="text-align: center; color: gray; font-size: 0.9rem;">
                <img src="{logo_url}" width="40" style="vertical-align: middle; margin-right: 10px;">
                Desarrollado por <a href='https://estrategiaempresarial.com.co'text-decoration: none; color: #1E90FF; font-weight: bold;'>Estrategia Empresatial
            </div>
            """,
            unsafe_allow_html=True
        )

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
            "estrategia.dev": {
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

inyectar_estilos_compactos()

with st.sidebar:
    with st.container():
        col1, col2 = st.columns([1.2, 5], gap="small")

        with col1:
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; height: 60px;">
                    <a href="https://www.estrategiaempresarial.com" target="_blank">
                        <img src="{logo_url}" width="50" style="border-radius: 7px;" />
                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                """
                <div style="display: flex; flex-direction: column; justify-content: center; height: 60px; line-height: 1.2;">
                    <span style="font-size: 18px; font-weight: 700; color: #222;">
                        Estrategia Empresarial
                    </span>
                    <span style="font-size: 16px; color: #444;">
                        te da la bienvenida <b>FAM TEAM</b>
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
    
    authenticator.logout("Cerrar Sesión", "sidebar")

st.sidebar.divider()



if st.session_state.get("username") == "estrategia.dev":
    # Título con ícono desde Bootstrap Icons
    st.sidebar.markdown("""
    <span style="font-size:18px;">
        <i class="bi bi-person-gear"></i> <strong>Panel de Administrador</strong>
    </span>
    """, unsafe_allow_html=True)

    # Expander debajo
    with st.sidebar.expander("Opciones", expanded=True):
        # ... (Toda la lógica de carga de datos que ya tienes y funciona bien va aquí)
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
            st.success(f"**{len(st.session_state.df_nuevos)}** registros nuevos para cargar.")
            st.info(f"**{len(st.session_state.df_existentes)}** registros ya existentes en la BD.")
            if not st.session_state.df_duplicados_internos.empty:
                st.warning(f"**{len(st.session_state.df_duplicados_internos)}** filas duplicadas en el archivo (descartadas).")
                st.download_button( label="Descargar Reporte de Duplicados", data=to_excel(st.session_state.df_duplicados_internos), file_name="reporte_duplicados.xlsx", use_container_width=True, key="descargar_duplicados" )
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

df_operaciones = cargar_datos_desde_bd()

# CÓDIGO AVANZADO (NO RECOMENDADO PARA EL TÍTULO PRINCIPAL)
st.markdown(
    """
    <style>
        /* Oculta el título h1 por defecto que crea Streamlit */
        .st-emotion-cache-183lzff { 
            display: none;
        }
    </style>
    <h1><i class="bi bi-graph-up-arrow"></i> FAM | Análisis de Operaciones</h1>
    """,
    unsafe_allow_html=True
)
# st.title("Un título falso para que Streamlit no se queje") # A veces se necesita un placeholder

# --- Lógica de carga con animación ---
# Usamos st.session_state para cargar los datos solo una vez por sesión
if 'df_operaciones' not in st.session_state or st.session_state.df_operaciones.empty:
    # URL de una animación de Lottie (puedes buscar otras en lottiefiles.com)
    lottie_url = "https://lottie.host/89c2b271-9337-46b5-8c38-7012019b1689/VCL2goaisq.json"
    lottie_animation = load_lottie_url(lottie_url)
    
    # Creamos un contenedor centrado para la animación
    with st.container():
        st.write("") # Espacio en blanco para centrar verticalmente
        cols = st.columns([1, 1, 1])
        with cols[1]: # Columna central
            if lottie_animation:
                st_lottie(lottie_animation, speed=1, height=200, key="loading")
            st.info("Cargando datos por primera vez. Esto puede tardar un momento...")
    
    # Este es el momento en que se cargan los datos
    st.session_state.df_operaciones = cargar_datos_desde_bd()
    # Volvemos a ejecutar el script para quitar la animación y mostrar el dashboard
    st.rerun() 

# Una vez cargados, usamos los datos desde el session_state
df_operaciones = st.session_state.df_operaciones
# ==========================================================

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

    tabs = st.tabs([
        "Análisis General", "Asignación", "Capacidad",
        "Clasificación", "Resumen", "Tiempos",
        "Pronósticos", "Ayuda"
    ])
    # --- FIN DE LA MODIFICACIÓN #2 ---
    
    # --- INICIO DE LA MODIFICACIÓN #3: Llamada a la función de CSS ---
    # Esta línea aplica la magia de los iconos
    inyectar_iconos_en_tabs()
    # --- FIN DE LA MODIFICACIÓN #3 ---

    with tabs[0]: analisis_general.mostrar_analisis_general(df_filtrado)
    with tabs[1]: asignacion.mostrar_asignacion(df_filtrado)
    with tabs[2]: soporte.mostrar_soporte(df_filtrado)
    with tabs[3]: clasificacion.mostrar_clasificacion(df_filtrado, num_meses)
    with tabs[4]: resumen.mostrar_resumen(df_filtrado)
    with tabs[5]: analisis_tiempos.mostrar_analisis_tiempos(df_filtrado)
    with tabs[6]: pronosticos.mostrar_pronosticos(df_operaciones)
    with tabs[7]: glosario.mostrar_glosario_y_soporte()

    mostrar_footer()
    inyectar_estilos_compactos()