import pandas as pd

# --- Matrices de Riesgo (Probabilidad vs. Impacto) ---
matriz_probabilidad = pd.DataFrame({
    'Clasificacion': ['Muy Bajo', 'Bajo', 'Moderado', 'Alto', 'Muy Alto'],
    'Factor': [0.1, 0.2, 0.4, 0.6, 0.8],
    'Justificacion': [
        'Probabilidad menor al 10%',
        'Probabilidad entre 10% y 30%',
        'Probabilidad entre 31% y 50%',
        'Probabilidad entre 51% y 70%',
        'Probabilidad mayor al 70%'
    ]
})

matriz_impacto = pd.DataFrame({
    'Clasificacion': ['Muy Bajo', 'Bajo', 'Moderado', 'Alto', 'Muy Alto'],
    'Factor': [0.1, 0.3, 0.5, 0.7, 0.9],
    'Justificacion': [
        'Impacto insignificante',
        'Impacto menor, fácilmente manejable',
        'Impacto significativo, requiere atención',
        'Impacto grave, interrupción considerable',
        'Impacto crítico, amenaza a la continuidad'
    ]
})

# --- Factores Adicionales ---
factor_exposicion = pd.DataFrame({
    'Clasificacion': ['Diaria', 'Semanal', 'Mensual', 'Trimestral', 'Anual'],
    'Factor': [1.0, 0.8, 0.6, 0.4, 0.2]
})

factor_probabilidad = pd.DataFrame({
    'Clasificacion': ['Improbable', 'Raro', 'Posible', 'Probable', 'Casi Seguro'],
    'Factor': [0.1, 0.3, 0.5, 0.7, 0.9]
})

efectividad_controles = pd.DataFrame({
    'Clasificacion': ['Muy Baja', 'Baja', 'Media', 'Alta', 'Muy Alta'],
    'Factor': [0.1, 0.3, 0.5, 0.7, 0.9]
})

# --- Tabla de Tipos de Impacto Actualizada ---
# Alineada con ISO/ASIS y tus ponderaciones
tabla_tipo_impacto = pd.DataFrame({
    'Código': ['H', 'A', 'F', 'R', 'O', 'E', 'C', 'S', 'I'],
    'Tipo de Impacto': ['Humanos', 'Ambiental', 'Financiero', 'Reputacional', 'Operacional', 'Económicos', 'Comercial', 'Social', 'Infraestructura'],
    'Ponderación': [1.0, 0.9, 0.8, 0.8, 0.7, 0.7, 0.6, 0.6, 0.5],
    'Justificación Técnica': [
        'Impacto en vida o salud; siempre crítico según ISO 45001 y cualquier norma ética o legal.',
        'Riesgos ecológicos graves, sancionables, a menudo irreversibles (ISO 14001).',
        'Afecta sostenibilidad y viabilidad; alta prioridad según ISO 22301 y análisis de continuidad.',
        'Daño a imagen pública puede destruir confianza; difícil de recuperar (ASIS lo clasifica como severo).',
        'Puede detener producción, logística, o servicios críticos; clave en ISO 22301.',
        'Costos monetarios directos, penalizaciones, reducción de ingresos operativos.',
        'Pérdida de clientes, contratos, penetración de mercado. Afecta ingresos futuros.',
        'Impacta comunidades o grupos de interés; puede generar conflictos o presión social. (ISO 26000)',
        'Daños materiales a equipos o instalaciones; usualmente recuperables y asegurables.'
    ]
})


# --- Factores de Amenaza Deliberada ---
factores_amenaza_deliberada = pd.DataFrame({
    'Clasificacion': ['No', 'Baja', 'Moderada', 'Alta'],
    'Factor': [0.0, 0.2, 0.5, 1.0]
})

# --- Límites de Criticidad (para clasificación de riesgo) ---
criticidad_límites = [
    [0, 20, 'Bajo', '#d4edda', 'Low'],       # Verde claro
    [21, 40, 'Medio', '#ffc107', 'Medium'],   # Amarillo
    [41, 60, 'Alto', '#fd7e14', 'High'],     # Naranja
    [61, 100, 'Crítico', '#dc3545', 'Critical'] # Rojo
]

