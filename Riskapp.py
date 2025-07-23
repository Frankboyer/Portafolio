import pandas as pd

# Tablas base para el modelo de riesgo
tabla_tipo_impacto = pd.DataFrame({
    'Tipo de Impacto': ['Humano', 'Operacional', 'Económico', 'Reputacional', 'Legal'],
    'Ponderación': [25, 20, 30, 15, 10], # Suma 100
    'Explicación ASIS': [
        'Afectación a la vida, salud o seguridad de personas.',
        'Interrupción o degradación de procesos y funciones del negocio.',
        'Pérdidas financieras directas o indirectas.',
        'Daño a la imagen, confianza o credibilidad de la organización.',
        'Incumplimiento de leyes, regulaciones o contratos.'
    ]
})

matriz_probabilidad = pd.DataFrame({
    'Clasificacion': ['Muy Baja', 'Baja', 'Media', 'Alta', 'Muy Alta'],
    'Valor': [0.1, 0.3, 0.5, 0.7, 0.9],
    'Definición': [
        'Probabilidad de ocurrencia menor al 10%',
        'Probabilidad de ocurrencia entre 10% y 30%',
        'Probabilidad de ocurrencia entre 30% y 50%',
        'Probabilidad de ocurrencia entre 50% y 70%',
        'Probabilidad de ocurrencia mayor al 70%'
    ]
})

matriz_impacto = pd.DataFrame({
    'Clasificacion': ['Insignificante', 'Menor', 'Moderado', 'Mayor', 'Catastrófico'],
    'Valor': [1, 2, 3, 4, 5], # Para mapeo interno si es necesario, aunque el slider es el principal
    'Definición': [
        'Daño mínimo, fácilmente recuperable.',
        'Daño localizado, impacto limitado.',
        'Daño significativo, impacto moderado en áreas clave.',
        'Daño extenso, impacto severo en la operación.',
        'Daño crítico, amenaza la viabilidad de la organización.'
    ]
})

factor_exposicion = pd.DataFrame({
    'Clasificacion': ['Baja', 'Media', 'Alta'],
    'Factor': [0.3, 0.6, 0.9],
    'Definición': [
        'Contacto con la amenaza es ocasional o nulo.',
        'Contacto con la amenaza es frecuente o regular.',
        'Contacto con la amenaza es constante o inevitable.'
    ]
})

factor_probabilidad = pd.DataFrame({
    'Clasificacion': ['Baja', 'Media', 'Alta'],
    'Factor': [0.3, 0.6, 0.9],
    'Definición': [
        'La probabilidad de que una amenaza se materialice es baja.',
        'La probabilidad de que una amenaza se materialice es media.',
        'La probabilidad de que una amenaza se materialice es alta.'
    ]
})

efectividad_controles = pd.DataFrame({
    'Efectividad': ['Inefectiva', 'Parcialmente Efectiva', 'Efectiva', 'Muy Efectiva'],
    'Rango % Min': [0, 26, 51, 76],
    'Rango % Max': [25, 50, 75, 100],
    'Factor': [0.1, 0.3, 0.7, 0.9], # Factor para reducir el riesgo
    'Mitigacion': [
        'Los controles no reducen significativamente el riesgo.',
        'Los controles ofrecen una reducción limitada del riesgo.',
        'Los controles reducen el riesgo de manera considerable.',
        'Los controles casi eliminan el riesgo.'
    ]
})

criticidad_límites = [
    (0, 0.1, 'ACEPTABLE', '#28a745', 'ACCEPTABLE'), # Verde
    (0.1, 0.2, 'TOLERABLE', '#90EE90', 'TOLERABLE'), # Verde Claro
    (0.2, 0.4, 'MODERADO', '#ffc107', 'MODERATE'), # Amarillo
    (0.4, 0.6, 'ALTO', '#fd7e14', 'HIGH'), # Naranja
    (0.6, 1.0, 'CRÍTICO', '#dc3545', 'CRITICAL')  # Rojo
]

