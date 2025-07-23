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
