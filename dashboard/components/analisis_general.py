# ================================================
# ARCHIVO A CREAR: dashboard/components/analisis_general.py
# ================================================
import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import Client

def mostrar_kpis_calidad(supabase: Client):
    try:
        log_response = supabase.table('cargas_log').select("*").order('fecha_carga', desc=True).limit(1).single().execute()
        last_log = log_response.data
        if last_log:
            st.subheader("Calidad de la Última Carga de Datos")
            col1, col2, col3 = st.columns([1, 1, 2])
            col1.metric("Registros Únicos Cargados", last_log.get('registros_limpios', 0))
            col2.metric("Registros Duplicados Encontrados", last_log.get('registros_duplicados', 0), delta_color="inverse")
            
            calidad_df = pd.DataFrame(last_log.get('calidad_json', []))
            if not calidad_df.empty:
                col3.write("**Campos con Datos Faltantes (%):**")
                col3.dataframe(calidad_df, hide_index=True)
    except Exception:
        pass # Si no hay logs, no muestra nada.
    st.divider()

def mostrar_analisis_general(df_filtrado):
    st.header("🔬 Análisis General y Tendencias")
    
    if df_filtrado.empty:
        st.warning("No hay datos para analizar con los filtros seleccionados.")
        return
        
    df = df_filtrado.copy()
    df.dropna(subset=['fecha_file'], inplace=True)
    if df.empty:
        st.warning("No hay datos con fechas válidas para mostrar tendencias.")
        return
        
    df['año_mes'] = df['fecha_file'].dt.to_period('M').astype(str)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Tendencia de Operaciones Mensuales")
        operaciones_por_mes = df.groupby('año_mes')['file'].count().reset_index()
        fig1 = px.line(operaciones_por_mes.sort_values('año_mes'), x='año_mes', y='file', title="Evolución del Nº de Operaciones", labels={'año_mes': 'Mes', 'file': 'Cantidad'}, markers=True)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("Distribución por Tipo de Operación")
        operaciones_por_tipo = df['tipo'].value_counts().reset_index()
        fig2 = px.pie(operaciones_por_tipo, names='tipo', values='count', title="Proporción por Tipo de Operación", hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)
        
    st.divider()
    st.subheader("Carga de Trabajo por Operativo")
    carga_por_operativo = df['operativo'].value_counts().reset_index()
    fig3 = px.bar(carga_por_operativo.sort_values('count', ascending=False).head(15), x='operativo', y='count', title="Operaciones por Operativo (Top 15)", labels={'operativo': 'Operativo', 'count': 'Cantidad'}, color='operativo')
    st.plotly_chart(fig3, use_container_width=True)