# Diccionario para manejo de múltiples idiomas
textos = {
    "es": {
        "sidebar_language_toggle": "English",
        "app_title": "Calculadora de Riesgos y Simulador Monte Carlo",
        "tax_info_title": "Consideraciones sobre Impuestos",
        "tax_info_text": "Las implicaciones fiscales de las pérdidas por riesgos pueden ser complejas y varían significativamente según la jurisdicción y el tipo de negocio. Esta sección proporciona información general. Es crucial consultar a un asesor fiscal profesional para comprender cómo las pérdidas relacionadas con riesgos podrían afectar su situación fiscal específica, incluyendo posibles deducciones, créditos o tratamientos contables. Factores como la naturaleza de la pérdida (ej. operativa vs. capital), la estructura legal de la entidad y las leyes fiscales locales e internacionales son determinantes. Este simulador no ofrece asesoramiento fiscal.",
        "risk_input_form_title": "1. Entrada de Datos del Riesgo",
        "risk_name": "Nombre del Riesgo",
        "risk_description": "Descripción Detallada del Riesgo",
        "risk_type_impact": "Tipo de Impacto Principal",
        "risk_probability": "Probabilidad de Ocurrencia (Amenaza Inherente)",
        "risk_exposure": "Exposición (Amenaza Inherente)",
        "risk_impact_numeric": "Impacto Numérico (0-100)",
        "risk_control_effectiveness": "Efectividad del Control (%)",
        "risk_deliberate_threat": "¿Amenaza Deliberada?",
        "add_risk_button": "Agregar Riesgo",
        "error_risk_name_empty": "Por favor, ingresa un nombre para el riesgo.",
        "success_risk_added": "Riesgo agregado exitosamente.",
        "deterministic_results_title": "2. Resultados del Modelo Determinista",
        "inherent_threat": "Amenaza Inherente",
        "residual_threat": "Amenaza Residual",
        "adjusted_residual_threat": "Amenaza Residual Ajustada",
        "residual_risk": "Riesgo Residual",
        "classification": "Clasificación",
        "montecarlo_input_title": "3. Configuración de Simulación Monte Carlo",
        "economic_value_asset": "Valor Económico del Activo Bajo Riesgo (USD)",
        "num_iterations": "Número de Iteraciones Monte Carlo",
        "run_montecarlo_button": "Lanzar Simulación Monte Carlo",
        "montecarlo_results_title": "4. Resultados de la Simulación Monte Carlo",
        "expected_loss": "Pérdida Esperada (Media)",
        "median_loss": "Pérdida Mediana (Percentil 50)",
        "p5_loss": "Pérdida del Percentil 5",
        "p90_loss": "Pérdida del Percentil 90",
        "max_loss": "Máxima Pérdida Simulada",
        "cvar_95": "CVaR (95% - Cola de Riesgo)",
        "sensitivity_analysis_title": "Análisis de Sensibilidad (Correlación con Pérdida Económica)",
        "added_risks_title": "5. Riesgos Evaluados Acumulados",
        "download_excel_button": "Descargar Datos a Excel",
        "no_risks_yet": "Aún no se han agregado riesgos.",
        "risk_heatmap_title": "6. Mapa de Calor de Riesgos (Modelo Determinista)",
        "risk_pareto_chart_title": "7. Gráfico de Pareto de Riesgos",
        "risk_distribution_title": "8. Distribución del Riesgo Residual Simulado (Índice)",
        "economic_loss_distribution_title": "9. Distribución de Pérdidas Económicas Simuladas (USD)",
        "edit_risk": "Editar",
        "delete_risk": "Eliminar",
        "confirm_delete": "¿Estás seguro de que quieres eliminar este riesgo?",
        "risk_deleted": "Riesgo eliminado exitosamente."

    },
    "en": {
        "sidebar_language_toggle": "Español",
        "app_title": "Risk Calculator and Monte Carlo Simulator",
        "tax_info_title": "Tax Considerations",
        "tax_info_text": "The tax implications of risk losses can be complex and vary significantly by jurisdiction and business type. This section provides general information. It is crucial to consult a professional tax advisor to understand how risk-related losses might affect your specific tax situation, including potential deductions, credits, or accounting treatments. Factors such as the nature of the loss (e.g., operational vs. capital), the legal structure of the entity, and local and international tax laws are determining factors. This simulator does not provide tax advice.",
        "risk_input_form_title": "1. Risk Data Input",
        "risk_name": "Risk Name",
        "risk_description": "Detailed Risk Description",
        "risk_type_impact": "Primary Impact Type",
        "risk_probability": "Probability of Occurrence (Inherent Threat)",
        "risk_exposure": "Exposure (Inherent Threat)",
        "risk_impact_numeric": "Numeric Impact (0-100)",
        "risk_control_effectiveness": "Control Effectiveness (%)",
        "risk_deliberate_threat": "Deliberate Threat?",
        "add_risk_button": "Add Risk",
        "error_risk_name_empty": "Please enter a name for the risk.",
        "success_risk_added": "Risk added successfully.",
        "deterministic_results_title": "2. Deterministic Model Results",
        "inherent_threat": "Inherent Threat",
        "residual_threat": "Residual Threat",
        "adjusted_residual_threat": "Adjusted Residual Threat",
        "residual_risk": "Residual Risk",
        "classification": "Classification",
        "montecarlo_input_title": "3. Monte Carlo Simulation Setup",
        "economic_value_asset": "Economic Value of Asset at Risk (USD)",
        "num_iterations": "Number of Monte Carlo Iterations",
        "run_montecarlo_button": "Run Monte Carlo Simulation",
        "montecarlo_results_title": "4. Monte Carlo Simulation Results",
        "expected_loss": "Expected Loss (Mean)",
        "median_loss": "Median Loss (50th Percentile)",
        "p5_loss": "5th Percentile Loss",
        "p90_loss": "90th Percentile Loss",
        "max_loss": "Maximum Simulated Loss",
        "cvar_95": "CVaR (95% - Tail Risk)",
        "sensitivity_analysis_title": "Sensitivity Analysis (Correlation with Economic Loss)",
        "added_risks_title": "5. Accumulated Evaluated Risks",
        "download_excel_button": "Download Data to Excel",
        "no_risks_yet": "No risks have been added yet.",
        "risk_heatmap_title": "6. Risk Heatmap (Deterministic Model)",
        "risk_pareto_chart_title": "7. Risk Pareto Chart",
        "risk_distribution_title": "8. Simulated Residual Risk Distribution (Index)",
        "economic_loss_distribution_title": "9. Simulated Economic Loss Distribution (USD)",
        "edit_risk": "Edit",
        "delete_risk": "Delete",
        "confirm_delete": "Are you sure you want to delete this risk?",
        "risk_deleted": "Risk deleted successfully."
    }
}



