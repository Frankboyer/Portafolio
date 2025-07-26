# modules/data_config.py
"""
Este módulo contiene todas las configuraciones estáticas, tablas de datos,
y textos necesarios para la aplicación de gestión de riesgos.
Incluye la estructura detallada de perfiles de riesgo con múltiples tipos de impacto,
tablas base para el modelo determinista, y configuraciones de simulación Monte Carlo.
"""

import pandas as pd
import json
import os
import numpy as np

# --- Configuraciones Base de Perfiles de Riesgo ---
# Los nombres aquí estarán en el idioma que definas como base (ej. español).
# Si necesitas que los nombres de perfil, categoría, etc. también sean traducibles,
# la estructura de PERFILES_BASE debería ser más compleja (ej. anidada por idioma).
PERFILES_BASE = {
    "Seguridad Patrimonial": { # Este nombre se mostrará directamente
        "categorias": {
            "Físico": {"weight": 20, "impacts": {"Humano": 15, "Operacional": 10, "Económico": 5, "Reputacional": 10, "Legal": 5, "Ambiental": 15}},
            "Humano": {"weight": 15, "impacts": {"Humano": 25, "Operacional": 10, "Reputacional": 15, "Legal": 10}},
            "Infraestructura": {"weight": 15, "impactos": {"Operacional": 20, "Económico": 15, "Legal": 5}},
            "Tecnológico": {"weight": 10, "impactos": {"Operacional": 15, "Económico": 10, "Reputacional": 10, "Legal": 15}},
            "Legal": {"weight": 10, "impactos": {"Legal": 25, "Económico": 15, "Reputacional": 10, "Operacional": 5}},
            "Financiero": {"weight": 10, "impactos": {"Económico": 25, "Operacional": 10, "Reputacional": 5}},
            "Reputacional": {"weight": 10, "impactos": {"Reputacional": 25, "Humano": 5, "Económico": 10, "Legal": 5}},
            "Operativo": {"weight": 5, "impactos": {"Operacional": 20, "Económico": 10, "Humano": 5}},
            "Ambiental": {"weight": 5, "impactos": {"Ambiental": 25, "Legal": 10, "Reputacional": 10, "Económico": 5}}
        },
        "subcategorias": {
            "Físico": ["Robo", "Intrusión", "Sabotaje", "Vandalismo"],
            "Humano": ["Acceso no autorizado", "Error humano", "Amenaza interna"],
            "Infraestructura": ["Falla estructural", "Corte de energía", "Sistemas obsoletos"],
            "Tecnológico": ["Falla de CCTV", "Pérdida de datos", "Interferencia en redes"],
            "Legal": ["Incumplimiento normativo", "Multas", "Auditorías negativas"],
            "Financiero": ["Pérdida directa", "Pérdida de activos", "Costos operativos"],
            "Reputacional": ["Medios negativos", "Pérdida de clientes", "Desconfianza"],
            "Operativo": ["Retrasos logísticos", "Errores de procedimiento"],
            "Ambiental": ["Incendio", "Inundación", "Contaminación"]
        }
    },
    "Gestión de Proyectos": {
        "categorias": {
            "Tiempo": {"weight": 15, "impacts": {"Tiempo": 25, "Operacional": 5}},
            "Costo": {"weight": 15, "impactos": {"Económico": 25, "Financiero": 10}},
            "Alcance": {"weight": 10, "impactos": {"Operacional": 10, "Calidad": 5}},
            "Calidad": {"weight": 10, "impactos": {"Operacional": 15, "Económico": 5}},
            "Técnico": {"weight": 10, "impactos": {"Tecnológico": 20, "Operacional": 10}},
            "Humanos": {"weight": 10, "impactos": {"Humano": 20, "Reputacional": 5}},
            "Comunicación": {"weight": 8, "impactos": {"Reputacional": 15, "Organizacional": 10}},
            "Organizacional": {"weight": 7, "impactos": {"Organizacional": 15, "Humano": 5}},
            "Proveedores": {"weight": 5, "impactos": {"Operacional": 15, "Contractual / Legal": 10}},
            "Contractual / Legal": {"weight": 4, "impactos": {"Legal": 25, "Financiero": 5}},
            "Financiero": {"weight": 3, "impactos": {"Económico": 20, "Financiero": 10}},
            "Externo": {"weight": 3, "impactos": {"Ambiental": 10, "Legal": 5, "Reputacional": 5}}
        },
        "subcategorias": {
            "Tiempo": ["Retrasos en entregables", "Dependencias críticas", "Aprobaciones lentas"],
            "Costo": ["Sobrecostos", "Estimaciones erróneas", "Penalizaciones"],
            "Alcance": ["Cambios no controlados", "Requisitos mal definidos"],
            "Calidad": ["Defectos", "Falta de control", "Reproceso"],
            "Técnico": ["Errores de diseño", "Fallas de integración", "Complejidad técnica"],
            "Humanos": ["Falta de capacitación", "Rotación", "Desmotivación"],
            "Comunicación": ["Malos canales", "Información tardía", "Malentendidos"],
            "Organizacional": ["Falta de apoyo", "Cambios internos", "Conflictos"],
            "Proveedores": ["Incumplimiento", "Retrasos", "Subcontratistas poco confiables"],
            "Contractual / Legal": ["Litigios", "Falta de cláusulas claras"],
            "Financiero": ["Falta de fondos", "Riesgos cambiarios"],
            "Externo": ["Cambios regulatorios", "Eventos naturales", "Política"]
        }
    }
}

