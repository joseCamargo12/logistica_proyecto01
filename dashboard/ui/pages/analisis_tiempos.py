# dashboard/ui/pages/analisis_tiempos.py
import streamlit as st
import pandas as pd
import plotly.express as px
from core.processing import to_excel
from config import REFERENCIA_DATA

@st.cache_data
def calcular_duracion_real(df):
    df_calc = df.copy()
    if 'fecha_cierre' not in df_calc.columns or 'fecha_file' not in df_calc.columns:
        return pd.DataFrame()
    df_calc['fecha_cierre'] = pd.to_datetime(df_calc['fecha_cierre'], errors='coerce')
    df_calc['fecha_file'] = pd.to_datetime(df_calc['fecha_file'], errors='coerce')
    df_calc.dropna(subset=['fecha_file', 'fecha_cierre'], inplace=True)
    if df_calc.empty: return pd.DataFrame()
    df_calc['duracion_real_dias'] = (df_calc['fecha_cierre'] - df_calc['fecha_file']).dt.days
    df_calc = df_calc[df_calc['duracion_real_dias'] >= 0]
    return df_calc

# --- NUEVA FUNCIÓN ANALÍTICA ---
def analizar_cuellos_de_botella(df_operaciones_cerradas):
    """
    Esta función toma las operaciones cerradas, identifica las más lentas
    y extrae los patrones comunes que causan los retrasos.
    """
    # Para que el análisis estadístico sea relevante, necesitamos un mínimo de datos.
    if len(df_operaciones_cerradas) < 20:
        st.info("No hay suficientes operaciones cerradas en este período para realizar un diagnóstico de cuellos de botella.")
        return

    st.divider()
    st.markdown('<h3><i class="bi bi-search"></i> Diagnóstico de Cuellos de Botella</h3>', unsafe_allow_html=True)

    # ¿Qué es una operación "lenta"? En lugar de un número fijo, usamos estadística.
    # El percentil 80 nos da el umbral por encima del cual se encuentra el 20% de las operaciones más lentas.
    umbral_lento = df_operaciones_cerradas['duracion_real_dias'].quantile(0.80)
    df_lentos = df_operaciones_cerradas[df_operaciones_cerradas['duracion_real_dias'] > umbral_lento]

    st.info(f"""
    A continuación, analizamos el **20% de las operaciones más lentas** (aquellas que tardan más de **{int(umbral_lento)} días** en cerrarse). 
    Esto nos ayuda a identificar las causas raíz de los retrasos más significativos.
    """)

    if df_lentos.empty:
        st.success("¡Buenas noticias! No se han encontrado operaciones con retrasos significativos en el período seleccionado.")
        return

    # Análisis de Causa Raíz: Contamos qué factores son más comunes en las operaciones lentas.
    causas_por_tipo = df_lentos['tipo'].value_counts().nlargest(3)
    causas_por_operativo = df_lentos['operativo'].value_counts().nlargest(3)
    causas_por_cliente = df_lentos['cliente'].value_counts().nlargest(3) if 'cliente' in df_lentos else None

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Por Tipo de Operación")
        st.dataframe(causas_por_tipo)
    with col2:
        st.subheader("Por Operativo")
        st.dataframe(causas_por_operativo)
    with col3:
        if causas_por_cliente is not None and not causas_por_cliente.empty:
            st.subheader("Por Cliente")
            st.dataframe(causas_por_cliente)
    
    # El insight final y accionable, traducido a lenguaje de negocio.
    try:
        insight = f"""
        **Conclusión Accionable:** El tipo de operación **'{causas_por_tipo.index[0]}'** es el que más frecuentemente aparece entre los casos más lentos. 
        Adicionalmente, el operativo **'{causas_por_operativo.index[0]}'** es quien maneja la mayor cantidad de estas operaciones demoradas.
        """
        if causas_por_cliente is not None and not causas_por_cliente.empty:
            insight += f" El cliente **'{causas_por_cliente.index[0]}'** también es un factor común en estos retrasos."
        
        st.success(insight + " Se recomienda revisar los procesos y recursos asignados a estos casos específicos para optimizar los tiempos.")
    except IndexError:
        st.warning("No se pudo generar una conclusión automática con los datos disponibles.")