#2 modulo
import numpy as np
import pandas as pd
from data_config import criticidad_límites # Importar desde el nuevo archivo

def clasificar_criticidad(valor, idioma="es"):
    """
    Clasifica un valor numérico de riesgo en una categoría de criticidad
    y asigna un color asociado.
    """
    for v_min, v_max, clasificacion_es, color, clasificacion_en in criticidad_límites:
        if v_min <= valor <= v_max:
            if idioma == "es":
                return clasificacion_es, color
            else:
                return clasificacion_en, color
    return "DESCONOCIDO", "#cccccc" # Default si no se encuentra en ningún rango

def calcular_criticidad(probabilidad, exposicion, amenaza_deliberada_factor, efectividad, valor_impacto_numerico, ponderacion_impacto):
    """
    Calcula las diferentes métricas de riesgo basadas en un modelo determinista.
    """
    try:
        # Asegurarse de que los valores numéricos estén en el rango correcto
        probabilidad = float(probabilidad)
        exposicion = float(exposicion)
        amenaza_deliberada_factor = float(amenaza_deliberada_factor)
        efectividad = float(efectividad) / 100.0 # Convertir porcentaje a factor (0-1)
        valor_impacto_numerico = float(valor_impacto_numerico)
        ponderacion_impacto = float(ponderacion_impacto)

        # Normalizar el impacto numérico y la ponderación para la fórmula
        # El impacto numérico (0-100) se normaliza a un factor de 0-1
        impacto_norm = valor_impacto_numerico / 100.0 if valor_impacto_numerico > 0 else 0
        # La ponderación del impacto (ej. 25 para humano) se normaliza a un factor de 0-1
        ponderacion_factor = ponderacion_impacto / 100.0

        # Cálculos de riesgo
        amenaza_inherente = probabilidad * exposicion
        amenaza_residual = amenaza_inherente * (1 - efectividad)

        # Si amenaza_deliberada_factor es 0 (No), no ajusta; si es 1 (Sí), multiplica
        amenaza_residual_ajustada = amenaza_residual * (1 + amenaza_deliberada_factor) # Si es 0, es 1, si es 1, es 2
        # Considerar si quieres que una amenaza deliberada multiplique por 1 (es decir, el mismo valor si es 'Si')
        # o por un factor mayor a 1. Aquí, 1 para 'Sí' significa que no se ajusta, 2 para 'Sí' lo duplica.
        # Ajuste a la lógica original: si amenaza_deliberada_factor es 1 (Sí), duplica amenaza_residual
        # Si es 0 (No), mantiene amenaza_residual.
        amenaza_residual_ajustada = amenaza_residual * (1 + amenaza_deliberada_factor)

        # El riesgo residual final se calcula combinando la amenaza ajustada con el impacto y la ponderación
        riesgo_residual = amenaza_residual_ajustada * impacto_norm * ponderacion_factor

        # Asegurar que el riesgo residual no exceda 1
        riesgo_residual = np.clip(riesgo_residual, 0, 1)

        return amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual

    except Exception as e:
        print(f"Error en calcular_criticidad: {e}")
        return 0.0, 0.0, 0.0, 0.0 # Retornar valores seguros en caso de error

