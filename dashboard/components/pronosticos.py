import streamlit as st
import pandas as pd
from prophet import Prophet

@st.cache_data(ttl=3600)
def generar_pronostico_filtrado(_df_historico, periodos, tipo_operacion=None):
    """
    Genera un pronóstico para todos los datos o filtrado por un tipo de operación.
    """
    df_filtrado = _df_historico.copy()
    if tipo_operacion != "TODOS":
        df_filtrado = df_filtrado[df_filtrado['tipo'] == tipo_operacion]
    
    if len(df_filtrado) < 10: # Prophet necesita un mínimo de datos
        return None, None

    # Agrupar por día para la serie temporal
    df_prophet = df_filtrado.groupby(df_filtrado['fecha_file'].dt.date).size().reset_index(name='y')
    df_prophet.rename(columns={'fecha_file': 'ds'}, inplace=True)
    
    if len(df_prophet) < 2: # Prophet necesita al menos 2 puntos de datos
        return None, None

    model = Prophet(daily_seasonality=False, weekly_seasonality=True, yearly_seasonality=True, changepoint_prior_scale=0.05)
    model.fit(df_prophet)
    
    future = model.make_future_dataframe(periods=periodos, freq='D')
    forecast = model.predict(future)
    return model, forecast

def mostrar_pronosticos(df_operaciones):
    st.markdown('<h2><i class="bi bi-calendar-week"></i> Pronóstico de Carga de Trabajo Futura</h2>', unsafe_allow_html=True)
    st.info("Utiliza esta herramienta para predecir el volumen de operaciones futuras, ya sea en general o para un tipo de operación específico. Esto te ayudará a anticipar la demanda y planificar recursos.")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Configuración del Pronóstico")
        
        # Filtro para Tipo de Operación
        tipos_disponibles = ["TODOS"] + sorted(df_operaciones['tipo'].unique())
        tipo_seleccionado = st.selectbox(
            "Selecciona un Tipo de Operación para pronosticar:",
            options=tipos_disponibles,
            index=0
        )

        # Slider para el período
        periodo_a_predecir = st.slider(
            "Selecciona el horizonte de pronóstico (en días):",
            min_value=30, max_value=365, value=90, step=15
        )

    with col2:
        try:
            with st.spinner(f"Generando pronóstico para '{tipo_seleccionado}'..."):
                model, forecast = generar_pronostico_filtrado(df_operaciones, periodo_a_predecir, tipo_seleccionado)
            
            if model is None or forecast is None:
                st.warning(f"No hay suficientes datos históricos para el tipo '{tipo_seleccionado}' para generar un pronóstico confiable.")
            else:
                st.subheader("Gráfico del Pronóstico")
                fig = model.plot(forecast, xlabel="Fecha", ylabel=f"Operaciones de Tipo '{tipo_seleccionado}'")
                ax = fig.gca()
                ax.set_title(f"Pronóstico de Operaciones Diarias", size=18)
                st.pyplot(fig)
        except Exception as e:
            st.error(f"Ocurrió un error al generar el pronóstico: {e}")

    st.divider()
    with st.expander("📖 ¿Cómo interpretar estos gráficos?"):
        st.write("""
        - **Gráfico Principal:** Muestra la predicción (línea azul oscuro) y el intervalo de incertidumbre (área azul claro). Si los puntos negros (datos reales) se mantienen dentro del área clara, el modelo es preciso. Un área clara muy ancha indica alta incertidumbre.
        - **Tendencia (Trend):** Indica si la demanda para este tipo de operación está creciendo, decreciendo o se mantiene estable a largo plazo.
        - **Estacionalidad Semanal (Weekly):** Revela patrones dentro de la semana. Por ejemplo, si los lunes y viernes son consistentemente los días de mayor volumen.
        - **Estacionalidad Anual (Yearly):** Muestra los patrones a lo largo del año, como picos de demanda en ciertas temporadas.
        """)
        if model:
            st.subheader("Desglose de Componentes del Pronóstico")
            fig_components = model.plot_components(forecast)
            st.pyplot(fig_components)
