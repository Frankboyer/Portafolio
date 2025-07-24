import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data_config import textos # Asegúrate de importar 'textos' para la función get_text_plotting

# Función auxiliar para obtener textos específicos de este módulo
def get_text_plotting(key, idioma='es'):
    return textos[idioma].get(key, key)

def create_heatmap(df, idioma='es'):
    """
    Crea un mapa de calor interactivo de riesgos residuales.
    El tamaño de los marcadores indica el riesgo residual.
    El color indica la clasificación de criticidad.
    """
    if df.empty:
        return go.Figure().update_layout(title=get_text_plotting("no_risks_for_heatmap", idioma))

    fig = px.scatter(df,
                     x="Impacto Numérico",
                     y="Probabilidad",
                     size="Riesgo Residual",
                     color="Clasificación",
                     hover_name="Nombre del Riesgo",
                     color_discrete_map={ # Usa los colores definidos en data_config para clasificacion
                        'Bajo': '#d4edda',
                        'Low': '#d4edda',
                        'Medio': '#ffc107',
                        'Medium': '#ffc107',
                        'Alto': '#fd7e14',
                        'High': '#fd7e14',
                        'Crítico': '#dc3545',
                        'Critical': '#dc3545'
                     },
                     labels={
                         "Impacto Numérico": get_text_plotting("heatmap_x_axis", idioma),
                         "Probabilidad": get_text_plotting("heatmap_y_axis", idioma),
                         "Riesgo Residual": get_text_plotting("heatmap_size_legend", idioma),
                         "Clasificación": get_text_plotting("heatmap_color_legend", idioma)
                     },
                     title=get_text_plotting("risk_heatmap_title", idioma),
                     size_max=50)

    fig.update_layout(
        xaxis_title=get_text_plotting("heatmap_x_axis", idioma),
        yaxis_title=get_text_plotting("heatmap_y_axis", idioma),
        height=500,
        margin=dict(l=40, r=40, b=40, t=80)
    )
    return fig

def create_pareto_chart(df, idioma='es'):
    """
    Crea un gráfico de Pareto para el riesgo residual.
    Muestra los riesgos ordenados por riesgo residual y su contribución acumulada.
    """
    if df.empty:
        return go.Figure().update_layout(title=get_text_plotting("no_risks_for_pareto", idioma))

    df_sorted = df.sort_values(by="Riesgo Residual", ascending=False).head(10).copy()
    df_sorted["Riesgo Residual Acumulado"] = df_sorted["Riesgo Residual"].cumsum() / df_sorted["Riesgo Residual"].sum() * 100

    fig = go.Figure()

    # Barra de riesgo residual
    fig.add_trace(go.Bar(
        x=df_sorted["Nombre del Riesgo"],
        y=df_sorted["Riesgo Residual"],
        name=get_text_plotting("pareto_y_axis", idioma),
        marker_color='skyblue'
    ))

    # Línea de porcentaje acumulado
    fig.add_trace(go.Scatter(
        x=df_sorted["Nombre del Riesgo"],
        y=df_sorted["Riesgo Residual Acumulado"],
        mode='lines+markers',
        name=get_text_plotting("pareto_cumulative_y_axis", idioma),
        yaxis='y2',
        line=dict(color='red', dash='dot')
    ))

    fig.update_layout(
        title=get_text_plotting("pareto_chart_title", idioma),
        xaxis_title=get_text_plotting("pareto_x_axis", idioma),
        yaxis=dict(
            title=get_text_plotting("pareto_y_axis", idioma),
            side='left',
            showgrid=True
        ),
        yaxis2=dict(
            title=get_text_plotting("pareto_cumulative_y_axis", idioma),
            side='right',
            overlaying='y',
            range=[0, 100],
            ticksuffix='%',
            showgrid=False
        ),
        height=500,
        margin=dict(l=40, r=40, b=40, t=80)
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
    Crea un gráfico de barras de sensibilidad (correlación).
    """
    if correlations_df.empty:
        return go.Figure().update_layout(title=get_text_plotting("no_data_for_sensitivity", idioma))

    fig = px.bar(correlations_df.sort_values(by="Correlacion", ascending=True),
                 x="Correlacion",
                 y="Variable",
                 orientation='h',
                 title=get_text_plotting("correlation_title", idioma),
                 labels={
                     "Correlacion": get_text_plotting("correlation_x_axis", idioma),
                     "Variable": get_text_plotting("correlation_y_axis", idioma)
                 })
    fig.update_layout(height=400, margin=dict(l=40, r=40, b=40, t=80))
    return fig
