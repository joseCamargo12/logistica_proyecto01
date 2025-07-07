# --- START OF FILE components/filtros.py ---

import streamlit as st
import pandas as pd
import locale # <-- Nueva importación para el idioma

# Configurar el locale a español para que los nombres de los meses salgan correctamente
# Esto puede variar un poco entre sistemas operativos. 'es_ES' o 'es_ES.UTF-8' son comunes.
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'es')
    except locale.Error:
        st.sidebar.warning("No se pudo configurar el idioma a español para los meses.")


def mostrar_filtros(df):
    with st.sidebar:
        st.header("🔍 Filtros globales")

        # --- Filtro de Año ---
        all_years = sorted(df['fecha_file'].dt.year.dropna().astype(int).unique())
        select_all_years = st.checkbox("Seleccionar todos los años", value=True, key="cb_years")
        default_years = all_years if select_all_years else []
        year_range = st.multiselect(
            "Año de operación", 
            options=all_years, 
            default=default_years
        )
        
        st.markdown("---")

        # --- Filtro de Mes ---
        df_meses_disponibles = df[df['fecha_file'].dt.year.isin(year_range)]
        if not df_meses_disponibles.empty:
            df_meses_disponibles_copy = df_meses_disponibles.copy()
            df_meses_disponibles_copy['display_month'] = df_meses_disponibles_copy['fecha_file'].dt.strftime('%Y-%m %B').str.capitalize()
            mes_options = sorted(df_meses_disponibles_copy['display_month'].unique())
            
            select_all_months = st.checkbox("Seleccionar todos los meses", value=True, key="cb_months")
            default_months = mes_options if select_all_months else []
            meses_seleccionados_display = st.multiselect(
                "Seleccionar Mes(es)",
                options=mes_options,
                default=default_months,
                help="Puedes desmarcar 'Seleccionar todos' para elegir meses específicos."
            )
        else:
            meses_seleccionados_display = []

        st.markdown("---")
        
        # --- Filtro de Tipo de Operación ---
        tipo_options = sorted(df['tipo'].unique())
        select_all_tipos = st.checkbox("Seleccionar todos los tipos", value=True, key="cb_tipos")
        default_tipos = tipo_options if select_all_tipos else []
        tipo = st.multiselect(
            "Tipo de operación", 
            options=tipo_options, 
            default=default_tipos
        )

        st.markdown("---")

        # --- Filtro de Operativo ---
        operativo_options = sorted(df['operativo'].unique())
        select_all_operativos = st.checkbox("Seleccionar todos los operativos", value=True, key="cb_operativos")
        default_operativos = operativo_options if select_all_operativos else []
        operativo = st.multiselect(
            "Operativo", 
            options=operativo_options, 
            default=default_operativos
        )

        # --- APLICACIÓN DE FILTROS ---
        df_filtrado = df.copy()

        if not year_range:
            return pd.DataFrame()
        df_filtrado = df_filtrado[df_filtrado['fecha_file'].dt.year.isin(year_range)]
        
        if meses_seleccionados_display:
            df_filtrado['display_month'] = df_filtrado['fecha_file'].dt.strftime('%Y-%m %B').str.capitalize()
            df_filtrado = df_filtrado[df_filtrado['display_month'].isin(meses_seleccionados_display)]

        if tipo:
            df_filtrado = df_filtrado[df_filtrado['tipo'].isin(tipo)]
        else:
             return pd.DataFrame()
            
        if operativo:
            df_filtrado = df_filtrado[df_filtrado['operativo'].isin(operativo)]
        else:
            return pd.DataFrame()

        return df_filtrado