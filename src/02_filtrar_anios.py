import pandas as pd

# Cargar archivo limpio
df = pd.read_csv('output/operaciones_limpio.csv')

# Convertir fecha_file a datetime
df['fecha_file'] = pd.to_datetime(df['fecha_file'], errors='coerce')

# Filtrar por años 2024 y 2025
df_filtrado = df[df['fecha_file'].dt.year.isin([2024, 2025])]

print(f"✅ Registros encontrados para 2024 y 2025: {len(df_filtrado)}")

# Guardar
df_filtrado.to_csv('output/operaciones_2024_2025.csv', index=False)
print("📁 Archivo guardado en: output/operaciones_2024_2025.csv")
