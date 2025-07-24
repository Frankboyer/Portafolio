import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from data_config import criticidad_límites, factores_amenaza_deliberada

# --- Funciones de Cálculo ---

def calcular_criticidad(probabilidad, exposicion, nivel_amenaza_deliberada_str, efectividad_control_pct, impacto_numerico, ponderacion_impacto, es_amenaza_deliberada_checkbox):
    """
    Calcula la amenaza inherente, residual y la criticidad final de un riesgo,
    considerando el nivel de amenaza deliberada y un checkbox de existencia.

    Args:
        probabilidad (float): Factor de probabilidad (0-1).
        exposicion (float): Factor de exposición (0-1).
        nivel_amenaza_deliberada_str (str): Nivel de amenaza deliberada ('No', 'Baja', 'Moderada', 'Alta').
        efectividad_control_pct (float): Efectividad del control existente en porcentaje (0-100).
        impacto_numerico (float): Impacto numérico del riesgo (0-100).
        ponderacion_impacto (float): Ponderación del tipo de impacto (0-1).
        es_amenaza_deliberada_checkbox (bool): True si el checkbox de amenaza deliberada está marcado, False si no.

    Returns:
        tuple: (amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual)
    """
    efectividad_control = efectividad_control_pct / 100.0

    # Obtener el factor de amenaza deliberada
    if es_amenaza_deliberada_checkbox:
        amenaza_deliberada_factor_val = factores_amenaza_deliberada[factores_amenaza_deliberada['Clasificacion'] == nivel_amenaza_deliberada_str]['Factor'].iloc[0]
    else:
        amenaza_deliberada_factor_val = 0.0

    amenaza_inherente = probabilidad * exposicion * (impacto_numerico / 100.0) * ponderacion_impacto
    amenaza_residual = amenaza_inherente * (1 + amenaza_deliberada_factor_val)
    amenaza_residual_ajustada = amenaza_residual * (1 - efectividad_control)
    riesgo_residual = amenaza_residual_ajustada * 100
    riesgo_residual = np.clip(riesgo_residual, 0, 100) # Asegura que el riesgo esté en el rango 0-100
    return amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual

def clasificar_criticidad(valor_riesgo, idioma='es'):
    """
    Clasifica un valor de riesgo en una categoría de criticidad.
    """
    for min_val, max_val, clasificacion_es, color, clasificacion_en in criticidad_límites:
        if min_val <= valor_riesgo <= max_val:
            return (clasificacion_es if idioma == 'es' else clasificacion_en), color
    return "Desconocido", "#cccccc" # Fallback

def simular_montecarlo(probabilidad_base, exposicion_base, impacto_numerico_base,
                       efectividad_base_pct, nivel_amenaza_deliberada_str_base, es_amenaza_deliberada_checkbox_base,
                       ponderacion_impacto, valor_economico, iteraciones=10000):
    """
    Realiza una simulación de Monte Carlo para el riesgo residual y las pérdidas económicas.
    Ahora considera el nivel de amenaza deliberada y el checkbox.

    Args:
        probabilidad_base (float): Probabilidad base del riesgo (0-1).
        exposicion_base (float): Exposición base del riesgo (0-1).
        impacto_numerico_base (float): Impacto numérico base del riesgo (0-100).
        efectividad_base_pct (float): Efectividad del control base en porcentaje (0-100).
        nivel_amenaza_deliberada_str_base (str): Nivel base de amenaza deliberada ('No', 'Baja', 'Moderada', 'Alta').
        es_amenaza_deliberada_checkbox_base (bool): Estado base del checkbox de amenaza deliberada.
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

    # Simular el factor de amenaza deliberada:
    if not es_amenaza_deliberada_checkbox_base:
        amenaza_deliberada_factores_sim = np.full(iteraciones, 0.0)
    else:
        base_factor = factores_amenaza_deliberada[factores_amenaza_deliberada['Clasificacion'] == nivel_amenaza_deliberada_str_base]['Factor'].iloc[0]
        if base_factor > 0:
            amenaza_deliberada_factores_sim = np.random.normal(base_factor, base_factor * 0.1, iteraciones)
            amenaza_deliberada_factores_sim = np.clip(amenaza_deliberada_factores_sim, 0, factores_amenaza_deliberada['Factor'].max())
        else:
            amenaza_deliberada_factores_sim = np.full(iteraciones, 0.0)


    riesgos_residuales_simulados = []
    for i in range(iteraciones):
        amenaza_inherente_sim = probabilidades_sim[i] * exposiciones_sim[i] * \
                                (impactos_num_sim[i] / 100.0) * ponderacion_impacto
        amenaza_residual_inicial_sim = amenaza_inherente_sim * (1 + amenaza_deliberada_factores_sim[i])
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
        'Amenaza Deliberada': amenaza_deliberada_factores_sim,
        'Riesgo Residual': riesgos_simulados_array
    })

    correlaciones_list = []
    variables_input = ['Probabilidad', 'Exposicion', 'Impacto Numerico', 'Efectividad Control', 'Amenaza Deliberada']
    for var in variables_input:
        if var in data_for_correlation.columns:
            if data_for_correlation[var].nunique() > 1:
                corr_val = pearsonr(data_for_correlation[var], data_for_correlation['Riesgo Residual'])[0]
                correlaciones_list.append({'Variable': var, 'Correlacion': corr_val})
            else:
                correlaciones_list.append({'Variable': var, 'Correlacion': 0.0}) # Correlación 0 si la variable no varía

    correlaciones_df = pd.DataFrame(correlaciones_list)

    return riesgos_simulados_array, perdidas_simuladas_array, correlaciones_df
