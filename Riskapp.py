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
# Variables de estado de la sesión para mantener la información a través de las reruns de Streamlit.
# Es crucial inicializar todas las claves aquí para evitar errores de acceso.
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

# --- Inicializaciones Cruciales para Campos del Formulario ---
# Estas claves se usan para almacenar el estado de los widgets del formulario
# y para que la función reset_form_fields() pueda limpiar los campos.
# Se inicializan aquí para asegurar su existencia desde la primera ejecución.
if 'risk_name_input' not in st.session_state:
    st.session_state['risk_name_input'] = ""
if 'risk_description_input' not in st.session_state:
    st.session_state['risk_description_input'] = ""

# Valores por defecto para selectbox y sliders (usados en la inicialización y el reseteo)
if 'default_type_impact' not in st.session_state:
    st.session_state['default_type_impact'] = tabla_tipo_impacto['Tipo de Impacto'].iloc[0]
if 'selected_type_impact' not in st.session_state: # Clave real del selectbox
    st.session_state['selected_type_impact'] = st.session_state['default_type_impact']

if 'default_probabilidad' not in st.session_state:
    st.session_state['default_probabilidad'] = factor_probabilidad['Clasificacion'].iloc[0]
if 'selected_probabilidad' not in st.session_state: # Clave real del selectbox
    st.session_state['selected_probabilidad'] = st.session_state['default_probabilidad']

if 'default_exposicion' not in st.session_state:
    st.session_state['default_exposicion'] = factor_exposicion['Clasificacion'].iloc[0]
if 'selected_exposicion' not in st.session_state: # Clave real del selectbox
    st.session_state['selected_exposicion'] = st.session_state['default_exposicion']

if 'default_impacto_numerico' not in st.session_state:
    st.session_state['default_impacto_numerico'] = 50
if 'impacto_numerico_slider' not in st.session_state: # Clave real del slider
    st.session_state['impacto_numerico_slider'] = st.session_state['default_impacto_numerico']

if 'default_control_effectiveness' not in st.session_state:
    st.session_state['default_control_effectiveness'] = 50
if 'control_effectiveness_slider' not in st.session_state: # Clave real del slider
    st.session_state['control_effectiveness_slider'] = st.session_state['default_control_effectiveness']

if 'deliberate_threat_checkbox' not in st.session_state:
    st.session_state['deliberate_threat_checkbox'] = False

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