def simular_montecarlo(probabilidad_base, exposicion_base, impacto_numerico_base, efectividad_base_pct, amenaza_deliberada_factor_base, ponderacion_impacto, valor_economico, iteraciones=10000):
    """
    Ejecuta una simulación Monte Carlo para el cálculo de riesgos y pérdidas económicas.
    """
    if valor_economico <= 0:
        return np.array([]), np.array([]), None, None # Retornar arrays vacíos si el valor económico es 0 o negativo

    try:
        # Convertir efectividad de porcentaje a factor
        efectividad_base = efectividad_base_pct / 100.0
        
        # Parámetros de variabilidad para cada factor (desviación estándar)
        # Ajustar sigmas según la incertidumbre deseada
        sigma_probabilidad = 0.1 # Pequeña variabilidad para probabilidades
        sigma_exposicion = 0.1
        sigma_impacto_norm = 0.05 # Menor variabilidad para impacto ya normalizado 0-1
        sigma_efectividad = 0.1
        # sigma_amenaza_deliberada = 0 # Normalmente binario, no se simula variabilidad aquí

        # Impacto monetario (USD)
        # Si el impacto_numerico_base va de 0-100, se puede mapear a un rango de pérdida monetaria
        # Por ejemplo, un impacto de 100 significa el 100% del valor económico se pierde.
        # Vamos a asumir que el 'impacto_numerico_base' de 0-100 es un porcentaje de daño al 'valor_economico'
        # o que el usuario introducirá V_min y V_max para las pérdidas, como en la petición.

        # Nueva lógica para el impacto de Monte Carlo: rangos en USD
        # Usaremos el impacto_numerico_base (0-100) para definir un rango de pérdida monetaria base.
        # Por ejemplo, si impacto_numerico_base es 50, la pérdida base es 50% del valor económico.
        # Luego, simulamos alrededor de ese valor base.
        # Definiremos un rango de incertidumbre para la pérdida monetaria.
        
        # Transformamos el impacto numérico base (0-100) en un porcentaje del valor económico
        # Esto es un factor base para la pérdida económica.
        factor_perdida_base = impacto_numerico_base / 100.0

        # Definimos un rango de incertidumbre para este factor de pérdida monetaria.
        # Por ejemplo, +/- 20% del factor de pérdida base.
        sigma_factor_perdida = 0.20 * factor_perdida_base
        if sigma_factor_perdida == 0 and factor_perdida_base > 0: # Evitar sigma 0 si hay impacto
             sigma_factor_perdida = 0.05 # Mínima variabilidad si el impacto es bajo pero existente
        elif factor_perdida_base == 0:
            sigma_factor_perdida = 0 # No hay variabilidad si no hay impacto base

        # Arrays para almacenar los resultados de la simulación
        riesgo_residual_sim = np.zeros(iteraciones)
        perdidas_usd_sim = np.zeros(iteraciones)

        for i in range(iteraciones):
            # Generar valores aleatorios para cada parámetro usando una distribución normal
            # y asegurándose de que estén dentro de rangos lógicos [0,1] o [1,100]
            probabilidad_sim = np.clip(np.random.normal(probabilidad_base, sigma_probabilidad), 0.01, 1.0)
            exposicion_sim = np.clip(np.random.normal(exposicion_base, sigma_exposicion), 0.01, 1.0)
            efectividad_sim = np.clip(np.random.normal(efectividad_base, sigma_efectividad), 0.0, 1.0)

            # Simular el factor de pérdida monetaria
            sim_factor_perdida = np.clip(np.random.normal(factor_perdida_base, sigma_factor_perdida), 0.0, 1.0)
            
            # Recalcular impacto_norm para la simulación
            # Usamos el factor de pérdida simulado como el impacto_norm para la fórmula
            impacto_norm_sim = sim_factor_perdida

            # Amenaza deliberada se mantiene base o se puede introducir una probabilidad binaria
            amenaza_deliberada_sim = amenaza_deliberada_factor_base # Asumimos que no varía en la simulación a menos que se indique

            # Reutilizar la lógica de cálculo de riesgo con los valores simulados
            amenaza_inherente_sim = probabilidad_sim * exposicion_sim
            amenaza_residual_sim = amenaza_inherente_sim * (1 - efectividad_sim)
            amenaza_residual_ajustada_sim = amenaza_residual_sim * (1 + amenaza_deliberada_sim)
            
            # Calcular el riesgo residual simulado
            riesgo_residual_iter = amenaza_residual_ajustada_sim * impacto_norm_sim * (ponderacion_impacto / 100.0)
            riesgo_residual_sim[i] = np.clip(riesgo_residual_iter, 0, 1)

            # Calcular la pérdida económica simulada
            perdidas_usd_sim[i] = riesgo_residual_sim[i] * valor_economico # El riesgo residual es un índice de criticidad que se aplica al valor económico

        # Calcular correlaciones para análisis de sensibilidad
        df_sim = pd.DataFrame({
            'probabilidad': np.array([np.random.normal(probabilidad_base, sigma_probabilidad) for _ in range(iteraciones)]),
            'exposicion': np.array([np.random.normal(exposicion_base, sigma_exposicion) for _ in range(iteraciones)]),
            'impacto_norm': np.array([np.random.normal(factor_perdida_base, sigma_factor_perdida) for _ in range(iteraciones)]),
            'efectividad': np.array([np.random.normal(efectividad_base, sigma_efectividad) for _ in range(iteraciones)]),
            'perdida_usd': perdidas_usd_sim
        })
        
        # Calcular correlaciones de Pearson con la pérdida económica
        # Asegurarse de que las columnas tengan varianza para calcular correlación
        valid_cols = [col for col in ['probabilidad', 'exposicion', 'impacto_norm', 'efectividad'] if df_sim[col].std() > 0]
        
        if valid_cols:
            correlations = df_sim[valid_cols + ['perdida_usd']].corr(method='pearson')['perdida_usd'].drop('perdida_usd').abs().sort_values(ascending=False)
        else:
            correlations = pd.Series(dtype=float) # No hay columnas válidas para correlación

        # Correlación de Spearman puede ser más robusta para relaciones no lineales
        # correlations_spearman = df_sim[valid_cols + ['perdida_usd']].corr(method='spearman')['perdida_usd'].drop('perdida_usd').abs().sort_values(ascending=False)

        return riesgo_residual_sim, perdidas_usd_sim, correlations #, correlations_spearman

    except Exception as e:
        print(f"Error en simular_montecarlo: {e}")
        return np.array([]), np.array([]), None, None # Retornar arrays vacíos y None para correlaciones

