# archivo: dashboard/components/analisis_tiempos.py

import streamlit as st
import pandas as pd
import plotly.express as px
from utils import to_excel

def calcular_duracion_real(df):
    df_calc = df.copy()
    if 'fecha_cierre' not in df_calc.columns or 'fecha_file' not in df_calc.columns:
        return pd.DataFrame()
    df_calc['fecha_cierre'] = pd.to_datetime(df_calc['fecha_cierre'], errors='coerce')
    df_calc['fecha_file'] = pd.to_datetime(df_calc['fecha_file'], errors='coerce')
    df_calc.dropna(subset=['fecha_file', 'fecha_cierre'], inplace=True)
    if df_calc.empty: return pd.DataFrame()
    df_calc['duracion_real_dias'] = (df_calc['fecha_cierre'] - df_calc['fecha_file']).dt.days
    df_calc = df_calc[df_calc['duracion_real_dias'] >= 0]
    return df_calc

def mostrar_analisis_tiempos(df_filtrado):
    st.subheader("⏱️ Análisis de Tiempos de Ciclo y Cumplimiento")
    if df_filtrado.empty:
        st.warning("No hay datos para calcular los tiempos.")
        return
    referencia_data = {"Tipo": ["A", "M", "F", "B", "S", "T", "C"], "Tiempo Estándar (días)": [30, 90, 90, 90, 90, 30, 30], "Meta de Mejora (días)": [20, 70, 70, 70, 70, 15, 15]}
    df_referencia = pd.DataFrame(referencia_data)
    df_calculo = calcular_duracion_real(df_filtrado)
    if df_calculo.empty:
        st.info("No hay operaciones cerradas con fechas válidas para analizar.")
        return
    st.markdown("#### 1. Comparativa de Tiempos: Estándar vs. Realidad")
    df_promedio_real = df_calculo.groupby('tipo')['duracion_real_dias'].mean().reset_index()
    df_promedio_real.rename(columns={'tipo': 'Tipo', 'duracion_real_dias': 'Duración Real Promedio (días)'}, inplace=True)
    df_final = pd.merge(df_referencia, df_promedio_real, on="Tipo", how="left")
    df_final['Duración Real Promedio (días)'] = df_final['Duración Real Promedio (días)'].round(1)
    st.dataframe(df_final, use_container_width=True)
    if not df_final.empty:
        st.download_button("📥 Descargar Tabla Comparativa", to_excel(df_final), "comparativa_tiempos.xlsx")
    st.markdown("#### 2. Distribución de Tiempos de Operación por Tipo")
    fig = px.box(df_calculo, x='tipo', y='duracion_real_dias', labels={'tipo': 'Tipo de Operación', 'duracion_real_dias': 'Duración (días)'})
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("#### 3. Rendimiento por Operativo")
    df_operativo_tiempos = df_calculo.groupby('operativo')['duracion_real_dias'].agg(['mean', 'count', 'min', 'max']).reset_index()
    df_operativo_tiempos.rename(columns={'mean': 'Duración Promedio', 'count': 'Nº Op. Cerradas', 'min': 'Más Rápido (días)', 'max': 'Más Lento (días)'}, inplace=True)
    df_operativo_tiempos['Duración Promedio'] = df_operativo_tiempos['Duración Promedio'].round(1)
    st.dataframe(df_operativo_tiempos.sort_values(by='Duración Promedio'), use_container_width=True)
    if not df_operativo_tiempos.empty:
        st.download_button("📥 Descargar Rendimiento por Operativo", to_excel(df_operativo_tiempos), "rendimiento_operativo.xlsx")