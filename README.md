<<<<<<< HEAD
# Sistema de Análisis de Operaciones Logísticas

Este proyecto permite analizar automáticamente las cargas de trabajo asignadas a cada operativo, generar reportes como clasificación de flujo, soporte de carga, y construir un dashboard interactivo para tomar decisiones basadas en datos. Está diseñado para ser reutilizable, escalable y ejecutable desde cero en cualquier entorno.

## Estructura del Proyecto

proyecto_logistica/
├── data/                     # Datos originales (Excel, CSV)
│   └── operaciones.csv
├── output/                   # Archivos procesados y generados
│   ├── operaciones_limpio.csv
│   ├── operaciones_2024_2025.csv
│   ├── resumen_operaciones.csv
│   ├── clasificacion_flujo.csv
│   ├── soporte_carga_operativo.csv
│   └── guia_asignacion_cargas.csv
├── src/                      # Scripts de procesamiento
│   ├── 01_limpiar_datos.py
│   ├── 02_filtrar_anios.py
│   ├── 03_resumen_operaciones.py
│   ├── 04_clasificacion_flujo.py
│   ├── 05_soporte_carga.py
│   ├── 06_guia_asignacion.py
│   └── main.py               # Script para correr todo junto
├── dashboard/                # Aplicación Streamlit
│   └── app.py
├── requirements.txt          # Dependencias del proyecto
└── README.md                 # Este archivo

## Requisitos del Sistema

- Python 3.9 o superior
- pip
- Recomendado: uso de entorno virtual

## Instalación del Proyecto (desde cero)

1. Clonar el repositorio:
   git clone https://github.com/tu_usuario/proyecto_logistica.git
   cd proyecto_logistica

2. Crear entorno virtual:
   python -m venv env
   .\env\Scripts\activate   (en Windows)
   source env/bin/activate (en Linux o Mac)

3. Instalar dependencias:
   pip install -r requirements.txt

## Uso paso a paso

### Procesamiento Automático

Puedes correr todo el pipeline de una sola vez con el siguiente comando:

   python src/main.py

Esto ejecutará los siguientes pasos:

1. Limpieza de datos
2. Filtro de años (2024 y 2025)
3. Resumen por operativo y tipo
4. Clasificación de flujo según estándar
5. Soporte de carga actual
6. Guía sugerida para asignación

Todos los resultados se guardan automáticamente en la carpeta `output/`.

### Visualización con el Dashboard

Para lanzar el dashboard interactivo en tu navegador, ejecuta:

   streamlit run dashboard/app.py

Desde allí podrás:

- Visualizar las operaciones activas
- Ver el índice de carga de cada operativo
- Consultar recomendaciones de asignación
- Filtrar por tipo, agente u operación
- Ver alertas de sobrecarga
- Analizar el promedio por tipo

## Scripts Explicados

| Script                          | Función principal                                                  |
|--------------------------------|--------------------------------------------------------------------|
| 01_limpiar_datos.py            | Limpia el archivo base, normaliza columnas y elimina errores       |
| 02_filtrar_anios.py            | Extrae solo registros de 2024 y 2025                               |
| 03_resumen_operaciones.py      | Cuenta operaciones por operativo y tipo                            |
| 04_clasificacion_flujo.py      | Compara carga real vs ideal para clasificar (ALTO, MEDIO, BAJO)    |
| 05_soporte_carga.py            | Estima cuántas cargas más puede asumir cada agente                 |
| 06_guia_asignacion.py          | Genera guía de asignación balanceada de nuevas cargas              |
| main.py                        | Orquesta todos los anteriores automáticamente                      |

## Recomendaciones

- Coloca siempre los archivos originales en la carpeta `data/`.
- No edites los archivos de `output/` manualmente.
- Personaliza los promedios ideales y los días estimados por tipo si es necesario.

## Posible despliegue en servidor

Este sistema puede integrarse en servidores con Docker o herramientas como N8n para que funcione con automatizaciones y cargas remotas. (Ver guía avanzada más adelante.)

## Créditos

Proyecto desarrollado por: José Camargo  
Asistencia técnica y estructura por: ChatGPT (OpenAI)
=======
# logistica_proyecto
>>>>>>> 6d744dac8d3ea0a0a4dbd21934d9a2b8ea1a9870
