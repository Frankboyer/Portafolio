import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from data_config import criticidad_límites # Asegúrate de importar esto

def create_heatmap(df_risks, matriz_probabilidad, matriz_impacto, idioma="es"):
    """
    Crea un mapa de calor 5x5 basado en el riesgo residual promedio
    para combinaciones de probabilidad de amenaza y rangos de impacto numérico.

    Args:
        df_risks (pd.DataFrame): DataFrame con los riesgos evaluados, incluyendo 'Riesgo Residual',
                                 'Probabilidad' e 'Impacto Numérico'.
        matriz_probabilidad (pd.DataFrame): DataFrame con las clasificaciones y valores de probabilidad.
        matriz_impacto (pd.DataFrame): DataFrame con las clasificaciones y valores de impacto (no usado directamente para bins).
        idioma (str, optional): El idioma para las etiquetas y el título ('es' para español, 'en' para inglés).
                                 Por defecto es 'es'.

    Returns:
        plotly.graph_objects.Figure or None: Un objeto Figure de Plotly que representa el mapa de calor,
                                            o None si el DataFrame df_risks está vacío.
    """
    if df_risks.empty:
        return None

    # Definir los bins para Probabilidad e Impacto
    prob_bins = [0] + matriz_probabilidad['Valor'].tolist() + [1.0] # Añadir 0 para el bin inicial
    prob_labels = matriz_probabilidad['Clasificacion'].tolist()

    # Mapear el impacto numérico (0-100) a 5 categorías (ej. 0-20, 21-40, ...)
    impact_bins = [0, 20, 40, 60, 80, 100]
    impact_labels_es = ['Muy Bajo (0-20)', 'Bajo (21-40)', 'Medio (41-60)', 'Alto (61-80)', 'Muy Alto (81-100)']
    impact_labels_en = ['Very Low (0-20)', 'Low (21-40)', 'Medium (41-60)', 'High (61-80)', 'Very High (81-100)']
    impact_labels = impact_labels_es if idioma == "es" else impact_labels_en

    df_risks_copy = df_risks.copy()
    # Asignar cada riesgo a un bin de probabilidad
    df_risks_copy['Prob_Bin'] = pd.cut(df_risks_copy['Probabilidad'], bins=prob_bins, labels=prob_labels, right=True, include_lowest=True)
    # Asignar cada riesgo a un bin de impacto numérico
    df_risks_copy['Impact_Bin'] = pd.cut(df_risks_copy['Impacto Numérico'], bins=impact_bins, labels=impact_labels, right=True, include_lowest=True)

    # Calcular el riesgo residual promedio para cada combinación de bins
    pivot_table = df_risks_copy.pivot_table(values='Riesgo Residual', index='Prob_Bin', columns='Impact_Bin', aggfunc='mean')

    # Reordenar las filas y columnas para asegurar el orden correcto
    pivot_table = pivot_table.reindex(index=prob_labels, columns=impact_labels)

    # Crear la matriz de colores y texto para el heatmap
    z_values = pivot_table.values.tolist()
    text_values = []
    
    # Generar texto y colores basados en criticidad_límites
    for r in range(len(prob_labels)):
        row_text = []
        for c in range(len(impact_labels)):
            val = pivot_table.iloc[r, c]
            if pd.isna(val):
                row_text.append('N/A')
            else:
                for v_min, v_max, clasif_es, color, clasif_en in criticidad_límites:
                    if v_min <= val <= v_max:
                        row_text.append(f"{val:.2f}\n" + (clasif_es if idioma == "es" else clasif_en))
                        break
        text_values.append(row_text)

    # Crear el heatmap con Plotly
    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=impact_labels,
        y=prob_labels,
        text=text_values,
        texttemplate="%{text}",
        hoverinfo="text",
        colorscale=[[limit[0], limit[3]] for limit in criticidad_límites], # Utilizar los límites y colores de criticidad_límites
        showscale=True,
        colorbar=dict(
            title=('Riesgo Residual Promedio' if idioma == "es" else 'Average Residual Risk'),
            tickvals=[(l[0]+l[1])/2 for l in criticidad_límites], # Etiquetas en el medio de los rangos
            ticktext=[(l[2] if idioma == "es" else l[4]) for l in criticidad_límites], # Nombres de las clasificaciones
            lenmode="fraction", len=0.75, yanchor="middle", y=0.5
        )
    ))

    fig.update_layout(
        title=('Mapa de Calor de Riesgos (Riesgo Residual Promedio)' if idioma == "es" else 'Risk Heatmap (Average Residual Risk)'),
        xaxis_title=('Impacto Numérico' if idioma == "es" else 'Numeric Impact'),
        yaxis_title=('Probabilidad de Amenaza' if idioma == "es" else 'Threat Probability'),
        xaxis=dict(side='top'), # Mover etiquetas X a la parte superior
        height=450,
        margin=dict(t=80, b=20)
    )
    return fig