# --- Tablas Base para el Modelo de Riesgo Determinista ---
tabla_tipo_impacto_global = pd.DataFrame({
    'Tipo de Impacto': ['Humano', 'Operacional', 'Económico', 'Reputacional', 'Legal', 'Ambiental', 'Tecnológico', 'Contractual / Legal', 'Organizacional', 'Tiempo', 'Costo', 'Calidad', 'Financiero', 'Externo'],
    'Ponderación': [25, 20, 30, 15, 10, 5, 10, 4, 7, 15, 15, 10, 3, 3],
    'Explicación ASIS': [
        'Afectación a la vida, salud o seguridad de personas.', 'Interrupción o degradación de procesos y funciones del negocio.',
        'Pérdidas financieras directas o indirectas.', 'Daño a la imagen, confianza o credibilidad de la organización.',
        'Incumplimiento de leyes, regulaciones o contratos.', 'Impacto en el medio ambiente.',
        'Impacto en sistemas de información, redes o tecnología.', 'Incumplimiento de contratos o regulaciones.',
        'Impacto en la estructura u operación interna de la organización.', 'Retraso o fallo en la entrega del proyecto.',
        'Costos adicionales o pérdida de presupuesto.', 'Degradación de la calidad del producto o servicio.',
        'Impacto financiero general, como flujo de caja o solvencia.', 'Factores externos no controlables.'
    ]
})

matriz_probabilidad = pd.DataFrame({
    'Clasificacion': ['Muy Baja', 'Baja', 'Media', 'Alta', 'Muy Alta'],
    'Valor': [0.1, 0.3, 0.5, 0.7, 0.9],
    'Definicion': [
        'Probabilidad de ocurrencia menor al 10%', 'Probabilidad de ocurrencia entre 10% y 30%',
        'Probabilidad de ocurrencia entre 30% y 50%', 'Probabilidad de ocurrencia entre 50% y 70%',
        'Probabilidad de ocurrencia mayor al 70%'
    ]
})

factor_exposicion = pd.DataFrame({
    'Clasificacion': ['Muy Baja', 'Baja', 'Media', 'Alta', 'Muy Alta'],
    'Factor': [0.1, 0.3, 0.6, 0.9, 1.0],
    'Definicion': [
        'Ocurrencia muy infrecuente (ej. 1-2 veces cada 100 años)',
        'Ocurrencia infrecuente (ej. 1-2 veces cada 10 años)',
        'Ocurrencia ocasional (ej. algunas pocas veces al año)',
        'Ocurrencia frecuente (ej. 1-2 veces por mes)',
        'Ocurrencia muy frecuente (ej. 1 vez a la semana o más)'
    ]
})

