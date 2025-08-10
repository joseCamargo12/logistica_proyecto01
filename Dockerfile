# Dockerfile (Versión corregida y simplificada)
FROM python:3.11-slim

# Configurar timezone para Colombia
ENV TZ=America/Bogota
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Instalar curl para healthcheck
# Combinamos apt-get update y install en una sola capa para optimizar
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copia requirements primero para mejor cache de Docker
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# --- CAMBIO CLAVE ---
# Copia el CONTENIDO de la carpeta 'dashboard' a la carpeta de trabajo actual '/app'
COPY dashboard/ .

# Crear directorio para logs de métricas
RUN mkdir -p /app/logs

# Exponer puerto
EXPOSE 8501

# Variables de entorno para Streamlit (estas ya las tenías, están perfectas)
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# --- CAMBIO CLAVE ---
# Comando para ejecutar la aplicación ahora es más simple porque app.py está en /app
CMD ["streamlit", "run", "app.py"]