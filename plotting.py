import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt # Importar matplotlib si lo vas a usar

# Las matrices y tablas serán pasadas como argumentos desde riskapp.py
# así que no necesitamos importarlas directamente aquí en plotting.py
# PERO, para que esta función get_text dummy funcione para probar, la he incluido.

def create_heatmap(df_risks, matriz_probabilidad, matriz_impacto, idioma="es"):
    if df_risks.empty:
        return None

    df_risks_copy = df_risks.copy()

    # --- Clasificación de Probabilidad para el Heatmap ---
    # Asegurarse de que Probabilidad es un valor numérico (0-1)
    # Los bordes de los bins para Probabilidad.
    prob_bins_edges = sorted(list(matriz_probabilidad['Rango Min'].unique()) + [matriz_probabilidad['Rango Max'].max()])
    prob_labels = matriz_probabilidad['Clasificacion'].tolist()

    # Si hay un desajuste entre etiquetas y bordes de bins, ajustar.
    if len(prob_labels) != len(prob_bins_edges) - 1:
        # Esto es un respaldo; lo ideal es que tus rangos en data_config sean coherentes.
        # Aquí, forzamos la creación de bordes equitativos para que pd.cut funcione.
        min_prob_global = matriz_probabilidad['Rango Min'].min()
        max_prob_global = matriz_probabilidad['Rango Max'].max()
        prob_bins_edges = np.linspace(min_prob_global, max_prob_global, len(prob_labels) + 1).tolist()

    df_risks_copy['Prob_Bin'] = pd.cut(df_risks_copy['Probabilidad'],
                                       bins=prob_bins_edges,
                                       labels=prob_labels,
                                       right=True,
                                       include_lowest=True)

    # --- Clasificación de Impacto Numérico para el Heatmap ---
    # Asegurarse de que Impacto Numérico es un valor numérico (0-100)
    # Los bordes de los bins para Impacto.
    impact_bins_edges = sorted(list(matriz_impacto['Rango Min'].unique()) + [matriz_impacto['Rango Max'].max()])
    impact_labels = matriz_impacto['Clasificacion'].tolist()

    # Si hay un desajuste entre etiquetas y bordes de bins, ajustar.
    if len(impact_labels) != len(impact_bins_edges) - 1:
        min_impact_global = matriz_impacto['Rango Min'].min()
        max_impact_global = matriz_impacto['Rango Max'].max()
        impact_bins_edges = np.linspace(min_impact_global, max_impact_global, len(impact_labels) + 1).tolist()

    df_risks_copy['Impact_Bin'] = pd.cut(df_risks_copy['Impacto Numérico'],
                                        bins=impact_bins_edges,
                                        labels=impact_labels,
                                        right=True,
                                        include_lowest=True)

    # --- Crear la Matriz para el Heatmap ---
    heatmap_data = df_risks_copy.groupby(['Prob_Bin', 'Impact_Bin']).size().unstack(fill_value=0)

    ordered_prob_labels = matriz_probabilidad['Clasificacion'].tolist()
    ordered_impact_labels = matriz_impacto['Clasificacion'].tolist()

    # Reindexar para asegurar el orden correcto y rellenar celdas vacías con 0.
    heatmap_data = heatmap_data.reindex(index=ordered_prob_labels, columns=ordered_impact_labels, fill_value=0)

    # --- Creación del Heatmap con Plotly ---
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='Viridis',
        colorbar=dict(title=f"{get_text('risk_count_title')}")
    ))

    fig.update_layout(
        title=f"{get_text('risk_heatmap_title')}",
        xaxis_title=f"{get_text('impact_category_label')}",
        yaxis_title=f"{get_text('probability_category_label')}",
        xaxis=dict(side="top"),
        yaxis=dict(autorange="reversed")
    )

    # Añadir texto a las celdas
    annotations = []
    # Usamos try-except para manejar el caso de heatmap_data vacía si no hay riesgos.
    try:
        max_count = heatmap_data.max().max() if not heatmap_data.empty else 0
    except AttributeError: # Si heatmap_data es un Series (e.g. 1 row/col)
        max_count = heatmap_data.max() if not heatmap_data.empty else 0
    
    for i, prob_label in enumerate(heatmap_data.index):
        for j, impact_label in enumerate(heatmap_data.columns):
            count = heatmap_data.loc[prob_label, impact_label]
            annotations.append(go.layout.Annotation(
                text=str(count),
                x=impact_label,
                y=prob_label,
                xref="x1",
                yref="y1",
                showarrow=False,
                # Ajuste del color del texto para visibilidad
                font=dict(color="white" if count > max_count / 2 and max_count > 0 else "black")
            ))
    fig.update_layout(annotations=annotations)

    return fig

