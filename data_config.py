import pandas as pd

# --- Tabla de Tipos de Impacto ---
tabla_tipo_impacto = pd.DataFrame({
    'Tipo de Impacto': ['Financiero', 'Reputacional', 'Operacional', 'Legal/Regulatorio'],
    'Ponderación': [0.5, 0.3, 0.15, 0.05]
})

# --- Matriz de Probabilidad ---
matriz_probabilidad = pd.DataFrame({
    'Clasificacion': ['Muy Bajo', 'Bajo', 'Medio', 'Alto', 'Muy Alto'],
    'Rango Min': [0.00, 0.20, 0.40, 0.60, 0.80],
    'Rango Max': [0.20, 0.40, 0.60, 0.80, 1.00]
})

# --- Matriz de Impacto (para Heatmap) ---
matriz_impacto = pd.DataFrame({
    'Clasificacion': ['Insignificante', 'Menor', 'Moderado', 'Mayor', 'Catastrófico'],
    'Rango Min': [0, 20, 40, 60, 80],
    'Rango Max': [20, 40, 60, 80, 100]
})

# --- Factor de Exposición ---
factor_exposicion = pd.DataFrame({
    'Clasificacion': ['Diaria', 'Semanal', 'Mensual', 'Trimestral', 'Anual'],
    'Factor': [1.0, 0.75, 0.5, 0.25, 0.1]
})

# --- Factor de Probabilidad (general, no la matriz para heatmap) ---
factor_probabilidad = pd.DataFrame({
    'Clasificacion': ['Improbable', 'Poco probable', 'Moderado', 'Probable', 'Casi seguro'],
    'Factor': [0.1, 0.3, 0.5, 0.7, 0.9]
})

