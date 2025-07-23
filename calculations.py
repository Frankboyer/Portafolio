import numpy as np
import pandas as pd
from data_config import criticidad_límites # Importar desde el nuevo archivo

def clasificar_criticidad(valor, idioma="es"):
    """
    Clasifica un valor numérico de riesgo en una categoría de criticidad
    y asigna un color asociado.

    Args:
        valor (float): El valor numérico del riesgo residual (entre 0 y 1).
        idioma (str, optional): El idioma para la clasificación ('es' para español, 'en' para inglés).
                                 Por defecto es 'es'.

    Returns:
        tuple: Una tupla que contiene la clasificación del riesgo (str) y el color hexadecimal (str).
               Ejemplo: ('ACEPTABLE', '#28a745')
    """
    for v_min, v_max, clasificacion_es, color, clasificacion_en in criticidad_límites:
        if v_min <= valor <= v_max:
            if idioma == "es":
                return clasificacion_es, color
            else:
                return clasificacion_en, color
    return "DESCONOCIDO", "#cccccc" # Default si no se encuentra en ningún rango

def calcular_criticidad(probabilidad, exposicion, amenaza_deliberada_factor, efectividad, valor_impacto_numerico, ponderacion_impacto):
    """
    Calcula las diferentes métricas de riesgo basadas en un modelo determinista.

    Args:
        probabilidad (float): Valor de probabilidad de ocurrencia (0-1).
        exposicion (float): Valor de exposición (0-1).
        amenaza_deliberada_factor (float): Factor que indica si es una amenaza deliberada (0 para No, 1 para Sí).
        efectividad (float): Efectividad del control en porcentaje (0-100).
        valor_impacto_numerico (float): Valor de impacto numérico (0-100).
        ponderacion_impacto (float): Ponderación del tipo de impacto (ej. 25 para Humano).

    Returns:
        tuple: Una tupla que contiene:
               - amenaza_inherente (float): Amenaza inherente calculada.
               - amenaza_residual (float): Amenaza residual antes del ajuste por amenaza deliberada.
               - amenaza_residual_ajustada (float): Amenaza residual ajustada por amenaza deliberada.
               - riesgo_residual (float): El riesgo residual final, normalizado entre 0 y 1.
    """
    try:
        # Asegurarse de que los valores numéricos estén en el rango correcto
        probabilidad = float(probabilidad)
        exposicion = float(exposicion)
        amenaza_deliberada_factor = float(amenaza_deliberada_factor)
        efectividad = float(efectividad) / 100.0 # Convertir porcentaje a factor (0-1)
        valor_impacto_numerico = float(valor_impacto_numerico)
        ponderacion_impacto = float(ponderacion_impacto)

        # Normalizar el impacto numérico y la ponderación para la fórmula
        # El impacto numérico (0-100) se normaliza a un factor de 0-1
        impacto_norm = valor_impacto_numerico / 100.0 if valor_impacto_numerico > 0 else 0
        # La ponderación del impacto (ej. 25 para humano) se normaliza a un factor de 0-1
        ponderacion_factor = ponderacion_impacto / 100.0

        # Cálculos de riesgo
        amenaza_inherente = probabilidad * exposicion
        amenaza_residual = amenaza_inherente * (1 - efectividad)

        # Ajuste a la lógica original: si amenaza_deliberada_factor es 1 (Sí), duplica amenaza_residual
        # Si es 0 (No), mantiene amenaza_residual.
        amenaza_residual_ajustada = amenaza_residual * (1 + amenaza_deliberada_factor)

        # El riesgo residual final se calcula combinando la amenaza ajustada con el impacto y la ponderación
        riesgo_residual = amenaza_residual_ajustada * impacto_norm * ponderacion_factor

        # Asegurar que el riesgo residual no exceda 1
        riesgo_residual = np.clip(riesgo_residual, 0, 1)

        return amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual

    except Exception as e:
        print(f"Error en calcular_criticidad: {e}")
        return 0.0, 0.0, 0.0, 0.0 # Retornar valores seguros en caso de error

