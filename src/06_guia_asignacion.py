import pandas as pd
import os

# Leer archivos necesarios
flujo = pd.read_csv('output/clasificacion_flujo.csv')
soporte = pd.read_csv('output/soporte_carga_operativo.csv')

# Unir por operativo y tipo
df = pd.merge(flujo, soporte, on=['operativo', 'tipo'], how='outer')

# Rellenar valores nulos
df['cargas_posibles_adicionales'] = df['cargas_posibles_adicionales'].fillna(0)
df['clasificacion'] = df['clasificacion'].fillna('NO CLASIFICADO')

# Filtrar los operativos que pueden recibir más cargas
df_filtrado = df[
    (df['cargas_posibles_adicionales'] > 0) &
    (df['clasificacion'].isin(['BAJO', 'MEDIO']))
].copy()

# Ordenar por tipo y mayor soporte
df_filtrado = df_filtrado.sort_values(by=['tipo', 'cargas_posibles_adicionales'], ascending=[True, False])

# Seleccionar columnas útiles
asignacion = df_filtrado[['tipo', 'operativo', 'clasificacion', 'cargas_posibles_adicionales']]

# Guardar
os.makedirs('output', exist_ok=True)
asignacion.to_csv('output/guia_asignacion_cargas.csv', index=False)

print("✅ Guía de asignación generada: output/guia_asignacion_cargas.csv")
