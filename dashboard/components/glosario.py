# ================================================
# ARCHIVO A MODIFICAR: dashboard/components/glosario.py (VERSIÓN COMPLETA)
# ================================================
import streamlit as st

def mostrar_glosario():
    st.header("📖 Guía del Dashboard y Metodología")
    st.info("Esta sección explica el propósito de cada pestaña y cómo se calculan las métricas clave para ayudar a la toma de decisiones.")
    st.divider()

    # Usamos columnas para organizar mejor los expanders
    col1, col2 = st.columns(2)

    with col1:
        with st.expander("🔬 **Análisis General**", expanded=True):
            st.write("""
            **Propósito:** Ofrecer una vista panorámica del estado de las operaciones.
            - **Tendencia de Operaciones:** Muestra el volumen de trabajo a lo largo del tiempo. Permite identificar si estamos creciendo, decreciendo o si hay patrones estacionales.
            - **Distribución por Tipo:** Revela cuáles son los servicios más demandados (Aéreo, Marítimo, etc.).
            - **Carga por Operativo:** Muestra cómo se distribuye el trabajo entre el equipo. Ideal para detectar desequilibrios en la carga.
            """)

        with st.expander("🧮 **Capacidad**", expanded=True):
            st.write("""
            **Propósito:** Evaluar la carga de trabajo actual de cada operativo frente a su capacidad ideal.
            - **Abiertas:** Número de operaciones que el operativo tiene actualmente en proceso.
            - **Cerradas:** Operaciones completadas en el período filtrado.
            - **Cargas Posibles Adicionales:** El "espacio" que le queda a un operativo para recibir nuevo trabajo, calculado como `Capacidad Ideal - Cargas Abiertas`. Ayuda a evitar la sobrecarga.
            """)

        with st.expander("📈 **Resumen**", expanded=True):
            st.write("""
            **Propósito:** Proveer una tabla detallada con el conteo total de operaciones, agrupadas por operativo y tipo.
            Es una vista de "zoom-in" para entender en qué tipos de operaciones se especializa cada miembro del equipo. Ideal para descargar y usar en reportes externos.
            """)
        
    with col2:
        with st.expander("🚦 **Asignación**", expanded=True):
            st.write("""
            **Propósito:** Sugerir de manera inteligente a quién asignar una nueva operación.
            - **Índice de Asignación:** Una puntuación que combina **disponibilidad** (cuánto espacio tiene) y **eficiencia** (qué tan rápido ha sido en el pasado).
            - **Fórmula:** `(Capacidad Disponible / (Velocidad Promedio + 1)) * 100`
            - **Uso Práctico:** Al recibir una nueva tarea, consulta esta guía. El operativo con el índice más alto es, en teoría, el mejor candidato.
            """)
        
        with st.expander("📊 **Clasificación**", expanded=True):
            st.write("""
            **Propósito:** Calificar el rendimiento de cada operativo basado en su volumen de trabajo mensual.
            - **Índice de Flujo:** Compara el promedio mensual real de operaciones de un operativo con el promedio ideal esperado.
            - **Niveles:**
                - **ALTO (≥ 100%):** Rendimiento excepcional.
                - **MEDIO (70% - 99%):** Rendimiento dentro de lo esperado.
                - **BAJO (< 70%):** Rendimiento por debajo de las expectativas, puede indicar poca carga de trabajo.
            """)
        
        with st.expander("⏱️ **Tiempos**", expanded=True):
            st.write("""
            **Propósito:** Analizar la eficiencia y el cumplimiento de los plazos.
            - **Gráfico Comparativo:** Visualiza la diferencia entre el "Tiempo Estándar" (la meta) y la "Duración Real Promedio" (el resultado) para cada tipo de operación.
            - **Tabla de Rendimiento:** Detalla los tiempos promedio, mínimo y máximo de cada operativo para identificar a los más rápidos y consistentes.
            """)