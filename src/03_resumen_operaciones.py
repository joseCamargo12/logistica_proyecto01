import pandas as pd
import os

# Cargar archivo filtrado
archivo = 'output/operaciones_2024_2025.csv'
df = pd.read_csv(archivo)

# Reemplazar espacios vacíos por 'NO ESPECIFICADO'
df['operativo'] = df['operativo'].fillna('NO ESPECIFICADO').str.strip()
df['tipo'] = df['tipo'].fillna('NO ESPECIFICADO').str.strip()

# Agrupar por operativo y tipo
resumen = df.groupby(['operativo', 'tipo']).size().reset_index(name='total_operaciones')

# Guardar archivo
salida = 'output/resumen_operaciones.csv'
resumen.to_csv(salida, index=False)

print(f"✅ Resumen generado: {salida}")
print(resumen.head(10))
