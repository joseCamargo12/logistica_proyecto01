# archivo: dashboard/components/clasificacion.py

import streamlit as st
import pandas as pd
import numpy as np
from utils import to_excel

def mostrar_clasificacion(df, numero_de_meses_analizados):
    st.subheader("📊 Clasificación de Flujo Operativo")
    st.info(f"El promedio mensual se calcula sobre un período de **{numero_de_meses_analizados}** meses.")
    if df.empty:
        st.warning("No hay datos para mostrar con los filtros seleccionados.")
        return
    PROMEDIO_IDEAL = {'A': 15, 'M': 10, 'F': 8, 'B': 8, 'S': 10, 'T': 12, 'C': 5}
    df_agrupado = df.groupby(['operativo', 'tipo'])['file'].count().reset_index()
    df_agrupado.rename(columns={'file': 'Total general'}, inplace=True)
    if df_agrupado.empty:
        st.info("No hay datos suficientes para clasificar.")
        return
    df_agrupado['Promedio mensual'] = df_agrupado['Total general'] / numero_de_meses_analizados
    df_agrupado['Promedio ideal'] = df_agrupado['tipo'].map(PROMEDIO_IDEAL)
    df_agrupado['Índice flujo (%)'] = (df_agrupado['Promedio mensual'] / df_agrupado['Promedio ideal'].replace(0, np.nan)) * 100
    df_agrupado.fillna({'Índice flujo (%)': 0, 'Promedio ideal': 0}, inplace=True)
    def clasificar_nivel(indice):
        if pd.isna(indice) or indice < 70: return "BAJO"
        elif 70 <= indice < 100: return "MEDIO"
        else: return "ALTO"
    df_agrupado['Nivel'] = df_agrupado['Índice flujo (%)'].apply(clasificar_nivel)
    df_agrupado['Índice flujo (%)'] = df_agrupado['Índice flujo (%)'].round(2)
    columnas_ordenadas = ['operativo', 'tipo', 'Total general', 'Promedio mensual', 'Promedio ideal', 'Índice flujo (%)', 'Nivel']
    df_agrupado = df_agrupado[columnas_ordenadas] # Reordenar columnas
    df_agrupado.columns = [c.replace('_', ' ').title() for c in df_agrupado.columns]
    st.dataframe(df_agrupado, use_container_width=True)
    if not df_agrupado.empty:
        datos_excel = to_excel(df_agrupado)
        st.download_button(label="📥 Descargar Clasificación", data=datos_excel, file_name="clasificacion_flujo.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    alto = df_agrupado[df_agrupado["Nivel"] == "ALTO"].shape[0]
    medio = df_agrupado[df_agrupado["Nivel"] == "MEDIO"].shape[0]
    bajo = df_agrupado[df_agrupado["Nivel"] == "BAJO"].shape[0]
    col1, col2, col3 = st.columns(3)
    col1.metric("Clasificaciones en ALTO", alto)
    col2.metric("Clasificaciones en MEDIO", medio)
    col3.metric("Clasificaciones en BAJO", bajo)