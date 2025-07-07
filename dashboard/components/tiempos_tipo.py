# --- START OF FILE components/analisis_tiempos.py ---
# (Recuerda renombrar el archivo y cambiar el import en app.py)

import streamlit as st
import pandas as pd

def mostrar_analisis_tiempos(df_filtrado):
    st.subheader("⏱️ Análisis de Tiempos de Ciclo por Operación")

    if df_filtrado.empty:
        st.warning("No hay datos para calcular los tiempos.")
        return

    # --- DATOS DE REFERENCIA (TUS ESTÁNDARES) ---
    referencia_data = {
        "Tipo": ["A", "M", "F", "B", "S", "T", "C"],
        "Medio": ["Aéreo", "Marítimo", "Interflow", "Bertschi", "Shanghai Supreme", "Terrestre", "Aduana"],
        "Tiempo Estándar (días)": [30, 90, 90, 90, 90, 30, 30],
        "Meta de Mejora (días)": [20, 70, 70, 70, 70, 15, 15] # Tu "Propuesta ING"
    }
    df_referencia = pd.DataFrame(referencia_data)

    # --- CÁLCULO DINÁMICO DESDE LOS DATOS ---
    # 1. Asegurarse que las columnas de fecha son datetime
    df_calculo = df_filtrado.copy()
    df_calculo['fecha_cierre'] = pd.to_datetime(df_calculo['fecha_cierre'], errors='coerce')
    df_calculo['fecha_file'] = pd.to_datetime(df_calculo['fecha_file'], errors='coerce')

    # 2. Calcular la duración solo para filas con fechas válidas
    df_calculo.dropna(subset=['fecha_file', 'fecha_cierre'], inplace=True)
    df_calculo['Duración Real (días)'] = (df_calculo['fecha_cierre'] - df_calculo['fecha_file']).dt.days

    # 3. Agrupar para obtener el promedio real
    df_real = df_calculo.groupby('tipo')['Duración Real (días)'].mean().reset_index()
    df_real.rename(columns={'tipo': 'Tipo', 'Duración Real (días)': 'Duración Real Promedio (días)'}, inplace=True)

    # --- UNIR TODO Y MOSTRAR ---
    df_final = pd.merge(df_referencia, df_real, on="Tipo", how="left")
    df_final['Duración Real Promedio (días)'] = df_final['Duración Real Promedio (días)'].round(1).fillna("N/A")

    st.dataframe(df_final, use_container_width=True)

    st.markdown("Esta tabla compara el **Tiempo Estándar** y la **Meta de Mejora** con la **Duración Real Promedio** calculada a partir de los datos filtrados.")

    # EXTRA: Añadir un gráfico de barras para visualizar la diferencia
    st.write("#### Comparación Visual: Meta vs. Realidad")
    df_chart = df_final.copy()
    df_chart = df_chart[df_chart['Duración Real Promedio (días)'] != "N/A"] # Quitar los N/A para graficar
    df_chart.set_index('Medio', inplace=True)
    st.bar_chart(df_chart[['Meta de Mejora (días)', 'Duración Real Promedio (días)']])