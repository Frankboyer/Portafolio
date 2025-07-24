import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any

def clasificar_criticidad(valor: float, idioma: str = 'es') -> Tuple[str, str]:
    """Clasifica el riesgo según su valor numérico"""
    if valor >= 0.8:
        return ("Muy Alto", "#FF0000") if idioma == 'es' else ("Very High", "#FF0000")
    elif valor >= 0.6:
        return ("Alto", "#FFA500") if idioma == 'es' else ("High", "#FFA500")
    elif valor >= 0.4:
        return ("Moderado", "#FFFF00") if idioma == 'es' else ("Moderate", "#FFFF00")
    elif valor >= 0.2:
        return ("Bajo", "#90EE90") if idioma == 'es' else ("Low", "#90EE90")
    else:
        return ("Muy Bajo", "#008000") if idioma == 'es' else ("Very Low", "#008000")

def calcular_criticidad(
    probabilidad: float,
    exposicion: float,
    nivel_amenaza: str,
    efectividad_control: float,
    impacto_numerico: float,
    ponderacion_impacto: float,
    amenaza_deliberada: bool
) -> Tuple[float, float, float, float]:
    """
    Calcula la criticidad del riesgo con todos los factores
    
    Returns:
        Tuple[amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual]
    """
    try:
        # Normalizar valores
        impacto_normalizado = impacto_numerico / 100
        efectividad_normalizada = efectividad_control / 100
        
        # Calcular amenaza inherente
        amenaza_inherente = probabilidad * exposicion
        
        # Ajustar por amenaza deliberada si aplica
        if amenaza_deliberada:
            factor_amenaza = 1 + (probabilidad * 0.5)  # Aumento del 50% base
            amenaza_inherente *= factor_amenaza
        
        # Calcular amenaza residual
        amenaza_residual = amenaza_inherente * (1 - efectividad_normalizada)
        
        # Ajuste final por ponderación de impacto
        riesgo_residual = amenaza_residual * impacto_normalizado * ponderacion_impacto
        
        return (
            round(amenaza_inherente, 4),
            round(amenaza_residual, 4),
            round(amenaza_residual * ponderacion_impacto, 4),
            round(riesgo_residual, 4)
        )
        
    except Exception as e:
        raise ValueError(f"Error en cálculo de criticidad: {str(e)}")

def simular_montecarlo(
    riesgo_base: float,
    iteraciones: int = 10000,
    variabilidad_probabilidad: float = 0.1,
    variabilidad_impacto: float = 0.15
) -> Dict[str, Any]:
    """Simulación Monte Carlo para análisis de riesgo"""
    try:
        # Generar distribuciones normales
        prob_simulada = np.random.normal(
            loc=riesgo_base,
            scale=riesgo_base * variabilidad_probabilidad,
            size=iteraciones
        )
        
        impacto_simulado = np.random.normal(
            loc=riesgo_base,
            scale=riesgo_base * variabilidad_impacto,
            size=iteraciones
        )
        
        # Calcular riesgos simulados
        riesgos_simulados = prob_simulada * impacto_simulado
        riesgos_simulados = np.clip(riesgos_simulados, 0, 1)  # Asegurar valores entre 0-1
        
        return {
            "mean": float(np.mean(riesgos_simulados)),
            "std": float(np.std(riesgos_simulados)),
            "percentiles": {
                "5": float(np.percentile(riesgos_simulados, 5)),
                "25": float(np.percentile(riesgos_simulados, 25)),
                "50": float(np.percentile(riesgos_simulados, 50)),
                "75": float(np.percentile(riesgos_simulados, 75)),
                "95": float(np.percentile(riesgos_simulados, 95))
            },
            "data": riesgos_simulados.tolist()
        }
    except Exception as e:
        raise ValueError(f"Error en simulación Monte Carlo: {str(e)}")
