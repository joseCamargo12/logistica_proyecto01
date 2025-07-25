# archivo: dashboard/utils.py (VERSIÓN FINAL, A PRUEBA DE DATOS EN BRUTO)

import streamlit as st
import pandas as pd
from supabase import Client
import io
import numpy as np # Importamos numpy para manejar valores nulos

def limpiar_y_preparar_dataframe(df_crudo: pd.DataFrame) -> pd.DataFrame:
    """
    Toma un DataFrame de un archivo en bruto, lo limpia a fondo, y lo prepara para la base de datos.
    """
    df = df_crudo.copy()

    # --- PASO 1: LIMPIEZA INICIAL ---
    # Eliminar columnas fantasma 'Unnamed'
    df = df.loc[:, ~df.columns.str.contains('^unnamed')]
    # Normalizar todos los nombres de columna: quitar acentos, espacios, a minúsculas
    df.columns = df.columns.str.strip().str.lower()
    df.columns = df.columns.str.replace(' ', '_', regex=False).str.replace('.', '', regex=False)
    df.columns = df.columns.str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

    # --- PASO 2: RENOMBRAR COLUMNAS CONOCIDAS ---
    # Mapeo de nombres comunes en el Excel a nuestro estándar de base de datos
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

    # --- PASO 3: PROCESAR FECHAS (MANEJANDO ERRORES Y FECHAS NULAS) ---
    columnas_fecha = ['fecha_file', 'fecha_cierre', 'fecha_arribo', 'fecha_zarpe', 'fecha_de_factura', 'fecha_envio_cierre']
    for col in columnas_fecha:
        if col in df.columns:
            # Convertir a datetime, los errores se vuelven NaT (Not a Time)
            df[col] = pd.to_datetime(df[col], errors='coerce')
            # Reemplazar fechas absurdas (como 1900) con NaT
            df[col] = df[col].apply(lambda x: pd.NaT if x and x.year < 1990 else x)

    # --- PASO 4: PROCESAR TEXTO Y OTRAS COLUMNAS ---
    columnas_texto = ['file', 'cliente', 'operativo', 'comercial', 'estado', 'tipo', 'nit_cliente']
    for col in columnas_texto:
        if col in df.columns:
            # Rellenar nulos, convertir a texto, quitar espacios y a mayúsculas
            df[col] = df[col].fillna('No especificado').astype(str).str.strip().str.upper()
        else: # Si una columna no existe, la crea vacía
            df[col] = 'NO ESPECIFICADO'

    # --- PASO 5: FILTRADO FINAL Y SELECCIÓN DE COLUMNAS ---
    # Eliminar filas que no tienen un identificador 'file' o una 'fecha_file' válida
    df.dropna(subset=['file', 'fecha_file'], inplace=True)
    df = df[df['file'] != 'NO ESPECIFICADO']

    # Seleccionar solo las columnas que coinciden con nuestra tabla de Supabase para evitar errores
    columnas_bd = [
        'file', 'cliente', 'operativo', 'comercial', 'estado', 'fecha_file',
        'fecha_cierre', 'tipo', 'nit_cliente', 'fecha_arribo', 'fecha_zarpe',
        'fecha_de_factura', 'fecha_envio_cierre'
    ]
    # Nos aseguramos de que solo pasamos las columnas que existen tanto en el DF como en la lista de la BD
    columnas_a_mantener = [col for col in columnas_bd if col in df.columns]
    df_final = df[columnas_a_mantener]
    
    return df_final

# ====================================================================================
# LAS FUNCIONES 'actualizar_bd_con_nuevos_datos' Y 'to_excel' SE QUEDAN IGUAL.
# NO ES NECESARIO CAMBIARLAS. LAS INCLUYO PARA QUE TENGAS EL ARCHIVO COMPLETO.
# ====================================================================================

def actualizar_bd_con_nuevos_datos(df_limpio: pd.DataFrame, supabase: Client) -> int:
    if df_limpio.empty:
        st.warning("El archivo no contiene datos nuevos o válidos para subir.")
        return 0
    try:
        with st.spinner("Consultando registros existentes en la base de datos..."):
            response = supabase.table('operaciones').select('file', count='exact').execute()
            archivos_existentes = {item['file'] for item in response.data}
        
        df_nuevos = df_limpio[~df_limpio['file'].isin(archivos_existentes)]
        num_nuevos = len(df_nuevos)
        
        if num_nuevos > 0:
            with st.spinner(f"Insertando {num_nuevos} operaciones nuevas..."):
                # Reemplazar NaT de pandas con None, que es el NULL de SQL
                df_insertar = df_nuevos.replace({pd.NaT: None})
                data_to_insert = df_insertar.to_dict(orient='records')
                supabase.table('operaciones').insert(data_to_insert).execute()
            st.success(f"✅ ¡Éxito! Se han añadido {num_nuevos} operaciones nuevas.")
        else:
            st.info("ℹ️ No se encontraron operaciones nuevas. La base de datos ya está actualizada con los datos de este archivo.")
        return num_nuevos
        
    except Exception as e:
        st.error(f"❌ Error al actualizar la base de datos: {e}")
        return -1

@st.cache_data
def to_excel(df: pd.DataFrame):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Datos')
        worksheet = writer.sheets['Datos']
        for idx, col in enumerate(df):
            series = df[col]
            max_len = max((series.astype(str).map(len).max(), len(str(series.name)))) + 1
            worksheet.set_column(idx, idx, max_len)
    return output.getvalue()