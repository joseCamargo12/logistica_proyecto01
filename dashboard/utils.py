# ================================================
# ARCHIVO: dashboard/utils.py (VERSIÓN CON ANÁLISIS DE CALIDAD)
# ================================================
import streamlit as st
import pandas as pd
from supabase import Client
import io
import numpy as np
import re

def procesar_y_validar_dataframe(df_crudo: pd.DataFrame):
    """
    Toma un DataFrame en bruto y lo divide en:
    1. df_limpio: Datos únicos listos para la BD.
    2. df_duplicados: Un informe de todas las filas con 'file' duplicado.
    3. resumen_calidad: Un análisis de los datos faltantes en el df_limpio.
    """
    df = df_crudo.copy()

    # --- PASO 1: LIMPIEZA Y NORMALIZACIÓN DE NOMBRES ---
    df = df.loc[:, ~df.columns.str.contains('^Unnamed', case=False, na=False)]
    
    def normalize_column_name(name):
        name = str(name)
        name = pd.Series([name]).str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').iloc[0]
        name = re.sub(r'[^a-z0-9_]', ' ', name.lower())
        name = re.sub(r'\s+', '_', name)
        name = name.strip('_')
        return name

    df.columns = [normalize_column_name(col) for col in df.columns]
    
    mapa_post_normalizacion = {'fch_primera_fact_prov': 'fecha_primera_factura'}
    df.rename(columns=mapa_post_normalizacion, inplace=True)

    # --- PASO 2: PROCESAR TEXTO Y RELLENAR DATOS FALTANTES ---
    columnas_texto = [
        'file', 'nit_cliente', 'cliente', 'tipo', 'operativo',
        'comercial', 'envio_facturar', 'estado'
    ]
    for col in columnas_texto:
        if col not in df.columns: df[col] = 'NO ESPECIFICADO'
        else:
            df[col] = df[col].fillna('NO ESPECIFICADO').astype(str).str.strip().str.upper()
            df[col] = df[col].replace(['', 'NAN', 'NONE'], 'NO ESPECIFICADO')

    # --- PASO 3: SEPARAR DATOS LIMPIOS DE DUPLICADOS ---
    # Marcar todas las filas que son parte de un conjunto de duplicados
    es_duplicado = df.duplicated(subset=['file'], keep=False)
    
    # Crear el informe de duplicados (contiene todas las instancias de un 'file' repetido)
    df_duplicados = df[es_duplicado].sort_values('file')

    # Crear el conjunto de datos limpio (se queda con la primera aparición de cada 'file')
    df_limpio = df.drop_duplicates(subset=['file'], keep='first')
    
    # Eliminar del set limpio las filas sin un 'file' válido
    df_limpio = df_limpio[df_limpio['file'] != 'NO ESPECIFICADO']

    # --- PASO 4: ANÁLISIS DE CALIDAD SOBRE LOS DATOS LIMPIOS ---
    resumen_calidad = []
    total_registros = len(df_limpio)
    if total_registros > 0:
        columnas_a_revisar = ['operativo', 'comercial', 'estado']
        for col in columnas_a_revisar:
            faltantes = df_limpio[df_limpio[col] == 'NO ESPECIFICADO'].shape[0]
            porcentaje = (faltantes / total_registros) * 100 if total_registros > 0 else 0
            resumen_calidad.append({
                "Campo": col.replace('_', ' ').title(),
                "Registros Faltantes": faltantes,
                "Porcentaje (%)": f"{porcentaje:.1f}%"
            })
    
    # --- PASO 5: PROCESAR FECHAS Y SELECCIONAR COLUMNAS FINALES EN EL DF LIMPIO ---
    columnas_fecha = [
        'fecha_file', 'fecha_cierre', 'fecha_primera_factura', 'fecha_arribo',
        'fecha_zarpe', 'fecha_de_factura', 'fecha_envio_cierre'
    ]
    for col in columnas_fecha:
        if col in df_limpio.columns:
            df_limpio[col] = pd.to_datetime(df_limpio[col], errors='coerce')
            
    columnas_bd_final = [
        'file', 'nit_cliente', 'cliente', 'fecha_file', 'tipo', 'operativo',
        'comercial', 'fecha_primera_factura', 'fecha_arribo', 'fecha_zarpe',
        'envio_facturar', 'fecha_de_factura', 'fecha_envio_cierre',
        'fecha_cierre', 'estado'
    ]
    columnas_a_mantener = [col for col in columnas_bd_final if col in df_limpio.columns]
    df_limpio = df_limpio[columnas_a_mantener]

    return df_limpio, df_duplicados, pd.DataFrame(resumen_calidad)

def actualizar_bd_con_nuevos_datos(df_limpio: pd.DataFrame, supabase: Client) -> int:
    # Esta función ya no necesita cambios, funcionará con el df_limpio
    if df_limpio.empty:
        st.warning("No hay datos limpios para subir.")
        return 0
    try:
        with st.spinner("Consultando registros existentes en la base de datos..."):
            response = supabase.table('operaciones').select('file', count='exact').execute()
            archivos_existentes = {item['file'] for item in response.data}
        
        df_nuevos = df_limpio[~df_limpio['file'].isin(archivos_existentes)]
        num_nuevos = len(df_nuevos)
        
        if num_nuevos > 0:
            with st.spinner(f"Preparando e insertando {num_nuevos} operaciones nuevas..."):
                df_insertar = df_nuevos.copy()
                columnas_fecha = ['fecha_file', 'fecha_cierre', 'fecha_primera_factura', 'fecha_arribo', 'fecha_zarpe', 'fecha_de_factura', 'fecha_envio_cierre']
                for col in columnas_fecha:
                    if col in df_insertar.columns:
                        df_insertar[col] = df_insertar[col].apply(lambda x: x.isoformat() if pd.notna(x) else None)
                df_insertar = df_insertar.replace({np.nan: None})
                data_to_insert = df_insertar.to_dict(orient='records')
                supabase.table('operaciones').insert(data_to_insert).execute()
            st.success(f"✅ ¡Éxito! Se han añadido {num_nuevos} operaciones nuevas a la base de datos.")
        else:
            st.info("ℹ️ No se encontraron operaciones nuevas. La base de datos ya está actualizada.")
        return num_nuevos
        
    except Exception as e:
        st.error(f"❌ Error al actualizar la base de datos: {e}")
        return -1

@st.cache_data
def to_excel(df: pd.DataFrame):
    # Sin cambios
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Datos')
        worksheet = writer.sheets['Datos']
        for idx, col in enumerate(df):
            series = df[col]
            if not series.empty:
                max_len = max((series.astype(str).map(len).max(), len(str(series.name)))) + 1
                worksheet.set_column(idx, idx, max_len)
    return output.getvalue()