# ================================================
# ARCHIVO A CREAR: dashboard/components/pronosticos.py
# ================================================
import streamlit as st
import pandas as pd
from prophet import Prophet
import plotly.graph_objects as go

@st.cache_data(ttl=3600) # Cachear por 1 hora
def generar_pronostico(_df_historico, periodos):
    """
    Toma el historial de operaciones y genera un pronóstico futuro.
    """
    df_prophet = _df_historico.groupby(_df_historico['fecha_file'].dt.date).size().reset_index(name='y')
    df_prophet.rename(columns={'fecha_file': 'ds'}, inplace=True)

    model = Prophet(daily_seasonality=False, weekly_seasonality=True, yearly_seasonality=True, changoint_prior_scale=0.05)
    model.fit(df_prophet)

    future = model.make_future_dataframe(periods=periodos, freq='D')
    forecast = model.predict(future)
    return model, forecast

def mostrar_pronosticos(df_operaciones):
    st.header("🔮 Pronóstico de Carga de Trabajo Futura")
    st.info("Esta sección utiliza el historial completo de operaciones para predecir el volumen de trabajo. Ayuda a anticipar picos de alta demanda y valles de baja actividad para una mejor planificación de recursos.")

    periodo_a_predecir = st.slider(
        "Selecciona el horizonte de pronóstico (en días):",
        min_value=30, max_value=365, value=90, step=15
    )

    try:
        with st.spinner(f"Generando pronóstico para los próximos {periodo_a_predecir} días..."):
            model, forecast = generar_pronostico(df_operaciones, periodo_a_predecir)
        
        st.subheader("Gráfico del Pronóstico")
        fig = model.plot(forecast, xlabel="Fecha", ylabel="Volumen de Operaciones")
        ax = fig.gca()
        ax.set_title(f"Pronóstico de Operaciones Diarias", size=20)
        st.pyplot(fig)

        with st.expander("Ver detalle y componentes del pronóstico"):
            st.write("El gráfico muestra la predicción (línea azul oscuro), con el área azul claro representando el intervalo de incertidumbre. Los puntos negros son los datos históricos.")
            fig_components = model.plot_components(forecast)
            st.pyplot(fig_components)
            st.write("""
            - **Tendencia (Trend):** Muestra la dirección general a largo plazo.
            - **Estacionalidad Semanal (Weekly):** Patrones que se repiten cada semana (ej. más trabajo los lunes).
            - **Estacionalidad Anual (Yearly):** Patrones estacionales del año (ej. picos en temporada alta).
            """)
    except Exception as e:
        st.error(f"No se pudo generar el pronóstico. Puede que no haya suficientes datos históricos. Error: {e}")