def mostrar_analisis_tiempos(df_filtrado):
    st.markdown('<h3><i class="bi bi-clock-history"></i> Análisis de Tiempos de Ciclo y Cumplimiento</h3>', unsafe_allow_html=True)
    if df_filtrado.empty:
        st.warning("No hay datos para calcular los tiempos."); return
        
    df_referencia = pd.DataFrame(REFERENCIA_DATA)
    df_calculo = calcular_duracion_real(df_filtrado)
    
    if df_calculo.empty:
        st.info("No hay operaciones cerradas con fechas válidas para analizar en el período seleccionado."); return

    # --- TU CÓDIGO ORIGINAL SE MANTIENE INTACTO AQUÍ ---
    st.markdown("#### 1. Comparativa de Tiempos: Estándar vs. Realidad (Tabla)")
    # ... tu código de la tabla ...
    df_promedio_real = df_calculo.groupby('tipo')['duracion_real_dias'].mean().reset_index()
    df_promedio_real.rename(columns={'tipo': 'Tipo', 'duracion_real_dias': 'Duración Real Promedio (días)'}, inplace=True)
    df_final = pd.merge(df_referencia, df_promedio_real, on="Tipo", how="left")
    df_final['Duración Real Promedio (días)'] = df_final['Duración Real Promedio (días)'].round(1)
    st.dataframe(df_final, use_container_width=True)
    if not df_final.empty:
        st.download_button("Descargar Tabla Comparativa", to_excel(df_final), "comparativa_tiempos.xlsx")
    st.divider()
    st.markdown("#### 2. Comparativa de Tiempos: Estándar vs. Realidad (Gráfico)")
    # ... tu código del gráfico ...
    df_grafico = df_final.melt(id_vars=['Tipo'], value_vars=['Tiempo Estándar (días)', 'Duración Real Promedio (días)'], var_name='Métrica', value_name='Días')
    df_grafico.dropna(subset=['Días'], inplace=True)
    fig = px.bar(df_grafico, x='Tipo', y='Días', color='Métrica', barmode='group', title="Tiempo Estándar vs. Tiempo Real Promedio por Tipo de Operación", labels={'Días': 'Duración en Días', 'Tipo': 'Tipo de Operación'})
    st.plotly_chart(fig, use_container_width=True)
    st.info("Este gráfico compara directamente el objetivo (tiempo estándar) con el rendimiento real. Barras más bajas en 'Duración Real' son mejores.")
    st.divider()
    st.markdown("#### 3. Rendimiento por Operativo")
    # ... tu código de la tabla de rendimiento ...
    df_operativo_tiempos = df_calculo.groupby('operativo')['duracion_real_dias'].agg(['mean', 'count', 'min', 'max']).reset_index()
    df_operativo_tiempos.rename(columns={'mean': 'Duración Promedio', 'count': 'Nº Op. Cerradas', 'min': 'Más Rápido (días)', 'max': 'Más Lento (días)'}, inplace=True)
    df_operativo_tiempos['Duración Promedio'] = df_operativo_tiempos['Duración Promedio'].round(1)
    st.dataframe(df_operativo_tiempos.sort_values(by='Duración Promedio'), use_container_width=True)
    if not df_operativo_tiempos.empty:
        st.download_button("Descargar Rendimiento por Operativo", to_excel(df_operativo_tiempos), "rendimiento_operativo.xlsx")

    # --- AQUÍ INTEGRAMOS LA NUEVA SECCIÓN ANALÍTICA ---
    # Usamos merge para asegurarnos de que el dataframe de cálculos tenga toda la info necesaria (como el cliente).
    df_calculo_enriquecido = pd.merge(df_calculo, df_filtrado, on='file', how='left', suffixes=('', '_y'))
    analizar_cuellos_de_botella(df_calculo_enriquecido)