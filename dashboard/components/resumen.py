import streamlit as st
import pandas as pd
from utils import to_excel

def mostrar_resumen(df):
    st.markdown('<h3><i class="bi bi-card-checklist"></i> Resumen de Operaciones por Operativo y Tipo</h3>', unsafe_allow_html=True)
    if df.empty:
        st.warning("No hay datos para mostrar.")
        return
    df_resumen = df.groupby(['operativo', 'tipo']).agg(total_operaciones=('file', 'count')).reset_index()
    df_resumen.sort_values(by=['operativo', 'total_operaciones'], ascending=[True, False], inplace=True)
    st.dataframe(df_resumen, use_container_width=True)
    if not df_resumen.empty:
        datos_excel = to_excel(df_resumen)
        st.download_button(
            label="Descargar Resumen en Excel",
            data=datos_excel,
            file_name="resumen_operaciones.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    total_operaciones = df.shape[0]
    st.metric(label="Total de operaciones (según filtros)", value=f"{total_operaciones:,}")