def simular_montecarlo(probabilidad_base, exposicion_base, impacto_numerico_base, efectividad_base_pct, amenaza_deliberada_factor_base, ponderacion_impacto, valor_economico, iteraciones=10000):
    """
    Ejecuta una simulación Monte Carlo para el cálculo de riesgos y pérdidas económicas.
    Simula la variabilidad de los factores de riesgo y calcula la distribución de pérdidas.

    Args:
        probabilidad_base (float): Probabilidad base de ocurrencia.
        exposicion_base (float): Exposición base.
        impacto_numerico_base (float): Impacto numérico base (0-100).
        efectividad_base_pct (float): Efectividad del control base en porcentaje (0-100).
        amenaza_deliberada_factor_base (float): Factor de amenaza deliberada (0 o 1).
        ponderacion_impacto (float): Ponderación del tipo de impacto (0-100).
        valor_economico (float): Valor económico del activo bajo riesgo en USD.
        iteraciones (int, optional): Número de iteraciones para la simulación. Por defecto es 10000.

    Returns:
        tuple: Una tupla que contiene:
               - riesgo_residual_sim (np.array): Array de los valores de riesgo residual simulados.
               - perdidas_usd_sim (np.array): Array de las pérdidas económicas simuladas en USD.
               - correlations (pd.Series or None): Series de pandas con las correlaciones de Pearson
                                                   entre los factores de riesgo y la pérdida económica.
                                                   None si no hay datos para correlacionar.
    """
    if valor_economico <= 0:
        return np.array([]), np.array([]), None # Retornar arrays vacíos si el valor económico es 0 o negativo

    try:
        # Convertir efectividad de porcentaje a factor
        efectividad_base = efectividad_base_pct / 100.0
        
        # Parámetros de variabilidad para cada factor (desviación estándar)
        # Ajustar sigmas según la incertidumbre deseada
        sigma_probabilidad = 0.1 # Pequeña variabilidad para probabilidades
        sigma_exposicion = 0.1
        sigma_impacto_norm = 0.05 # Menor variabilidad para impacto ya normalizado 0-1
        sigma_efectividad = 0.1
        # sigma_amenaza_deliberada = 0 # Normalmente binario, no se simula variabilidad aquí

        # Transformamos el impacto numérico base (0-100) en un porcentaje del valor económico
        factor_perdida_base = impacto_numerico_base / 100.0

        # Definimos un rango de incertidumbre para este factor de pérdida monetaria.
        sigma_factor_perdida = 0.20 * factor_perdida_base
        if sigma_factor_perdida == 0 and factor_perdida_base > 0: # Evitar sigma 0 si hay impacto
            sigma_factor_perdida = 0.05 # Mínima variabilidad si el impacto es bajo pero existente
        elif factor_perdida_base == 0:
            sigma_factor_perdida = 0 # No hay variabilidad si no hay impacto base

        # Arrays para almacenar los resultados de la simulación
        riesgo_residual_sim = np.zeros(iteraciones)
        perdidas_usd_sim = np.zeros(iteraciones)

        for i in range(iteraciones):
            # Generar valores aleatorios para cada parámetro usando una distribución normal
            # y asegurándose de que estén dentro de rangos lógicos [0,1] o [1,100]
            probabilidad_sim = np.clip(np.random.normal(probabilidad_base, sigma_probabilidad), 0.01, 1.0)
            exposicion_sim = np.clip(np.random.normal(exposicion_base, sigma_exposicion), 0.01, 1.0)
            efectividad_sim = np.clip(np.random.normal(efectividad_base, sigma_efectividad), 0.0, 1.0)

            # Simular el factor de pérdida monetaria
            sim_factor_perdida = np.clip(np.random.normal(factor_perdida_base, sigma_factor_perdida), 0.0, 1.0)
            
            # Recalcular impacto_norm para la simulación
            # Usamos el factor de pérdida simulado como el impacto_norm para la fórmula
            impacto_norm_sim = sim_factor_perdida

            # Amenaza deliberada se mantiene base o se puede introducir una probabilidad binaria
            amenaza_deliberada_sim = amenaza_deliberada_factor_base # Asumimos que no varía en la simulación a menos que se indique

            # Reutilizar la lógica de cálculo de riesgo con los valores simulados
            amenaza_inherente_sim = probabilidad_sim * exposicion_sim
            amenaza_residual_sim = amenaza_inherente_sim * (1 - efectividad_sim)
            amenaza_residual_ajustada_sim = amenaza_residual_sim * (1 + amenaza_deliberada_sim)
            
            # Calcular el riesgo residual simulado
            riesgo_residual_iter = amenaza_residual_ajustada_sim * impacto_norm_sim * (ponderacion_impacto / 100.0)
            riesgo_residual_sim[i] = np.clip(riesgo_residual_iter, 0, 1)

            # Calcular la pérdida económica simulada
            perdidas_usd_sim[i] = riesgo_residual_sim[i] * valor_economico # El riesgo residual es un índice de criticidad que se aplica al valor económico

        # Calcular correlaciones para análisis de sensibilidad
        df_sim = pd.DataFrame({
            'probabilidad': np.array([np.random.normal(probabilidad_base, sigma_probabilidad) for _ in range(iteraciones)]),
            'exposicion': np.array([np.random.normal(exposicion_base, sigma_exposicion) for _ in range(iteraciones)]),
            'impacto_norm': np.array([np.random.normal(factor_perdida_base, sigma_factor_perdida) for _ in range(iteraciones)]),
            'efectividad': np.array([np.random.normal(efectividad_base, sigma_efectividad) for _ in range(iteraciones)]),
            'perdida_usd': perdidas_usd_sim
        })
        
        # Calcular correlaciones de Pearson con la pérdida económica
        # Asegurarse de que las columnas tengan varianza para calcular correlación
        valid_cols = [col for col in ['probabilidad', 'exposicion', 'impacto_norm', 'efectividad'] if df_sim[col].std() > 0]
        
        if valid_cols:
            correlations = df_sim[valid_cols + ['perdida_usd']].corr(method='pearson')['perdida_usd'].drop('perdida_usd').abs().sort_values(ascending=False)
        else:
            correlations = pd.Series(dtype=float) # No hay columnas válidas para correlación

        return riesgo_residual_sim, perdidas_usd_sim, correlations

    except Exception as e:
        print(f"Error en simular_montecarlo: {e}")
        return np.array([]), np.array([]), None # Retornar arrays vacíos y None para correlaciones
