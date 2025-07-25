# --- 2. calculations.py ---
# (Reutilizamos las funciones de cálculo de la versión anterior)
def clasificar_criticidad(valor, idioma="es"):
    for v_min, v_max, clasificacion_es, color, clasificacion_en in criticidad_límites:
        if v_min <= valor <= v_max:
            if idioma == "es": return clasificacion_es, color
            else: return clasificacion_en, color
    return "DESCONOCIDO", "#cccccc"

def calcular_criticidad(probabilidad, exposicion, amenaza_deliberada_factor, efectividad, valor_impacto_numerico, ponderacion_impacto):
    try:
        probabilidad = float(probabilidad)
        exposicion = float(exposicion)
        amenaza_deliberada_factor = float(amenaza_deliberada_factor)
        efectividad = float(efectividad) / 100.0
        valor_impacto_numerico = float(valor_impacto_numerico)
        ponderacion_impacto = float(ponderacion_impacto)

        impacto_norm = valor_impacto_numerico / 100.0 if valor_impacto_numerico > 0 else 0
        ponderacion_factor = ponderacion_impacto / 100.0

        amenaza_inherente = probabilidad * exposicion
        amenaza_residual = amenaza_inherente * (1 - efectividad)
        amenaza_residual_ajustada = amenaza_residual * (1 + amenaza_deliberada_factor)
        riesgo_residual = amenaza_residual_ajustada * impacto_norm * ponderacion_factor
        riesgo_residual = np.clip(riesgo_residual, 0, 1)
        return amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual
    except Exception as e:
        print(f"Error en calcular_criticidad: {e}")
        return 0.0, 0.0, 0.0, 0.0

