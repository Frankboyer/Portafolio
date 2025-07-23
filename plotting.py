import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.express as px

# Asegúrate de que matriz_probabilidad y matriz_impacto se importen o definan aquí
# si create_heatmap los necesita directamente y no se pasan como argumentos desde riskapp.py
# (En tu riskapp.py actual, se pasan como argumentos, lo cual es correcto).

def create_heatmap(df_risks, matriz_probabilidad, matriz_impacto, idioma="es"):
    if df_risks.empty:
        return None

    df_risks_copy = df_risks.copy()

    # --- Clasificación de Probabilidad para el Heatmap ---
    # La columna 'Probabilidad' en df_risks_copy ya debería ser el factor numérico (ej. 0.0 a 1.0)

    # 1. Definir los bordes de los bins para Probabilidad.
    # Queremos incluir el mínimo y el máximo de todos los rangos para formar los bordes.
    # sorted() para asegurar el orden.
    # El primer borde será el mínimo global (ej., 0.0), y el último el máximo global (ej., 1.0).
    prob_bins_edges = sorted(list(matriz_probabilidad['Rango Min'].unique()) + [matriz_probabilidad['Rango Max'].max()])

    # 2. Definir las etiquetas para los bins de Probabilidad.
    # Estas son las clasificaciones que ya tienes.
    prob_labels = matriz_probabilidad['Clasificacion'].tolist()

    # **Verificación crucial:** La cantidad de etiquetas debe ser (bordes - 1)
    # Si tus rangos son continuos y los bordes se definen correctamente,
    # len(prob_bins_edges) debería ser len(prob_labels) + 1.
    if len(prob_labels) != len(prob_bins_edges) - 1:
        # Esto indica un problema en cómo matriz_probabilidad define sus rangos/clasificaciones.
        # Podría ser que hay rangos superpuestos, gaps, o el mínimo/máximo no se capturan bien.
        # Para forzar la compatibilidad y evitar el error, podemos ajustar los bordes o las etiquetas.
        # Una solución robusta es crear bordes de forma que siempre haya un bin menos que etiquetas.
        # Si tus etiquetas son "Muy Bajo", "Bajo", "Medio", "Alto", "Muy Alto" (5 etiquetas),
        # entonces necesitas 6 bordes.

        # Vamos a construir los bins de forma más explícita para asegurar la consistencia.
        # Asumimos que la columna 'Factor' en factor_probabilidad (usada en otro lugar)
        # define los puntos centrales o los puntos que separan las clasificaciones.
        # Sin embargo, para `pd.cut`, necesitamos bordes.
        # La forma más segura es usar los rangos min y max de tu matriz_probabilidad:
        # Asegúrate de que los rangos son como [0.0, 0.2), [0.2, 0.4), etc.
        # Si son como [0.0, 0.2] y [0.21, 0.40], pd.cut podría tener problemas con los gaps.
        # La mejor práctica es hacer los bordes contiguos para pd.cut.

        # Opción 1: Reconstruir bins de forma que coincidan con las etiquetas, asumiendo rangos continuos
        # Esto crea bins basados en la cantidad de clasificaciones.
        # Si tienes 5 clasificaciones, tendrás 5 bins. Necesitas 6 bordes.
        # Esto es más seguro si tus clasificaciones son equitativas o si quieres forzar N bins.
        min_prob = df_risks_copy['Probabilidad'].min() if not df_risks_copy.empty else 0.0
        max_prob = df_risks_copy['Probabilidad'].max() if not df_risks_copy.empty else 1.0

        # Ajuste para asegurarnos de que el rango sea de 0 a 1.
        min_prob_global = matriz_probabilidad['Rango Min'].min()
        max_prob_global = matriz_probabilidad['Rango Max'].max()

        # Genera bins equidistantes o usa los rangos definidos para crear los N+1 bordes.
        # Los bordes deben ser el "Rango Min" de cada clasificación más el "Rango Max" del último.
        prob_bins_edges = sorted(matriz_probabilidad['Rango Min'].tolist() + [matriz_probabilidad['Rango Max'].max()])
        prob_labels = matriz_probabilidad['Clasificacion'].tolist()

        # Si aún hay un desajuste, es porque tus rangos en matriz_probabilidad no forman intervalos
        # contiguos adecuados para pd.cut directamente con solo los 'Rango Min' y el 'Rango Max' final.
        # La solución más simple y robusta es forzar la creación de N+1 bordes.
        if len(prob_labels) != len(prob_bins_edges) - 1:
            # Crear bins basados en el número de etiquetas. Por ejemplo, si hay 5 etiquetas, crear 5 bins (6 bordes).
            # Esto asume que la 'Probabilidad' está normalizada entre 0 y 1.
            prob_bins_edges = np.linspace(min_prob_global, max_prob_global, len(prob_labels) + 1).tolist()
            # Esta solución es más genérica y puede ser menos precisa si tus rangos no son equitativos.
            # Pero asegura que el número de bordes y etiquetas sea correcto para pd.cut.


    # Crear la columna 'Prob_Bin'
    df_risks_copy['Prob_Bin'] = pd.cut(df_risks_copy['Probabilidad'],
                                       bins=prob_bins_edges,
                                       labels=prob_labels,
                                       right=True,
                                       include_lowest=True) # include_lowest=True para asegurar que el valor mínimo (0.0) esté incluido


    # --- Clasificación de Impacto Numérico para el Heatmap ---
    # Esto asume que 'Impacto Numérico' está en un rango 0-100.
    # Definir los bordes de los bins para impacto (0-100)
    # Similar a probabilidad, obtenemos los bordes de matriz_impacto.
    impact_bins_edges = sorted(list(matriz_impacto['Rango Min'].unique()) + [matriz_impacto['Rango Max'].max()])
    impact_labels = matriz_impacto['Clasificacion'].tolist()

    # **Verificación crucial para Impacto:**
    if len(impact_labels) != len(impact_bins_edges) - 1:
        min_impact_global = matriz_impacto['Rango Min'].min()
        max_impact_global = matriz_impacto['Rango Max'].max()
        impact_bins_edges = np.linspace(min_impact_global, max_impact_global, len(impact_labels) + 1).tolist()


    # Crear la columna 'Impact_Bin'
    df_risks_copy['Impact_Bin'] = pd.cut(df_risks_copy['Impacto Numérico'],
                                        bins=impact_bins_edges,
                                        labels=impact_labels,
                                        right=True,
                                        include_lowest=True) # include_lowest=True para incluir el 0

    # --- Crear la Matriz para el Heatmap ---
    # Contar la frecuencia de riesgos en cada intersección de bin
    heatmap_data = df_risks_copy.groupby(['Prob_Bin', 'Impact_Bin']).size().unstack(fill_value=0)

    # Reindexar para asegurar el orden correcto de las etiquetas en el heatmap
    # Esto es vital para que el heatmap se muestre correctamente.
    # Asegúrate de que las clasificaciones estén ordenadas en matriz_probabilidad y matriz_impacto
    # para que esta reindexación funcione.
    ordered_prob_labels = matriz_probabilidad['Clasificacion'].tolist()
    ordered_impact_labels = matriz_impacto['Clasificacion'].tolist()

    # Reindexar la matriz para asegurar que todas las combinaciones posibles estén presentes
    # y en el orden correcto, rellenando con 0 donde no haya riesgos.
    heatmap_data = heatmap_data.reindex(index=ordered_prob_labels, columns=ordered_impact_labels, fill_value=0)

    # --- Creación del Heatmap con Plotly ---
    # Asignar colores de criticidad al heatmap
    # Esto requiere una lógica que asocie cada celda del heatmap (combinación Prob_Bin, Impact_Bin)
    # con un nivel de criticidad y su color.
    # Por ahora, haremos un heatmap de conteo. Si quieres color por criticidad,
    # necesitarías calcular la criticidad promedio para cada bin y luego mapear a colores.

    # Aquí usaremos un heatmap simple de conteo.
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='Viridis', # Puedes elegir otra escala de color, ej: 'Blues', 'Greens'
        colorbar=dict(title=f"{get_text('risk_count_title')}")
    ))

    # Actualizar layout para títulos y etiquetas
    fig.update_layout(
        title=f"{get_text('risk_heatmap_title')}",
        xaxis_title=f"{get_text('impact_category_label')}",
        yaxis_title=f"{get_text('probability_category_label')}",
        xaxis=dict(side="top"), # Mover etiquetas de impacto a la parte superior
        yaxis=dict(autorange="reversed") # Invertir el eje Y para que "Muy Alto" esté arriba
    )

    # Añadir texto a las celdas
    annotations = []
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
                font=dict(color="white" if count > heatmap_data.max().max() / 2 else "black") # Color de texto dinámico
            ))
    fig.update_layout(annotations=annotations)

    return fig


