import pandas as pd
import os

archivo = 'C:/Users/Casa/proyecto_logistica/data/operaciones.xls'
salida = 'output/operaciones_limpio.csv'

if not os.path.exists(archivo):
    print(f"❌ Archivo no encontrado: {archivo}")
    exit()

df = pd.read_excel(archivo)

# Normalizar columnas
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('.', '', regex=False)

# Rellenar vacíos importantes
columnas_reemplazo = ['cliente', 'operativo', 'comercial', 'estado']
for col in columnas_reemplazo:
    if col in df.columns:
        df[col] = df[col].fillna('No especificado')

# Guardar resultado
df.to_csv(salida, index=False)
print(f"✅ Archivo limpio guardado en: {salida}")
