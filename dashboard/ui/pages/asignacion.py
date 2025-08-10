# dashboard/ui/pages/asignacion.py
import streamlit as st
import pandas as pd
import plotly.express as px

# Importamos las funciones y configs necesarias
from .soporte import calcular_capacidad_disponible
from .analisis_tiempos import calcular_duracion_real
from config import TIEMPOS_ESTANDAR_POR_TIPO

@st.cache_data
def calcular_eficacia_operativos(df_operaciones_cerradas):
    """
    Calcula la "tasa de éxito" de cada operativo por tipo de operación.
    Un "éxito" se define como cerrar una operación dentro de su tiempo estándar.
    """
    if df_operaciones_cerradas.empty:
        return pd.DataFrame(columns=['operativo', 'tipo', 'eficacia_historica'])

    # Añadimos la columna de tiempo estándar a cada operación
    df_operaciones_cerradas['tiempo_estandar'] = df_operaciones_cerradas['tipo'].map(TIEMPOS_ESTANDAR_POR_TIPO)
    
    # Comparamos: ¿la duración real fue menor o igual al estándar?
    df_operaciones_cerradas['fue_exitoso'] = df_operaciones_cerradas['duracion_real_dias'] <= df_operaciones_cerradas['tiempo_estandar']
    
    # Agrupamos por operativo y tipo, y calculamos el promedio de éxitos (que es la tasa de éxito)
    df_eficacia = df_operaciones_cerradas.groupby(['operativo', 'tipo'])['fue_exitoso'].mean().reset_index()
    df_eficacia.rename(columns={'fue_exitoso': 'eficacia_historica'}, inplace=True)
    
    # Convertimos a porcentaje para que sea más legible
    df_eficacia['eficacia_historica'] = (df_eficacia['eficacia_historica'] * 100).round(1)
    
    return df_eficacia


def mostrar_asignacion(df_filtrado):
    st.markdown('<h3><i class="bi bi-sign-turn-right-fill"></i> Asignación Estratégica de Cargas</h3>', unsafe_allow_html=True)
    if df_filtrado.empty:
        st.warning("No hay datos para generar una guía de asignación."); return
    
    # Obtenemos los 3 componentes de nuestro análisis
    df_capacidad = calcular_capacidad_disponible(df_filtrado)
    df_duracion = calcular_duracion_real(df_filtrado)
    df_eficacia = calcular_eficacia_operativos(df_duracion)
    
    if df_capacidad.empty:
        st.info("No hay datos para calcular la asignación."); return

    if not df_duracion.empty:
        df_velocidad = df_duracion.groupby(['operativo', 'tipo'])['duracion_real_dias'].mean().reset_index()
        df_velocidad.rename(columns={'duracion_real_dias': 'velocidad_promedio_dias'}, inplace=True)
        # Unimos capacidad y velocidad
        df_guia = pd.merge(df_capacidad, df_velocidad, on=['operativo', 'tipo'], how='left')
    else:
        df_guia = df_capacidad.copy()
        df_guia['velocidad_promedio_dias'] = 90 # Valor por defecto
    
    # Unimos la eficacia al dataframe principal
    df_guia = pd.merge(df_guia, df_eficacia, on=['operativo', 'tipo'], how='left')
    df_guia['eficacia_historica'].fillna(50.0, inplace=True) # Damos un 50% por defecto si no hay datos

    # Rellenamos NaN de velocidad con el promedio del tipo, y luego con el promedio general
    promedio_por_tipo = df_guia.groupby('tipo')['velocidad_promedio_dias'].transform('mean')
    df_guia['velocidad_promedio_dias'].fillna(promedio_por_tipo, inplace=True)
    df_guia['velocidad_promedio_dias'].fillna(df_guia['velocidad_promedio_dias'].mean(), inplace=True)

    # --- CÁLCULO DEL NUEVO ÍNDICE ESTRATÉGICO ---
    # Índice base (el que ya tenías)
    indice_base = (df_guia['cargas_posibles_adicionales'] / (df_guia['velocidad_promedio_dias'] + 1)) * 100
    # Factor de eficacia (un valor entre 0 y 1)
    factor_eficacia = 1 + (df_guia['eficacia_historica'] / 100)
    # Índice final
    df_guia['indice_estrategico'] = (indice_base * factor_eficacia).round(2)
    
    st.info("""
    Esta guía recomienda a quién asignar una nueva operación basándose en 3 factores:
    1. **Disponibilidad:** ¿Quién tiene espacio para más trabajo?
    2. **Velocidad:** ¿Quién suele cerrar operaciones de este tipo más rápido?
    3. **Eficacia:** ¿Quién tiene el mejor historial cumpliendo los plazos para este tipo de operación?
    """)
    
    df_guia_final = df_guia[df_guia['cargas_posibles_adicionales'] > 0].copy()
    
    if df_guia_final.empty:
        st.warning("Todos los operativos han alcanzado su capacidad ideal."); return

    df_guia_final.sort_values(by=['tipo', 'indice_estrategico'], ascending=[True, False], inplace=True)
    
    df_guia_final.rename(columns={
        'tipo': 'Tipo', 
        'operativo': 'Operativo', 
        'cargas_posibles_adicionales': 'Capacidad Disponible', 
        'velocidad_promedio_dias': 'Velocidad Promedio (días)', 
        'eficacia_historica': 'Eficacia Histórica (%)',
        'indice_estrategico': 'Índice Estratégico'
    }, inplace=True)

    columnas_a_mostrar = ['Tipo', 'Operativo', 'Capacidad Disponible', 'Velocidad Promedio (días)', 'Eficacia Histórica (%)', 'Índice Estratégico']
    st.dataframe(df_guia_final[columnas_a_mostrar], use_container_width=True)
    
    st.divider()
    st.markdown('<h3><i class="bi bi-trophy-fill"></i> Ranking Visual de Asignación Estratégica</h3>', unsafe_allow_html=True)
    
    df_chart = df_guia_final.sort_values('Índice Estratégico', ascending=False).head(15)
    
    fig = px.bar(
        df_chart.sort_values('Índice Estratégico', ascending=True),
        x='Índice Estratégico',
        y='Operativo',
        color='Tipo',
        orientation='h',
        title='Top 15 Operativos por Índice Estratégico',
        labels={'Índice Estratégico': 'Puntuación de Asignación', 'Operativo': 'Operativo'}
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    st.success("Una barra más larga indica una mejor combinación de disponibilidad, velocidad y calidad histórica para ese tipo de tarea.")