matriz_impacto = pd.DataFrame({
    'Clasificacion': ['Insignificante', 'Menor', 'Moderado', 'Mayor', 'Catastrófico'],
    'Valor': [1, 2, 3, 4, 5],
    'Definicion': [
        'Daño mínimo, fácilmente recuperable.', 'Daño localizado, impacto limitado.',
        'Daño significativo, impacto moderado en áreas clave.', 'Daño extenso, impacto severo en la operación.',
        'Daño crítico, amenaza la viabilidad de la organización.'
    ]
})

efectividad_controles = pd.DataFrame({
    'Efectividad': ['Inefectiva', 'Parcialmente Efectiva', 'Efectiva', 'Muy Efectiva'],
    'Rango % Min': [0, 26, 51, 76], 'Rango % Max': [25, 50, 75, 100],
    'Factor': [0.1, 0.3, 0.7, 0.9],
    'Mitigacion': ['Los controles no reducen significativamente el riesgo.', 'Los controles ofrecen una reducción limitada del riesgo.',
                   'Los controles reducen el riesgo de manera considerable.', 'Los controles casi eliminan el riesgo.']
})

# Límites de criticidad para clasificar el Riesgo Residual (0-1)
criticidad_límites = [
    (0, 0.1, 'ACEPTABLE', '#28a745', 'ACCEPTABLE'), (0.1, 0.2, 'TOLERABLE', '#90EE90', 'TOLERABLE'),
    (0.2, 0.4, 'MODERADO', '#ffc107', 'MODERATE'), (0.4, 0.6, 'ALTO', '#fd7e14', 'HIGH'),
    (0.6, 1.0, 'CRÍTICO', '#dc3545', 'CRITICAL')
]