def simular_montecarlo(riesgos_para_simular, valor_economico_global, iteraciones=10000):
    """
    Ejecuta una simulación Monte Carlo para uno o varios riesgos,
    considerando sus rangos de pérdida monetaria.
    """
    if valor_economico_global <= 0:
        return np.array([]), np.array([]), None, None

    if not riesgos_para_simular:
        return np.array([]), np.array([]), None, None

    try:
        num_riesgos = len(riesgos_para_simular)
        # Arrays para almacenar resultados agregados
        riesgo_residual_sim_agg = np.zeros(iteraciones)
        perdidas_usd_sim_agg = np.zeros(iteraciones)
        
        # Diccionario para almacenar datos de simulación por riesgo (para sensibilidad)
        sim_data_per_risk = {}

        # Parámetros base y variabilidad para simulación
        # Estos se determinarán por cada riesgo individual
        
        # Sigma común para probabilidad, exposición, efectividad
        sigma_comun = 0.1 

        for idx_risk, riesgo in enumerate(riesgos_para_simular):
            # Extraer parámetros del riesgo
            probabilidad_base = riesgo['Probabilidad']
            exposicion_base = riesgo['Exposición']
            efectividad_base_pct = riesgo['Efectividad del Control (%)']
            amenaza_deliberada_factor_base = 1 if riesgo['Amenaza Deliberada'] == 'Sí' else 0
            ponderacion_impacto = tabla_tipo_impacto[tabla_tipo_impacto['Tipo de Impacto'] == riesgo['Tipo de Impacto']]['Ponderación'].iloc[0]
            
            # Nuevos campos para rangos de pérdida monetaria
            min_loss_usd = riesgo.get('Min Loss USD', 0.0)
            max_loss_usd = riesgo.get('Max Loss USD', valor_economico_global) # Usar valor_economico_global si no está definido

            # Si el riesgo no tiene rangos definidos o son inválidos, usar un valor base derivado del riesgo residual y valor económico
            if min_loss_usd <= 0 and max_loss_usd <= 0:
                # Usar el riesgo residual determinista como una estimación central
                riesgo_residual_det = float(riesgo['Riesgo Residual'])
                min_loss_usd = riesgo_residual_det * valor_economico_global * 0.8 # 80% del valor determinista
                max_loss_usd = riesgo_residual_det * valor_economico_global * 1.2 # 120% del valor determinista
                if min_loss_usd <= 0 and max_loss_usd <= 0: # Si el riesgo determinista es 0
                    min_loss_usd = 0
                    max_loss_usd = 0 # O un valor muy pequeño para evitar divisiones por cero

            # Asegurar que min_loss <= max_loss
            if min_loss_usd > max_loss_usd:
                min_loss_usd, max_loss_usd = max_loss_usd, min_loss_usd

            # Manejo de caso donde ambos son cero
            if min_loss_usd == 0 and max_loss_usd == 0:
                loss_range_mid = 0
                loss_range_std = 0
            else:
                loss_range_mid = (min_loss_usd + max_loss_usd) / 2
                loss_range_std = (max_loss_usd - min_loss_usd) / 4 # Aproximación: Rango ~ 2*sigma

            # Convertir efectividad de porcentaje a factor
            efectividad_base = efectividad_base_pct / 100.0
            
            # Arrays para almacenar resultados de este riesgo específico
            riesgo_residual_sim_risk = np.zeros(iteraciones)
            perdidas_usd_sim_risk = np.zeros(iteraciones)

            # Datos para correlación de este riesgo
            sim_data_risk_dict = {}

            for i in range(iteraciones):
                probabilidad_sim = np.clip(np.random.normal(probabilidad_base, sigma_comun), 0.01, 1.0)
                exposicion_sim = np.clip(np.random.normal(exposicion_base, sigma_comun), 0.01, 1.0)
                efectividad_sim = np.clip(np.random.normal(efectividad_base, sigma_comun), 0.0, 1.0)

                # Simular la pérdida monetaria directamente
                sim_loss_usd = np.clip(np.random.normal(loss_range_mid, loss_range_std), min_loss_usd, max_loss_usd)
                perdidas_usd_sim_risk[i] = sim_loss_usd
                
                # Reutilizar la lógica de cálculo de riesgo residual con los parámetros simulados
                amenaza_inherente_sim = probabilidad_sim * exposicion_sim
                amenaza_residual_sim_iter = amenaza_inherente_sim * (1 - efectividad_sim)
                amenaza_residual_ajustada_sim = amenaza_residual_sim_iter * (1 + amenaza_deliberada_factor_base)
                
                # El riesgo residual aquí se recalcula para consistencia, aunque la pérdida principal viene de la simulación de pérdida
                # Si queremos el riesgo residual simulado, debe ser consistente con la simulación de pérdida
                # La manera más directa es usar la simulación de pérdida y relacionarla con el valor económico.
                # Si queremos el riesgo residual como un índice (0-1), debemos recalcularlo usando el factor de pérdida simulado.
                
                # Para simplificar y usar la pérdida monetaria directa:
                # Riesgo residual simulado_loss = sim_loss_usd / valor_economico_global
                # Pero esto puede ser problemático si el valor_economico_global es muy grande o pequeño.
                # Una mejor forma es mantener el cálculo original del riesgo residual y luego multiplicar por el valor económico.
                # Sin embargo, si la simulación principal es sobre la pérdida monetaria, usamos esa.
                # Optemos por mantener el cálculo del riesgo residual (0-1) para consistencia con las visualizaciones y luego la pérdida simulada.
                
                # Asumiendo que la simulación de pérdida ya incorpora el impacto, podemos derivar un 'impacto_norm_sim'
                impacto_norm_sim = sim_loss_usd / valor_economico_global if valor_economico_global > 0 else 0
                impacto_norm_sim = np.clip(impacto_norm_sim, 0, 1)

                riesgo_residual_sim_iter_calc = amenaza_residual_ajustada_sim * impacto_norm_sim * (ponderacion_impacto / 100.0)
                riesgo_residual_sim[i] = np.clip(riesgo_residual_sim_iter, 0, 1) # Usamos el riesgo_residual_sim_iter original para consistencia
                                                                                # con la idea de que es un factor de severidad
                                                                                # aunque la pérdida venga de otra simulación.

                # Guardar datos para sensibilidad de este riesgo
                sim_data_risk_dict[f"prob_{idx_risk}"] = probabilidad_sim
                sim_data_risk_dict[f"exp_{idx_risk}"] = exposicion_sim
                sim_data_risk_dict[f"eff_{idx_risk}"] = efectividad_sim
                sim_data_risk_dict[f"loss_{idx_risk}"] = sim_loss_usd # La pérdida simulada específica de este riesgo

            # Agregar los resultados de este riesgo a los agregados (simple suma para este ejemplo)
            # Para una agregación más sofisticada, se necesitaría considerar dependencias
            riesgo_residual_sim_agg += riesgo_residual_sim # Suma simple de los índices de riesgo residual
            perdidas_usd_sim_agg += perdidas_usd_sim_risk # Suma simple de las pérdidas

            # Guardar los datos de simulación por riesgo
            sim_data_per_risk[f"Riesgo_{idx_risk}"] = {
                "probabilidad": sim_data_risk_dict.get(f"prob_{idx_risk}", np.array([])),
                "exposicion": sim_data_risk_dict.get(f"exp_{idx_risk}", np.array([])),
                "efectividad": sim_data_risk_dict.get(f"eff_{idx_risk}", np.array([])),
                "perdida_usd": sim_data_risk_dict.get(f"loss_{idx_risk}", np.array([])),
            }

        # Normalizar el riesgo residual agregado
        riesgo_residual_sim_agg /= num_riesgos # Promedio simple

        # Calcular correlaciones agregadas
        df_sim_agg = pd.DataFrame({
            'probabilidad_agg': np.array([np.random.normal(probabilidad_base, sigma_comun) for _ in range(iteraciones)]), # Esto debería ser un promedio de los probs simulados
            'exposicion_agg': np.array([np.random.normal(exposicion_base, sigma_comun) for _ in range(iteraciones)]), # Esto debería ser un promedio de los expos simulados
            'efectividad_agg': np.array([np.random.normal(efectividad_base, sigma_comun) for _ in range(iteraciones)]), # Esto debería ser un promedio de los eff simulados
            'perdida_usd_agg': perdidas_usd_sim_agg
        })
        
        # Recrear promedios para el análisis de sensibilidad agregado
        # Esto es una aproximación; idealmente deberíamos promediar los arrays simulados
        # Pero para simplificar aquí, volvemos a generar valores base promedio
        # (Una mejor implementación promediaría los arrays ya generados)
        
        # Promediamos los arrays simulados para el análisis de sensibilidad agregado
        if num_riesgos > 0:
            avg_prob = np.mean([sim_data['probabilidad'] for sim_data in sim_data_per_risk.values() if 'probabilidad' in sim_data], axis=0)
            avg_exp = np.mean([sim_data['exposicion'] for sim_data in sim_data_per_risk.values() if 'exposicion' in sim_data], axis=0)
            avg_eff = np.mean([sim_data['efectividad'] for sim_data in sim_data_per_risk.values() if 'efectividad' in sim_data], axis=0)

            df_sim_agg_final = pd.DataFrame({
                'probabilidad_avg': avg_prob,
                'exposicion_avg': avg_exp,
                'efectividad_avg': avg_eff,
                'perdida_usd_agg': perdidas_usd_sim_agg
            })
        else:
            df_sim_agg_final = pd.DataFrame()


        valid_cols_agg = [col for col in ['probabilidad_avg', 'exposicion_avg', 'efectividad_avg'] if col in df_sim_agg_final.columns and df_sim_agg_final[col].std() > 0]
        correlations_agg = pd.Series(dtype=float)
        if valid_cols_agg and not df_sim_agg_final.empty:
            correlations_agg = df_sim_agg_final[valid_cols_agg + ['perdida_usd_agg']].corr(method='pearson')['perdida_usd_agg'].drop('perdida_usd_agg').abs().sort_values(ascending=False)

        return riesgo_residual_sim_agg, perdidas_usd_sim_agg, correlations_agg, sim_data_per_risk

    except Exception as e:
        print(f"Error en simular_montecarlo: {e}")
        return np.array([]), np.array([]), None, None