# Función dummy get_text para que plotting.py no dependa de Streamlit directamente para los textos.
# Idealmente, esta función se pasaría como argumento o se importaría de un módulo compartido.
# Para que el código sea ejecutable de forma independiente para pruebas:
def get_text(key):
    texts = {
        'es': {
            "risk_count_title": "Conteo de Riesgos",
            "risk_heatmap_title": "Cuadrante de Riesgos: Conteo por Categoría",
            "impact_category_label": "Categoría de Impacto",
            "probability_category_label": "Categoría de Probabilidad"
        },
        'en': {
            "risk_count_title": "Risk Count",
            "risk_heatmap_title": "Risk Quadrant: Count by Category",
            "impact_category_label": "Impact Category",
            "probability_category_label": "Probability Category"
        }
    }
    # Esto es solo para que plotting.py no falle si se ejecuta solo.
    # En tu aplicación real, st.session_state.idioma ya estaría disponible.
    current_lang = 'es' # O st.session_state.idioma si está disponible
    return texts[current_lang].get(key, key)


# --- Resto de las funciones en plotting.py (create_pareto_chart, etc.) se mantienen igual ---

def create_pareto_chart(df_risks, idioma="es"):
    if df_risks.empty:
        return None

    # Agrupar por Clasificación y sumar el Riesgo Residual
    df_grouped = df_risks.groupby('Clasificación')['Riesgo Residual'].sum().sort_values(ascending=False).reset_index()
    df_grouped.columns = ['Clasificación', 'Suma Riesgo Residual']

    # Calcular porcentaje y porcentaje acumulado
    df_grouped['Porcentaje'] = (df_grouped['Suma Riesgo Residual'] / df_grouped['Suma Riesgo Residual'].sum()) * 100
    df_grouped['Porcentaje Acumulado'] = df_grouped['Porcentaje'].cumsum()

    # Obtener textos según el idioma
    clasificacion_label = get_text("classification_label")
    sum_residual_risk_label = get_text("sum_residual_risk_label")
    percentage_label = get_text("percentage_label")
    cumulative_percentage_label = get_text("cumulative_percentage_label")
    pareto_chart_title = get_text("pareto_chart_title")

    fig = go.Figure()

    # Barra para la suma del riesgo residual
    fig.add_trace(go.Bar(
        x=df_grouped[clasificacion_label if idioma == 'es' else 'Clasificación'], # Ajustar si tu Clasificación cambia con el idioma
        y=df_grouped['Suma Riesgo Residual'],
        name=sum_residual_risk_label,
        marker_color='skyblue',
        yaxis='y1'
    ))

    # Línea para el porcentaje acumulado
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
            range=[0, df_grouped['Suma Riesgo Residual'].max() * 1.1] # Ajustar el rango Y
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

    # Calcular estadísticas básicas
    mean_val = np.mean(data)
    median_val = np.median(data)
    std_val = np.std(data)

    # Añadir líneas para media y mediana
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

    # Convertir a Matplotlib Figure para compatibilidad con st.pyplot
    # Plotly figures are not directly compatible with st.pyplot.
    # If you intend to use st.plotly_chart, return fig directly.
    # If you intend to use st.pyplot, you'd need to convert,
    # or just use plotly_chart directly. Given you're importing matplotlib,
    # let's assume you wanted matplotlib plots.
    # For now, I'll return the plotly figure and suggest using st.plotly_chart.

    # Si tu intención es usar `st.pyplot(fig_riesgo)` como en riskapp.py,
    # entonces necesitas una figura de Matplotlib.
    # Si quieres usar Plotly, usa `st.plotly_chart(fig_riesgo)`.
    # Dado el contexto, asumo que quieres mantener Plotly ya que estás importando go.
    # Cambia st.pyplot a st.plotly_chart en riskapp.py para estas figuras.
    # O si de verdad quieres Matplotlib, tendrías que reescribir esta función para usar plt.
    # Por ahora, devuelvo la figura de Plotly.

    # Si se requiere Matplotlib:
    # fig_mpl, ax_mpl = plt.subplots()
    # ax_mpl.hist(data, bins=50, color='lightgreen', edgecolor='black')
    # ax_mpl.axvline(mean_val, color='blue', linestyle='dashed', linewidth=1, label=f'Mean: {mean_val:,.2f}')
    # ax_mpl.axvline(median_val, color='red', linestyle='dotted', linewidth=1, label=f'Median: {median_val:,.2f}')
    # ax_mpl.set_title(title)
    # ax_mpl.set_xlabel(x_label)
    # ax_mpl.set_ylabel(get_text("frequency_label"))
    # ax_mpl.legend()
    # return fig_mpl
    #
    # Por ahora, asumo que quieres usar plotly, por lo que devolveré la figura de plotly.
    # Si recibes un error de "TypeError: Object of type Figure is not JSON serializable"
    # al pasar la figura de plotly a st.pyplot, es porque debes usar st.plotly_chart.
    return fig


