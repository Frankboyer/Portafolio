import pandas as pd
import numpy as np
from scipy.stats import norm, pearsonr

# --- Funciones de Cálculo ---

def calcular_criticidad(probabilidad, exposicion, amenaza_deliberada_factor, efectividad_control_pct, impacto_numerico, ponderacion_impacto):
    """
    Calcula la amenaza inherente, residual y la criticidad final de un riesgo.

    Args:
        probabilidad (float): Factor de probabilidad (0-1).
        exposicion (float): Factor de exposición (0-1).
        amenaza_deliberada_factor (float): 1.0 si es amenaza deliberada, 0.0 si no.
        efectividad_control_pct (float): Efectividad del control existente en porcentaje (0-100).
        impacto_numerico (float): Impacto numérico del riesgo (0-100).
        ponderacion_impacto (float): Ponderación del tipo de impacto (0-1).

    Returns:
        tuple: (amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual)
    """
    efectividad_control = efectividad_control_pct / 100.0
    amenaza_inherente = probabilidad * exposicion * (impacto_numerico / 100.0) * ponderacion_impacto
    amenaza_residual = amenaza_inherente * (1 + amenaza_deliberada_factor)
    amenaza_residual_ajustada = amenaza_residual * (1 - efectividad_control)
    riesgo_residual = amenaza_residual_ajustada * 100
    riesgo_residual = np.clip(riesgo_residual, 0, 100)
    return amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual

def clasificar_criticidad(valor_riesgo, idioma='es'):
    """
    Clasifica un valor de riesgo en una categoría de criticidad.

    Args:
        valor_riesgo (float): El valor numérico del riesgo residual.
        idioma (str): 'es' para español, 'en' para inglés.

    Returns:
        tuple: (clasificación, color_hex)
    """
    # Importar aquí para asegurar acceso a criticidad_límites
    from data_config import criticidad_límites

    for min_val, max_val, clasificacion_es, color, clasificacion_en in criticidad_límites:
        if min_val <= valor_riesgo <= max_val:
            return (clasificacion_es if idioma == 'es' else clasificacion_en), color
    return "Desconocido", "#cccccc" # Fallback

def simular_montecarlo(probabilidad_base, exposicion_base, impacto_numerico_base,
                       efectividad_base_pct, amenaza_deliberada_factor_base,
                       ponderacion_impacto, valor_economico, iteraciones=10000):
    """
    Realiza una simulación de Monte Carlo para el riesgo residual y las pérdidas económicas.

    Args:
        probabilidad_base (float): Probabilidad base del riesgo (0-1).
        exposicion_base (float): Exposición base del riesgo (0-1).
        impacto_numerico_base (float): Impacto numérico base del riesgo (0-100).
        efectividad_base_pct (float): Efectividad del control base en porcentaje (0-100).
        amenaza_deliberada_factor_base (float): 1.0 si es amenaza deliberada, 0.0 si no.
        ponderacion_impacto (float): Ponderación del tipo de impacto (0-1).
        valor_economico (float): Valor económico del activo afectado.
        iteraciones (int): Número de iteraciones de la simulación.

    Returns:
        tuple: (np.array de riesgos residuales simulados, np.array de pérdidas económicas simuladas, pd.DataFrame de correlaciones)
    """
    efectividad_base = efectividad_base_pct / 100.0

    probabilidades_sim = np.random.normal(probabilidad_base, probabilidad_base * 0.1, iteraciones)
    probabilidades_sim = np.clip(probabilidades_sim, 0.01, 0.99)

    exposiciones_sim = np.random.normal(exposicion_base, exposicion_base * 0.1, iteraciones)
    exposiciones_sim = np.clip(exposiciones_sim, 0.01, 0.99)

    impactos_num_sim = np.random.normal(impacto_numerico_base, 5, iteraciones)
    impactos_num_sim = np.clip(impactos_num_sim, 0, 100)

    efectividades_sim = np.random.normal(efectividad_base, 0.05, iteraciones)
    efectividades_sim = np.clip(efectividades_sim, 0, 0.99)

    amenaza_deliberada_sim = np.full(iteraciones, amenaza_deliberada_factor_base)

    riesgos_residuales_simulados = []
    for i in range(iteraciones):
        amenaza_inherente_sim = probabilidades_sim[i] * exposiciones_sim[i] * \
                                (impactos_num_sim[i] / 100.0) * ponderacion_impacto
        amenaza_residual_inicial_sim = amenaza_inherente_sim * (1 + amenaza_deliberada_sim[i])
        amenaza_residual_ajustada_sim = amenaza_residual_inicial_sim * (1 - efectividades_sim[i])
        riesgo_residual_val_sim = amenaza_residual_ajustada_sim * 100
        riesgos_residuales_simulados.append(np.clip(riesgo_residual_val_sim, 0, 100))

    riesgos_simulados_array = np.array(riesgos_residuales_simulados)
    perdidas_simuladas_array = riesgos_simulados_array / 100 * valor_economico

    data_for_correlation = pd.DataFrame({
        'Probabilidad': probabilidades_sim,
        'Exposicion': exposiciones_sim,
        'Impacto Numerico': impactos_num_sim,
        'Efectividad Control': efectividades_sim,
        'Amenaza Deliberada': amenaza_deliberada_sim,
        'Riesgo Residual': riesgos_simulados_array
    })

    correlaciones_list = []
    variables_input = ['Probabilidad', 'Exposicion', 'Impacto Numerico', 'Efectividad Control', 'Amenaza Deliberada']
    for var in variables_input:
        if var in data_for_correlation.columns:
            if data_for_correlation[var].nunique() > 1: # Solo calcular correlación si la variable varía
                corr_val = pearsonr(data_for_correlation[var], data_for_correlation['Riesgo Residual'])[0]
                correlaciones_list.append({'Variable': var, 'Correlacion': corr_val})
            else: # Si la variable es constante, su correlación con cualquier otra variable es NaN o 0
                correlaciones_list.append({'Variable': var, 'Correlacion': 0.0})


    correlaciones_df = pd.DataFrame(correlaciones_list)

    return riesgos_simulados_array, perdidas_simuladas_array, correlaciones_df
