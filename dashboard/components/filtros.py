import streamlit as st
import pandas as pd
import locale

try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except:
    pass

st.markdown("""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
""", unsafe_allow_html=True)

def mostrar_filtros(df):
    with st.sidebar:
        st.markdown(""" <h2 style='font-size:25px;'> <i class="bi bi-funnel-fill"></i> Filtros Globales </h2> """, unsafe_allow_html=True)
        st.divider()

        # --- Filtro de Período con Expanders ---
        with st.expander("🗓️ **Período de Tiempo**", expanded=True):
            all_years = sorted(df['fecha_file'].dt.year.unique())
            select_all_years = st.checkbox("Todos los años", value=True, key="cb_years")
            default_years = all_years if select_all_years else (all_years[-1:] if all_years else [])
            selected_years = st.multiselect("Año(s)", all_years, default=default_years)

            df_meses_disponibles = df[df['fecha_file'].dt.year.isin(selected_years)]
            if not df_meses_disponibles.empty:
                df_meses_disponibles = df_meses_disponibles.copy()
                df_meses_disponibles['año_mes_num'] = df_meses_disponibles['fecha_file'].dt.strftime('%Y-%m')
                df_meses_disponibles['display_month'] = df_meses_disponibles['fecha_file'].dt.strftime('%B %Y').str.capitalize()
                mes_options = df_meses_disponibles.sort_values('año_mes_num')['display_month'].unique()
                
                select_all_months = st.checkbox("Todos los meses", value=True, key="cb_months")
                default_months = list(mes_options) if select_all_months else []
                meses_seleccionados_display = st.multiselect("Mes(es)", mes_options, default=default_months)

        # --- Filtros de Categorías con Expanders ---
        with st.expander("🗂️ **Categorías de Operación**", expanded=True):
            tipo_options = sorted(df['tipo'].unique())
            tipo = st.multiselect("Tipo de operación", tipo_options, default=tipo_options)

            operativo_options = sorted(df['operativo'].unique())
            operativo = st.multiselect("Operativo", operativo_options, default=operativo_options)

        # --- APLICACIÓN DE FILTROS ---
        df_filtrado = df[
            (df['fecha_file'].dt.year.isin(selected_years)) &
            (df['tipo'].isin(tipo)) &
            (df['operativo'].isin(operativo))
        ]
        
        if 'meses_seleccionados_display' in locals() and not select_all_months:
            df_filtrado['display_month'] = df_filtrado['fecha_file'].dt.strftime('%B %Y').str.capitalize()
            df_filtrado = df_filtrado[df_filtrado['display_month'].isin(meses_seleccionados_display)]
            
        return df_filtrado
    