def create_sensitivity_plot(correlations_df, idioma="es"):
    if correlations_df.empty:
        return None

    # Columnas esperadas: 'Variable', 'Correlacion'
    # Ordenar por el valor absoluto de correlación
    correlations_df['Abs_Correlacion'] = correlations_df['Correlacion'].abs()
    correlations_df = correlations_df.sort_values(by='Abs_Correlacion', ascending=True)

    fig = px.bar(correlations_df,
                 x='Correlacion',
                 y='Variable',
                 orientation='h',
                 title=get_text("correlation_plot_title"),
                 labels={'Correlacion': get_text("correlation_coefficient_label"),
                         'Variable': get_text("variable_label")},
                 color='Correlacion',
                 color_continuous_scale=px.colors.sequential.RdBu # Rojo-Azul para mostrar positivos/negativos
                )

    fig.update_layout(
        xaxis_title=get_text("correlation_coefficient_label"),
        yaxis_title=get_text("variable_label"),
        xaxis_range=[-1, 1] # Rango de correlación de -1 a 1
    )
    return fig

# Extension del dummy get_text para que las funciones arriba tengan los textos necesarios.
def get_text(key):
    # Esto es solo para que plotting.py no falle si se ejecuta solo o en un test.
    # En tu aplicación real, st.session_state.idioma ya estaría disponible para riskapp.py
    # y los textos vendrían del módulo data_config.
    texts_placeholder = {
        'es': {
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
            "factor": "Factor" # Añadido para los mensajes métricos
            # Asegúrate de que todos los textos usados en las funciones de plotting estén aquí si no se importan globalmente
        },
        'en': {
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
    # En tu aplicación, la función get_text de riskapp.py ya tomará el idioma de session_state.
    # Aquí, para que plotting.py sea autocontenido, usamos un placeholder.
    # Si ejecutas plotting.py directamente, el idioma será 'es' por defecto.
    return texts_placeholder.get('es', {}).get(key, key)
