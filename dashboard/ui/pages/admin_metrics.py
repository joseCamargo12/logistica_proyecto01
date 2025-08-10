# dashboard/ui/pages/admin_metrics.py

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime # Esta sí la necesitamos para el nombre del archivo

def mostrar_metricas_admin(metrics_instance):
    """Muestra el dashboard de métricas solo para administradores."""
    
    st.markdown('<h2><i class="bi bi-graph-up"></i> Métricas de Uso del Sistema</h2>', unsafe_allow_html=True)
    
    # Selector de período
    periodo = st.selectbox(
        "Período de análisis:",
        options=[7, 15, 30, 60, 90],
        index=2,
        format_func=lambda x: f"Últimos {x} días"
    )
    
    # Obtener métricas
    summary = metrics_instance.get_metrics_summary(days=periodo)
    
    if not summary:
        st.warning("No hay datos de métricas disponibles para este período.")
        return
    
    # KPIs principales (versión robusta con .get())
    st.subheader("📊 Resumen General")
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Sesiones Totales", summary.get('total_sessions', 0))
    col2.metric("Usuarios Únicos", summary.get('unique_users', 0))
    col3.metric("Duración Promedio", f"{summary.get('avg_duration_minutes', 0):.1f} min")
    col4.metric("Tiempo Total de Uso", f"{summary.get('total_hours', 0):.1f} hrs")
    
    st.divider()
    
    # Gráficos (sin cambios, ya eran robustos)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔄 Actividad por Usuario")
        if summary.get('sessions_by_user'):
            df_users = pd.DataFrame(list(summary['sessions_by_user'].items()), columns=['Usuario', 'Sesiones'])
            fig_users = px.bar(df_users.sort_values('Sesiones', ascending=True), x='Sesiones', y='Usuario', orientation='h', title="Número de Sesiones por Usuario")
            st.plotly_chart(fig_users, use_container_width=True)
    
    with col2:
        st.subheader("📅 Actividad Diaria")
        if summary.get('sessions_by_day'):
            df_days = pd.DataFrame(list(summary['sessions_by_day'].items()), columns=['Fecha', 'Sesiones'])
            df_days['Fecha'] = pd.to_datetime(df_days['Fecha'])
            df_days = df_days.sort_values('Fecha')
            fig_days = px.line(df_days, x='Fecha', y='Sesiones', title="Sesiones por Día", markers=True)
            st.plotly_chart(fig_days, use_container_width=True)
    
    # Tabla detallada (ahora usando la capa de abstracción)
    st.subheader("📋 Sesiones Recientes")
    df_sessions = metrics_instance.get_recent_sessions()
    
    if not df_sessions.empty:
        # Procesamiento de datos para visualización
        df_sessions['session_start'] = pd.to_datetime(df_sessions['session_start']).dt.strftime('%Y-%m-%d %H:%M')
        df_sessions['session_end'] = pd.to_datetime(df_sessions['session_end']).dt.strftime('%Y-%m-%d %H:%M')
        
        columns_to_show = ['username', 'session_start', 'session_end', 'duration_minutes']
        df_display = df_sessions[columns_to_show].rename(columns={
            'username': 'Usuario',
            'session_start': 'Inicio de Sesión',
            'session_end': 'Fin de Sesión',
            'duration_minutes': 'Duración (min)'
        })
        
        st.dataframe(df_display, use_container_width=True)
        
        # Botón de descarga
        csv = df_sessions.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar datos completos (CSV)",
            data=csv,
            file_name=f"metricas_usuarios_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No hay sesiones recientes para mostrar.")