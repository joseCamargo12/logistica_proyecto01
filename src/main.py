import subprocess
import sys

scripts = [
    "src/01_limpiar_datos.py",
    "src/02_filtrar_anios.py",
    "src/03_resumen_operaciones.py",
    "src/04_clasificacion_flujo.py",
    "src/05_soporte_carga.py",
    "src/06_guia_asignacion.py"
]

print("🔄 Iniciando procesamiento de datos logísticos...\n")

for script in scripts:
    print(f"▶️ Ejecutando: {script}")
    try:
        subprocess.run([sys.executable, script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando {script}: {e}\n")
    print()

print("✅ Todos los scripts han sido ejecutados.")