# --- Diccionario para manejo de múltiples idiomas ---
textos = {
    "es": {
        "sidebar_language_toggle": "English", "app_title": "Calculadora de Riesgos Integral",
        "tax_info_title": "Consideraciones sobre Impuestos",
        "tax_info_text": "Las implicaciones fiscales de las pérdidas por riesgos pueden ser complejas y varían significativamente según la jurisdicción y el tipo de negocio. Esta sección proporciona información general. Es crucial consultar a un asesor fiscal profesional para comprender cómo las pérdidas relacionadas con riesgos podrían afectar su situación fiscal específica, incluyendo posibles deducciones, créditos o tratamientos contables. Factores como la naturaleza de la pérdida (ej. operativa vs. capital), la estructura legal de la entidad y las leyes fiscales locales e internacionales son determinantes. Este simulador no ofrece asesoramiento fiscal.",
        "risk_input_form_title": "1. Entrada de Datos del Riesgo",
        "risk_name": "Nombre del Riesgo", "risk_description": "Descripción Detallada del Riesgo",
        "risk_type_impact": "Tipo de Impacto Principal",
        "risk_probability": "Probabilidad de Ocurrencia",
        "risk_exposure": "Exposición",
        "risk_impact_numeric": "Severidad del Impacto General (0-100)",
        "risk_control_effectiveness": "Efectividad del Control (%)",
        "risk_deliberate_threat": "¿Amenaza Deliberada?",
        "add_risk_button": "Agregar Riesgo",
        "error_risk_name_empty": "Por favor, ingresa un nombre para el riesgo.",
        "success_risk_added": "Riesgo agregado exitosamente.",
        "deterministic_results_title": "2. Resultados del Modelo Determinista",
        "inherent_threat": "Amenaza Inherente", "residual_threat": "Amenaza Residual",
        "adjusted_residual_threat": "Amenaza Residual Ajustada", "residual_risk": "Riesgo Residual",
        "classification": "Clasificación",
        "montecarlo_input_title": "3. Configuración de Simulación Monte Carlo",
        "economic_value_asset": "Valor Económico del Activo Bajo Riesgo (USD)",
        "num_iterations": "Número de Iteraciones Monte Carlo",
        "run_montecarlo_button": "Lanzar Simulación Monte Carlo",
        "montecarlo_results_title": "4. Resultados de la Simulación Monte Carlo",
        "expected_loss": "Pérdida Esperada (Media)", "median_loss": "Pérdida Mediana (Percentil 50)",
        "p5_loss": "Pérdida del Percentil 5", "p90_loss": "Pérdida del Percentil 90",
        "max_loss": "Máxima Pérdida Simulada", "cvar_95": "CVaR (95% - Cola de Riesgo)",
        "sensitivity_analysis_title": "Análisis de Sensibilidad (Correlación con Pérdida Económica)",
        "added_risks_title": "5. Riesgos Evaluados Acumulados",
        "download_excel_button": "Descargar Datos a Excel", "no_risks_yet": "Aún no se han agregado riesgos.",
        "risk_heatmap_title": "6. Mapa de Calor de Riesgos (Modelo Determinista)",
        "risk_pareto_chart_title": "7. Gráfico de Pareto de Riesgos",
        "risk_distribution_title": "8. Distribución del Riesgo Residual Simulado (Índice)",
        "economic_loss_distribution_title": "9. Distribución de Pérdidas Económicas Simuladas (USD)",
        "edit_risk": "Editar", "delete_risk": "Eliminar",
        "confirm_delete": "¿Estás seguro de que quieres eliminar este riesgo?", "risk_deleted": "Riesgo eliminado exitosamente.",
        "select_risk_to_simulate": "Selecciona el Riesgo a Simular",
        "all_risks_for_simulation": "Todos los Riesgos (Agregado)",
        "simulate_button": "Simular Riesgo(s) Seleccionado(s)",
        "custom_profile_creation": "Crear/Editar Perfil Personalizado",
        "profile_name_input": "Nombre del Perfil",
        "category_name_input": "Nombre de la Categoría",
        "category_weight_input": "Ponderación de la Categoría (%)",
        "add_category_button": "Agregar Categoría",
        "save_profile_button": "Guardar Perfil",
        "delete_profile_button": "Eliminar Perfil",
        "edit_profile_button": "Editar Perfil",
        "add_subcategory_button": "Agregar Subcategoría",
        "subcategory_name_input": "Nombre de la Subcategoría",
        "profile_saved": "Perfil guardado exitosamente.",
        "profile_deleted": "Perfil eliminado exitosamente.",
        "profile_updated": "Perfil actualizado exitosamente.",
        "profile_name_empty": "El nombre del perfil no puede estar vacío.",
        "profile_name_exists": "Ya existe un perfil con ese nombre.",
        "category_weight_invalid": "La ponderación de la categoría debe ser un número entre 0 y 100 y la suma total de ponderaciones del perfil no debe exceder 100.",
        "category_name_empty": "El nombre de la categoría no puede estar vacío.",
        "subcategory_name_empty": "El nombre de la subcategoría no puede estar vacío.",
        "no_risks_to_simulate": "No hay riesgos agregados para simular.",
        "select_at_least_one_risk": "Por favor, selecciona al menos un riesgo para simular.",
        "min_loss_input_label": "Mínima Pérdida Potencial (USD)",
        "max_loss_input_label": "Máxima Pérdida Potencial (USD)",
        "max_theoretical_risk": "Máx. Riesgo Teórico del Perfil",
        "impact_type_label": "Tipo de Impacto",
        "impact_severity_label": "Severidad (0-100)",
        "impact_weight_label": "Ponderación del Impacto"
    },
    "en": {
        "sidebar_language_toggle": "Español", "app_title": "Risk Calculator and Monte Carlo Simulator",
        "tax_info_title": "Tax Considerations",
        "tax_info_text": "The tax implications of risk losses can be complex and vary significantly by jurisdiction and business type. This section provides general information. It is crucial to consult a professional tax advisor to understand how risk-related losses might affect your specific tax situation, including potential deductions, credits, or accounting treatments. Factors such as the nature of the loss (e.g., operational vs. capital), the legal structure of the entity, and local and international tax laws are determining factors. This simulator does not provide tax advice.",
        "risk_input_form_title": "1. Risk Data Input", "risk_name": "Risk Name", "risk_description": "Detailed Risk Description",
        "risk_type_impact": "Primary Impact Type",
        "risk_probability": "Probability of Occurrence (Inherent Threat)", "risk_exposure": "Exposure (Inherent Threat)",
        "risk_impact_numeric": "Numeric Impact (0-100)",
        "risk_control_effectiveness": "Control Effectiveness (%)", "risk_deliberate_threat": "Deliberate Threat?",
        "add_risk_button": "Add Risk", "error_risk_name_empty": "Please enter a name for the risk.",
        "success_risk_added": "Risk added successfully.",
        "deterministic_results_title": "2. Deterministic Model Results",
        "inherent_threat": "Inherent Threat", "residual_threat": "Residual Threat",
        "adjusted_residual_threat": "Adjusted Residual Threat", "residual_risk": "Residual Risk",
        "classification": "Classification",
        "montecarlo_input_title": "3. Monte Carlo Simulation Setup",
        "economic_value_asset": "Economic Value of Asset at Risk (USD)", "num_iterations": "Number of Monte Carlo Iterations",
        "run_montecarlo_button": "Run Monte Carlo Simulation",
        "montecarlo_results_title": "4. Monte Carlo Simulation Results",
        "expected_loss": "Expected Loss (Mean)", "median_loss": "Median Loss (50th Percentile)",
        "p5_loss": "5th Percentile Loss", "p90_loss": "90th Percentile Loss",
        "max_loss": "Maximum Simulated Loss", "cvar_95": "CVaR (95% - Tail Risk)",
        "sensitivity_analysis_title": "Sensitivity Analysis (Correlation with Economic Loss)",
        "added_risks_title": "5. Accumulated Evaluated Risks",
        "download_excel_button": "Download Data to Excel", "no_risks_yet": "No risks have been added yet.",
        "risk_heatmap_title": "6. Risk Heatmap (Deterministic Model)",
        "risk_pareto_chart_title": "7. Risk Pareto Chart",
        "risk_distribution_title": "8. Simulated Residual Risk Distribution (Index)",
        "economic_loss_distribution_title": "9. Simulated Economic Loss Distribution (USD)",
        "edit_risk": "Edit", "delete_risk": "Delete",
        "confirm_delete": "Are you sure you want to delete this risk?", "risk_deleted": "Risk deleted successfully.",
        "select_risk_to_simulate": "Select Risk to Simulate",
        "all_risks_for_simulation": "All Risks (Aggregated)",
        "simulate_button": "Simulate Selected Risk(s)",
        "custom_profile_creation": "Create/Edit Custom Profile",
        "profile_name_input": "Profile Name",
        "category_name_input": "Category Name",
        "category_weight_input": "Category Weight (%)",
        "add_category_button": "Add Category",
        "save_profile_button": "Save Profile",
        "delete_profile_button": "Delete Profile",
        "edit_profile_button": "Edit Profile",
        "add_subcategory_button": "Add Subcategory",
        "subcategory_name_input": "Subcategory Name",
        "profile_saved": "Profile saved successfully.",
        "profile_deleted": "Profile deleted successfully.",
        "profile_updated": "Profile updated successfully.",
        "profile_name_empty": "Profile name cannot be empty.",
        "profile_name_exists": "A profile with this name already exists.",
        "category_weight_invalid": "Category weight must be between 0 and 100, and total profile weights cannot exceed 100.",
        "category_name_empty": "Category name cannot be empty.",
        "subcategory_name_empty": "Subcategory name cannot be empty.",
        "no_risks_to_simulate": "No risks have been added to simulate.",
        "select_at_least_one_risk": "Please select at least one risk to simulate.",
        "min_loss_input_label": "Min Potential Loss (USD)",
        "max_loss_input_label": "Max Potential Loss (USD)",
        "max_theoretical_risk": "Max Theoretical Profile Risk"
    }
}
