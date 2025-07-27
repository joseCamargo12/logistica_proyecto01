# ================================================
# ARCHIVO A MODIFICAR: dashboard/components/glosario.py (CON ICONOS)
# ================================================
import streamlit as st

def mostrar_glosario_y_soporte():
    # --- TÍTULO PRINCIPAL CON ICONO ---
    st.markdown('<h2><i class="bi bi-question-circle-fill"></i> Guía de Usuario y Soporte Técnico</h2>', unsafe_allow_html=True)
    st.info("Aquí encontrarás quién desarrolló esta herramienta, cómo contactarlo y el propósito de cada módulo.")
    st.divider()

    # ==== INFORMACIÓN DEL DESARROLLADOR CON ICONOS ---
    st.markdown('<h3><i class="bi bi-person-workspace"></i> Desarrollado por</h3>', unsafe_allow_html=True)
    st.markdown("""
    Esta plataforma fue desarrollada a medida por **[Estrategia Empresarial](https://estrategiaempresarial.com.co/)** para potenciar el análisis de datos de **FAM Logística**.

    Si encuentras algún problema, tienes una idea para una nueva funcionalidad o necesitas soporte técnico, no dudes en contactarme:

    ---
    **Camilo Camargo**  
    *Consultor de Business Intelligence*

    - **WhatsApp:** +57 313 8300526  
    - **Correo:** camilo.camargo@estrategiaempresarial.com.co  
    - **Instagram:** [@estrategia__empresarial](https://www.instagram.com/estrategia__empresarial)
    """)

    st.success("¡Tu feedback es valioso para seguir mejorando esta herramienta!")
    st.divider()

    # ==== EXPLICACIÓN DE LOS MÓDULOS CON ICONOS ---
    st.markdown('<h3><i class="bi bi-book-half"></i> ¿Cómo funciona cada módulo?</h3>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        # Usamos texto simple para el label del expander y ponemos el título con icono dentro
        with st.expander("Análisis General", expanded=True):
            st.markdown('<h5><i class="bi bi-graph-up-arrow"></i> Análisis General</h5>', unsafe_allow_html=True)
            st.markdown("""
            **Objetivo:** Ofrecer una vista panorámica del estado de las operaciones.

            - **Tendencia de Operaciones:** Analiza crecimiento, caídas o estacionalidad.
            - **Distribución por Tipo:** Muestra los servicios más solicitados.
            - **Carga por Operativo:** Permite ver si hay desequilibrio en el trabajo.
            """)

        with st.expander("Capacidad", expanded=True):
            st.markdown('<h5><i class="bi bi-box-seam"></i> Capacidad</h5>', unsafe_allow_html=True)
            st.markdown("""
            **Objetivo:** Medir la carga actual de cada operativo frente a su capacidad ideal.

            - **Abiertas:** Operaciones en curso.
            - **Cerradas:** Operaciones completadas.
            - **Cargas Posibles:** Capacidad restante = Capacidad Ideal - Abiertas.
            """)

        with st.expander("Resumen", expanded=True):
            st.markdown('<h5><i class="bi bi-card-checklist"></i> Resumen</h5>', unsafe_allow_html=True)
            st.markdown("""
            **Objetivo:** Proveer una tabla detallada del volumen de trabajo por operativo y tipo.

            - Ideal para reportes.
            - Muestra especialización por tipo de operación.
            """)

    with col2:
        with st.expander("Asignación", expanded=True):
            st.markdown('<h5><i class="bi bi-sign-turn-right-fill"></i> Asignación</h5>', unsafe_allow_html=True)
            st.markdown("""
            **Objetivo:** Recomendar a quién asignar una nueva operación.

            - **Índice de Asignación:** Evalúa disponibilidad y eficiencia.
            - **Fórmula:** `(Capacidad Disponible / (Velocidad Promedio + 1)) * 100`
            - Útil para balancear la carga de trabajo.
            """)

        with st.expander("Clasificación", expanded=True):
            st.markdown('<h5><i class="bi bi-sort-down"></i> Clasificación</h5>', unsafe_allow_html=True)
            st.markdown("""
            **Objetivo:** Calificar el rendimiento mensual de cada operativo.

            - **Índice de Flujo:** Compara desempeño real vs. esperado.
            - **Niveles:**
                - **ALTO (≥ 100%):** Excelente.
                - **MEDIO (70% - 99%):** Aceptable.
                - **BAJO (< 70%):** Posible subutilización.
            """)

        with st.expander("Tiempos", expanded=True):
            st.markdown('<h5><i class="bi bi-clock-history"></i> Tiempos</h5>', unsafe_allow_html=True)
            st.markdown("""
            **Objetivo:** Analizar eficiencia y cumplimiento de plazos.

            - **Gráfico Comparativo:** Meta vs. duración real promedio.
            - **Tabla de Rendimiento:** Promedios, mínimos y máximos por operativo.
            """)