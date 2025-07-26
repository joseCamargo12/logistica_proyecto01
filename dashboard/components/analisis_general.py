# ================================================
# ARCHIVO A MODIFICAR: dashboard/components/analisis_general.py
# ================================================
import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import Client

@st.cache_data(ttl=600)
def cargar_logs_de_carga(_supabase: Client):
    response = _supabase.table('cargas_log').select("*").order('fecha_carga', desc=True).execute()
    return pd.DataFrame(response.data)

def mostrar_kpis_calidad(supabase: Client):
    logs_df = cargar_logs_de_carga(supabase)
    if logs_df.empty:
        return

    with st.expander("🔍 **Historial y Calidad de Cargas de Datos**", expanded=False): # Agregamos expander
        st.subheader("Métricas Históricas Totales")
        total_cargados = logs_df['registros_limpios'].sum()
        total_descartados = logs_df['registros_duplicados'].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Cargas Realizadas", len(logs_df))
        col2.metric("Total de Registros Únicos en BD", f"{int(total_cargados):,}")
        col3.metric("Total de Registros Descartados", f"{int(total_descartados):,}")
        
        st.divider()
        st.subheader("Detalle de la Última Carga")
        last_log = logs_df.iloc[0]
        
        col1_last, col2_last = st.columns(2)
        col1_last.metric("Registros Nuevos en la Última Carga", last_log.get('registros_limpios', 0))
        col2_last.metric("Descartados en la Última Carga", last_log.get('registros_duplicados', 0), delta_color="inverse")
        
        calidad_df = pd.DataFrame(last_log.get('calidad_json', []))
        if not calidad_df.empty:
            st.write("**Calidad de Datos de la Última Carga:**")
            st.dataframe(calidad_df, hide_index=True)

def mostrar_analisis_general(df_filtrado):
    st.header("🔬 Análisis General y Tendencias")
    
    if df_filtrado.empty:
        st.warning("No hay datos para analizar con los filtros seleccionados."); return
    df = df_filtrado.copy()
    df.dropna(subset=['fecha_file'], inplace=True)
    if df.empty:
        st.warning("No hay datos con fechas válidas para mostrar tendencias."); return
        
    df['año_mes'] = df['fecha_file'].dt.to_period('M').astype(str)
    
    col1, col2 = st.columns(2);
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