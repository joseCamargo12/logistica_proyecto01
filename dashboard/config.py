# dashboard/config.py
LOGO_URL = "https://res.cloudinary.com/dwqahfw5n/image/upload/v1753630828/copia-removebg-preview_yced1y.png"
LOTTIE_URL = "https://lottie.host/89c2b271-9337-46b5-8c38-7012019b1689/VCL2goaisq.json"

# Regla de negocio para capacidad y clasificación
PROMEDIO_IDEAL = {'A': 15, 'M': 10, 'F': 8, 'B': 8, 'S': 10, 'T': 12, 'C': 5}

# Regla de negocio para análisis de tiempos
REFERENCIA_DATA = {
    "Tipo": ["A", "M", "F", "B", "S", "T", "C"], 
    "Tiempo Estándar (días)": [30, 90, 90, 90, 90, 30, 30], 
    "Meta de Mejora (días)": [20, 70, 70, 70, 70, 15, 15]
}
ESFUERZO_POR_TIPO = {'A': 3, 'M': 9, 'F': 9, 'B': 9, 'S': 9, 'T': 3, 'C': 3}
TIEMPOS_ESTANDAR_POR_TIPO = {'A': 30, 'M': 90, 'F': 90, 'B': 90, 'S': 90, 'T': 30, 'C': 30}