# --- Efectividad de Controles ---
efectividad_controles = pd.DataFrame({
    'Nivel': ['Bajo', 'Medio', 'Alto', 'Muy Alto'],
    'Reduccion': [0.2, 0.5, 0.75, 0.9]
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
        "sidebar_language_toggle": "Cambiar a Inglés",
        "tax_info_title": "Información Importante",
        "tax_info_text": "Esta aplicación es una herramienta de simulación de riesgos. Los resultados son estimaciones y no deben interpretarse como asesoramiento financiero, legal o de seguridad. Consulta siempre a un profesional calificado para decisiones específicas. No considera implicaciones fiscales ni requisitos regulatorios específicos.",
        "app_title": "Calculadora y Simulador de Riesgos Empresariales",
        "risk_input_form_title": "1. Entrada de Datos del Riesgo",
        "risk_name": "Nombre del Riesgo",
        "risk_description": "Descripción del Riesgo",
        "risk_type_impact": "Tipo de Impacto",
        "risk_probability": "Probabilidad",
        "risk_exposure": "Exposición",
        "risk_impact_numeric": "Impacto Numérico (0-100%)",
        "risk_control_effectiveness": "Efectividad del Control Existente (%)",
        "risk_deliberate_threat": "¿Amenaza Deliberada?",
        "add_risk_button": "Agregar/Actualizar Riesgo",
        "error_risk_name_empty": "¡Por favor, ingresa un nombre para el riesgo!",
        "success_risk_added": "Riesgo agregado exitosamente.",
        "risk_list_title": "2. Lista de Riesgos",
        "no_risks_added_yet": "Aún no se han agregado riesgos. Usa el formulario de arriba para añadir uno.",
        "select_risk_to_edit": "Selecciona un riesgo para editar",
        "edit_selected_risk_button": "Editar Riesgo Seleccionado",
        "editing_risk": "Editando riesgo",
        "edit_in_form": "Modifica los campos en el formulario de arriba.",
        "please_select_risk_to_edit": "Por favor, selecciona un riesgo para editar.",
        "select_risk_to_delete": "Selecciona un riesgo para eliminar",
        "delete_selected_risk_button": "Eliminar Riesgo Seleccionado",
        "successfully_deleted": "eliminado exitosamente",
        "please_select_risk_to_delete": "Por favor, selecciona un riesgo para eliminar.",
        "risk_quadrant_title": "3. Cuadrante de Riesgos (Heatmap)",
        "add_risks_for_heatmap": "Agrega riesgos para visualizar el cuadrante de riesgos.",
        "heatmap_error": "No se pudo generar el cuadrante de riesgos. Asegúrate de tener datos válidos.",
        "pareto_analysis_title": "4. Análisis de Pareto",
        "add_risks_for_pareto": "Agrega riesgos para ver el análisis de Pareto.",
        "pareto_error": "No se pudo generar el gráfico de Pareto. Asegúrate de tener datos válidos.",
        "monte_carlo_simulation_title": "5. Simulación de Monte Carlo",
        "monte_carlo_info": "Simula la distribución de riesgos residuales y pérdidas económicas para un riesgo específico.",
        "add_risks_for_montecarlo": "Agrega riesgos para ejecutar una simulación de Monte Carlo.",
        "select_risk_for_mc": "Selecciona un riesgo para la simulación de Monte Carlo",
        "simulation_for_risk": "Simulación para el Riesgo",
        "mc_risk_name": "Nombre del Riesgo",
        "mc_type_impact": "Tipo de Impacto",
        "mc_probability": "Probabilidad",
        "mc_exposure": "Exposición",
        "mc_impact_numeric": "Impacto Numérico",
        "mc_control_effectiveness": "Efectividad del Control",
        "mc_deliberate_threat": "Amenaza Deliberada",
        "mc_current_residual_risk": "Riesgo Residual Actual",
        "economic_value_asset": "Valor Económico del Activo Afectado ($)",
        "num_montecarlo_iterations": "Número de Iteraciones de Monte Carlo",
        "run_montecarlo_button": "Ejecutar Simulación de Monte Carlo",
        "economic_value_positive": "Por favor, ingresa un valor económico positivo.",
        "running_simulation": "Ejecutando simulación...",
        "simulation_complete": "Simulación completa. Resultados:",
        "simulated_risk_distribution": "Distribución del Riesgo Residual Simulado",
        "histogram_risk_title": "Distribución del Riesgo Residual Simulado",
        "risk_value_label": "Valor del Riesgo Residual",
        "simulated_economic_losses": "Pérdidas Económicas Simuladas",
        "histogram_losses_title": "Distribución de Pérdidas Económicas Simuladas",
        "losses_value_label": "Valor de la Pérdida Económica ($)",
        "sensitivity_analysis_title": "Análisis de Sensibilidad",
        "sensitivity_analysis_info": "Muestra la correlación de cada factor con el Riesgo Residual simulado.",
        "no_sensitivity_data": "No hay datos de sensibilidad disponibles para mostrar.",
        "select_risk_to_start_mc": "Selecciona un riesgo para iniciar la simulación de Monte Carlo.",
        "impact_probability_matrix_title": "6. Matrices de Referencia",
        "probability_factors": "Factores de Probabilidad",
        "exposure_factors": "Factores de Exposición",
        "impact_types": "Tipos de Impacto",
        "control_effectiveness_levels": "Niveles de Efectividad del Control",
        "criticality_limits": "Límites de Criticidad (Riesgo Residual)",
        "factor": "Factor", # Para mostrar junto al número
        "classification_label": "Clasificación",
        "sum_residual_risk_label": "Suma Riesgo Residual",
        "percentage_label": "Porcentaje",
        "cumulative_percentage_label": "Porcentaje Acumulado",
        "pareto_chart_title": "Análisis de Pareto por Clasificación de Riesgo",
        "frequency_label": "Frecuencia",
        "correlation_plot_title": "Análisis de Sensibilidad: Correlación con Riesgo Residual",
        "correlation_coefficient_label": "Coeficiente de Correlación",
        "variable_label": "Variable",
        "risk_count_title": "Conteo de Riesgos",
        "risk_heatmap_title": "Cuadrante de Riesgos: Conteo por Categoría",
        "impact_category_label": "Categoría de Impacto",
        "probability_category_label": "Categoría de Probabilidad"
    },
    'en': {
        "sidebar_language_toggle": "Switch to Spanish",
        "tax_info_title": "Important Information",
        "tax_info_text": "This application is a risk simulation tool. Results are estimates and should not be construed as financial, legal, or security advice. Always consult with a qualified professional for specific decisions. It does not consider tax implications or specific regulatory requirements.",
        "app_title": "Enterprise Risk Calculator and Simulator",
        "risk_input_form_title": "1. Risk Data Entry",
        "risk_name": "Risk Name",
        "risk_description": "Risk Description",
        "risk_type_impact": "Type of Impact",
        "risk_probability": "Probability",
        "risk_exposure": "Exposure",
        "risk_impact_numeric": "Numeric Impact (0-100%)",
        "risk_control_effectiveness": "Existing Control Effectiveness (%)",
        "risk_deliberate_threat": "Deliberate Threat?",
        "add_risk_button": "Add/Update Risk",
        "error_risk_name_empty": "Please enter a risk name!",
        "success_risk_added": "Risk added successfully.",
        "risk_list_title": "2. Risk List",
        "no_risks_added_yet": "No risks added yet. Use the form above to add one.",
        "select_risk_to_edit": "Select a risk to edit",
        "edit_selected_risk_button": "Edit Selected Risk",
        "editing_risk": "Editing risk",
        "edit_in_form": "Modify the fields in the form above.",
        "please_select_risk_to_edit": "Please select a risk to edit.",
        "select_risk_to_delete": "Select a risk to delete",
        "successfully_deleted": "successfully deleted",
        "please_select_risk_to_delete": "Please select a risk to delete.",
        "risk_quadrant_title": "3. Risk Quadrant (Heatmap)",
        "add_risks_for_heatmap": "Add risks to visualize the risk quadrant.",
        "heatmap_error": "Could not generate the risk quadrant. Ensure you have valid data.",
        "pareto_analysis_title": "4. Pareto Analysis",
        "add_risks_for_pareto": "Add risks to see the Pareto analysis.",
        "pareto_error": "Could not generate the Pareto chart. Ensure you have valid data.",
        "monte_carlo_simulation_title": "5. Monte Carlo Simulation",
        "monte_carlo_info": "Simulate the distribution of residual risks and economic losses for a specific risk.",
        "add_risks_for_montecarlo": "Add risks to run a Monte Carlo simulation.",
        "select_risk_for_mc": "Select a risk for Monte Carlo simulation",
        "simulation_for_risk": "Simulation for Risk",
        "mc_risk_name": "Risk Name",
        "mc_type_impact": "Impact Type",
        "mc_probability": "Probability",
        "mc_exposure": "Exposure",
        "mc_impact_numeric": "Numeric Impact",
        "mc_control_effectiveness": "Control Effectiveness",
        "mc_deliberate_threat": "Deliberate Threat",
        "mc_current_residual_risk": "Current Residual Risk",
        "economic_value_asset": "Economic Value of Affected Asset ($)",
        "num_montecarlo_iterations": "Number of Monte Carlo Iterations",
        "run_montecarlo_button": "Run Monte Carlo Simulation",
        "economic_value_positive": "Please enter a positive economic value.",
        "running_simulation": "Running simulation...",
        "simulation_complete": "Simulation complete. Results:",
        "simulated_risk_distribution": "Simulated Residual Risk Distribution",
        "histogram_risk_title": "Simulated Residual Risk Distribution",
        "risk_value_label": "Residual Risk Value",
        "simulated_economic_losses": "Simulated Economic Losses",
        "histogram_losses_title": "Simulated Economic Losses Distribution",
        "losses_value_label": "Economic Loss Value ($)",
        "sensitivity_analysis_title": "Sensitivity Analysis",
        "sensitivity_analysis_info": "Shows the correlation of each factor with the simulated Residual Risk.",
        "no_sensitivity_data": "No sensitivity data available to display.",
        "select_risk_to_start_mc": "Select a risk to start Monte Carlo simulation.",
        "impact_probability_matrix_title": "6. Reference Matrices",
        "probability_factors": "Probability Factors",
        "exposure_factors": "Exposure Factors",
        "impact_types": "Impact Types",
        "control_effectiveness_levels": "Control Effectiveness Levels",
        "criticality_limits": "Criticality Limits (Residual Risk)",
        "factor": "Factor",
        "classification_label": "Classification",
        "sum_residual_risk_label": "Sum of Residual Risk",
        "percentage_label": "Percentage",
        "cumulative_percentage_label": "Cumulative Percentage",
        "pareto_chart_title": "Pareto Analysis by Risk Classification",
        "frequency_label": "Frequency",
        "correlation_plot_title": "Sensitivity Analysis: Correlation with Residual Risk",
        "correlation_coefficient_label": "Correlation Coefficient",
        "variable_label": "Variable",
        "risk_count_title": "Risk Count",
        "risk_heatmap_title": "Risk Quadrant: Count by Category",
        "impact_category_label": "Impact Category",
        "probability_category_label": "Probability Category"
    }
}
