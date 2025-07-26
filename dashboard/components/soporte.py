# ================================================
# ARCHIVO A MODIFICAR: dashboard/components/soporte.py
# ================================================
import streamlit as st
import pandas as pd
import plotly.express as px
from utils import to_excel

@st.cache_data
def calcular_soporte(df):
    if df.empty: return pd.DataFrame()
    PROMEDIO_IDEAL = {'A': 15, 'M': 10, 'F': 8, 'B': 8, 'S': 10, 'T': 12, 'C': 5}
    df_copy = df.copy()
    if 'estado' in df_copy.columns:
        df_copy['estado_map'] = df_copy['estado'].apply(lambda x: 'CERRADA' if str(x).upper() == 'CERRADO' else 'ABIERTA')
    else:
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
        st.warning("No hay datos para mostrar."); return

    st.dataframe(df_calculado[['operativo', 'tipo', 'ABIERTA', 'CERRADA', 'cargas_posibles_adicionales']], use_container_width=True)
    
    # --- GRÁFICO AÑADIDO ---
    st.divider()
    st.subheader("📊 Visualización de Carga por Operativo (Top 20)")
    
    # Agrupamos por operativo para tener una visión general
    df_agrupado = df_calculado.groupby('operativo').agg({
        'ABIERTA': 'sum',
        'cargas_posibles_adicionales': 'sum'
    }).reset_index()
    
    # Calculamos el total para ordenar
    df_agrupado['carga_total'] = df_agrupado['ABIERTA'] + df_agrupado['cargas_posibles_adicionales']
    df_agrupado = df_agrupado.sort_values('carga_total', ascending=False).head(20)

    fig = px.bar(
        df_agrupado,
        x='operativo',
        y=['ABIERTA', 'cargas_posibles_adicionales'],
        title='Carga Actual vs. Capacidad Disponible',
        labels={'value': 'Cantidad de Operaciones', 'operativo': 'Operativo'},
        color_discrete_map={
            'ABIERTA': '#FF6347', # Tomate
            'cargas_posibles_adicionales': '#90EE90' # Verde claro
        }
    )
    fig.update_layout(barmode='stack')
    st.plotly_chart(fig, use_container_width=True)
    st.info("Cada barra representa la capacidad total de un operativo. La sección roja son las cargas actuales y la verde es el espacio disponible para nuevas operaciones.")