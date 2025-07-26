# modules/calculations.py
"""
Este módulo contiene la lógica para los cálculos del modelo de riesgo determinista
y la simulación Monte Carlo, incluyendo soporte para múltiples impactos ponderados
y cálculo de máximo riesgo teórico.
"""
import streamlit as st
import pandas as pd
import numpy as np
import json
from typing import Dict, List, Tuple, Any

# --- Importaciones ---
# Asegúrate de que las rutas de importación sean correctas según tu estructura
from modules.data_config import (tabla_tipo_impacto_global, matriz_probabilidad, matriz_impacto,
                                  factor_exposicion, factor_probabilidad, efectividad_controles,
                                  criticidad_límites, textos, PERFILES_BASE) # Importar todos los datos necesarios

# --- Mapeos ---
matriz_probabilidad_vals = {
    'Muy Baja': 0.1, 'Baja': 0.3, 'Media': 0.5, 'Alta': 0.7, 'Muy Alta': 0.9
}
factor_exposicion_vals = {
    'Muy Baja': 0.1, 'Baja': 0.3, 'Media': 0.6, 'Alta': 0.9, 'Muy Alta': 1.0
}

def clasificar_criticidad(valor, idioma="es"):
    """Clasifica un valor numérico de riesgo (0-1) en una categoría y color."""
    for v_min, v_max, clasificacion_es, color, clasificacion_en in criticidad_límites:
        if v_min <= valor <= v_max:
            if idioma == "es": return clasificacion_es, color
            else: return clasificacion_en, color
    return "DESCONOCIDO", "#cccccc"

def calcular_criticidad(probabilidad_clasificacion, exposicion_clasificacion, amenaza_deliberada_factor, efectividad, severidades_impacto_dict):
    """
    Calcula las métricas de riesgo determinista considerando múltiples tipos de impacto
    con ponderaciones (basado en tabla_tipo_impacto_global por defecto).

    Args:
        probabilidad_clasificacion (str): Clasificación de probabilidad.
        exposicion_clasificacion (str): Clasificación de exposición.
        amenaza_deliberada_factor (int): 1 si la amenaza es deliberada, 0 si no.
        efectividad (float): Porcentaje de efectividad del control (0-100).
        severidades_impacto_dict (dict): Diccionario { 'TipoImpacto': Severidad (0-100), ... }.

    Returns:
        tuple: (amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual).
               Retorna valores de 0.0 en caso de error.
    """
    try:
        probabilidad = matriz_probabilidad_vals.get(probabilidad_clasificacion, 0.5)
        exposicion = factor_exposicion_vals.get(exposicion_clasificacion, 0.6)

        amenaza_deliberada_factor = float(amenaza_deliberada_factor)
        efectividad_factor = float(efectividad) / 100.0

        # Calcular el Impacto Total Ponderado
        impacto_total_ponderado = 0.0
        # Usamos las ponderaciones globales de tabla_tipo_impacto_global
        # Si las ponderaciones fueran dinámicas por perfil/categoría, esta lógica debería cambiar.
        ponderaciones_globales = dict(zip(tabla_tipo_impacto_global['Tipo de Impacto'], tabla_tipo_impacto_global['Ponderación']))

        for tipo_impacto, severidad_valor in severidades_impacto_dict.items():
            # Si el tipo de impacto no está en las ponderaciones globales, se puede asignar un valor por defecto o ignorar
            ponderacion_global = ponderaciones_globales.get(tipo_impacto, 0)
            
            severidad_norm = float(severidad_valor) / 100.0
            ponderacion_norm = float(ponderacion_global) / 100.0
            
            impacto_ponderado_i = severidad_norm * ponderacion_norm
            impacto_total_ponderado += impacto_ponderado_i
        
        # Normalizar el impacto total ponderado si es necesario (asumimos que la suma de ponderaciones globales es 100)

        amenaza_inherente = probabilidad * exposicion
        amenaza_residual = amenaza_inherente * (1 - efectividad_factor)
        amenaza_residual_ajustada = amenaza_residual * (1 + amenaza_deliberada_factor)

        riesgo_residual = amenaza_residual_ajustada * impacto_total_ponderado
        riesgo_residual = np.clip(riesgo_residual, 0, 1)

        return amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual

    except Exception as e:
        print(f"Error en calcular_criticidad: {e}")
        return 0.0, 0.0, 0.0, 0.0

