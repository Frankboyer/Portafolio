import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Importar desde los módulos locales
from data_config import tabla_tipo_impacto, matriz_probabilidad, matriz_impacto, factor_exposicion, factor_probabilidad, efectividad_controles, criticidad_límites, textos
from calculations import clasificar_criticidad, calcular_criticidad, simular_montecarlo
from plotting import create_heatmap, create_pareto_chart, plot_montecarlo_histogram, create_sensitivity_plot
from utils import reset_form_fields, format_risk_dataframe

# --- Configuración de la página ---
st.set_page_config(layout="wide", page_title="Calculadora de Riesgos", page_icon="🛡️")

# --- CSS Personalizado ---
st.markdown("""
    <style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 8px 16px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 14px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stSelectbox>div>div {
        border-radius: 8px;
    }
    .stSlider > div > div:first-child {
        color: #4CAF50;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 5px solid #4CAF50;
    }
    .metric-box h3 {
        color: #333;
        font-size: 1em;
        margin-bottom: 5px;
    }
    .metric-box p {
        font-size: 1.2em;
        font-weight: bold;
        color: #000;
    }
    .stAlert {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Inicialización de Session State ---
# Variables de estado de la sesión para mantener la información a través de las reruns de Streamlit
if 'idioma' not in st.session_state:
    st.session_state.idioma = 'es'
if 'riesgos' not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "ID", "Nombre del Riesgo", "Descripción", "Tipo de Impacto",
        "Probabilidad", "Exposición", "Impacto Numérico",
        "Efectividad del Control (%)", "Amenaza Deliberada",
        "Amenaza Inherente", "Amenaza Residual", "Amenaza Residual Ajustada",
        "Riesgo Residual", "Clasificación", "Color"
    ])
if 'current_edit_index' not in st.session_state:
    st.session_state.current_edit_index = -1 # -1 significa que no estamos editando

# Valores por defecto para reiniciar el formulario
if 'default_type_impact' not in st.session_state:
    st.session_state['default_type_impact'] = tabla_tipo_impacto['Tipo de Impacto'].iloc[0]
if 'default_probabilidad' not in st.session_state:
    st.session_state['default_probabilidad'] = factor_probabilidad['Clasificacion'].iloc[0]
if 'default_exposicion' not in st.session_state:
    st.session_state['default_exposicion'] = factor_exposicion['Clasificacion'].iloc[0]
if 'default_impacto_numerico' not in st.session_state:
    st.session_state['default_impacto_numerico'] = 50
if 'default_control_effectiveness' not in st.session_state:
    st.session_state['default_control_effectiveness'] = 50

# --- Función para obtener textos en el idioma actual ---
def get_text(key):
    """
    Obtiene el texto correspondiente a una clave en el idioma actual de la sesión.

    Args:
        key (str): La clave del texto a buscar en el diccionario 'textos'.

    Returns:
        str: El texto en el idioma configurado, o la clave si no se encuentra el texto.
    """
    return textos[st.session_state.idioma].get(key, key)

# --- Sidebar para selección de idioma y texto de impuestos ---
with st.sidebar:
    # Toggle de idioma
    if st.checkbox(get_text("sidebar_language_toggle"), value=(st.session_state.idioma == 'en')):
        st.session_state.idioma = 'en'
    else:
        st.session_state.idioma = 'es'

    st.markdown("---")
    st.header(get_text("tax_info_title"))
    st.info(get_text("tax_info_text"))

# --- Título de la Aplicación ---
st.title(get_text("app_title"))

# --- 1. Entrada de Datos del Riesgo ---
st.header(get_text("risk_input_form_title"))

# Formulario para agregar/editar riesgos
with st.form("risk_form", clear_on_submit=False):
    # Inicializar valores del formulario para edición
    if st.session_state.current_edit_index != -1:
        risk_to_edit = st.session_state.riesgos.loc[st.session_state.current_edit_index]
        nombre_riesgo_default = risk_to_edit["Nombre del Riesgo"]
        descripcion_default = risk_to_edit["Descripción"]
        tipo_impacto_default = risk_to_edit["Tipo de Impacto"]
        probabilidad_default = factor_probabilidad[factor_probabilidad['Factor'] == risk_to_edit["Probabilidad"]]['Clasificacion'].iloc[0]
        exposicion_default = factor_exposicion[factor_exposicion['Factor'] == risk_to_edit["Exposición"]]['Clasificacion'].iloc[0]
        impacto_numerico_default = risk_to_edit["Impacto Numérico"]
        efectividad_control_default = risk_to_edit["Efectividad del Control (%)"]
        amenaza_deliberada_default = bool(risk_to_edit["Amenaza Deliberada"])
    else:
        nombre_riesgo_default = st.session_state.get('risk_name_input', "")
        descripcion_default = st.session_state.get('risk_description_input', "")
        tipo_impacto_default = st.session_state.get('selected_type_impact', st.session_state['default_type_impact'])
        probabilidad_default = st.session_state.get('selected_probabilidad', st.session_state['default_probabilidad'])
        exposicion_default = st.session_state.get('selected_exposicion', st.session_state['default_exposicion'])
        impacto_numerico_default = st.session_state.get('impacto_numerico_slider', st.session_state['default_impacto_numerico'])
        efectividad_control_default = st.session_state.get('control_effectiveness_slider', st.session_state['default_control_effectiveness'])
        amenaza_deliberada_default = st.session_state.get('deliberate_threat_checkbox', False)

    col1, col2 = st.columns(2)
    with col1:
        nombre_riesgo = st.text_input(get_text("risk_name"), value=nombre_riesgo_default, key="risk_name_input")
        tipo_impacto = st.selectbox(
            get_text("risk_type_impact"),
            tabla_tipo_impacto['Tipo de Impacto'].tolist(),
            index=tabla_tipo_impacto['Tipo de Impacto'].tolist().index(tipo_impacto_default),
            key="selected_type_impact"
        )
        probabilidad = st.selectbox(
            get_text("risk_probability"),
            factor_probabilidad['Clasificacion'].tolist(),
            index=factor_probabilidad['Clasificacion'].tolist().index(probabilidad_default),
            key="selected_probabilidad"
        )
        exposicion = st.selectbox(
            get_text("risk_exposure"),
            factor_exposicion['Clasificacion'].tolist(),
            index=factor_exposicion['Clasificacion'].tolist().index(exposicion_default),
            key="selected_exposicion"
        )
    with col2:
        descripcion_riesgo = st.text_area(get_text("risk_description"), value=descripcion_default, height=100, key="risk_description_input")
        impacto_numerico = st.slider(get_text("risk_impact_numeric"), 0, 100, value=int(impacto_numerico_default), key="impacto_numerico_slider")
        efectividad_control = st.slider(get_text("risk_control_effectiveness"), 0, 100, value=int(efectividad_control_default), key="control_effectiveness_slider")
        amenaza_deliberada = st.checkbox(get_text("risk_deliberate_threat"), value=amenaza_deliberada_default, key="deliberate_threat_checkbox")

    submitted = st.form_submit_button(get_text("add_risk_button"))

    if submitted:
        if not nombre_riesgo:
            st.error(get_text("error_risk_name_empty"))
        else:
            # Obtener valores numéricos de probabilidad, exposición y ponderación de impacto
            probabilidad_val = factor_probabilidad[factor_probabilidad['Clasificacion'] == probabilidad]['Factor'].iloc[0]
            exposicion_val = factor_exposicion[factor_exposicion['Clasificacion'] == exposicion]['Factor'].iloc[0]
            ponderacion_impacto_val = tabla_tipo_impacto[tabla_tipo_impacto['Tipo de Impacto'] == tipo_impacto]['Ponderación'].iloc[0]
            amenaza_deliberada_factor = 1.0 if amenaza_deliberada else 0.0

            # Calcular criticidad
            amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual_val = calcular_criticidad(
                probabilidad_val, exposicion_val, amenaza_deliberada_factor, efectividad_control, impacto_numerico, ponderacion_impacto_val
            )

            # Clasificar el riesgo y obtener el color
            clasificacion, color = clasificar_criticidad(riesgo_residual_val, st.session_state.idioma)

            new_risk_data = {
                "ID": st.session_state.current_edit_index if st.session_state.current_edit_index != -1 else (len(st.session_state.riesgos) + 1),
                "Nombre del Riesgo": nombre_riesgo,
                "Descripción": descripcion_riesgo,
                "Tipo de Impacto": tipo_impacto,
                "Probabilidad": probabilidad_val, # Guardar el valor numérico
                "Exposición": exposicion_val,     # Guardar el valor numérico
                "Impacto Numérico": impacto_numerico,
                "Efectividad del Control (%)": efectividad_control,
                "Amenaza Deliberada": amenaza_deliberada_factor, # Guardar el factor numérico
                "Amenaza Inherente": amenaza_inherente,
                "Amenaza Residual": amenaza_residual,
                "Amenaza Residual Ajustada": amenaza_residual_ajustada,
                "Riesgo Residual": riesgo_residual_val,
                "Clasificación": clasificacion,
                "Color": color
            }

            if st.session_state.current_edit_index != -1:
                # Actualizar riesgo existente
                st.session_state.riesgos.loc[st.session_state.current_edit_index] = new_risk_data
                st.success(f"Riesgo '{nombre_riesgo}' actualizado exitosamente.")
            else:
                # Agregar nuevo riesgo
                st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([new_risk_data])], ignore_index=True)
                st.success(get_text("success_risk_added"))
            
            reset_form_fields() # Reiniciar el formulario después de agregar/editar

# --- 2. Resultados del Modelo Determinista ---
st.header(get_text("deterministic_results_title"))

if not st.session_state.riesgos.empty:
    latest_risk = st.session_state.riesgos.iloc[-1]
    col_d1, col_d2, col_d3, col_d4, col_d5 = st.columns(5)
    
    with col_d1:
        st.markdown(f"""
        <div class="metric-box">
            <h3>{get_text("inherent_threat")}</h3>
            <p>{latest_risk["Amenaza Inherente"]:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    with col_d2:
        st.markdown(f"""
        <div class="metric-box">
            <h3>{get_text("residual_threat")}</h3>
            <p>{latest_risk["Amenaza Residual"]:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    with col_d3:
        st.markdown(f"""
        <div class="metric-box">
            <h3>{get_text("adjusted_residual_threat")}</h3>
            <p>{latest_risk["Amenaza Residual Ajustada"]:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    with col_d4:
        st.markdown(f"""
        <div class="metric-box">
            <h3>{get_text("residual_risk")}</h3>
            <p style="color: {latest_risk['Color']};">{latest_risk["Riesgo Residual"]:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    with col_d5:
        st.markdown(f"""
        <div class="metric-box">
            <h3>{get_text("classification")}</h3>
            <p style="color: {latest_risk['Color']};">{latest_risk["Clasificación"]}</p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info(get_text("no_risks_yet"))

st.markdown("---")

# --- 3. Configuración de Simulación Monte Carlo ---
st.header(get_text("montecarlo_input_title"))

if not st.session_state.riesgos.empty:
    col_mc1, col_mc2 = st.columns(2)
    with col_mc1:
        valor_economico_activo = st.number_input(
            get_text("economic_value_asset"),
            min_value=0.0,
            value=100000.0,
            step=1000.0,
            format="%.2f"
        )
    with col_mc2:
        num_iteraciones = st.number_input(
            get_text("num_iterations"),
            min_value=1000,
            max_value=100000,
            value=10000,
            step=1000
        )

    if st.button(get_text("run_montecarlo_button")):
        if valor_economico_activo > 0 and not st.session_state.riesgos.empty:
            # Seleccionar el último riesgo agregado/editado para la simulación
            risk_for_simulation = st.session_state.riesgos.iloc[-1]
            
            probabilidad_sim_base = risk_for_simulation["Probabilidad"]
            exposicion_sim_base = risk_for_simulation["Exposición"]
            impacto_numerico_sim_base = risk_for_simulation["Impacto Numérico"]
            efectividad_control_sim_base_pct = risk_for_simulation["Efectividad del Control (%)"]
            amenaza_deliberada_sim_factor_base = risk_for_simulation["Amenaza Deliberada"]
            ponderacion_impacto_sim = tabla_tipo_impacto[tabla_tipo_impacto['Tipo de Impacto'] == risk_for_simulation["Tipo de Impacto"]]['Ponderación'].iloc[0]

            riesgo_residual_sim, perdidas_usd_sim, correlations = simular_montecarlo(
                probabilidad_sim_base, exposicion_sim_base, impacto_numerico_sim_base,
                efectividad_control_sim_base_pct, amenaza_deliberada_sim_factor_base,
                ponderacion_impacto_sim, valor_economico_activo, num_iteraciones
            )
            
            st.session_state['riesgo_residual_sim'] = riesgo_residual_sim
            st.session_state['perdidas_usd_sim'] = perdidas_usd_sim
            st.session_state['correlations'] = correlations
            
            if len(perdidas_usd_sim) > 0:
                st.session_state['expected_loss'] = np.mean(perdidas_usd_sim)
                st.session_state['median_loss'] = np.median(perdidas_usd_sim)
                st.session_state['p5_loss'] = np.percentile(perdidas_usd_sim, 5)
                st.session_state['p90_loss'] = np.percentile(perdidas_usd_sim, 90)
                st.session_state['max_loss'] = np.max(perdidas_usd_sim)
                
                # Calcular CVaR (Conditional Value at Risk) al 95%
                # CVaR 95% es la media de las peores 5% pérdidas.
                # Asegúrate de que haya suficientes datos para calcular el percentil 5.
                if len(perdidas_usd_sim) >= 20: # 5% de 10000 iteraciones es 500 datos
                    tail_losses = perdidas_usd_sim[perdidas_usd_sim >= np.percentile(perdidas_usd_sim, 95)]
                    st.session_state['cvar_95'] = np.mean(tail_losses)
                else:
                    st.session_state['cvar_95'] = 0.0 # No se puede calcular con pocos datos
            else:
                st.session_state['expected_loss'] = 0.0
                st.session_state['median_loss'] = 0.0
                st.session_state['p5_loss'] = 0.0
                st.session_state['p90_loss'] = 0.0
                st.session_state['max_loss'] = 0.0
                st.session_state['cvar_95'] = 0.0
            st.success("Simulación Monte Carlo completada.")
        else:
            st.warning("Por favor, asegúrate de haber agregado al menos un riesgo y que el valor económico del activo sea mayor que cero.")

else:
    st.info(get_text("no_risks_yet"))

st.markdown("---")

# --- 4. Resultados de la Simulación Monte Carlo ---
st.header(get_text("montecarlo_results_title"))

if 'perdidas_usd_sim' in st.session_state and len(st.session_state['perdidas_usd_sim']) > 0:
    col_mc_res1, col_mc_res2, col_mc_res3 = st.columns(3)
    col_mc_res4, col_mc_res5, col_mc_res6 = st.columns(3)

    with col_mc_res1:
        st.markdown(f"""
        <div class="metric-box">
            <h3>{get_text("expected_loss")}</h3>
            <p>${st.session_state['expected_loss']:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    with col_mc_res2:
        st.markdown(f"""
        <div class="metric-box">
            <h3>{get_text("median_loss")}</h3>
            <p>${st.session_state['median_loss']:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    with col_mc_res3:
        st.markdown(f"""
        <div class="metric-box">
            <h3>{get_text("p90_loss")}</h3>
            <p>${st.session_state['p90_loss']:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    with col_mc_res4:
        st.markdown(f"""
        <div class="metric-box">
            <h3>{get_text("max_loss")}</h3>
            <p>${st.session_state['max_loss']:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    with col_mc_res5:
        st.markdown(f"""
        <div class="metric-box">
            <h3>{get_text("cvar_95")}</h3>
            <p>${st.session_state['cvar_95']:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    with col_mc_res6:
        st.markdown(f"""
        <div class="metric-box">
            <h3>{get_text("p5_loss")}</h3>
            <p>${st.session_state['p5_loss']:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.subheader(get_text("sensitivity_analysis_title"))
    if 'correlations' in st.session_state and not st.session_state['correlations'].empty:
        sensitivity_fig = create_sensitivity_plot(st.session_state['correlations'], st.session_state.idioma)
        if sensitivity_fig:
            st.plotly_chart(sensitivity_fig, use_container_width=True)
        else:
            st.info("No hay datos suficientes para generar el gráfico de sensibilidad o todas las varianzas son cero.")
    else:
        st.info("No hay resultados de simulación Monte Carlo disponibles para el análisis de sensibilidad.")

else:
    st.info("Ejecuta la simulación Monte Carlo para ver los resultados.")

st.markdown("---")

# --- 5. Riesgos Evaluados Acumulados ---
st.header(get_text("added_risks_title"))

if not st.session_state.riesgos.empty:
    # Ordenar por Riesgo Residual de mayor a menor
    df_risks_display = st.session_state.riesgos.sort_values(by="Riesgo Residual", ascending=False).reset_index(drop=True)
    
    # Formatear el DataFrame para visualización con colores
    styled_df_risks = format_risk_dataframe(df_risks_display, st.session_state.idioma)
    st.dataframe(styled_df_risks, use_container_width=True)

    # Botón para descargar datos
    csv = st.session_state.riesgos.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=get_text("download_excel_button"),
        data=csv,
        file_name="riesgos_evaluados.csv",
        mime="text/csv",
    )

    # Funcionalidad de edición y eliminación
    st.subheader("Acciones sobre Riesgos")
    cols_actions = st.columns(df_risks_display.shape[0]) # Crear columnas dinámicamente

    for i, row in df_risks_display.iterrows():
        unique_key_edit = f"edit_button_{row['ID']}_{i}"
        unique_key_delete = f"delete_button_{row['ID']}_{i}"
        
        with cols_actions[i % len(cols_actions)]: # Distribuir botones en las columnas
            if st.button(get_text("edit_risk"), key=unique_key_edit):
                st.session_state.current_edit_index = st.session_state.riesgos[st.session_state.riesgos['ID'] == row['ID']].index[0]
                st.rerun() # Volver a ejecutar para cargar los datos en el formulario

            if st.button(get_text("delete_risk"), key=unique_key_delete):
                if st.session_state.get(f"confirm_delete_{row['ID']}", False):
                    # Si ya se confirmó, eliminar
                    st.session_state.riesgos = st.session_state.riesgos.drop(st.session_state.riesgos[st.session_state.riesgos['ID'] == row['ID']].index).reset_index(drop=True)
                    st.success(get_text("risk_deleted"))
                    st.session_state[f"confirm_delete_{row['ID']}"] = False # Resetear confirmación
                    st.rerun()
                else:
                    st.warning(get_text("confirm_delete"))
                    st.session_state[f"confirm_delete_{row['ID']}"] = True # Pedir confirmación
else:
    st.info(get_text("no_risks_yet"))

st.markdown("---")

# --- 6. Mapa de Calor de Riesgos ---
st.header(get_text("risk_heatmap_title"))
if not st.session_state.riesgos.empty:
    heatmap_fig = create_heatmap(st.session_state.riesgos, matriz_probabilidad, matriz_impacto, st.session_state.idioma)
    if heatmap_fig:
        st.plotly_chart(heatmap_fig, use_container_width=True)
else:
    st.info(get_text("no_risks_yet"))

st.markdown("---")

# --- 7. Gráfico de Pareto de Riesgos ---
st.header(get_text("risk_pareto_chart_title"))
if not st.session_state.riesgos.empty:
    pareto_fig = create_pareto_chart(st.session_state.riesgos, st.session_state.idioma)
    if pareto_fig:
        st.plotly_chart(pareto_fig, use_container_width=True)
else:
    st.info(get_text("no_risks_yet"))

st.markdown("---")

# --- 8. Distribución del Riesgo Residual Simulado (Índice) ---
st.header(get_text("risk_distribution_title"))
if 'riesgo_residual_sim' in st.session_state and len(st.session_state['riesgo_residual_sim']) > 0:
    hist_risk_fig = plot_montecarlo_histogram(
        st.session_state['riesgo_residual_sim'],
        get_text("risk_distribution_title"),
        get_text("residual_risk"),
        st.session_state.idioma
    )
    if hist_risk_fig:
        st.pyplot(hist_risk_fig)
else:
    st.info("Ejecuta la simulación Monte Carlo para ver la distribución del riesgo residual.")

st.markdown("---")

# --- 9. Distribución de Pérdidas Económicas Simuladas (USD) ---
st.header(get_text("economic_loss_distribution_title"))
if 'perdidas_usd_sim' in st.session_state and len(st.session_state['perdidas_usd_sim']) > 0:
    hist_loss_fig = plot_montecarlo_histogram(
        st.session_state['perdidas_usd_sim'],
        get_text("economic_loss_distribution_title"),
        get_text("economic_value_asset"),
        st.session_state.idioma
    )
    if hist_loss_fig:
        st.pyplot(hist_loss_fig)
else:
    st.info("Ejecuta la simulación Monte Carlo para ver la distribución de pérdidas económicas.")
