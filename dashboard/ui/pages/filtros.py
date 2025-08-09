# dashboard/ui/pages/filtros.py

import streamlit as st
import pandas as pd
import locale

# Esta era la línea que causaba el error. La hemos eliminado.
# from config import CAPACIDAD_IDEAL_OPERACIONES, ...

try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except:
    pass

# El resto de tu archivo de filtros se queda exactamente igual.
def mostrar_filtros(df):
    with st.sidebar:
        st.markdown('<h3><i class="bi bi-funnel-fill"></i> Filtros Globales</h3>', unsafe_allow_html=True)
        st.divider()

        with st.expander("Seleccionar Fechas", expanded=True):
            st.markdown('<h5><i class="bi bi-calendar3"></i> Período de Tiempo</h5>', unsafe_allow_html=True)

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

        with st.expander("Operaciones", expanded=True):
            st.markdown('<h5><i class="bi bi-tags-fill"></i> Categorías de Operación</h5>', unsafe_allow_html=True)

            tipo_options = sorted(df['tipo'].unique())
            tipo = st.multiselect("Tipo de operación", tipo_options, default=tipo_options)

            operativo_options = sorted(df['operativo'].unique())
            operativo = st.multiselect("Operativo", operativo_options, default=operativo_options)

    # --- APLICACIÓN DE FILTROS (SIN NINGÚN CAMBIO) ---
    df_filtrado = df.copy()

    if selected_years:
        df_filtrado = df_filtrado[df_filtrado['fecha_file'].dt.year.isin(selected_years)]
    else:
        return pd.DataFrame()

    if 'meses_seleccionados_display' in locals() and not select_all_months:
         if meses_seleccionados_display:
            df_filtrado['display_month'] = df_filtrado['fecha_file'].dt.strftime('%B %Y').str.capitalize()
            df_filtrado = df_filtrado[df_filtrado['display_month'].isin(meses_seleccionados_display)]
         else:
            return pd.DataFrame()

    if tipo:
        df_filtrado = df_filtrado[df_filtrado['tipo'].isin(tipo)]
    else:
        return pd.DataFrame()

    if operativo:
        df_filtrado = df_filtrado[df_filtrado['operativo'].isin(operativo)]
    else:
        return pd.DataFrame()

    return df_filtrado