# --- Función de Callback para el envío del formulario ---
def handle_form_submit():
    """
    Maneja la lógica de envío del formulario de riesgo.
    Esta función se llama cuando se presiona el botón de envío del formulario.
    """
    nombre_riesgo = st.session_state['risk_name_input'] # Acceder a los valores a través de session_state
    descripcion_riesgo = st.session_state['risk_description_input']
    tipo_impacto = st.session_state['selected_type_impact']
    probabilidad_str = st.session_state['selected_probabilidad']
    exposicion_str = st.session_state['selected_exposicion']
    impacto_numerico = st.session_state['impacto_numerico_slider']
    efectividad_control = st.session_state['control_effectiveness_slider']
    amenaza_deliberada = st.session_state['deliberate_threat_checkbox']

    if not nombre_riesgo:
        st.error(get_text("error_risk_name_empty"))
    else:
        # Obtener valores numéricos de probabilidad, exposición y ponderación de impacto
        probabilidad_val = factor_probabilidad[factor_probabilidad['Clasificacion'] == probabilidad_str]['Factor'].iloc[0]
        exposicion_val = factor_exposicion[factor_exposicion['Clasificacion'] == exposicion_str]['Factor'].iloc[0]
        ponderacion_impacto_val = tabla_tipo_impacto[tabla_tipo_impacto['Tipo de Impacto'] == tipo_impacto]['Ponderación'].iloc[0]
        amenaza_deliberada_factor = 1.0 if amenaza_deliberada else 0.0

        # Calcular criticidad
        amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual_val = calcular_criticidad(
            probabilidad_val, exposicion_val, amenaza_deliberada_factor, efectividad_control, impacto_numerico, ponderacion_impacto_val
        )

        # Clasificar el riesgo y obtener el color
        clasificacion, color = clasificar_criticidad(riesgo_residual_val, st.session_state.idioma)

        new_risk_data = {
            "ID": st.session_state.current_edit_index if st.session_state.current_edit_index != -1 else (st.session_state.riesgos['ID'].max() + 1 if not st.session_state.riesgos.empty else 1),
            "Nombre del Riesgo": nombre_riesgo,
            "Descripción": descripcion_riesgo,
            "Tipo de Impacto": tipo_impacto,
            "Probabilidad": probabilidad_val,
            "Exposición": exposicion_val,
            "Impacto Numérico": impacto_numerico,
            "Efectividad del Control (%)": efectividad_control,
            "Amenaza Deliberada": amenaza_deliberada_factor,
            "Amenaza Inherente": amenaza_inherente,
            "Amenaza Residual": amenaza_residual,
            "Amenaza Residual Ajustada": amenaza_residual_ajustada,
            "Riesgo Residual": riesgo_residual_val,
            "Clasificación": clasificacion,
            "Color": color
        }

        if st.session_state.current_edit_index != -1:
            st.session_state.riesgos.loc[st.session_state.current_edit_index] = new_risk_data
            st.success(f"Riesgo '{nombre_riesgo}' actualizado exitosamente.")
        else:
            st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([new_risk_data])], ignore_index=True)
            st.success(get_text("success_risk_added"))

        # Después de agregar/editar, reiniciar el índice de edición y los campos del formulario.
        st.session_state.current_edit_index = -1
        reset_form_fields() # Llama a la función de utils.py para resetear los campos
        # st.rerun() # Ya no es necesario un st.rerun() explícito aquí, el callback lo maneja

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
    # Lógica para determinar los valores iniciales de los campos del formulario
    if st.session_state.current_edit_index != -1:
        risk_to_edit = st.session_state.riesgos.loc[st.session_state.current_edit_index]
        nombre_riesgo_default = risk_to_edit["Nombre del Riesgo"]
        descripcion_default = risk_to_edit["Descripción"]
        tipo_impacto_default = risk_to_edit["Tipo de Impacto"]
        probabilidad_default = factor_probabilidad[factor_probabilidad['Factor'] == risk_to_edit["Probabilidad"]]['Clasificacion'].iloc[0] if not factor_probabilidad[factor_probabilidad['Factor'] == risk_to_edit["Probabilidad"]].empty else st.session_state['default_probabilidad']
        exposicion_default = factor_exposicion[factor_exposicion['Factor'] == risk_to_edit["Exposición"]]['Clasificacion'].iloc[0] if not factor_exposicion[factor_exposicion['Factor'] == risk_to_edit["Exposición"]].empty else st.session_state['default_exposicion']
        impacto_numerico_default = risk_to_edit["Impacto Numérico"]
        efectividad_control_default = risk_to_edit["Efectividad del Control (%)"]
        amenaza_deliberada_default = bool(risk_to_edit["Amenaza Deliberada"])
    else:
        # Modo Nuevo Riesgo: Usar los valores de session_state
        nombre_riesgo_default = st.session_state['risk_name_input'] # Acceder directamente
        descripcion_default = st.session_state['risk_description_input'] # Acceder directamente
        tipo_impacto_default = st.session_state['selected_type_impact'] # Acceder directamente
        probabilidad_default = st.session_state['selected_probabilidad'] # Acceder directamente
        exposicion_default = st.session_state['selected_exposicion'] # Acceder directamente
        impacto_numerico_default = st.session_state['impacto_numerico_slider'] # Acceder directamente
        efectividad_control_default = st.session_state['control_effectiveness_slider'] # Acceder directamente
        amenaza_deliberada_default = st.session_state['deliberate_threat_checkbox'] # Acceder directamente

    # Definición de los campos del formulario utilizando las claves de session_state
    col1, col2 = st.columns(2)
    with col1:
        st.text_input(get_text("risk_name"), value=nombre_riesgo_default, key="risk_name_input")
        st.selectbox(
            get_text("risk_type_impact"),
            tabla_tipo_impacto['Tipo de Impacto'].tolist(),
            index=tabla_tipo_impacto['Tipo de Impacto'].tolist().index(tipo_impacto_default),
            key="selected_type_impact"
        )
        st.selectbox(
            get_text("risk_probability"),
            factor_probabilidad['Clasificacion'].tolist(),
            index=factor_probabilidad['Clasificacion'].tolist().index(probabilidad_default),
            key="selected_probabilidad"
        )
        st.selectbox(
            get_text("risk_exposure"),
            factor_exposicion['Clasificacion'].tolist(),
            index=factor_exposicion['Clasificacion'].tolist().index(exposicion_default),
            key="selected_exposicion"
        )
    with col2:
        st.text_area(get_text("risk_description"), value=descripcion_default, height=100, key="risk_description_input")
        st.slider(get_text("risk_impact_numeric"), 0, 100, value=int(impacto_numerico_default), key="impacto_numerico_slider")
        st.slider(get_text("risk_control_effectiveness"), 0, 100, value=int(efectividad_control_default), key="control_effectiveness_slider")
        st.checkbox(get_text("risk_deliberate_threat"), value=amenaza_deliberada_default, key="deliberate_threat_checkbox")

    # Botón de envío del formulario, ahora con un callback
    st.form_submit_button(get_text("add_risk_button"), on_click=handle_form_submit)

