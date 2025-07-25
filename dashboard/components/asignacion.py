# archivo: dashboard/components/asignacion.py

import streamlit as st
import pandas as pd
from .soporte import calcular_soporte
from .analisis_tiempos import calcular_duracion_real
from utils import to_excel

def mostrar_asignacion(df_filtrado):
    st.subheader("🚦 Guía Inteligente para Asignación de Nuevas Cargas")
    if df_filtrado.empty:
        st.warning("No hay datos para generar una guía de asignación.")
        return
    df_soporte = calcular_soporte(df_filtrado)
    df_duracion = calcular_duracion_real(df_filtrado)
    if df_soporte.empty:
        st.info("No hay datos para calcular la asignación.")
        return
    if not df_duracion.empty:
        df_velocidad = df_duracion.groupby(['operativo', 'tipo'])['duracion_real_dias'].mean().reset_index()
        df_velocidad.rename(columns={'duracion_real_dias': 'velocidad_promedio_dias'}, inplace=True)
        df_guia = pd.merge(df_soporte, df_velocidad, on=['operativo', 'tipo'], how='left')
        promedio_por_tipo = df_guia.groupby('tipo')['velocidad_promedio_dias'].transform('mean')
        df_guia['velocidad_promedio_dias'].fillna(promedio_por_tipo, inplace=True)
        df_guia['velocidad_promedio_dias'].fillna(df_guia['velocidad_promedio_dias'].mean(), inplace=True)
    else:
        df_guia = df_soporte.copy()
        df_guia['velocidad_promedio_dias'] = 90
        st.info("No hay datos de operaciones cerradas para calcular la eficiencia.")
    df_guia['indice_asignacion'] = (df_guia['cargas_posibles_adicionales'] / (df_guia['velocidad_promedio_dias'] + 1)) * 100
    df_guia['indice_asignacion'] = df_guia['indice_asignacion'].round(2)
    st.info("Esta guía ordena a los operativos por un Índice de Asignación, que considera su disponibilidad y eficiencia. Un índice más alto sugiere una mejor opción.")
    df_guia_final = df_guia[df_guia['cargas_posibles_adicionales'] > 0].copy()
    if df_guia_final.empty:
        st.warning("Todos los operativos han alcanzado su capacidad ideal.")
        return
    df_guia_final.sort_values(by=['tipo', 'indice_asignacion'], ascending=[True, False], inplace=True)
    df_guia_final.rename(columns={'tipo': 'Tipo', 'operativo': 'Operativo', 'cargas_posibles_adicionales': 'Capacidad Disponible', 'velocidad_promedio_dias': 'Velocidad Promedio (días)', 'indice_asignacion': 'Índice de Asignación'}, inplace=True)
    columnas_a_mostrar = ['Tipo', 'Operativo', 'Capacidad Disponible', 'Velocidad Promedio (días)', 'Índice de Asignación']
    st.dataframe(df_guia_final[columnas_a_mostrar], column_config={"Velocidad Promedio (días)": st.column_config.NumberColumn(format="%.1f días"), "Índice de Asignación": st.column_config.ProgressColumn("Puntuación (más es mejor)", format="%.2f", min_value=0, max_value=df_guia_final['Índice de Asignación'].max() if not df_guia_final.empty else 1)}, use_container_width=True)
    if not df_guia_final.empty:
        datos_excel = to_excel(df_guia_final[columnas_a_mostrar])
        st.download_button(label="📥 Descargar Guía de Asignación", data=datos_excel, file_name="guia_asignacion.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")