def create_pareto_chart(df_risks, idioma="es"):
    """
    Crea un gráfico de Pareto para los riesgos, mostrando el riesgo residual y el porcentaje acumulado.

    Args:
        df_risks (pd.DataFrame): DataFrame con los riesgos evaluados, incluyendo 'Riesgo Residual'
                                 y 'Nombre del Riesgo'.
        idioma (str, optional): El idioma para las etiquetas y el título ('es' para español, 'en' para inglés).
                                 Por defecto es 'es'.

    Returns:
        plotly.graph_objects.Figure or None: Un objeto Figure de Plotly que representa el gráfico de Pareto,
                                            o None si el DataFrame df_risks está vacío.
    """
    if df_risks.empty:
        return None

    df_sorted = df_risks.sort_values(by='Riesgo Residual', ascending=False).copy()
    df_sorted['Riesgo Residual Acumulado'] = df_sorted['Riesgo Residual'].cumsum()
    df_sorted['Porcentaje Acumulado'] = (df_sorted['Riesgo Residual Acumulado'] / df_sorted['Riesgo Residual'].sum()) * 100

    fig = go.Figure()

    # Barras para el riesgo residual
    fig.add_trace(go.Bar(
        x=df_sorted['Nombre del Riesgo'],
        y=df_sorted['Riesgo Residual'],
        name=('Riesgo Residual' if idioma == "es" else 'Residual Risk'),
        marker_color='#1f77b4'
    ))

    # Línea para el porcentaje acumulado
    fig.add_trace(go.Scatter(
        x=df_sorted['Nombre del Riesgo'],
        y=df_sorted['Porcentaje Acumulado'],
        mode='lines+markers',
        name=('Porcentaje Acumulado' if idioma == "es" else 'Cumulative Percentage'),
        yaxis='y2', # Usar un segundo eje Y
        marker_color='#d62728'
    ))

    fig.update_layout(
        title=('Gráfico de Pareto de Riesgos' if idioma == "es" else 'Risk Pareto Chart'),
        xaxis_title=('Nombre del Riesgo' if idioma == "es" else 'Risk Name'),
        yaxis_title=('Riesgo Residual' if idioma == "es" else 'Residual Risk'),
        yaxis2=dict(
            title=('Porcentaje Acumulado' if idioma == "es" else 'Cumulative Percentage'),
            overlaying='y',
            side='right',
            range=[0, 100],
            tickvals=np.arange(0, 101, 10)
        ),
        legend=dict(x=0.01, y=0.99),
        height=450,
        margin=dict(t=80, b=20)
    )
    return fig

def plot_montecarlo_histogram(data, title, x_label, idioma="es"):
    """
    Crea un histograma para los datos de la simulación Monte Carlo.

    Args:
        data (np.array): Array de los datos a graficar (ej. riesgo residual simulado o pérdidas económicas).
        title (str): Título del histograma.
        x_label (str): Etiqueta del eje X.
        idioma (str, optional): El idioma para la etiqueta del eje Y ('es' para español, 'en' para inglés).
                                 Por defecto es 'es'.

    Returns:
        matplotlib.figure.Figure or None: Un objeto Figure de Matplotlib que representa el histograma,
                                          o None si los datos están vacíos.
    """
    if data is None or len(data) == 0:
        return None

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(data, kde=True, ax=ax, color='#28a745')
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel('Frecuencia' if idioma == "es" else 'Frequency')
    plt.tight_layout()
    return fig

def create_sensitivity_plot(correlations, idioma="es"):
    """
    Crea un gráfico de barras para el análisis de sensibilidad, mostrando la correlación
    de los factores de riesgo con la pérdida económica.

    Args:
        correlations (pd.Series): Series de pandas con las correlaciones de los factores de riesgo
                                  con la pérdida económica.
        idioma (str, optional): El idioma para las etiquetas y el título ('es' para español, 'en' para inglés).
                                 Por defecto es 'es'.

    Returns:
        plotly.graph_objects.Figure or None: Un objeto Figure de Plotly que representa el gráfico de sensibilidad,
                                            o None si las correlaciones están vacías.
    """
    if correlations is None or correlations.empty:
        return None

    fig = px.bar(
        x=correlations.index,
        y=correlations.values,
        title=('Análisis de Sensibilidad: Correlación con Pérdida Económica' if idioma == "es" else 'Sensitivity Analysis: Correlation with Economic Loss'),
        labels={
            'x': ('Factor de Riesgo' if idioma == "es" else 'Risk Factor'),
            'y': ('Magnitud de Correlación' if idioma == "es" else 'Correlation Magnitude')
        },
        color_discrete_sequence=px.colors.qualitative.Plotly # O cualquier otra paleta
    )
    fig.update_layout(xaxis_tickangle=-45, height=400, margin=dict(t=80, b=20))
    return fig
