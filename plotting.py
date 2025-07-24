import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# --- Helper para obtener textos (similar al de riskapp.py pero simplificado para este módulo) ---
# Se asume que `textos` y `criticidad_límites` serán importados de data_config.py
# Opcional: Podrías pasar el idioma directamente como parámetro a cada función de plotting si prefieres.
from data_config import textos, matriz_probabilidad, matriz_impacto, criticidad_límites

def get_text_plotting(key, idioma='es'):
    """Obtiene el texto correspondiente a una clave en el idioma especificado."""
    return textos[idioma].get(key, key)

# --- Funciones de Trazado ---

def create_heatmap(df_riesgos, matriz_probabilidad_df, matriz_impacto_df, idioma='es'):
    """
    Crea un mapa de calor interactivo de riesgos basado en Probabilidad vs Impacto.
    """
    if df_riesgos.empty:
        return None

    # Obtener las clasificaciones de probabilidad e impacto numérico
    # Para el heatmap, necesitamos clasificaciones cualitativas de Probabilidad e Impacto.
    # Usaremos las matrices de data_config para clasificar el 'Impacto Numérico' y 'Probabilidad' original del riesgo.

    # Clasificar la Probabilidad original del riesgo
    prob_bins = matriz_probabilidad_df['Rango Min'].tolist() + [matriz_probabilidad_df['Rango Max'].iloc[-1]]
    prob_labels = matriz_probabilidad_df['Clasificacion'].tolist()
    df_riesgos['Probabilidad_Clasificacion'] = pd.cut(
        df_riesgos['Probabilidad'],
        bins=prob_bins,
        labels=prob_labels,
        right=True, # Incluye el límite superior del intervalo
        include_lowest=True # Incluye el límite inferior del primer intervalo
    )

    # Clasificar el Impacto Numérico original del riesgo
    impact_bins = matriz_impacto_df['Rango Min'].tolist() + [matriz_impacto_df['Rango Max'].iloc[-1]]
    impact_labels = matriz_impacto_df['Clasificacion'].tolist()
    df_riesgos['Impacto_Clasificacion'] = pd.cut(
        df_riesgos['Impacto Numérico'],
        bins=impact_bins,
        labels=impact_labels,
        right=True,
        include_lowest=True
    )

    # Ordenar las categorías para asegurar el orden correcto en el heatmap
    prob_order = matriz_probabilidad_df['Clasificacion'].tolist()
    impact_order = matriz_impacto_df['Clasificacion'].tolist()

    # Contar la frecuencia de riesgos por cada cuadrante
    heatmap_data = df_riesgos.groupby(['Impacto_Clasificacion', 'Probabilidad_Clasificacion']).size().unstack(fill_value=0)

    # Reindexar para asegurar que todas las categorías estén presentes y en orden
    heatmap_data = heatmap_data.reindex(index=impact_order, columns=prob_order).fillna(0)

    # Crear el heatmap
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='YlOrRd',
        colorbar=dict(title=get_text_plotting("risk_count_title", idioma)),
        hovertemplate='<b>%{y}</b><br><b>%{x}</b><br>' + get_text_plotting("risk_count_title", idioma) + ': %{z}<extra></extra>'
    ))

    fig.update_layout(
        title=get_text_plotting("risk_heatmap_title", idioma),
        xaxis_title=get_text_plotting("probability_category_label", idioma),
        yaxis_title=get_text_plotting("impact_category_label", idioma),
        xaxis=dict(side="top"), # Poner la probabilidad en la parte superior
        height=500,
        margin=dict(l=0, r=0, t=50, b=0) # Ajustar márgenes
    )
    return fig