#3er modulo 

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
    colorscale = []

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

    # Crear una escala de colores personalizada para el heatmap
    # Normalizar los límites de criticidad a un rango de 0 a 1 para Plotly
    for i, (v_min, v_max, _, color, _) in enumerate(criticidad_límites):
        colorscale.append([v_min, color])
        if i < len(criticidad_límites) - 1:
            colorscale.append([v_max, color])
    # Asegurar que el último límite superior también tenga su color
    colorscale.append([criticidad_límites[-1][1], criticidad_límites[-1][3]])


    # Crear el heatmap con Plotly
    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=impact_labels,
        y=prob_labels,
        text=text_values,
        texttemplate="%{text}",
        hoverinfo="text",
        colorscale=[[limit[0], limit[1]] for limit in criticidad_límites], # Utilizar los límites y colores de criticidad_límites
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
    Crea un gráfico de barras para el análisis de sensibilidad.
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
    
    #4 to modulo 
    
    import streamlit as st
import pandas as pd
from data_config import criticidad_límites

def reset_form_fields():
    """Reinicia los campos del formulario de entrada de riesgo."""
    st.session_state['risk_name_input'] = ""
    st.session_state['risk_description_input'] = ""
    st.session_state['selected_type_impact'] = st.session_state['default_type_impact']
    st.session_state['selected_probabilidad'] = st.session_state['default_probabilidad']
    st.session_state['selected_exposicion'] = st.session_state['default_exposicion']
    st.session_state['impacto_numerico_slider'] = st.session_state['default_impacto_numerico']
    st.session_state['control_effectiveness_slider'] = st.session_state['default_control_effectiveness']
    st.session_state['deliberate_threat_checkbox'] = False
    st.session_state['current_edit_index'] = -1 # Asegurarse de que no estamos en modo edición


def format_risk_dataframe(df_risks, idioma="es"):
    """
    Formatea el DataFrame de riesgos para una mejor visualización en Streamlit,
    aplicando colores de criticidad.
    """
    if df_risks.empty:
        return df_risks

    def get_color(val):
        for v_min, v_max, _, color, _ in criticidad_límites:
            if v_min <= val <= v_max:
                return f'background-color: {color};'
        return ''

    styled_df = df_risks.style.applymap(get_color, subset=['Riesgo Residual'])

    return styled_df
    
    #5to modulo
    
    import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from data_config import tabla_tipo_impacto, matriz_probabilidad, matriz_impacto, factor_exposicion, factor_probabilidad, efectividad_controles, criticidad_límites, textos
from calculations import clasificar_criticidad, calcular_criticidad, simular_montecarlo
from plotting import create_heatmap, create_pareto_chart, plot_montecarlo_histogram, create_sensitivity_plot
from utils import reset_form_fields, format_risk_dataframe

# --- Configuración de la página ---
st.set_page_config(layout="wide", page_title="Calculadora de Riesgos", page_icon="🛡️")

