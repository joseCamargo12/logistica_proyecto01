# ================================================
# ARCHIVO A MODIFICAR: dashboard/components/filtros.py (CORREGIDO)
# ================================================
import streamlit as st
import pandas as pd
import locale

# Configuración del idioma para nombres de meses en español
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'es')
    except locale.Error:
        st.sidebar.warning("No se pudo configurar el idioma a español para los meses.")

def mostrar_filtros(df):
    with st.sidebar:
        st.header("🔍 Filtros Globales")

        # --- Filtro de Año ---
        st.subheader("🗓️ Período")
        all_years = sorted(df['fecha_file'].dt.year.unique())
        select_all_years = st.checkbox("Seleccionar todos los años", value=True)
        if select_all_years:
            selected_years = st.multiselect("Año(s)", all_years, default=all_years, key="years_multi")
        else:
            selected_years = st.multiselect("Año(s)", all_years, default=all_years[-1:] if all_years else [], key="years_multi_single")

        # --- Filtro de Mes (Corregido) ---
        df_meses_disponibles = df[df['fecha_file'].dt.year.isin(selected_years)]
        if not df_meses_disponibles.empty:
            # Crear una columna 'año_mes_num' para ordenar correctamente
            df_meses_disponibles['año_mes_num'] = df_meses_disponibles['fecha_file'].dt.strftime('%Y-%m')
            # Crear la columna de display para el usuario
            df_meses_disponibles['display_month'] = df_meses_disponibles['fecha_file'].dt.strftime('%B %Y').str.capitalize()
            
            # Ordenar las opciones de mes cronológicamente
            mes_options = df_meses_disponibles.sort_values('año_mes_num')['display_month'].unique()
            
            select_all_months = st.checkbox("Seleccionar todos los meses", value=True)
            if select_all_months:
                meses_seleccionados_display = st.multiselect("Mes(es)", mes_options, default=list(mes_options))
            else:
                meses_seleccionados_display = st.multiselect("Mes(es)", mes_options, default=[])

        st.divider()

        # --- Filtros de Categorías (se mantienen) ---
        st.subheader("🗂️ Categorías")
        
        tipo_options = sorted(df['tipo'].unique())
        tipo = st.multiselect("Tipo de operación", tipo_options, default=tipo_options)

        operativo_options = sorted(df['operativo'].unique())
        operativo = st.multiselect("Operativo", operativo_options, default=operativo_options)

        # --- APLICACIÓN DE FILTROS ---
        df_filtrado = df.copy()

        if not selected_years:
            return pd.DataFrame() # No mostrar nada si no hay año seleccionado
        df_filtrado = df_filtrado[df_filtrado['fecha_file'].dt.year.isin(selected_years)]
        
        if 'meses_seleccionados_display' in locals() and meses_seleccionados_display:
            df_filtrado['display_month'] = df_filtrado['fecha_file'].dt.strftime('%B %Y').str.capitalize()
            df_filtrado = df_filtrado[df_filtrado['display_month'].isin(meses_seleccionados_display)]
        elif 'meses_seleccionados_display' in locals() and not meses_seleccionados_display and not select_all_months:
            return pd.DataFrame() # No mostrar nada si se deseleccionan todos los meses
            
        if tipo:
            df_filtrado = df_filtrado[df_filtrado['tipo'].isin(tipo)]
        else:
            return pd.DataFrame() # No mostrar nada si no hay tipo seleccionado
            
        if operativo:
            df_filtrado = df_filtrado[df_filtrado['operativo'].isin(operativo)]
        else:
            return pd.DataFrame() # No mostrar nada si no hay operativo seleccionado

        return df_filtrado