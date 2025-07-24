# --- START OF FILE app.py (VERSIÓN SÚPER SIMPLE) ---

import sys
import os
import streamlit as st # Solo necesitamos Streamlit y Pandas
import pandas as pd

# --- Ya no se necesita streamlit_authenticator ni yaml ---

# --- Configuración de la ruta (esto se mantiene igual) ---
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from components import filtros, resumen, clasificacion, soporte, asignacion, analisis_tiempos

# --- NUEVA FUNCIÓN DE CONTRASEÑA SIMPLE ---
def check_password():
    """Devuelve True si la contraseña es correcta, de lo contrario, pide la contraseña."""
    
    # Revisa si el usuario ya está "logueado" en esta sesión.
    if st.session_state.get("password_correct", False):
        return True

    # Si no, pide la contraseña.
    st.title("🔒 Acceso Protegido")
    password = st.text_input("Introduce la contraseña para continuar:", type="password")

    # Botón para verificar
    if st.button("Entrar"):
        # Compara la contraseña introducida con el secreto que guardamos
        if password == st.secrets["password"]:
            st.session_state["password_correct"] = True
            st.rerun()  # Vuelve a ejecutar el script para mostrar el dashboard
        else:
            st.error("La contraseña es incorrecta.")
    
    return False

# --- FIN DE LA NUEVA FUNCIÓN ---


# --- Ejecución principal de la App ---
# Configuración de la página
st.set_page_config(page_title="Dashboard Logística", layout="wide")

# Llama a la función de contraseña. Si no devuelve True, no se muestra nada más.
if check_password():

    # --- TODO TU CÓDIGO ORIGINAL DEL DASHBOARD VA AQUÍ ADENTRO ---
    
    st.title("📊 Dashboard Logístico - Análisis de Operaciones")

    @st.cache_data
    def cargar_y_limpiar_datos(path):
        try:
            df = pd.read_csv(path, encoding='utf-8')
            df.columns = df.columns.str.strip()
            df.rename(columns={'unnamed:_8': 'col_vacia'}, inplace=True)
            for col in ['operativo', 'tipo', 'estado', 'file']:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.strip()
            df['fecha_file'] = pd.to_datetime(df['fecha_file'], errors='coerce')
            df['operativo'].fillna("No especificado", inplace=True)
            return df
        except FileNotFoundError:
            st.error(f"Archivo NO encontrado: {path}")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Error desconocido al cargar o limpiar {path}: {e}")
            return pd.DataFrame()

    df_operaciones = cargar_y_limpiar_datos("output/operaciones_2024_2025.csv")

    if df_operaciones.empty:
        st.warning("El dataset principal no se pudo cargar. No se puede continuar.")
    else:
        df_filtrado = filtros.mostrar_filtros(df_operaciones)

        if not df_filtrado.empty:
            st.info(f"Mostrando {len(df_filtrado)} operaciones que coinciden con los filtros seleccionados.")
            df_fechas_validas = df_filtrado.dropna(subset=['fecha_file'])
            if not df_fechas_validas.empty:
                num_meses = len(pd.to_datetime(df_fechas_validas['fecha_file']).dt.to_period('M').unique())
                num_meses = 1 if num_meses == 0 else num_meses
            else:
                num_meses = 1
        else:
            st.warning("No hay datos que coincidan con los filtros seleccionados. Por favor, amplíe su selección.")
            num_meses = 1

        tabs = st.tabs([
            "🚦 **Asignación Sugerida**",
            "🧮 Capacidad de Carga",
            "📊 Clasificación de Flujo",
            "📈 Resumen de Operaciones",
            "⏱️ **Análisis de Tiempos**"
        ])

        with tabs[0]:
            asignacion.mostrar_asignacion(df_filtrado)
        with tabs[1]:
            soporte.mostrar_soporte(df_filtrado)
        with tabs[2]:
            clasificacion.mostrar_clasificacion(df_filtrado, num_meses)
        with tabs[3]:
            resumen.mostrar_resumen(df_filtrado)
        with tabs[4]:
            analisis_tiempos.mostrar_analisis_tiempos(df_filtrado)

# --- END OF FILE app.py ---