# --- CSS Personalizado ---
st.markdown("""
    <style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 8px 16px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 14px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stSelectbox>div>div {
        border-radius: 8px;
    }
    .stSlider > div > div:first-child {
        color: #4CAF50;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 5px solid #4CAF50;
    }
    .metric-box h3 {
        color: #333;
        font-size: 1em;
        margin-bottom: 5px;
    }
    .metric-box p {
        font-size: 1.2em;
        font-weight: bold;
        color: #000;
    }
    .stAlert {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Inicialización de Session State ---
if 'idioma' not in st.session_state:
    st.session_state.idioma = 'es'
if 'riesgos' not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "ID", "Nombre del Riesgo", "Descripción", "Tipo de Impacto",
        "Probabilidad", "Exposición", "Impacto Numérico",
        "Efectividad del Control (%)", "Amenaza Deliberada",
        "Amenaza Inherente", "Amenaza Residual", "Amenaza Residual Ajustada",
        "Riesgo Residual", "Clasificación", "Color"
    ])
if 'current_edit_index' not in st.session_state:
    st.session_state.current_edit_index = -1 # -1 significa que no estamos editando

# Valores por defecto para reiniciar el formulario
if 'default_type_impact' not in st.session_state:
    st.session_state['default_type_impact'] = tabla_tipo_impacto['Tipo de Impacto'].iloc[0]
if 'default_probabilidad' not in st.session_state:
    st.session_state['default_probabilidad'] = factor_probabilidad['Clasificacion'].iloc[0]
if 'default_exposicion' not in st.session_state:
    st.session_state['default_exposicion'] = factor_exposicion['Clasificacion'].iloc[0]
if 'default_impacto_numerico' not in st.session_state:
    st.session_state['default_impacto_numerico'] = 50
if 'default_control_effectiveness' not in st.session_state:
    st.session_state['default_control_effectiveness'] = 50

# --- Función para obtener textos en el idioma actual ---
def get_text(key):
    return textos[st.session_state.idioma].get(key, key)

# --- Sidebar para selección de idioma y texto de impuestos ---
with st.sidebar:
    # Toggle de idioma
    if st.checkbox(get_text("sidebar_language_toggle"), value=(st.session_state.idioma == 'en')):
        st.session_state.idioma = 'en'
    else:
        st.session_state.idioma = 'es'

    st.markdown("---")
    st.header(get_text("tax_info_title"))
    st.info(get_text("tax_info_text"))

# --- Título de la Aplicación ---
st.title(get_text("app_title"))
st.markdown("---")

# --- Contenido Principal de la Aplicación (Two Columns) ---
col_form, col_graf = st.columns([1, 1.5]) # Ajustar proporciones de columnas

with col_form:
    st.header(get_text("risk_input_form_title"))

    # Inputs del formulario de riesgo
    with st.form("risk_form", clear_on_submit=False):
        risk_name = st.text_input(get_text("risk_name"),
                                    key="risk_name_input",
                                    value=st.session_state.get('risk_name_input', ''))
        risk_description = st.text_area(get_text("risk_description"),
                                        key="risk_description_input",
                                        value=st.session_state.get('risk_description_input', ''))

        selected_type_impact = st.selectbox(
            get_text("risk_type_impact"),
            tabla_tipo_impacto['Tipo de Impacto'],
            format_func=lambda x: f"{x} (Ponderación: {tabla_tipo_impacto[tabla_tipo_impacto['Tipo de Impacto'] == x]['Ponderación'].iloc[0]})",
            key="selected_type_impact"
        )
        selected_probabilidad_clasificacion = st.selectbox(
            get_text("risk_probability"),
            factor_probabilidad['Clasificacion'],
            format_func=lambda x: f"{x} ({factor_probabilidad[factor_probabilidad['Clasificacion'] == x]['Definición'].iloc[0]})",
            key="selected_probabilidad"
        )
        selected_exposicion_clasificacion = st.selectbox(
            get_text("risk_exposure"),
            factor_exposicion['Clasificacion'],
            format_func=lambda x: f"{x} ({factor_exposicion[factor_exposicion['Clasificacion'] == x]['Definición'].iloc[0]})",
            key="selected_exposicion"
        )

        # Slider para Impacto Numérico (0-100)
        impacto_numerico_slider = st.slider(
            get_text("risk_impact_numeric"),
            min_value=0, max_value=100, value=st.session_state.get('impacto_numerico_slider', 50), step=1,
            help="Valor numérico del impacto del riesgo, donde 0 es insignificante y 100 es catastrófico.",
            key="impacto_numerico_slider"
        )

        # Slider para Efectividad del Control (%)
        control_effectiveness_slider = st.slider(
            get_text("risk_control_effectiveness"),
            min_value=0, max_value=100, value=st.session_state.get('control_effectiveness_slider', 50), step=1,
            help="Porcentaje de efectividad de los controles existentes para mitigar el riesgo.",
            key="control_effectiveness_slider"
        )

        deliberate_threat_checkbox = st.checkbox(get_text("risk_deliberate_threat"),
                                                  value=st.session_state.get('deliberate_threat_checkbox', False),
                                                  key="deliberate_threat_checkbox")

        submitted = st.form_submit_button(get_text("add_risk_button"))

        if submitted:
            if not risk_name:
                st.error(get_text("error_risk_name_empty"))
            else:
                probabilidad_factor = factor_probabilidad[factor_probabilidad['Clasificacion'] == selected_probabilidad_clasificacion]['Factor'].iloc[0]
                exposicion_factor = factor_exposicion[factor_exposicion['Clasificacion'] == selected_exposicion_clasificacion]['Factor'].iloc[0]
                amenaza_deliberada_factor_val = 1 if deliberate_threat_checkbox else 0 # 1 para SI, 0 para NO
                ponderacion_impacto_val = tabla_tipo_impacto[tabla_tipo_impacto['Tipo de Impacto'] == selected_type_impact]['Ponderación'].iloc[0]

                amenaza_inherente_det, amenaza_residual_det, amenaza_residual_ajustada_det, riesgo_residual_det = \
                    calcular_criticidad(
                        probabilidad_factor,
                        exposicion_factor,
                        amenaza_deliberada_factor_val,
                        control_effectiveness_slider, # Se envía como porcentaje, la función lo convierte
                        impacto_numerico_slider, # Se envía como 0-100
                        ponderacion_impacto_val
                    )

                clasificacion_det, color_det = clasificar_criticidad(riesgo_residual_det, st.session_state.idioma)

                # Si estamos editando, actualizamos el riesgo existente
                if st.session_state.current_edit_index != -1:
                    idx = st.session_state.current_edit_index
                    st.session_state.riesgos.loc[idx] = [
                        st.session_state.riesgos.loc[idx, 'ID'], # Mantener el ID existente
                        risk_name,
                        risk_description,
                        selected_type_impact,
                        probabilidad_factor, # Guardar el factor numérico
                        exposicion_factor,   # Guardar el factor numérico
                        impacto_numerico_slider,
                        control_effectiveness_slider,
                        "Sí" if deliberate_threat_checkbox else "No",
                        f"{amenaza_inherente_det:.2f}",
                        f"{amenaza_residual_det:.2f}",
                        f"{amenaza_residual_ajustada_det:.2f}",
                        riesgo_residual_det,
                        clasificacion_det,
                        color_det
                    ]
                    st.success(f"{get_text('risk_name').replace(':', '')} '{risk_name}' actualizado exitosamente.")
                    st.session_state.current_edit_index = -1 # Salir del modo edición
                    reset_form_fields() # Limpiar el formulario después de editar
                else:
                    # Crear nuevo riesgo
                    new_risk_id = len(st.session_state.riesgos) + 1
                    new_risk = {
                        "ID": new_risk_id,
                        "Nombre del Riesgo": risk_name,
                        "Descripción": risk_description,
                        "Tipo de Impacto": selected_type_impact,
                        "Probabilidad": probabilidad_factor,
                        "Exposición": exposicion_factor,
                        "Impacto Numérico": impacto_numerico_slider,
                        "Efectividad del Control (%)": control_effectiveness_slider,
                        "Amenaza Deliberada": "Sí" if deliberate_threat_checkbox else "No",
                        "Amenaza Inherente": f"{amenaza_inherente_det:.2f}",
                        "Amenaza Residual": f"{amenaza_residual_det:.2f}",
                        "Amenaza Residual Ajustada": f"{amenaza_residual_ajustada_det:.2f}",
                        "Riesgo Residual": riesgo_residual_det,
                        "Clasificación": clasificacion_det,
                        "Color": color_det
                    }
                    st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([new_risk])], ignore_index=True)
                    st.success(get_text("success_risk_added"))
                    reset_form_fields() # Limpiar el formulario después de agregar

    st.markdown("---")
    st.header(get_text("deterministic_results_title"))
    # Mostrar resultados del modelo determinista actual
    if 'riesgo_residual_det' in locals():
        col1_det, col2_det = st.columns(2)
        with col1_det:
            st.markdown(f"<div class='metric-box'><h3>{get_text('inherent_threat')}</h3><p>{amenaza_inherente_det:.2f}</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-box'><h3>{get_text('residual_threat')}</h3><p>{amenaza_residual_det:.2f}</p></div>", unsafe_allow_html=True)
        with col2_det:
            st.markdown(f"<div class='metric-box'><h3>{get_text('adjusted_residual_threat')}</h3><p>{amenaza_residual_ajustada_det:.2f}</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-box'><h3>{get_text('residual_risk')}</h3><p>{riesgo_residual_det:.2f}</p></div>", unsafe_allow_html=True)

        st.markdown(f"<p style='text-align: center; font-size: 1.2em; font-weight: bold;'>{get_text('classification')}: <span style='color:{color_det};'>{clasificacion_det}</span></p>", unsafe_allow_html=True)
    else:
        st.info("Ingresa los datos del riesgo para ver los resultados deterministas aquí.")

    st.markdown("---")
    st.header(get_text("added_risks_title"))
    if not st.session_state.riesgos.empty:
        # Añadir botones de editar/eliminar
        df_display = st.session_state.riesgos.copy()
        df_display['Acciones'] = '' # Columna dummy para los botones

        for i, row in df_display.iterrows():
            edit_button_key = f"edit_btn_{row['ID']}"
            delete_button_key = f"del_btn_{row['ID']}"

            col_btns = st.columns([1,1,10]) # Ajustar el ancho para los botones
            with col_btns[0]:
                if st.button(get_text("edit_risk"), key=edit_button_key):
                    st.session_state.current_edit_index = i
                    st.session_state.risk_name_input = row['Nombre del Riesgo']
                    st.session_state.risk_description_input = row['Descripción']
                    st.session_state.selected_type_impact = row['Tipo de Impacto']
                    
                    # Para la probabilidad y exposición, necesitamos el valor de clasificación para el selectbox
                    st.session_state.selected_probabilidad = factor_probabilidad[factor_probabilidad['Factor'] == row['Probabilidad']]['Clasificacion'].iloc[0]
                    st.session_state.selected_exposicion = factor_exposicion[factor_exposicion['Factor'] == row['Exposición']]['Clasificacion'].iloc[0]
                    
                    st.session_state.impacto_numerico_slider = row['Impacto Numérico']
                    st.session_state.control_effectiveness_slider = row['Efectividad del Control (%)']
                    st.session_state.deliberate_threat_checkbox = (row['Amenaza Deliberada'] == 'Sí')
                    st.rerun() # Volver a ejecutar para cargar los datos en el formulario
            with col_btns[1]:
                if st.button(get_text("delete_risk"), key=delete_button_key):
                    if st.session_state.idioma == "es":
                        if st.warning(get_text("confirm_delete")):
                            st.session_state.riesgos = st.session_state.riesgos.drop(i).reset_index(drop=True)
                            st.success(get_text("risk_deleted"))
                            st.rerun()
                    else: # English confirmation
                        if st.warning(get_text("confirm_delete")):
                            st.session_state.riesgos = st.session_state.riesgos.drop(i).reset_index(drop=True)
                            st.success(get_text("risk_deleted"))
                            st.rerun()

        st.dataframe(format_risk_dataframe(st.session_state.riesgos, st.session_state.idioma), hide_index=True)
        
        csv_data = st.session_state.riesgos.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=get_text("download_excel_button"),
            data=csv_data,
            file_name="riesgos_evaluados.csv",
            mime="text/csv",
            help="Descargar los datos de los riesgos evaluados en formato CSV."
        )
    else:
        st.info(get_text("no_risks_yet"))

    st.markdown("---")
    st.header(get_text("montecarlo_input_title"))
    # Asegurarse de que haya un riesgo determinista calculado para activar la simulación
    if 'riesgo_residual_det' in locals():
        valor_economico = st.number_input(
            get_text("economic_value_asset"),
            min_value=0.0, value=100000.0, step=1000.0, format="%.2f",
            help="Valor monetario del activo o impacto total esperado en USD."
        )
        num_iteraciones = st.slider(
            get_text("num_iterations"),
            min_value=1000, max_value=50000, value=10000, step=1000,
            help="Número de simulaciones para el cálculo Monte Carlo."
        )

        if valor_economico == 0:
            st.warning(get_text("economic_value_asset") + " es 0. Las pérdidas simuladas serán 0.")

        if st.button(get_text("run_montecarlo_button")):
            with st.spinner('Ejecutando simulación Monte Carlo...'):
                probabilidad_base_mc = probabilidad_factor
                exposicion_base_mc = exposicion_factor
                impacto_numerico_base_mc = impacto_numerico_slider # Usamos el slider para el base
                efectividad_base_pct_mc = control_effectiveness_slider
                amenaza_deliberada_factor_mc = amenaza_deliberada_factor_val
                ponderacion_impacto_mc = ponderacion_impacto_val # Se envía sin normalizar aquí

                riesgo_residual_sim_data, perdidas_usd_sim_data, correlations = simular_montecarlo(
                    probabilidad_base_mc, exposicion_base_mc, impacto_numerico_base_mc,
                    efectividad_base_pct_mc, amenaza_deliberada_factor_mc, ponderacion_impacto_mc,
                    valor_economico, num_iteraciones
                )
                
                if perdidas_usd_sim_data is not None and len(perdidas_usd_sim_data) > 0:
                    st.session_state.riesgo_residual_sim_data = riesgo_residual_sim_data
                    st.session_state.perdidas_usd_sim_data = perdidas_usd_sim_data
                    st.session_state.montecarlo_correlations = correlations
                else:
                    st.error("No se pudieron generar resultados de Monte Carlo. Verifique los valores de entrada.")

    else:
        st.info("Primero calcula un riesgo en la sección superior para habilitar la simulación Monte Carlo.")

    # Histograma de Monte Carlo (Pérdida Económica)
    st.markdown("---")
    if 'perdidas_usd_sim_data' in st.session_state and len(st.session_state.perdidas_usd_sim_data) > 0:
        st.header(get_text("economic_loss_distribution_title"))
        fig_loss = plot_montecarlo_histogram(st.session_state.perdidas_usd_sim_data, get_text("economic_loss_distribution_title"), get_text("economic_value_asset"), st.session_state.idioma)
        if fig_loss:
            col_left_hist, col_center_hist, col_right_hist = st.columns([1,3,1])
            with col_center_hist:
                st.pyplot(fig_loss)
                plt.close(fig_loss) # Cierra la figura para liberar memoria
    else:
        st.info("Ejecuta la simulación Monte Carlo para ver la distribución de pérdidas económicas.")


with col_graf:
    # Mapa de Calor de Riesgos (5x5)
    st.header(get_text("risk_heatmap_title"))
    if not st.session_state.riesgos.empty:
        fig_heatmap = create_heatmap(st.session_state.riesgos, matriz_probabilidad, matriz_impacto, st.session_state.idioma)
        if fig_heatmap:
            st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.info("Agrega riesgos para generar el mapa de calor.")

    st.markdown("---")
    # Gráfico de Pareto de Riesgos
    st.header(get_text("risk_pareto_chart_title"))
    if not st.session_state.riesgos.empty:
        fig_pareto = create_pareto_chart(st.session_state.riesgos, st.session_state.idioma)
        if fig_pareto:
            st.plotly_chart(fig_pareto, use_container_width=True)
    else:
        st.info("Agrega riesgos para generar el gráfico de Pareto.")

    st.markdown("---")
    # Resultados y Métricas de Monte Carlo
    st.header(get_text("montecarlo_results_title"))
    if 'perdidas_usd_sim_data' in st.session_state and len(st.session_state.perdidas_usd_sim_data) > 0:
        perdidas = st.session_state.perdidas_usd_sim_data
        
        # Calcular CVaR (Expected Shortfall)
        alpha = 0.95 # Para CVaR 95%
        # Ordenar las pérdidas y tomar el (1-alpha) superior
        sorted_losses = np.sort(perdidas)
        index_cvar = int(np.floor(len(sorted_losses) * alpha))
        cvar_95_val = sorted_losses[index_cvar:].mean()

        col_mc1, col_mc2 = st.columns(2)
        with col_mc1:
            st.markdown(f"<div class='metric-box'><h3>{get_text('expected_loss')}</h3><p>${np.mean(perdidas):,.2f}</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-box'><h3>{get_text('median_l
   
    
    