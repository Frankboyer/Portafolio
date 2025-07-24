# data_config.py

import pandas as pd

# ... (tus DataFrames existentes: tabla_tipo_impacto, matriz_probabilidad, matriz_impacto, factor_exposicion, factor_probabilidad, efectividad_controles) ...

# --- Factores de Amenaza Deliberada (NUEVO) ---
# Se mantiene el valor 0 si no es amenaza deliberada
# Estos factores se sumarán al 1 en la fórmula (1 + factor)
factores_amenaza_deliberada = pd.DataFrame({
    'Clasificacion': ['No', 'Baja', 'Moderada', 'Alta'], # Agregamos 'No'
    'Factor': [0.0, 0.2, 0.5, 1.0] # Factor 0.0 para 'No', y valores para Baja, Media, Alta
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
        # ... (tus textos existentes) ...
        "risk_deliberate_threat_present": "¿Amenaza Deliberada Presente?", # Nuevo texto para el checkbox
        "risk_deliberate_threat_level": "Nivel de Amenaza Deliberada", # Nuevo texto para el selectbox
        # ... (más textos para el nuevo 'No', 'Baja', 'Moderada', 'Alta' si quieres que se muestren diferentes a las clasificaciones)
        "no_deliberate_threat": "No",
        "low_deliberate_threat": "Baja",
        "moderate_deliberate_threat": "Moderada",
        "high_deliberate_threat": "Alta",
    },
    'en': {
        # ... (tus textos existentes) ...
        "risk_deliberate_threat_present": "Deliberate Threat Present?",
        "risk_deliberate_threat_level": "Deliberate Threat Level",
        "no_deliberate_threat": "No",
        "low_deliberate_threat": "Low",
        "moderate_deliberate_threat": "Moderate",
        "high_deliberate_threat": "High",
    }
}
