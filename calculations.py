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
from modules.data_config import (tabla_tipo_impacto_global, matriz_probabilidad, matriz_impacto,
                                  factor_exposicion, factor_probabilidad, efectividad_controles,
                                  criticidad_límites, textos, PERFILES_BASE)

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
        amenaza_deliberada_factor (int): 1 si es deliberada, 0 si no.
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
        ponderaciones_globales = dict(zip(tabla_tipo_impacto_global['Tipo de Impacto'], tabla_tipo_impacto_global['Ponderación']))

        for tipo_impacto, severidad_valor in severidades_impacto_dict.items():
            ponderacion_global = ponderaciones_globales.get(tipo_impacto, 0) # Ponderación global (0-100)
            
            severidad_norm = float(severidad_valor) / 100.0       # Severidad normalizada (0-1)
            ponderacion_norm = float(ponderacion_global) / 100.0 # Ponderación normalizada (0-1)
            
            impacto_ponderado_i = severidad_norm * ponderacion_norm
            impacto_total_ponderado += impacto_ponderado_i
        
        # Asegurarse de que el impacto total ponderado no exceda 1 si las ponderaciones globales suman > 100
        # O si la suma de ponderaciones es fija (ej. 100), entonces el máximo impacto_total_ponderado será 1.0
        # Si las ponderaciones *del perfil* se usaran y sumaran 100, esto sería correcto.
        # Por ahora, si suma > 1, se normaliza implícitamente al final si el riesgo_residual > 1.
        # Si queremos asegurar que el impacto total ponderado esté entre 0 y 1, se puede dividir por su suma máxima teórica.
        # Para este ejemplo, asumimos que la suma de ponderaciones (globales o del perfil) es 100 para que el máximo sea 1.0

        amenaza_inherente = probabilidad * exposicion
        amenaza_residual = amenaza_inherente * (1 - efectividad_factor)
        amenaza_residual_ajustada = amenaza_residual * (1 + amenaza_deliberada_factor)

        riesgo_residual = amenaza_residual_ajustada * impacto_total_ponderado
        riesgo_residual = np.clip(riesgo_residual, 0, 1)

        return amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual

    except Exception as e:
        print(f"Error en calcular_criticidad: {e}")
        return 0.0, 0.0, 0.0, 0.0

def calcular_max_theoretical_risk(probabilidad_clasificacion, exposicion_clasificacion, amenaza_deliberada_factor, efectividad_control_max_risk_pct, perfil_data, categoria_seleccionada):
    """
    Calcula el máximo riesgo residual teórico posible para una combinación dada de
    Probabilidad, Exposición, Efectividad (mínima), y los impactos con sus ponderaciones
    máximas definidas para la categoría del perfil.

    Args:
        probabilidad_clasificacion (str): Clasificación de probabilidad.
        exposicion_clasificacion (str): Clasificación de exposición.
        amenaza_deliberada_factor (int): 1 si es deliberada, 0 si no.
        efectividad_control_max_risk_pct (float): Valor de efectividad de control (0-100) que se asume para el peor caso (0% efectividad).
        perfil_data (dict): Datos del perfil seleccionado.
        categoria_seleccionada (str): La categoría seleccionada dentro del perfil.

    Returns:
        float: El máximo riesgo residual teórico posible (0-1).
    """
    try:
        probabilidad = matriz_probabilidad_vals.get(probabilidad_clasificacion, 0.5)
        exposicion = factor_exposicion_vals.get(exposicion_clasificacion, 0.6)
        
        amenaza_deliberada_factor = float(amenaza_deliberada_factor)
        efectividad_factor_min = float(efectividad_control_max_risk_pct) / 100.0 # Efectividad mínima para el peor caso

        # Obtener la máxima severidad (100) para todos los tipos de impacto en la categoría
        impactos_config = perfil_data.get("categorias", {}).get(categoria_seleccionada, {})
        severidades_maximas = {}
        if "impacts" in impactos_config:
            for tipo_impacto in impactos_config["impacts"].keys():
                severidades_maximas[tipo_impacto] = 100.0 # Máxima severidad posible

        max_impacto_total_ponderado = 0.0
        # Usar las ponderaciones globales como base
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

        # Máxima amenaza residual ajustada (considerando mínima efectividad y amenaza deliberada sí)
        max_amenaza_residual = max_amenaza_inherente * (1 - efectividad_factor_min) # Mínima efectividad para máximo riesgo
        max_amenaza_residual_ajustada = max_amenaza_residual * (1 + amenaza_deliberada_factor)

        max_riesgo_residual = max_amenaza_residual_ajustada * max_impacto_total_ponderado
        max_riesgo_residual = np.clip(max_riesgo_residual, 0, 1)
        
        return max_riesgo_residual

    except Exception as e:
        print(f"Error en calcular_max_theoretical_risk: {e}")
        return 0.0

# --- Simulación Monte Carlo ---
# (La simulación Monte Carlo no necesita cambios mayores para esta mejora,
# ya que sigue operando con los factores base y rangos de pérdida.
# El cálculo de riesgo residual simulado se basará en los inputs simulados,
# manteniendo la consistencia con el modelo determinista.)
def simular_montecarlo(riesgos_para_simular, valor_economico_global, iteraciones=10000):
    """
    Ejecuta una simulación Monte Carlo para uno o varios riesgos.
    Utiliza parámetros base de probabilidad, exposición, efectividad y rangos de pérdida monetaria.
    """
    # ... (mantener la implementación anterior de simular_montecarlo) ...
    # La lógica aquí se basa en los factores (0-1) de P, E, Eff y los rangos de pérdida.
    # No necesita cambios directos para la lógica de múltiples impactos del modelo determinista,
    # pero el 'riesgo_residual_det' que se usa como base para el fallback en la simulación
    # ya se calcula considerando los impactos dinámicos.
    pass # Placeholder
