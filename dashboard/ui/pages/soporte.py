# dashboard/ui/pages/soporte.py
import streamlit as st
import pandas as pd
import plotly.express as px
from config import ESFUERZO_POR_TIPO
from config import PROMEDIO_IDEAL # Importamos la regla de negocio que necesitamos

def calcular_capacidad_disponible(df):
    """
    Calcula la capacidad disponible de cada operativo.
    Esta función es usada por el módulo de Asignación.
    """
    if df.empty or 'estado' not in df.columns: 
        return pd.DataFrame()
    
    # Filtramos solo las operaciones abiertas
    df_abiertas = df[df['estado'].str.upper() != 'CERRADO'].copy()
    
    # Contamos las operaciones abiertas por operativo y tipo
    df_capacidad = df_abiertas.groupby(['operativo', 'tipo'])['file'].count().reset_index()
    df_capacidad.rename(columns={'file': 'operaciones_abiertas'}, inplace=True)
    
    # Unimos con todos los operativos y tipos para no perder a los que no tienen cargas
    df_todos = pd.DataFrame([(op, tipo) for op in df['operativo'].unique() for tipo in df['tipo'].unique()], columns=['operativo', 'tipo'])
    df_capacidad = pd.merge(df_todos, df_capacidad, on=['operativo', 'tipo'], how='left').fillna(0)
    
    # Mapeamos la capacidad ideal y calculamos la disponible
    df_capacidad['capacidad_ideal'] = df_capacidad['tipo'].map(PROMEDIO_IDEAL).fillna(0)
    df_capacidad['cargas_posibles_adicionales'] = df_capacidad['capacidad_ideal'] - df_capacidad['operaciones_abiertas']
    df_capacidad['cargas_posibles_adicionales'] = df_capacidad['cargas_posibles_adicionales'].clip(lower=0).astype(int)
    
    return df_capacidad[['operativo', 'tipo', 'cargas_posibles_adicionales']]


def analizar_balance_carga(df_filtrado):
    """
    Esta función analiza la carga de trabajo desde dos perspectivas:
    1. Cantidad de operaciones abiertas.
    2. Esfuerzo total ponderado por la complejidad de cada operación.
    """
    st.markdown('<h3><i class="bi bi-layers-fill"></i> Balance de Carga Real vs. Cantidad de Tareas</h3>', unsafe_allow_html=True)
    st.info("""
    Aquí comparamos dos formas de ver la carga de trabajo. A la izquierda, quién tiene **más operaciones**. 
    A la derecha, quién tiene el **mayor peso de trabajo** basado en la complejidad de esas operaciones.
    """)

    # Filtramos solo las operaciones que no están cerradas
    df_abiertas = df_filtrado[df_filtrado['estado'].str.upper() != 'CERRADO'].copy()
    
    if df_abiertas.empty:
        st.success("¡No hay operaciones abiertas en el período seleccionado para analizar la carga de trabajo!")
        return

    # Mapeamos la puntuación de esfuerzo a cada operación abierta
    df_abiertas['puntos_esfuerzo'] = df_abiertas['tipo'].map(ESFUERZO_POR_TIPO).fillna(1) # Asignamos 1 si el tipo no está en el dict

    # Agrupamos por operativo y calculamos ambas métricas
    df_carga = df_abiertas.groupby('operativo').agg(
        cantidad_operaciones=('file', 'count'),
        esfuerzo_total=('puntos_esfuerzo', 'sum')
    ).reset_index()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Carga por Cantidad")
        df_plot_cantidad = df_carga.sort_values('cantidad_operaciones', ascending=False).head(15)
        fig_cantidad = px.bar(
            df_plot_cantidad,
            x='cantidad_operaciones',
            y='operativo',
            orientation='h',
            title="Top 15 por Nº de Operaciones",
            labels={'cantidad_operaciones': 'Nº de Operaciones Abiertas', 'operativo': 'Operativo'}
        )
        fig_cantidad.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_cantidad, use_container_width=True)

    with col2:
        st.subheader("Carga por Esfuerzo")
        df_plot_esfuerzo = df_carga.sort_values('esfuerzo_total', ascending=False).head(15)
        fig_esfuerzo = px.bar(
            df_plot_esfuerzo,
            x='esfuerzo_total',
            y='operativo',
            orientation='h',
            title="Top 15 por Esfuerzo Ponderado",
            labels={'esfuerzo_total': 'Puntuación de Esfuerzo Total', 'operativo': 'Operativo'},
            color_continuous_scale=px.colors.sequential.Reds
        )
        fig_esfuerzo.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_esfuerzo, use_container_width=True)

    # --- El Insight Clave Automatizado ---
    top_esfuerzo = df_carga.nlargest(5, 'esfuerzo_total')['operativo'].tolist()
    top_cantidad = df_carga.nlargest(5, 'cantidad_operaciones')['operativo'].tolist()
    
    # Buscamos operativos que están en el top de esfuerzo pero no en el de cantidad
    sobrecargados_ocultos = [op for op in top_esfuerzo if op not in top_cantidad]
    
    if sobrecargados_ocultos:
        st.warning(f"""
        **⚠️ Alerta de Sobrecarga Oculta:** 
        Los operativos **{', '.join(sobrecargados_ocultos)}** tienen una de las cargas de trabajo más altas en términos de esfuerzo, 
        aunque no necesariamente tengan la mayor cantidad de tareas. Esto puede justificar su percepción de alta carga laboral.
        """)

def mostrar_soporte(df_filtrado):
    # La función principal ahora llama al nuevo análisis
    analizar_balance_carga(df_filtrado)