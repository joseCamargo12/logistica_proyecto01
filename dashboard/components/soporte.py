# archivo: dashboard/components/soporte.py

import streamlit as st
import pandas as pd
from utils import to_excel

def calcular_soporte(df):
    if df.empty:
        return pd.DataFrame()
    PROMEDIO_IDEAL = {'A': 15, 'M': 10, 'F': 8, 'B': 8, 'S': 10, 'T': 12, 'C': 5}
    df_copy = df.copy()
    
    # Manejar estado_map asegurando que la columna 'estado' exista
    if 'estado' in df_copy.columns:
        df_copy['estado_map'] = df_copy['estado'].apply(lambda x: 'CERRADA' if str(x).upper() == 'CERRADO' else 'ABIERTA')
    else:
        # Si no hay columna 'estado', asumimos que todas están abiertas
        df_copy['estado_map'] = 'ABIERTA'

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
        st.warning("No hay datos para mostrar.")
        return
    st.dataframe(df_calculado[['operativo', 'tipo', 'ABIERTA', 'CERRADA', 'cargas_posibles_adicionales']], use_container_width=True)
    if not df_calculado.empty:
        datos_excel = to_excel(df_calculado)
        st.download_button(
            label="📥 Descargar Soporte en Excel",
            data=datos_excel,
            file_name="soporte_carga.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )