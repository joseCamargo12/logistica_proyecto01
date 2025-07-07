# --- START OF FILE components/soporte.py ---

import streamlit as st
import pandas as pd
import io

@st.cache_data
def to_excel(df: pd.DataFrame):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='SoporteCarga')
        writer.sheets['SoporteCarga'].autofit()
    processed_data = output.getvalue()
    return processed_data

def calcular_soporte(df):
    if df.empty:
        return pd.DataFrame()
    PROMEDIO_IDEAL = {'A': 15, 'M': 10, 'F': 8, 'B': 8, 'S': 10, 'T': 12, 'C': 5}
    df_copy = df.copy()
    df_copy['estado_map'] = df_copy['estado'].apply(lambda x: 'CERRADA' if x == 'Cerrado' else 'ABIERTA')
    df_soporte = pd.crosstab(index=[df_copy['operativo'], df_copy['tipo']], columns=df_copy['estado_map'], values=df_copy['file'], aggfunc='count').fillna(0).astype(int)
    if 'ABIERTA' not in df_soporte.columns: df_soporte['ABIERTA'] = 0
    if 'CERRADA' not in df_soporte.columns: df_soporte['CERRADA'] = 0
    df_soporte = df_soporte.reset_index()
    df_soporte['capacidad_ideal_mensual'] = df_soporte['tipo'].map(PROMEDIO_IDEAL).fillna(0)
    df_soporte['cargas_posibles_adicionales'] = df_soporte['capacidad_ideal_mensual'] - df_soporte['ABIERTA']
    df_soporte['cargas_posibles_adicionales'] = df_soporte['cargas_posibles_adicionales'].clip(lower=0)
    return df_soporte

def mostrar_soporte(df_filtrado):
    st.subheader("🧮 Soporte de Carga Máxima por Operativo")
    df_calculado = calcular_soporte(df_filtrado)
    
    if df_calculado.empty:
        st.warning("No hay datos para mostrar con los filtros seleccionados.")
        return

    st.dataframe(df_calculado[['operativo', 'tipo', 'ABIERTA', 'CERRADA', 'cargas_posibles_adicionales']], use_container_width=True)

    if not df_calculado.empty:
        datos_excel = to_excel(df_calculado)
        st.download_button(
            label="📥 Descargar Soporte en Excel",
            data=datos_excel,
            file_name=f"soporte_carga_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with st.expander("Ver Metodología de Soporte de Carga"):
        st.markdown("""
        Este análisis determina la capacidad restante de cada operativo.
        - **ABIERTA:** Número de operaciones actualmente en proceso.
        - **CERRADA:** Número de operaciones completadas en el período filtrado.
        - **Cargas Posibles Adicionales:** Se calcula restando las operaciones `ABIERTAS` de la `Capacidad Ideal Mensual`.
        """)