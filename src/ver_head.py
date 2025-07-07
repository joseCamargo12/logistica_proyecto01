import pandas as pd

archivo = 'output/operaciones_limpio.csv'
df = pd.read_csv(archivo)

print("📋 Primeras filas del archivo:")
print(df.head(10))  # Puedes cambiar el número si quieres ver más
