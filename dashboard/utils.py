# ================================================
# ARCHIVO A MODIFICAR: dashboard/utils.py (VERSIÓN TRANSPARENTE)
# ================================================
import streamlit as st
import pandas as pd
from supabase import Client
import io
import numpy as np
import re

def analizar_archivo_cargado(df_crudo: pd.DataFrame, supabase: Client):
    """
    Función central que realiza un análisis completo y transparente. Devuelve:
    1. df_nuevos: Registros listos para ser insertados.
    2. df_existentes: Registros del archivo que ya están en la BD.
    3. df_duplicados_internos: Registros duplicados dentro del propio archivo.
    4. resumen_calidad: Análisis de datos faltantes sobre los registros nuevos.
    """
    # --- PASO 1: LIMPIEZA Y NORMALIZACIÓN INICIAL ---
    df = df_crudo.copy()
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

    columnas_texto = ['file', 'nit_cliente', 'cliente', 'tipo', 'operativo', 'comercial', 'envio_facturar', 'estado']
    for col in columnas_texto:
        if col not in df.columns: df[col] = 'NO ESPECIFICADO'
        else:
            df[col] = df[col].astype(str).fillna('NO ESPECIFICADO').str.strip().str.upper()
            df[col] = df[col].replace(['', 'NAN', 'NONE', 'NA'], 'NO ESPECIFICADO')

    # --- PASO 2: IDENTIFICAR Y SEPARAR DUPLICADOS INTERNOS ---
    df_validos = df[df['file'] != 'NO ESPECIFICADO'].copy()
    es_duplicado_interno = df_validos.duplicated(subset=['file'], keep=False)
    df_duplicados_internos = df_validos[es_duplicado_interno].sort_values('file')
    df_limpio = df_validos.drop_duplicates(subset=['file'], keep='first')

    # --- PASO 3: COMPARAR CON LA BASE DE DATOS ---
    # Cargar TODOS los 'file' existentes de la BD para una comparación justa
    all_files_db = []
    page = 0
    with st.spinner("Consultando todos los registros de la base de datos..."):
        while True:
            response = supabase.table('operaciones').select('file').range(page * 1000, (page + 1) * 1000 - 1).execute()
            data = response.data
            if not data: break
            all_files_db.extend(data)
            page += 1
    
    archivos_existentes_db = {str(item['file']).strip().upper() for item in all_files_db if item.get('file')}
    
    # Dividir df_limpio en nuevos y ya existentes
    mask_existentes = df_limpio['file'].isin(archivos_existentes_db)
    df_nuevos = df_limpio[~mask_existentes]
    df_existentes = df_limpio[mask_existentes]

    # --- PASO 4: ANÁLISIS DE CALIDAD (SOLO SOBRE LOS DATOS NUEVOS) ---
    resumen_calidad = []
    if not df_nuevos.empty:
        total_nuevos = len(df_nuevos)
        columnas_a_revisar = ['operativo', 'comercial', 'estado']
        for col in columnas_a_revisar:
            faltantes = df_nuevos[df_nuevos[col] == 'NO ESPECIFICADO'].shape[0]
            porcentaje = (faltantes / total_nuevos) * 100
            resumen_calidad.append({"Campo": col.replace('_', ' ').title(), "Registros Faltantes": faltantes, "Porcentaje (%)": f"{porcentaje:.1f}%"})
    
    # --- PASO 5: PROCESAR FECHAS Y SELECCIONAR COLUMNAS FINALES ---
    columnas_fecha = ['fecha_file', 'fecha_cierre', 'fecha_primera_factura', 'fecha_arribo', 'fecha_zarpe', 'fecha_de_factura', 'fecha_envio_cierre']
    for col in columnas_fecha:
        if col in df_nuevos.columns:
            df_nuevos[col] = pd.to_datetime(df_nuevos[col], errors='coerce')
            
    columnas_bd_final = ['file', 'nit_cliente', 'cliente', 'fecha_file', 'tipo', 'operativo', 'comercial', 'fecha_primera_factura', 'fecha_arribo', 'fecha_zarpe', 'envio_facturar', 'fecha_de_factura', 'fecha_envio_cierre', 'fecha_cierre', 'estado']
    columnas_a_mantener = [col for col in columnas_bd_final if col in df_nuevos.columns]
    df_nuevos = df_nuevos[columnas_a_mantener]

    return df_nuevos, df_existentes, df_duplicados_internos, pd.DataFrame(resumen_calidad)

def insertar_nuevos_datos(df_nuevos: pd.DataFrame, supabase: Client) -> int:
    """
    Función simplificada que solo inserta los datos que ya han sido validados como nuevos.
    """
    num_nuevos = len(df_nuevos)
    if num_nuevos == 0:
        st.info("No hay registros nuevos para insertar.")
        return 0
    try:
        with st.spinner(f"Insertando {num_nuevos} operaciones nuevas..."):
            df_insertar = df_nuevos.copy()
            columnas_fecha = ['fecha_file', 'fecha_cierre', 'fecha_primera_factura', 'fecha_arribo', 'fecha_zarpe', 'fecha_de_factura', 'fecha_envio_cierre']
            for col in columnas_fecha:
                if col in df_insertar.columns:
                    df_insertar[col] = df_insertar[col].apply(lambda x: x.isoformat() if pd.notna(x) else None)
            df_insertar = df_insertar.replace({np.nan: None})
            data_to_insert = df_insertar.to_dict(orient='records')
            supabase.table('operaciones').insert(data_to_insert).execute()
        st.success(f"✅ ¡Éxito! Se han añadido {num_nuevos} operaciones nuevas.")
        return num_nuevos
    except Exception as e:
        st.error(f"❌ Error al actualizar la base de datos: {e}")
        return -1

def registrar_log_de_carga(supabase: Client, num_nuevos: int, num_existentes: int, num_duplicados: int, resumen_calidad: pd.DataFrame):
    """Guarda un resumen de la carga en la tabla cargas_log."""
    try:
        calidad_dict = resumen_calidad.to_dict(orient='records')
        log_entry = {
            "registros_limpios": num_nuevos, # Logueamos el número correcto
            "registros_duplicados": num_duplicados + num_existentes, # Sumamos todos los descartados
            "calidad_json": calidad_dict
        }
        supabase.table('cargas_log').insert(log_entry).execute()
        return True
    except Exception as e:
        st.sidebar.error(f"Error al registrar el log de carga: {e}")
        return False

@st.cache_data
def to_excel(df: pd.DataFrame):
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