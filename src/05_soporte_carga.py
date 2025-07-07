import pandas as pd
import os
from datetime import datetime

# 1. Parámetros de capacidad
capacidad_ideal = {
    'A': 15,  # Aéreo
    'M': 10,  # Marítimo
    'F': 8,   # Interflow
    'B': 8,   # Bertschi
    'S': 10,  # Shanghai
    'T': 12,  # Terrestre
    'C': 5    # Aduana
}

tiempos_estimados = {
    'A': 30,
    'M': 90,
    'F': 90,
    'B': 90,
    'S': 90,
    'T': 30,
    'C': 30
}

# 2. Leer archivo
archivo = 'output/operaciones_2024_2025.csv'
df = pd.read_csv(archivo)

# 3. Normaliza fechas
df['fecha_file'] = pd.to_datetime(df['fecha_file'], errors='coerce')
df['fecha_cierre'] = pd.to_datetime(df['fecha_cierre'], errors='coerce')

# 4. Limpieza básica
df['operativo'] = df['operativo'].fillna('NO ESPECIFICADO').str.strip().str.upper()
df['tipo'] = df['tipo'].fillna('NO ESPECIFICADO').str.strip().str.upper()

# 5. Clasificar operaciones como abiertas/cerradas
df['estado_operacion'] = df['fecha_cierre'].isna().map({True: 'ABIERTA', False: 'CERRADA'})

# 6. Agrupar
resumen = df.groupby(['operativo', 'tipo', 'estado_operacion']).size().unstack(fill_value=0).reset_index()

# 7. Calcular soporte de carga
def calcular_soporte(row):
    tipo = row['tipo']
    abiertas = row.get('ABIERTA', 0)
    ideal = capacidad_ideal.get(tipo, 0)
    return max(ideal - abiertas, 0)

resumen['cargas_posibles_adicionales'] = resumen.apply(calcular_soporte, axis=1)

# 8. Guardar
os.makedirs('output', exist_ok=True)
resumen.to_csv('output/soporte_carga_operativo.csv', index=False)
print("✅ Soporte de carga guardado: output/soporte_carga_operativo.csv")
