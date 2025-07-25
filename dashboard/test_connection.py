# archivo: dashboard/test_connection.py

from supabase import create_client, Client
import os

# Reemplaza con tus credenciales EXACTAS
URL = "https://uiukuudvzkqfzvutmcyq.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVpdWt1dWR2emtxZnp2dXRtY3lxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM0MDIwNDgsImV4cCI6MjA2ODk3ODA0OH0.0S03jtI1uK-Z9XzsTfwn7-6BP24v8fAQ_birBk8saKo"

print("Intentando conectar a Supabase...")
try:
    supabase: Client = create_client(URL, KEY)
    print("✅ Cliente de Supabase creado con éxito.")
    
    print("\nIntentando obtener datos de la tabla 'operaciones'...")
    response = supabase.table('operaciones').select("*", count='exact').execute()
    
    print("\n✅ ¡Conexión y consulta exitosas!")
    print(f"Se encontraron {response.count} registros en la tabla.")
    # print("Datos recibidos:")
    # print(response.data)

except Exception as e:
    print("\n❌ Ocurrió un error durante la conexión o consulta.")
    print(f"Error: {e}")