def create_pareto_chart(df_riesgos, idioma='es'):
    """
    Crea un gráfico de Pareto mostrando los riesgos residuales por clasificación.
    """
    if df_riesgos.empty:
        return None

    # Agrupar por clasificación y sumar el Riesgo Residual
    pareto_data = df_riesgos.groupby('Clasificación')['Riesgo Residual'].sum().sort_values(ascending=False)
    total_riesgo = pareto_data.sum()

    if total_riesgo == 0:
        return None # Evitar división por cero si no hay riesgos significativos

    # Calcular porcentaje y porcentaje acumulado
    pareto_data_df = pd.DataFrame(pareto_data).reset_index()
    pareto_data_df.columns = [get_text_plotting("classification_label", idioma), get_text_plotting("sum_residual_risk_label", idioma)]
    pareto_data_df[get_text_plotting("percentage_label", idioma)] = (pareto_data_df[get_text_plotting("sum_residual_risk_label", idioma)] / total_riesgo) * 100
    pareto_data_df[get_text_plotting("cumulative_percentage_label", idioma)] = pareto_data_df[get_text_plotting("percentage_label", idioma)].cumsum()

    # Crear el gráfico de barras para la suma de riesgo residual
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=pareto_data_df[get_text_plotting("classification_label", idioma)],
        y=pareto_data_df[get_text_plotting("sum_residual_risk_label", idioma)],
        name=get_text_plotting("sum_residual_risk_label", idioma),
        marker_color='rgb(58, 116, 179)'
    ))

    # Crear el gráfico de línea para el porcentaje acumulado
    fig.add_trace(go.Scatter(
        x=pareto_data_df[get_text_plotting("classification_label", idioma)],
        y=pareto_data_df[get_text_plotting("cumulative_percentage_label", idioma)],
        mode='lines+markers',
        name=get_text_plotting("cumulative_percentage_label", idioma),
        yaxis='y2', # Usar un eje Y secundario
        line=dict(color='red', width=2),
        marker=dict(size=8, color='red')
    ))

    # Actualizar diseño del gráfico
    fig.update_layout(
        title=get_text_plotting("pareto_chart_title", idioma),
        xaxis_title=get_text_plotting("classification_label", idioma),
        yaxis_title=get_text_plotting("sum_residual_risk_label", idioma),
        yaxis2=dict(
            title=get_text_plotting("cumulative_percentage_label", idioma) + ' (%)',
            overlaying='y',
            side='right',
            range=[0, 100]
        ),
        hovermode="x unified",
        height=500
    )

    return fig

def plot_montecarlo_histogram(data, title, x_label, idioma='es'):
    """
    Crea un histograma de los resultados de la simulación de Monte Carlo.
    """
    if data is None or len(data) == 0:
        return go.Figure().update_layout(title="No data to display.")

    fig = px.histogram(x=data, nbins=50, title=title)
    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title=get_text_plotting("frequency_label", idioma),
        bargap=0.05,
        height=400
    )
    return fig

def create_sensitivity_plot(correlations_df, idioma='es'):
    """
    Crea un gráfico de barras mostrando la correlación de los factores de riesgo con el riesgo residual.
    """
    if correlations_df.empty:
        return None

    # Asegurarse de que la columna 'Correlacion' existe
    if 'Correlacion' not in correlations_df.columns:
        # Esto debería ser manejado antes de llamar a esta función,
        # pero es una seguridad. En principio, calculations.py ya la genera.
        return None

    correlations_df['Abs_Correlacion'] = correlations_df['Correlacion'].abs()
    # Ordenar por el valor absoluto de la correlación para que los factores más influyentes estén arriba
    correlations_df = correlations_df.sort_values(by='Abs_Correlacion', ascending=True)

    fig = px.bar(
        correlations_df,
        x='Correlacion',
        y='Variable',
        orientation='h',
        title=get_text_plotting("correlation_plot_title", idioma),
        labels={'Correlacion': get_text_plotting("correlation_coefficient_label", idioma),
                'Variable': get_text_plotting("variable_label", idioma)},
        color='Correlacion', # Colorea por el valor de la correlación
        color_continuous_scale=px.colors.sequential.RdBu, # Escala de color rojo-azul
        range_color=[-1, 1] # Asegura que la escala de color siempre vaya de -1 a 1
    )

    fig.update_layout(
        xaxis_range=[-1, 1], # Asegura que el eje X siempre vaya de -1 a 1 para correlaciones
        height=400,
        margin=dict(l=0, r=0, t=50, b=0) # Ajustar márgenes
    )
    return fig
