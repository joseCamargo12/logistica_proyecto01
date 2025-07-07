# --- START OF FILE components/resumen.py ---

import streamlit as st
import pandas as pd
import io  # <-- ¡NUEVA IMPORTACIÓN! Necesaria para manejar los datos en memoria.

# Función para convertir el DataFrame a un objeto de Excel en memoria
# Usamos el decorador @st.cache_data para que esta conversión no se repita innecesariamente
@st.cache_data
def to_excel(df: pd.DataFrame):
    output = io.BytesIO()
    # Usamos 'with' para asegurarnos de que el writer se cierre correctamente
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Resumen')
        # Opcional: ajustar el ancho de las columnas para que se vea bien
        writer.sheets['Resumen'].autofit()
    processed_data = output.getvalue()
    return processed_data

def mostrar_resumen(df):
    st.subheader("📈 Resumen de Operaciones por Operativo y Tipo")

    if df.empty:
        st.warning("No hay datos para mostrar con los filtros seleccionados.")
        return

    # CALCULAR EL RESUMEN EN TIEMPO REAL
    df_resumen = df.groupby(['operativo', 'tipo']).agg(
        total_operaciones=('file', 'count')
    ).reset_index()

    df_resumen.sort_values(by=['operativo', 'total_operaciones'], ascending=[True, False], inplace=True)
    
    st.dataframe(df_resumen, use_container_width=True)

    # --- INICIO DEL CÓDIGO PARA DESCARGAR ---
    if not df_resumen.empty:
        # Preparamos los datos para la descarga usando nuestra función
        datos_excel = to_excel(df_resumen)
        
        # Creamos el botón de descarga
        st.download_button(
            label="📥 Descargar Resumen en Excel",
            data=datos_excel,
            file_name=f"resumen_operaciones_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    # --- FIN DEL CÓDIGO PARA DESCARGAR ---

    # Métrica del total de operaciones
    total_operaciones = df.shape[0]
    st.metric(label="Total de operaciones (según filtros)", value=f"{total_operaciones:,}")