def calcular_max_theoretical_risk(probabilidad_clasificacion, exposicion_clasificacion, amenaza_deliberada_factor, efectividad_control_pct, perfil_data, categoria_seleccionada):
    """
    Calcula el máximo riesgo residual teórico posible para una combinación dada de
    Probabilidad, Exposición, Efectividad (mínima), y los impactos con sus ponderaciones
    máximas definidas para la categoría del perfil.

    Args:
        probabilidad_clasificacion (str): Clasificación de probabilidad.
        exposicion_clasificacion (str): Clasificación de exposición.
        amenaza_deliberada_factor (int): 1 si es deliberada, 0 si no.
        efectividad_control_max_risk_pct (float): Valor de efectividad (0-100) para el peor caso (0% efectividad).
        perfil_data (dict): Datos del perfil seleccionado.
        categoria_seleccionada (str): La categoría seleccionada dentro del perfil.

    Returns:
        float: El máximo riesgo residual teórico posible (0-1).
    """
    try:
        probabilidad = matriz_probabilidad_vals.get(probabilidad_clasificacion, 0.5)
        exposicion = factor_exposicion_vals.get(exposicion_clasificacion, 0.6)
        
        amenaza_deliberada_factor = float(amenaza_deliberada_factor)
        efectividad_factor_min = 0.0 # Para máximo riesgo, se asume mínima efectividad (0%)

        # Obtener la máxima severidad (100) para todos los tipos de impacto en la categoría
        impactos_config = perfil_data.get("categorias", {}).get(categoria_seleccionada, {}).get("impacts", {})
        severidades_maximas = {}
        if "impacts" in impactos_config:
            for tipo_impacto in impactos_config["impacts"].keys():
                severidades_maximas[tipo_impacto] = 100.0

        max_impacto_total_ponderado = 0.0
        ponderaciones_globales = dict(zip(tabla_tipo_impacto_global['Tipo de Impacto'], tabla_tipo_impacto_global['Ponderación']))

        for tipo_impacto, severidad_max in severidades_maximas.items():
            ponderacion_global = ponderaciones_globales.get(tipo_impacto, 0)
            severidad_norm = float(severidad_max) / 100.0
            ponderacion_norm = float(ponderacion_global) / 100.0
            impacto_ponderado_i = severidad_norm * ponderacion_norm
            max_impacto_total_ponderado += impacto_ponderado_i
        
        # Máxima amenaza inherente (usando la clasificación seleccionada)
        max_prob = matriz_probabilidad_vals.get(probabilidad_clasificacion, 0.5)
        max_exp = factor_exposicion_vals.get(exposicion_clasificacion, 0.6)
        max_amenaza_inherente = max_prob * max_exp

        # Máxima amenaza residual ajustada
        max_amenaza_residual = max_amenaza_inherente * (1 - efectividad_factor_min)
        max_amenaza_residual_ajustada = max_amenaza_residual * (1 + amenaza_deliberada_factor)

        max_riesgo_residual = max_amenaza_residual_ajustada * max_impacto_total_ponderado
        max_riesgo_residual = np.clip(max_riesgo_residual, 0, 1)
        
        return max_riesgo_residual

    except Exception as e:
        print(f"Error en calcular_max_theoretical_risk: {e}")
        return 0.0