# ... (El resto de tu código de visualización de riesgos, cuadrante, Pareto, Monte Carlo, etc. se mantiene igual) ...

# --- 2. Visualización de Riesgos ---
st.markdown("---")
st.header(get_text("risk_list_title"))

if st.session_state.riesgos.empty:
    st.info(get_text("no_risks_added_yet"))
else:
    st.dataframe(format_risk_dataframe(st.session_state.riesgos, st.session_state.idioma), use_container_width=True)

    col_edit, col_delete = st.columns(2)
    with col_edit:
        risk_to_select_edit = st.selectbox(get_text("select_risk_to_edit"), [""] + st.session_state.riesgos["Nombre del Riesgo"].tolist(), key="select_edit_risk")
        if st.button(get_text("edit_selected_risk_button")):
            if risk_to_select_edit:
                st.session_state.current_edit_index = st.session_state.riesgos[st.session_state.riesgos["Nombre del Riesgo"] == risk_to_select_edit].index[0]
                st.info(f"{get_text('editing_risk')} '{risk_to_select_edit}'. {get_text('edit_in_form')}.")
                st.rerun()
            else:
                st.warning(get_text("please_select_risk_to_edit"))

    with col_delete:
        risk_to_select_delete = st.selectbox(get_text("select_risk_to_delete"), [""] + st.session_state.riesgos["Nombre del Riesgo"].tolist(), key="select_delete_risk")
        if st.button(get_text("delete_selected_risk_button")):
            if risk_to_select_delete:
                st.session_state.riesgos = st.session_state.riesgos[st.session_state.riesgos["Nombre del Riesgo"] != risk_to_select_delete].reset_index(drop=True)
                st.success(f"Riesgo '{risk_to_select_delete}' {get_text('successfully_deleted')}.")
                if st.session_state.current_edit_index != -1 and not st.session_state.riesgos.empty:
                    if st.session_state.current_edit_index >= len(st.session_state.riesgos):
                        st.session_state.current_edit_index = -1
                elif st.session_state.riesgos.empty:
                    st.session_state.current_edit_index = -1
                reset_form_fields()
                st.rerun()
            else:
                st.warning(get_text("please_select_risk_to_delete"))

# --- 3. Cuadrante de Riesgos (Heatmap) ---
st.markdown("---")
st.header(get_text("risk_quadrant_title"))

if st.session_state.riesgos.empty:
    st.info(get_text("add_risks_for_heatmap"))
else:
    heatmap_fig = create_heatmap(st.session_state.riesgos, matriz_probabilidad, matriz_impacto, st.session_state.idioma)
    if heatmap_fig:
        st.plotly_chart(heatmap_fig, use_container_width=True)
    else:
        st.warning(get_text("heatmap_error"))

# --- 4. Análisis de Pareto ---
st.markdown("---")
st.header(get_text("pareto_analysis_title"))

if st.session_state.riesgos.empty:
    st.info(get_text("add_risks_for_pareto"))
else:
    pareto_fig = create_pareto_chart(st.session_state.riesgos, st.session_state.idioma)
    if pareto_fig:
        st.plotly_chart(pareto_fig, use_container_width=True)
    else:
        st.warning(get_text("pareto_error"))

# --- 5. Simulación de Monte Carlo ---
st.markdown("---")
st.header(get_text("monte_carlo_simulation_title"))
st.info(get_text("monte_carlo_info"))

if st.session_state.riesgos.empty:
    st.info(get_text("add_risks_for_montecarlo"))