# --- Textos para Multilingüe ---
textos = {
    'es': {
        "app_title": "Calculadora y Gestor de Riesgos",
        "language_select": "Idioma",
        "risk_input_form_title": "Entrada de Riesgo",
        "risk_name": "Nombre del Riesgo",
        "risk_description": "Descripción del Riesgo",
        "risk_type_impact": "Tipo de Impacto",
        "risk_probability": "Probabilidad",
        "risk_exposure": "Exposición",
        "risk_impact_numeric": "Impacto Numérico (0-100)",
        "risk_control_effectiveness": "Efectividad del Control (%)",
        "risk_deliberate_threat_present": "¿Amenaza Deliberada Presente?",
        "risk_deliberate_threat_level": "Nivel de Amenaza Deliberada",
        "add_risk_button": "Añadir/Actualizar Riesgo",
        "success_risk_added": "Riesgo añadido exitosamente.",
        "error_risk_name_empty": "El nombre del riesgo no puede estar vacío.",
        "editing_risk": "Editando Riesgo",
        "edit_in_form": "Modifica los campos en el formulario de arriba y haz clic en 'Añadir/Actualizar Riesgo'.",

        "risk_table_title": "Riesgos Registrados",
        "edit_button": "Editar",
        "delete_button": "Eliminar",
        "confirm_delete": "¿Estás seguro de que quieres eliminar el riesgo",
        "no_risks_added": "Aún no se han añadido riesgos.",

        "risk_heatmap_title": "Cuadrante de Riesgos Residuales",
        "heatmap_x_axis": "Impacto Numérico",
        "heatmap_y_axis": "Probabilidad",
        "heatmap_size_legend": "Riesgo Residual",
        "heatmap_color_legend": "Clasificación",
        "no_risks_for_heatmap": "Añade riesgos para ver el cuadrante.",

        "pareto_chart_title": "Análisis de Pareto de Riesgos (Top 10)",
        "pareto_x_axis": "Riesgo",
        "pareto_y_axis": "Riesgo Residual",
        "pareto_cumulative_y_axis": "Riesgo Residual Acumulado (%)",
        "no_risks_for_pareto": "Añade riesgos para ver el análisis de Pareto.",

        "monte_carlo_simulation_title": "Simulación de Monte Carlo",
        "monte_carlo_info": "Selecciona un riesgo y un valor económico para simular posibles escenarios de riesgo residual y pérdidas.",
        "select_risk_for_mc": "Selecciona un Riesgo para la Simulación",
        "simulation_for_risk": "Simulación para el Riesgo",
        "economic_value_asset": "Valor Económico del Activo Afectado ($)",
        "num_montecarlo_iterations": "Número de Iteraciones de Monte Carlo",
        "run_montecarlo_button": "Ejecutar Simulación de Monte Carlo",
        "economic_value_positive": "Por favor, introduce un valor económico positivo.",
        "running_simulation": "Ejecutando simulación... Esto puede tardar unos segundos.",
        "simulation_complete": "Simulación completada.",
        "simulation_failed": "No hay datos para la simulación o la simulación falló.",
        "add_risks_for_montecarlo": "Añade riesgos para poder ejecutar una simulación de Monte Carlo.",
        "select_risk_to_start_mc": "Selecciona un riesgo para iniciar la simulación de Monte Carlo.",

        "simulated_risk_distribution": "Distribución del Riesgo Residual Simulado",
        "histogram_risk_title": "Histograma de Riesgo Residual",
        "risk_value_label": "Valor del Riesgo Residual",
        "frequency_label": "Frecuencia",
        "simulated_economic_losses": "Pérdidas Económicas Simuladas",
        "histogram_losses_title": "Histograma de Pérdidas Económicas",
        "losses_value_label": "Pérdidas Económicas ($)",

        "sensitivity_analysis_title": "Análisis de Sensibilidad (Correlación)",
        "correlation_title": "Correlación de Pearson con el Riesgo Residual",
        "correlation_x_axis": "Correlación",
        "correlation_y_axis": "Variable de Entrada",

        "matrix_title": "Matriz de Probabilidad e Impacto",
        "matrix_prob_col": "Clasificación de Probabilidad",
        "matrix_impact_col": "Clasificación de Impacto",
        "matrix_factor_col": "Factor",
        "matrix_justification_col": "Justificación",
        "matrix_exposure_title": "Factores de Exposición",
        "matrix_threat_title": "Factores de Amenaza Deliberada",
        "matrix_control_title": "Factores de Efectividad de Control",
        "matrix_impact_type_title": "Ponderaciones de Tipo de Impacto",

        "mc_risk_name": "Nombre del Riesgo",
        "mc_type_impact": "Tipo de Impacto",
        "mc_probability": "Probabilidad",
        "mc_exposure": "Exposición",
        "mc_impact_numeric": "Impacto Numérico",
        "mc_control_effectiveness": "Efectividad del Control",
        "mc_deliberate_threat": "Amenaza Deliberada",
        "mc_current_residual_risk": "Riesgo Residual Actual",
        "yes": "Sí",
        "no": "No",

        # Nuevos textos para tipos de impacto
        "impact_type_humanos": "Humanos",
        "impact_type_ambiental": "Ambiental",
        "impact_type_financiero": "Financiero",
        "impact_type_reputacional": "Reputacional",
        "impact_type_operacional": "Operacional",
        "impact_type_economicos": "Económicos",
        "impact_type_comercial": "Comercial",
        "impact_type_social": "Social",
        "impact_type_infraestructura": "Infraestructura",

        # Nuevos textos para niveles de amenaza deliberada
        "no_deliberate_threat": "No",
        "low_deliberate_threat": "Baja",
        "moderate_deliberate_threat": "Moderada",
        "high_deliberate_threat": "Alta",
    },
    'en': {
        "app_title": "Risk Calculator and Manager",
        "language_select": "Language",
        "risk_input_form_title": "Risk Input Form",
        "risk_name": "Risk Name",
        "risk_description": "Risk Description",
        "risk_type_impact": "Type of Impact",
        "risk_probability": "Probability",
        "risk_exposure": "Exposure",
        "risk_impact_numeric": "Numerical Impact (0-100)",
        "risk_control_effectiveness": "Control Effectiveness (%)",
        "risk_deliberate_threat_present": "Deliberate Threat Present?",
        "risk_deliberate_threat_level": "Deliberate Threat Level",
        "add_risk_button": "Add/Update Risk",
        "success_risk_added": "Risk added successfully.",
        "error_risk_name_empty": "Risk name cannot be empty.",
        "editing_risk": "Editing Risk",
        "edit_in_form": "Modify fields in the form above and click 'Add/Update Risk'.",

        "risk_table_title": "Registered Risks",
        "edit_button": "Edit",
        "delete_button": "Delete",
        "confirm_delete": "Are you sure you want to delete the risk",
        "no_risks_added": "No risks have been added yet.",

        "risk_heatmap_title": "Residual Risk Quadrant",
        "heatmap_x_axis": "Numerical Impact",
        "heatmap_y_axis": "Probability",
        "heatmap_size_legend": "Residual Risk",
        "heatmap_color_legend": "Classification",
        "no_risks_for_heatmap": "Add risks to see the quadrant.",

        "pareto_chart_title": "Risk Pareto Analysis (Top 10)",
        "pareto_x_axis": "Risk",
        "pareto_y_axis": "Residual Risk",
        "pareto_cumulative_y_axis": "Cumulative Residual Risk (%)",
        "no_risks_for_pareto": "Add risks to see the Pareto analysis.",

        "monte_carlo_simulation_title": "Monte Carlo Simulation",
        "monte_carlo_info": "Select a risk and economic value to simulate possible residual risk and loss scenarios.",
        "select_risk_for_mc": "Select a Risk for Simulation",
        "simulation_for_risk": "Simulation for Risk",
        "economic_value_asset": "Economic Value of Affected Asset ($)",
        "num_montecarlo_iterations": "Number of Monte Carlo Iterations",
        "run_montecarlo_button": "Run Monte Carlo Simulation",
        "economic_value_positive": "Please enter a positive economic value.",
        "running_simulation": "Running simulation... This may take a few seconds.",
        "simulation_complete": "Simulation complete.",
        "simulation_failed": "No data for simulation or simulation failed.",
        "add_risks_for_montecarlo": "Add risks to run a Monte Carlo simulation.",
        "select_risk_to_start_mc": "Select a risk to start the Monte Carlo simulation.",

        "simulated_risk_distribution": "Simulated Residual Risk Distribution",
        "histogram_risk_title": "Residual Risk Histogram",
        "risk_value_label": "Residual Risk Value",
        "frequency_label": "Frequency",
        "simulated_economic_losses": "Simulated Economic Losses",
        "histogram_losses_title": "Economic Losses Histogram",
        "losses_value_label": "Economic Losses ($)",

        "sensitivity_analysis_title": "Sensitivity Analysis (Correlation)",
        "correlation_title": "Pearson Correlation with Residual Risk",
        "correlation_x_axis": "Correlation",
        "correlation_y_axis": "Input Variable",

        "matrix_title": "Probability and Impact Matrix",
        "matrix_prob_col": "Probability Classification",
        "matrix_impact_col": "Impact Classification",
        "matrix_factor_col": "Factor",
        "matrix_justification_col": "Justification",
        "matrix_exposure_title": "Exposure Factors",
        "matrix_threat_title": "Deliberate Threat Factors",
        "matrix_control_title": "Control Effectiveness Factors",
        "matrix_impact_type_title": "Impact Type Weightings",

        "mc_risk_name": "Risk Name",
        "mc_type_impact": "Type of Impact",
        "mc_probability": "Probability",
        "mc_exposure": "Exposure",
        "mc_impact_numeric": "Numerical Impact",
        "mc_control_effectiveness": "Control Effectiveness",
        "mc_deliberate_threat": "Deliberate Threat",
        "mc_current_residual_risk": "Current Residual Risk",
        "yes": "Yes",
        "no": "No",

        # New texts for impact types
        "impact_type_humanos": "Human",
        "impact_type_ambiental": "Environmental",
        "impact_type_financiero": "Financial",
        "impact_type_reputacional": "Reputational",
        "impact_type_operacional": "Operational",
        "impact_type_economicos": "Economic",
        "impact_type_comercial": "Commercial",
        "impact_type_social": "Social",
        "impact_type_infraestructura": "Infrastructure",

        # New texts for deliberate threat levels
        "no_deliberate_threat": "No",
        "low_deliberate_threat": "Low",
        "moderate_deliberate_threat": "Moderate",
        "high_deliberate_threat": "High",
    }
}

# Función para obtener texto del diccionario (para usar en otros módulos si es necesario)
def get_text_data_config(key, idioma='es'):
    return textos[idioma].get(key, key)
