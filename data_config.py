import pandas as pd

textos = {
    "es": {
        "app_title": "Calculadora de Riesgos",
        "language_select": "Selección de Idioma",
        "risk_name": "Nombre del Riesgo",
        "risk_description": "Descripción del Riesgo",
        "risk_type_impact": "Tipo de Impacto",
        "matrix_title": "Matrices de Configuración",
        "matrix_prob_col": "Probabilidad",
        "matrix_impact_type_title": "Tipos de Impacto",
        "error_risk_name_empty": "El nombre del riesgo no puede estar vacío",
        "error_invalid_impact_value": "El valor de impacto debe estar entre 0 y 100",
        "error_processing_risk": "Error al procesar el riesgo",
        "success_risk_added": "Riesgo agregado correctamente",
        "add_risk_button": "Agregar Riesgo",
        "deliberate_threat_section_title": "Amenaza Deliberada",
        "deliberate_threat_checkbox": "¿Existe amenaza deliberada?",
        "deliberate_threat_level": "Nivel de Amenaza Deliberada",
        "no_risks_added": "No se han agregado riesgos aún",
        "monte_carlo_simulation_title": "Simulación Monte Carlo",
        "add_risks_for_montecarlo": "Agregue riesgos para habilitar la simulación",
        "select_risk_for_mc": "Seleccione un riesgo para simular"
    },
    "en": {
        "app_title": "Risk Calculator",
        "language_select": "Language Selection",
        "risk_name": "Risk Name",
        "risk_description": "Risk Description",
        "risk_type_impact": "Impact Type",
        "matrix_title": "Configuration Matrices",
        "matrix_prob_col": "Probability",
        "matrix_impact_type_title": "Impact Types",
        "error_risk_name_empty": "Risk name cannot be empty",
        "error_invalid_impact_value": "Impact value must be between 0 and 100",
        "error_processing_risk": "Error processing risk",
        "success_risk_added": "Risk added successfully",
        "add_risk_button": "Add Risk",
        "deliberate_threat_section_title": "Deliberate Threat",
        "deliberate_threat_checkbox": "Is there a deliberate threat?",
        "deliberate_threat_level": "Deliberate Threat Level",
        "no_risks_added": "No risks added yet",
        "monte_carlo_simulation_title": "Monte Carlo Simulation",
        "add_risks_for_montecarlo": "Add risks to enable simulation",
        "select_risk_for_mc": "Select a risk to simulate"
    }
}

tabla_tipo_impacto = pd.DataFrame({
    "Tipo de Impacto": ["Financiero", "Operacional", "Legal", "Reputacional"],
    "Ponderación": [0.4, 0.3, 0.2, 0.1],
    "Justificación Técnica": [
        "Impacto económico directo",
        "Interrupción de operaciones",
        "Sanciones legales",
        "Daño a imagen pública"
    ]
})

factor_probabilidad = pd.DataFrame({
    "Clasificacion": ["Muy Alta", "Alta", "Media", "Baja", "Muy Baja"],
    "Factor": [1.0, 0.8, 0.5, 0.2, 0.1],
    "Descripción": [
        "Ocurre frecuentemente (más de 1 vez al mes)",
        "Ocurre regularmente (1 vez cada 1-6 meses)",
        "Ocurre ocasionalmente (1 vez cada 6-12 meses)",
        "Ocurre raramente (1 vez cada 1-3 años)",
        "Muy improbable (menos de 1 vez cada 3 años)"
    ]
})

factor_exposicion = pd.DataFrame({
    "Clasificacion": ["Continua", "Frecuente", "Ocasional", "Rara", "Muy Rara"],
    "Factor": [1.0, 0.7, 0.4, 0.2, 0.05],
    "Descripción": [
        "Exposición constante (24/7)",
        "Varias veces por semana",
        "Varias veces por mes",
        "Varias veces por año",
        "Menos de una vez al año"
    ]
})

factores_amenaza_deliberada = pd.DataFrame({
    "Clasificacion": ["Crítica", "Alta", "Media", "Baja", "Mínima"],
    "Factor": [1.0, 0.75, 0.5, 0.25, 0.1],
    "Descripción": [
        "Amenaza de actores altamente capacitados",
        "Amenaza de actores con recursos moderados",
        "Amenaza de actores con recursos limitados",
        "Amenaza de actores ocasionales",
        "Amenaza de actores sin recursos específicos"
    ]
})
