import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils import to_excel

def mostrar_clasificacion(df, numero_de_meses_analizados):
    st.subheader("📊 Clasificación de Flujo Operativo")
    st.info(f"El promedio mensual se calcula sobre un período de **{numero_de_meses_analizados}** meses.")
    if df.empty:
        st.warning("No hay datos para mostrar."); return
        
    PROMEDIO_IDEAL = {'A': 15, 'M': 10, 'F': 8, 'B': 8, 'S': 10, 'T': 12, 'C': 5}
    df_agrupado = df.groupby(['operativo', 'tipo'])['file'].count().reset_index()
    df_agrupado.rename(columns={'file': 'Total general'}, inplace=True)
    
    if df_agrupado.empty:
        st.info("No hay datos suficientes para clasificar."); return

    df_agrupado['Promedio mensual'] = df_agrupado['Total general'] / numero_de_meses_analizados
    df_agrupado['Promedio ideal'] = df_agrupado['tipo'].map(PROMEDIO_IDEAL)
    df_agrupado['Índice flujo (%)'] = (df_agrupado['Promedio mensual'] / df_agrupado['Promedio ideal'].replace(0, np.nan)) * 100
    df_agrupado.fillna({'Índice flujo (%)': 0, 'Promedio ideal': 0}, inplace=True)
    
    def clasificar_nivel(indice):
        if pd.isna(indice) or indice < 70: return "BAJO"
        elif 70 <= indice < 100: return "MEDIO"
        else: return "ALTO"
    df_agrupado['Nivel'] = df_agrupado['Índice flujo (%)'].apply(clasificar_nivel)

    st.dataframe(df_agrupado, use_container_width=True)
    
    alto = df_agrupado[df_agrupado["Nivel"] == "ALTO"].shape[0]
    medio = df_agrupado[df_agrupado["Nivel"] == "MEDIO"].shape[0]
    bajo = df_agrupado[df_agrupado["Nivel"] == "BAJO"].shape[0]

    # --- GRÁFICO Y MÉTRICAS JUNTOS ---
    st.divider()
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Resumen de Niveles")
        st.metric("Clasificaciones en ALTO", alto)
        st.metric("Clasificaciones en MEDIO", medio)
        st.metric("Clasificaciones en BAJO", bajo)
    
    with col2:
        st.subheader("Distribución de Niveles de Rendimiento")
        df_pie = pd.DataFrame({
            'Nivel': ['ALTO', 'MEDIO', 'BAJO'],
            'Cantidad': [alto, medio, bajo]
        })
        fig = px.pie(
            df_pie,
            names='Nivel',
            values='Cantidad',
            title='Proporción General de Rendimiento',
            hole=0.4,
            color_discrete_map={'ALTO': 'green', 'MEDIO': 'orange', 'BAJO': 'red'}
        )
        st.plotly_chart(fig, use_container_width=True)