def simular_montecarlo(riesgos_para_simular, valor_economico_global, iteraciones=10000):
    """
    Ejecuta una simulación Monte Carlo para uno o varios riesgos.
    Utiliza parámetros base de probabilidad, exposición, efectividad y rangos de pérdida monetaria.
    """
    if valor_economico_global <= 0 or not riesgos_para_simular:
        return np.array([]), np.array([]), None, {}

    try:
        num_riesgos = len(riesgos_para_simular)
        riesgo_residual_sim_agg = np.zeros(iteraciones)
        perdidas_usd_sim_agg = np.zeros(iteraciones)
        sim_data_per_risk = {}

        sigma_comun_factor = 0.1 # Sigma para factores (0-1)

        for idx_risk, riesgo in enumerate(riesgos_para_simular):
            # Parámetros base del riesgo (Factores 0-1)
            probabilidad_base_factor = float(riesgo['Probabilidad'])
            exposicion_base_factor = float(riesgo['Exposición'])
            efectividad_base_pct = riesgo['Efectividad del Control (%)']
            efectividad_base = efectividad_base_pct / 100.0
            amenaza_deliberada_factor_base = 1 if riesgo['Amenaza Deliberada'] == 'Sí' else 0
            
            min_loss_usd = riesgo.get('Min Loss USD', 0.0)
            max_loss_usd = riesgo.get('Max Loss USD', 0.0)

            # Fallback para rangos de pérdida monetaria
            if min_loss_usd <= 0 and max_loss_usd <= 0:
                riesgo_residual_det = float(riesgo['Riesgo Residual'])
                fallback_mid = riesgo_residual_det * valor_economico_global
                fallback_std = fallback_mid * 0.20
                if fallback_mid == 0: fallback_std = 1000
                min_loss_usd = max(0, fallback_mid - fallback_std)
                max_loss_usd = fallback_mid + fallback_std
            
            if min_loss_usd > max_loss_usd: min_loss_usd, max_loss_usd = max_loss_usd, min_loss_usd

            loss_range_mid = (min_loss_usd + max_loss_usd) / 2
            loss_range_std = (max_loss_usd - min_loss_usd) / 4 if max_loss_usd > min_loss_usd else 0

            # Arrays para resultados de este riesgo
            riesgo_residual_sim_risk = np.zeros(iteraciones)
            perdidas_usd_sim_risk = np.zeros(iteraciones)
            sim_data_risk_dict = {}

            for i in range(iteraciones):
                probabilidad_sim = np.clip(np.random.normal(probabilidad_base_factor, sigma_comun_factor), 0.01, 1.0)
                exposicion_sim = np.clip(np.random.normal(exposicion_base_factor, sigma_comun_factor), 0.01, 1.0)
                efectividad_sim = np.clip(np.random.normal(efectividad_base, sigma_comun_factor), 0.0, 1.0)

                sim_loss_usd = np.clip(np.random.normal(loss_range_mid, loss_range_std), min_loss_usd, max_loss_usd)
                perdidas_usd_sim_risk[i] = sim_loss_usd
                
                impacto_norm_sim = sim_loss_usd / valor_economico_global if valor_economico_global > 0 else 0
                impacto_norm_sim = np.clip(impacto_norm_sim, 0, 1)

                tipo_impacto_principal = riesgo.get('Tipo de Impacto', 'Económico')
                ponderacion_impacto_principal = dict(zip(tabla_tipo_impacto_global['Tipo de Impacto'], tabla_tipo_impacto_global['Ponderación'])).get(tipo_impacto_principal, 0)
                
                amenaza_inherente_sim = probabilidad_sim * exposicion_sim
                amenaza_residual_sim_iter = amenaza_inherente_sim * (1 - efectividad_sim)
                amenaza_residual_ajustada_sim = amenaza_residual_sim_iter * (1 + amenaza_deliberada_factor_base)
                
                riesgo_residual_sim_iter_calc = amenaza_residual_ajustada_sim * impacto_norm_sim * (ponderacion_impacto_principal / 100.0)
                riesgo_residual_sim_risk[i] = np.clip(riesgo_residual_sim_iter_calc, 0, 1)

                sim_data_risk_dict[f"prob_{idx_risk}"] = probabilidad_sim * 100
                sim_data_risk_dict[f"exp_{idx_risk}"] = exposicion_sim * 100
                sim_data_risk_dict[f"eff_{idx_risk}"] = efectividad_sim * 100
                sim_data_risk_dict[f"loss_{idx_risk}"] = sim_loss_usd

            riesgo_residual_sim_agg += riesgo_residual_sim_risk
            perdidas_usd_sim_agg += perdidas_usd_sim_risk
            sim_data_per_risk[f"Riesgo {idx_risk+1} ({riesgo['Nombre del Riesgo']})"] = sim_data_risk_dict

        if num_riesgos > 0: riesgo_residual_sim_agg /= num_riesgos
        else: riesgo_residual_sim_agg = np.zeros(iteraciones)

        df_sim_agg_final = pd.DataFrame()
        if sim_data_per_risk:
            avg_prob_100 = np.mean([data.get('prob_0', np.zeros(iteraciones)) for data in sim_data_per_risk.values() if 'prob_0' in data], axis=0)
            avg_exp_100 = np.mean([data.get('exp_0', np.zeros(iteraciones)) for data in sim_data_per_risk.values() if 'exp_0' in data], axis=0)
            avg_eff_100 = np.mean([data.get('eff_0', np.zeros(iteraciones)) for data in sim_data_per_risk.values() if 'eff_0' in data], axis=0)

            df_sim_agg_final = pd.DataFrame({
                'probabilidad_avg_%': avg_prob_100,
                'exposicion_avg_%': avg_exp_100,
                'efectividad_avg_%': avg_eff_100,
                'perdida_usd_agg': perdidas_usd_sim_agg
            })

        correlations_agg = pd.Series(dtype=float)
        if not df_sim_agg_final.empty:
            valid_cols_agg = [col for col in ['probabilidad_avg_%', 'exposicion_avg_%', 'efectividad_avg_%'] if df_sim_agg_final[col].std() > 0]
            if valid_cols_agg:
                correlations_agg = df_sim_agg_final[valid_cols_agg + ['perdida_usd_agg']].corr(method='pearson')['perdida_usd_agg'].drop('perdida_usd_agg').abs().sort_values(ascending=False)

        return riesgo_residual_sim_agg, perdidas_usd_sim_agg, correlations_agg, sim_data_per_risk

    except Exception as e:
        print(f"Error en simular_montecarlo: {e}")
        return np.array([]), np.array([]), None, None