else:
    selected_risk_mc_name = st.selectbox(
        get_text("select_risk_for_mc"),
        [""] + st.session_state.riesgos["Nombre del Riesgo"].tolist(),
        key="monte_carlo_risk_selector"
    )

    if selected_risk_mc_name:
        risk_mc = st.session_state.riesgos[st.session_state.riesgos["Nombre del Riesgo"] == selected_risk_mc_name].iloc[0]

        st.subheader(f"{get_text('simulation_for_risk')}: {risk_mc['Nombre del Riesgo']}")

        col_mc1, col_mc2 = st.columns(2)
        with col_mc1:
            st.metric(get_text("mc_risk_name"), risk_mc['Nombre del Riesgo'])
            st.metric(get_text("mc_type_impact"), risk_mc['Tipo de Impacto'])
            st.metric(get_text("mc_probability"), f"{risk_mc['Probabilidad']:.2f} ({get_text('factor')})")
            st.metric(get_text("mc_exposure"), f"{risk_mc['Exposición']:.2f} ({get_text('factor')})")
        with col_mc2:
            st.metric(get_text("mc_impact_numeric"), f"{risk_mc['Impacto Numérico']}%")
            st.metric(get_text("mc_control_effectiveness"), f"{risk_mc['Efectividad del Control (%)']}%")
            st.metric(get_text("mc_deliberate_threat"), "Sí" if risk_mc['Amenaza Deliberada'] else "No")
            st.metric(get_text("mc_current_residual_risk"), f"{risk_mc['Riesgo Residual']:.2f} ({risk_mc['Clasificación']})")

        valor_economico = st.number_input(
            get_text("economic_value_asset"),
            min_value=0.0,
            value=100000.0,
            step=10000.0,
            format="%.2f",
            key="mc_economic_value"
        )
        num_iteraciones = st.slider(get_text("num_montecarlo_iterations"), 1000, 100000, value=10000, step=1000, key="mc_iterations")

        if st.button(get_text("run_montecarlo_button"), key="run_mc_button"):
            if valor_economico <= 0:
                st.warning(get_text("economic_value_positive"))
            else:
                with st.spinner(get_text("running_simulation")):
                    riesgos_simulados, perdidas_simuladas, correlaciones = simular_montecarlo(
                        probabilidad_base=risk_mc['Probabilidad'],
                        exposicion_base=risk_mc['Exposición'],
                        impacto_numerico_base=risk_mc['Impacto Numérico'],
                        efectividad_base_pct=risk_mc['Efectividad del Control (%)'],
                        amenaza_deliberada_factor_base=risk_mc['Amenaza Deliberada'],
                        ponderacion_impacto=tabla_tipo_impacto[tabla_tipo_impacto['Tipo de Impacto'] == risk_mc['Tipo de Impacto']]['Ponderación'].iloc[0],
                        valor_economico=valor_economico,
                        iteraciones=num_iteraciones
                    )

                if riesgos_simulados is not None and len(riesgos_simulados) > 0:
                    st.success(get_text("simulation_complete"))

                    col_results1, col_results2 = st.columns(2)
                    with col_results1:
                        st.subheader(get_text("simulated_risk_distribution"))
                        fig_riesgo = plot_montecarlo_histogram(
                            riesgos_simulados,
                            get_text("histogram_risk_title"),
                            get_text("risk_value_label"),
                            st.session_state.idioma
                        )
                        st.pyplot(fig_riesgo)
                        plt.close(fig_riesgo)

                    with col_results2:
                        st.subheader(get_text("simulated_economic_losses"))
                        fig_perdida = plot_montecarlo_histogram(
                            perdidas_simuladas,
                            get_text("histogram_losses_title"),
                            get_text("losses_value_label"),
                            st.session_state.idioma
                        )
                        st.pyplot(fig_perdida)
                        plt.close(fig_perdida)

                    st.markdown("---")
                    st.subheader(get_text("sensitivity_analysis_title"))
                    st.info(get_text("sensitivity_analysis_info"))
                    if correlaciones is not None and not correlaciones.empty:
                        sensitivity_fig = create_sensitivity_plot(correlaciones, st.session_state.idioma)
                        st.plotly_chart(sensitivity_fig, use_container_width=True)
                    else:
                        st.warning(get_text("no_sensitivity_data"))
                else:
                    st.warning(get_text("no_simulation_data"))
    else:
        st.info(get_text("select_risk_to_start_mc"))

# --- 6. Matriz de Impacto y Probabilidad (Solo para referencia) ---
st.markdown("---")
st.header(get_text("impact_probability_matrix_title"))
st.subheader(get_text("probability_factors"))
st.dataframe(factor_probabilidad.style.format({"Factor": "{:.2f}"}), use_container_width=True)
st.subheader(get_text("exposure_factors"))
st.dataframe(factor_exposicion.style.format({"Factor": "{:.2f}"}), use_container_width=True)
st.subheader(get_text("impact_types"))
st.dataframe(tabla_tipo_impacto.style.format({"Ponderación": "{:.2f}"}), use_container_width=True)
st.subheader(get_text("control_effectiveness_levels"))
st.dataframe(efectividad_controles, use_container_width=True)
st.subheader(get_text("criticality_limits"))
df_criticidad_display = pd.DataFrame(criticidad_límites, columns=['Min', 'Max', 'Clasificación (ES)', 'Color', 'Clasificación (EN)'])
st.dataframe(df_criticidad_display[['Min', 'Max', 'Clasificación (ES)', 'Clasificación (EN)']], use_container_width=True)
