# dashboard/core/database.py
import pandas as pd
import streamlit as st
from supabase import Client

# Tu función 'cargar_datos_desde_bd' original
@st.cache_data(ttl=300)
def cargar_datos_desde_bd(_supabase: Client): # Añadido _ para evitar error de cache
    all_data = []
    page = 0
    while True:
        response = _supabase.table('operaciones').select("*").range(page * 1000, (page + 1) * 1000 - 1).execute()
        data = response.data
        if not data: break
        all_data.extend(data)
        page += 1
    df = pd.DataFrame(all_data)
    if df.empty: return df
    columnas_fecha = ['fecha_file', 'fecha_cierre', 'fecha_primera_factura', 'fecha_arribo', 'fecha_zarpe', 'fecha_de_factura', 'fecha_envio_cierre']
    for col in columnas_fecha:
        if col in df.columns: df[col] = pd.to_datetime(df[col], errors='coerce')
    df.dropna(subset=['fecha_file'], inplace=True)
    return df