import pandas as pd

# --- Tabla de Tipos de Impacto ---
tabla_tipo_impacto = pd.DataFrame({
    'Tipo de Impacto': ['Financiero', 'Reputacional', 'Operacional', 'Legal/Regulatorio'],
    'Ponderación': [0.5, 0.3, 0.15, 0.05]
})

# --- Matriz de Probabilidad ---
# ESTO ES CRÍTICO: Asegúrate de que las columnas se llamen 'Rango Min' y 'Rango Max' exactamente.
matriz_probabilidad = pd.DataFrame({
    'Clasificacion': ['Muy Bajo', 'Bajo', 'Medio', 'Alto', 'Muy Alto'],
    'Rango Min': [0.00, 0.20, 0.40, 0.60, 0.80],
    'Rango Max': [0.20, 0.40, 0.60, 0.80, 1.00]
})

# --- Matriz de Impacto (para Heatmap) ---
# ESTO ES CRÍTICO: Asegúrate de que las columnas se llamen 'Rango Min' y 'Rango Max' exactamente.
# Estos valores deberían coincidir con el rango de tu slider de Impacto Numérico (0-100).
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
# [Min, Max, Clasificación ES, Color, Clasificación EN]
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