def create_pareto_chart(df_risks, idioma="es"):
    if df_risks.empty:
        return None

    df_grouped = df_risks.groupby('Clasificación')['Riesgo Residual'].sum().sort_values(ascending=False).reset_index()
    df_grouped.columns = ['Clasificación', 'Suma Riesgo Residual']

    df_grouped['Porcentaje'] = (df_grouped['Suma Riesgo Residual'] / df_grouped['Suma Riesgo Residual'].sum()) * 100
    df_grouped['Porcentaje Acumulado'] = df_grouped['Porcentaje'].cumsum()

    clasificacion_label = get_text("classification_label")
    sum_residual_risk_label = get_text("sum_residual_risk_label")
    cumulative_percentage_label = get_text("cumulative_percentage_label")
    pareto_chart_title = get_text("pareto_chart_title")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_grouped[clasificacion_label if idioma == 'es' else 'Clasificación'],
        y=df_grouped['Suma Riesgo Residual'],
        name=sum_residual_risk_label,
        marker_color='skyblue',
        yaxis='y1'
    ))

    fig.add_trace(go.Scatter(
        x=df_grouped[clasificacion_label if idioma == 'es' else 'Clasificación'],
        y=df_grouped['Porcentaje Acumulado'],
        mode='lines+markers',
        name=cumulative_percentage_label,
        line=dict(color='red', dash='dot'),
        yaxis='y2'
    ))

    fig.update_layout(
        title_text=pareto_chart_title,
        xaxis_title_text=clasificacion_label,
        yaxis=dict(
            title=sum_residual_risk_label,
            side='left',
            showgrid=False,
            range=[0, df_grouped['Suma Riesgo Residual'].max() * 1.1]
        ),
        yaxis2=dict(
            title=cumulative_percentage_label,
            side='right',
            overlaying='y',
            range=[0, 100],
            tickvals=[0, 20, 40, 60, 80, 100],
            showgrid=False
        ),
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.7)', bordercolor='rgba(0,0,0,0.5)')
    )

    return fig

def plot_montecarlo_histogram(data, title, x_label, idioma="es"):
    fig = go.Figure(data=[go.Histogram(x=data, nbinsx=50, marker_color='lightgreen')])

    mean_val = np.mean(data)
    median_val = np.median(data)

    fig.add_vline(x=mean_val, line_dash="dash", line_color="blue",
                  annotation_text=f"Media: {mean_val:,.2f}", annotation_position="top right")
    fig.add_vline(x=median_val, line_dash="dot", line_color="red",
                  annotation_text=f"Mediana: {median_val:,.2f}", annotation_position="top left")

    fig.update_layout(
        title_text=title,
        xaxis_title_text=x_label,
        yaxis_title_text=get_text("frequency_label"),
        bargap=0.01
    )
    return fig


def create_sensitivity_plot(correlations_df, idioma="es"):
    if correlations_df.empty:
        return None

    correlations_df['Abs_Correlacion'] = correlations_df['Correlacion'].abs()
    correlations_df = correlations_df['Correlacion'].sort_values(ascending=True).reset_index() # Solo 'Correlacion'
    correlations_df.columns = ['Variable', 'Correlacion'] # Renombrar después del reset_index

    fig = px.bar(correlations_df,
                 x='Correlacion',
                 y='Variable',
                 orientation='h',
                 title=get_text("correlation_plot_title"),
                 labels={'Correlacion': get_text("correlation_coefficient_label"),
                         'Variable': get_text("variable_label")},
                 color='Correlacion',
                 color_continuous_scale=px.colors.sequential.RdBu
                )

    fig.update_layout(
        xaxis_title=get_text("correlation_coefficient_label"),
        yaxis_title=get_text("variable_label"),
        xaxis_range=[-1, 1]
    )
    return fig

# --- Función Dummy get_text para plotting.py (NO LA REAL DE TU APP) ---
# Esta función solo existe para que plotting.py pueda ser importado y sus funciones
# llamadas sin error si no hay un Streamlit session_state activo.
# La función get_text real de tu app está en riskapp.py y usa st.session_state.idioma
def get_text(key):
    texts_placeholder = {
        'es': {
            "risk_count_title": "Conteo de Riesgos",
            "risk_heatmap_title": "Cuadrante de Riesgos: Conteo por Categoría",
            "impact_category_label": "Categoría de Impacto",
            "probability_category_label": "Categoría de Probabilidad",
            "classification_label": "Clasificación",
            "sum_residual_risk_label": "Suma Riesgo Residual",
            "percentage_label": "Porcentaje",
            "cumulative_percentage_label": "Porcentaje Acumulado",
            "pareto_chart_title": "Análisis de Pareto por Clasificación de Riesgo",
            "frequency_label": "Frecuencia",
            "correlation_plot_title": "Análisis de Sensibilidad: Correlación con Riesgo Residual",
            "correlation_coefficient_label": "Coeficiente de Correlación",
            "variable_label": "Variable",
            "histogram_risk_title": "Distribución del Riesgo Residual Simulado",
            "risk_value_label": "Valor del Riesgo Residual",
            "histogram_losses_title": "Distribución de Pérdidas Económicas Simuladas",
            "losses_value_label": "Valor de la Pérdida Económica",
            "factor": "Factor"
        },
        'en': {
            "risk_count_title": "Risk Count",
            "risk_heatmap_title": "Risk Quadrant: Count by Category",
            "impact_category_label": "Impact Category",
            "probability_category_label": "Probability Category",
            "classification_label": "Classification",
            "sum_residual_risk_label": "Sum of Residual Risk",
            "percentage_label": "Percentage",
            "cumulative_percentage_label": "Cumulative Percentage",
            "pareto_chart_title": "Pareto Analysis by Risk Classification",
            "frequency_label": "Frequency",
            "correlation_plot_title": "Sensitivity Analysis: Correlation with Residual Risk",
            "correlation_coefficient_label": "Correlation Coefficient",
            "variable_label": "Variable",
            "histogram_risk_title": "Simulated Residual Risk Distribution",
            "risk_value_label": "Residual Risk Value",
            "histogram_losses_title": "Simulated Economic Losses Distribution",
            "losses_value_label": "Economic Loss Value",
            "factor": "Factor"
        }
    }
    # En tu app, la función real get_text en riskapp.py toma el idioma de session_state.
    # Aquí es solo un fallback para pruebas o si plotting.py se usa solo.
    return texts_placeholder.get('es', {}).get(key, key)
