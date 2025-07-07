import pandas as pd
import os

# Cargar resumen
df = pd.read_csv('output/resumen_operaciones.csv')

# Diccionario de operaciones ideales por tipo (estimación mensual)
meta_por_tipo = {
    'A': 15,
    'M': 10,
    'F': 8,
    'B': 8,
    'S': 10,
    'T': 12,
    'C': 5,
}

# Calcular promedio mensual (total / 12)
df['promedio_mensual'] = df['total_operaciones'] / 12

# Obtener el promedio ideal según tipo
df['promedio_ideal'] = df['tipo'].map(meta_por_tipo)

# Calcular índice de flujo (%)
df['indice_flujo'] = (df['promedio_mensual'] / df['promedio_ideal']) * 100

# Clasificación según índice
def clasificar(indice):
    if pd.isna(indice):
        return 'SIN META'
    elif indice >= 100:
        return 'ALTO'
    elif indice >= 70:
        return 'MEDIO'
    else:
        return 'BAJO'

df['clasificacion'] = df['indice_flujo'].apply(clasificar)

# Guardar archivo
salida = 'output/clasificacion_flujo.csv'
df.to_csv(salida, index=False)

print(f"✅ Clasificación de flujo generada: {salida}")
print(df.head(10))


