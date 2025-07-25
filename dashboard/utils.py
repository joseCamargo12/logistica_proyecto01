# archivo: dashboard/utils.py (VERSIÓN FINAL Y A PRUEBA DE "UNNAMED")

import streamlit as st
import pandas as pd
from supabase import Client

def limpiar_y_preparar_dataframe(df_crudo: pd.DataFrame) -> pd.DataFrame:
    """Toma un DataFrame de un archivo y lo prepara para la base de datos."""
    df = df_crudo.copy()

    # =============================================================================
    #           AQUÍ ESTÁ LA SOLUCIÓN: ELIMINAR COLUMNAS "UNNAMED"
    # Esta línea busca todas las columnas cuyo nombre empiece con "unnamed" y las elimina.
    # Así no importa si se llama "Unnamed: 0", "Unnamed: 8", o si no aparece.
    df = df.loc[:, ~df.columns.str.contains('^unnamed')]
    # =============================================================================

    # 1. Normalizar todos los nombres de columna restantes
    df.columns = df.columns.str.strip().str.lower().str.replace('  ', ' ', regex=False).str.replace(' ', '_', regex=False).str.replace('.', '', regex=False)

    # 2. Renombrar columnas específicas del Excel a nuestro estándar de BD
    mapa_renombre = {
        'nit_cliente': 'nit_cliente',
        'fecha_file': 'fecha_file',
        'operativo': 'operativo',
        'comercial': 'comercial',
        'fch_primera_fact_prov': 'fecha_primera_factura',
        'fecha_arribo': 'fecha_arribo',
        'fecha_zarpe': 'fecha_zarpe',
        'envio_facturar': 'envio_facturar',
        'fecha_de_factura': 'fecha_de_factura',
        'fecha_envio_cierre': 'fecha_envio_cierre',
        'fecha_cierre': 'fecha_cierre',
        'estado': 'estado',
        'tipo': 'tipo',
        'cliente': 'cliente',
        'file': 'file'
    }
    df.rename(columns=mapa_renombre, inplace=True)

    # 3. Procesar y estandarizar las columnas que SÍ usaremos
    columnas_texto = ['file', 'cliente', 'operativo', 'comercial', 'estado', 'tipo', 'nit_cliente']
    for col in columnas_texto:
        if col in df.columns:
            df[col] = df[col].fillna('No especificado').astype(str).str.strip().str.upper()
        else:
            df[col] = 'No especificado'

    columnas_fecha = ['fecha_file', 'fecha_cierre', 'fecha_arribo', 'fecha_zarpe', 'fecha_de_factura', 'fecha_envio_cierre']
    for col in columnas_fecha:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        else:
            df[col] = pd.NaT

    # 4. Filtrar filas inútiles
    df.dropna(subset=['file', 'fecha_file'], inplace=True)
    df = df[df['file'] != 'NO ESPECIFICADO']

    # 5. Seleccionar solo las columnas que coinciden con nuestra tabla de Supabase
    columnas_bd = [
        'file', 'cliente', 'operativo', 'comercial', 'estado', 'fecha_file',
        'fecha_cierre', 'tipo', 'nit_cliente', 'fecha_arribo', 'fecha_zarpe',
        'fecha_de_factura', 'fecha_envio_cierre'
    ]
    df_final = df[[col for col in columnas_bd if col in df.columns]]
    
    return df_final


# La función actualizar_bd no necesita cambios, se queda igual
def actualizar_bd(df_limpio: pd.DataFrame, supabase: Client):
    """Compara un DataFrame con la BD y solo sube los registros nuevos."""
    if df_limpio.empty:
        st.warning("No hay datos válidos para subir.")
        return

    try:
        with st.spinner("Consultando registros existentes en la base de datos..."):
            response = supabase.table('operaciones').select('file').execute()
            archivos_existentes = {item['file'] for item in response.data}
        
        df_nuevos = df_limpio[~df_limpio['file'].isin(archivos_existentes)]
        
        num_nuevos = len(df_nuevos)
        if num_nuevos > 0:
            with st.spinner(f"Insertando {num_nuevos} operaciones nuevas..."):
                df_insertar = df_nuevos.astype(object).where(pd.notnull(df_nuevos), None)
                data_to_insert = df_insertar.to_dict(orient='records')
                supabase.table('operaciones').insert(data_to_insert).execute()
            st.success(f"✅ ¡Éxito! Se han añadido {num_nuevos} operaciones nuevas.")
            st.cache_data.clear()
            st.rerun()
        else:
            st.info("ℹ️ No se encontraron operaciones nuevas. La base de datos ya está actualizada.")
        
    except Exception as e:
        st.error(f"❌ Error al actualizar la base de datos: {e}")