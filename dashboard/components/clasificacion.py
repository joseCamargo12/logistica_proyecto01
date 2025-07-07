# --- START OF FILE components/clasificacion.py ---

import streamlit as st
import pandas as pd
import numpy as np
import io

@st.cache_data
def to_excel(df: pd.DataFrame):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Clasificacion')
        writer.sheets['Clasificacion'].autofit()
    processed_data = output.getvalue()
    return processed_data

def mostrar_clasificacion(df, numero_de_meses_analizados): 
    st.subheader("📊 Clasificación de Flujo Operativo")
    
    st.info(f"El promedio mensual se está calculando sobre un período de **{numero_de_meses_analizados}** meses, basado en las fechas de los datos filtrados.")

    if df.empty:
        st.warning("No hay datos para mostrar con los filtros seleccionados.")
        return

    PROMEDIO_IDEAL = {'A': 15, 'M': 10, 'F': 8, 'B': 8, 'S': 10, 'T': 12, 'C': 5}

    df_agrupado = df.groupby(['operativo', 'tipo'])['file'].count().reset_index()
    df_agrupado.rename(columns={'file': 'Total general'}, inplace=True)

    if df_agrupado.empty:
        st.info("No hay datos suficientes para clasificar con los filtros actuales.")
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
    df_agrupado.columns = [c.replace('_', ' ').title() for c in columnas_ordenadas]
    
    st.dataframe(df_agrupado, use_container_width=True)

    if not df_agrupado.empty:
        datos_excel = to_excel(df_agrupado)
        st.download_button(
            label="📥 Descargar Clasificación en Excel",
            data=datos_excel,
            file_name=f"clasificacion_flujo_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    alto = df_agrupado[df_agrupado["Nivel"] == "ALTO"].shape[0]
    medio = df_agrupado[df_agrupado["Nivel"] == "MEDIO"].shape[0]
    bajo = df_agrupado[df_agrupado["Nivel"] == "BAJO"].shape[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Clasificaciones en ALTO", alto)
    col2.metric("Clasificaciones en MEDIO", medio)
    col3.metric("Clasificaciones en BAJO", bajo)

    with st.expander("Ver explicación de la metodología"):
        st.markdown("""
        #### Índice de Flujo
        Se calcula con la fórmula: `Índice de Flujo = (Promedio mensual real / Promedio ideal) × 100`
        #### Clasificación del flujo (Nivel)
        - **≥ 100% - ALTO:** Rendimiento excepcional.
        - **70%–99% - MEDIO:** Rendimiento aceptable.
        - **< 70% - BAJO:** Rendimiento por debajo de las expectativas.
        """)