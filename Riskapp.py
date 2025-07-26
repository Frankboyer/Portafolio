# Riskapp.py
"""
Aplicación principal de Streamlit para la Calculadora de Riesgos Integral.
Integra gestión de perfiles, entrada de riesgos con múltiples impactos dinámicos,
cálculo determinista, simulaciones Monte Carlo, visualizaciones y dashboard global.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
import json
import os

# --- Importaciones de Módulos ---
# Asegúrate de que las rutas de importación sean correctas según tu estructura de archivos
from modules.data_config import (tabla_tipo_impacto_global, matriz_probabilidad, matriz_impacto,
                                  factor_exposicion, factor_probabilidad, efectividad_controles,
                                  criticidad_límites, textos, PERFILES_BASE, HIERARCHY_TRANSLATIONS)
from modules.calculations import clasificar_criticidad, calcular_criticidad, simular_montecarlo, calcular_max_theoretical_risk
from modules.plotting import create_heatmap, create_pareto_chart, plot_montecarlo_histogram, create_sensitivity_plot
from modules.utils import reset_form_fields, format_risk_dataframe, get_text, render_impact_sliders # Utilidades
from modules.profile_manager import load_profiles, save_profiles, get_profile_data, delete_profile, update_profile, add_profile # Gestor de perfiles

# --- Configuración de la página ---
st.set_page_config(layout="wide", page_title="Calculadora de Riesgos Integral", icon="🛡️")

# --- CSS Personalizado ---
st.markdown("""
    <style>
    .stButton>button { background-color: #4CAF50; color: white; padding: 8px 16px; text-align: center; text-decoration: none; display: inline-block; font-size: 14px; margin: 4px 2px; cursor: pointer; border-radius: 8px; border: none; }
    .stButton>button:hover { background-color: #45a049; }
    .stSelectbox>div>div { border-radius: 8px; }
    .stSlider > div > div:first-child { color: #4CAF50; }
    .metric-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #4CAF50; }
    .metric-box h3 { color: #333; font-size: 1em; margin-bottom: 5px; }
    .metric-box p { font-size: 1.2em; font-weight: bold; color: #000; }
    .stAlert { border-radius: 8px; }
    .stTextInput>div>div, .stTextArea>div>div, .stNumberInput>div>div { border-radius: 8px; }
    .stDataFrame { border-radius: 10px; }
    .sidebar .sidebar-content { padding-top: 0; }
    .sidebar .stForm > div { padding-bottom: 5px; }
    .sidebar .stButton>button { font-size: 12px; padding: 5px 10px; }
    .sidebar .stTextInput>div>div, .sidebar .stNumberInput>div>div { font-size: 13px; }
    .sidebar .stSelectbox>div>div { font-size: 13px; }
    </style>
""", unsafe_allow_html=True)

# --- Inicialización de Session State ---
if 'idioma' not in st.session_state: st.session_state.idioma = 'es'
if 'riesgos' not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "ID", "Nombre del Riesgo", "Descripción", "Tipo de Impacto",
        "Probabilidad", "Exposición", "Impacto Numérico General",
        "Efectividad del Control (%)", "Amenaza Deliberada",
        "Min Loss USD", "Max Loss USD",
        "Perfil", "Categoria", "Subcategoria",
        "Impactos Detallados",
        "Amenaza Inherente", "Amenaza Residual", "Amenaza Residual Ajustada",
        "Riesgo Residual", "Clasificación", "Color"
    ])
if 'current_edit_index' not in st.session_state: st.session_state.current_edit_index = -1

# Valores por defecto
if 'default_type_impact' not in st.session_state: st.session_state['default_type_impact'] = tabla_tipo_impacto_global['Tipo de Impacto'].iloc[0]
if 'default_probabilidad' not in st.session_state: st.session_state['default_probabilidad'] = factor_probabilidad['Clasificacion'].iloc[0]
if 'default_exposicion' not in st.session_state: st.session_state['default_exposicion'] = factor_exposicion['Clasificacion'].iloc[0]
if 'default_impacto_numerico' not in st.session_state: st.session_state['default_impacto_numerico'] = 50
if 'default_control_effectiveness' not in st.session_state: st.session_state['default_control_effectiveness'] = 50
if 'default_min_loss' not in st.session_state: st.session_state['default_min_loss'] = 0.0
if 'default_max_loss' not in st.session_state: st.session_state['default_max_loss'] = 0.0

# Gestión de Perfiles Personalizados
if 'perfiles_usuario' not in st.session_state: st.session_state.perfiles_usuario = load_profiles()
if 'perfil_seleccionado_user' not in st.session_state: st.session_state.perfil_seleccionado_user = list(st.session_state.perfiles_usuario.keys())[0] if st.session_state.perfiles_usuario else ""
if 'current_editing_profile' not in st.session_state: st.session_state.current_editing_profile = None
if 'profile_categories_data' not in st.session_state: st.session_state.profile_categories_data = {}

# --- Sidebar ---
with st.sidebar:
    if st.checkbox(get_text("sidebar_language_toggle", context="app"), value=(st.session_state.idioma == 'en')):
        st.session_state.idioma = 'en'
    else: st.session_state.idioma = 'es'
    st.markdown("---")
    
    # --- Sección de Gestión de Perfiles Personalizados ---
    st.header(get_text("custom_profile_creation", context="app"))
    perfiles_existentes = list(st.session_state.perfiles_usuario.keys())
    perfil_a_gestionar = st.selectbox(get_text("Selecciona un perfil para gestionar"), perfiles_existentes, key="perfil_a_gestionar_sb")

    if st.button(get_text("edit_profile_button", context="app")):
        st.session_state.current_editing_profile = perfil_a_gestionar
        st.session_state.profile_name_input = perfil_a_gestionar
        profile_data_to_edit = get_profile_data(perfil_a_gestionar)
        if profile_data_to_edit:
            st.session_state.profile_categories_data = {cat: {'weight': weight, 'subcategories': subs}
                                                        for cat, weight in profile_data_to_edit.get('categorias', {}).items()
                                                        for subs in [profile_data_to_edit.get('subcategorias', {}).get(cat, [])]}
            st.session_state.new_category_name_input = ""
            st.session_state.new_category_weight_input = 0
            st.session_state.new_subcategories_input = ""
        st.rerun()

    if st.button(get_text("delete_profile_button", context="app")):
        if perfil_a_gestionar not in PERFILES_BASE:
            if delete_profile(perfil_a_gestionar):
                st.success(get_text("profile_deleted", context="app"))
                if st.session_state.perfil_seleccionado_user == perfil_a_gestionar:
                    st.session_state.perfil_seleccionado_user = list(st.session_state.perfiles_usuario.keys())[0] if st.session_state.perfiles_usuario else ""
                if st.session_state.perfil_a_gestionar_sb == perfil_a_gestionar:
                    st.session_state.current_editing_profile = None
                    st.session_state.profile_name_input = ""
                    st.session_state.profile_categories_data = {}
                st.rerun()
            else: st.warning("No se pudieron eliminar los perfiles base.")
        else: st.warning("No se pueden eliminar los perfiles base.")

    st.markdown("---")
    # Formulario para crear/modificar perfiles
    with st.form("profile_form", clear_on_submit=False):
        profile_name_input = st.text_input(get_text("profile_name_input", context="app"), key="profile_name_input")
        
        categories_to_display = list(st.session_state.profile_categories_data.keys())
        total_weight_current = sum(data['weight'] for data in st.session_state.profile_categories_data.values())

        if categories_to_display:
            st.write(f"Ponderación actual total: {total_weight_current}%")
            for cat_name in categories_to_display:
                col_cat_name, col_weight, col_subs, col_del_cat = st.columns([2, 1, 2, 0.5])
                with col_cat_name: st.text(cat_name)
                with col_weight:
                    new_weight = st.number_input(f"W_{cat_name}", value=st.session_state.profile_categories_data[cat_name]['weight'], min_value=0, max_value=100, step=1, label_visibility="collapsed")
                    st.session_state.profile_categories_data[cat_name]['weight'] = new_weight
                with col_subs:
                    current_subs = st.session_state.profile_categories_data[cat_name]['subcategories']
                    st.text(", ".join(current_subs) if current_subs else "(No subcats)")
                with col_del_cat:
                    if st.button("❌", key=f"del_cat_{cat_name}", help="Eliminar Categoría"):
                        del st.session_state.profile_categories_data[cat_name]
                        st.rerun()

        st.subheader(get_text("Agregar Nueva Categoría", context="app"))
        new_category_name = st.text_input(get_text("category_name_input", context="app"), key="new_category_name_input")
        new_category_weight = st.number_input(get_text("category_weight_input", context="app"), min_value=0, max_value=100, step=1, key="new_category_weight_input")
        new_subcategories_str = st.text_input(get_text("subcategory_name_input", context="app") + " (separadas por comas)", key="new_subcategories_input")
        
        if st.form_submit_button(get_text("add_category_button", context="app")):
            if new_category_name:
                if new_category_name not in st.session_state.profile_categories_data:
                    subs_list = [sub.strip() for sub in new_subcategories_str.split(',') if sub.strip()]
                    st.session_state.profile_categories_data[new_category_name] = {'weight': new_category_weight, 'subcategories': subs_list}
                    st.session_state.new_category_name_input = ""
                    st.session_state.new_category_weight_input = 0
                    st.session_state.new_subcategories_input = ""
                    st.rerun()
                else: st.warning("La categoría ya existe.")
            else: st.warning("El nombre de la categoría no puede estar vacío.")

        if st.form_submit_button(get_text("save_profile_button", context="app")):
            if not profile_name_input: st.error(get_text("profile_name_empty", context="app"))
            else:
                total_weight_current = sum(data['weight'] for data in st.session_state.profile_categories_data.values())
                if total_weight_current > 100:
                    st.error(get_text("category_weight_invalid", context="app"))
                else:
                    final_subcategories = {}
                    for cat_name, data in st.session_state.profile_categories_data.items():
                        final_subcategories[cat_name] = data['subcategories']
                    
                    updated_profile_data = {
                        "categorias": {cat: data['weight'] for cat, data in st.session_state.profile_categories_data.items()},
                        "subcategorias": final_subcategories
                    }

                    old_profile_name = st.session_state.current_editing_profile
                    if old_profile_name and old_profile_name != profile_name_input:
                        if old_profile_name in st.session_state.perfiles_usuario and old_profile_name not in PERFILES_BASE:
                            del st.session_state.perfiles_usuario[old_profile_name]
                    
                    if profile_name_input in st.session_state.perfiles_usuario and old_profile_name != profile_name_input:
                        st.error(get_text("profile_name_exists", context="app"))
                    else:
                        st.session_state.perfiles_usuario[profile_name_input] = updated_profile_data
                        save_profiles(st.session_state.perfiles_usuario)
                        st.success(get_text("profile_saved", context="app"))
                        
                        st.session_state.current_editing_profile = None
                        st.session_state.profile_name_input = ""
                        st.session_state.profile_categories_data = {}
                        st.session_state.new_category_name_input = ""
                        st.session_state.new_category_weight_input = 0
                        st.session_state.new_subcategories_input = ""
                        st.session_state.perfil_seleccionado_user = profile_name_input
                        st.rerun()

    st.markdown("---")
    st.caption("Modo Edición de Perfil: " + (st.session_state.current_editing_profile if st.session_state.current_editing_profile else "Ninguno"))

# --- Título de la Aplicación ---
st.title(get_text("app_title", context="app"))
st.markdown("---")

# --- Layout Principal ---
col_form, col_graf = st.columns([1, 1.5])

with col_form:
    st.header(get_text("risk_input_form_title", context="app"))

    # Selección del perfil para la entrada de riesgos
    available_profiles = list(st.session_state.perfiles_usuario.keys())
    initial_profile_index = 0
    if st.session_state.perfil_seleccionado_user in available_profiles:
        initial_profile_index = available_profiles.index(st.session_state.perfil_seleccionado_user)
    elif available_profiles:
        initial_profile_index = 0
        st.session_state.perfil_seleccionado_user = available_profiles[0]
    
    selected_profile_for_input = st.selectbox(
        get_text("Selecciona el perfil para este riesgo"),
        available_profiles,
        index=initial_profile_index,
        key="risk_profile_selector"
    )
    if selected_profile_for_input != st.session_state.perfil_seleccionado_user:
        st.session_state.perfil_seleccionado_user = selected_profile_for_input
        st.session_state.risk_category_selector = "" # Resetear selectores de categoría/subcategoría
        st.session_state.risk_subcategory_selector = ""
    
    current_profile_data = st.session_state.perfiles_usuario.get(selected_profile_for_input)
    
    if current_profile_data:
        categories_for_input = list(current_profile_data["categorias"].keys())
        if st.session_state.risk_category_selector not in categories_for_input and categories_for_input:
            st.session_state.risk_category_selector = categories_for_input[0]
        elif not categories_for_input:
            st.session_state.risk_category_selector = ""

        selected_category_for_input = st.selectbox(get_text("Categoría"), categories_for_input, key="risk_category_selector")
        
        subcategories_for_input = current_profile_data.get("subcategorias", {}).get(selected_category_for_input, [])
        if not subcategories_for_input: subcategories_for_input = ["(Sin subcategorías)"]
        if st.session_state.risk_subcategory_selector not in subcategories_for_input and subcategories_for_input:
             st.session_state.risk_subcategory_selector = subcategories_for_input[0]
        elif not subcategories_for_input:
            st.session_state.risk_subcategory_selector = ""
        selected_subcategory_for_input = st.selectbox(get_text("Subcategoría"), subcategories_for_input, key="risk_subcategory_selector")
        
        # Ponderación de la categoría del perfil (para referencia)
        category_weight_from_profile = current_profile_data["categorias"].get(selected_category_for_input, {}).get('weight', 0)

        with st.form("risk_form", clear_on_submit=False):
            risk_name = st.text_input(get_text("risk_name", context="app"), key="risk_name_input", value=st.session_state.get('risk_name_input', ''))
            risk_description = st.text_area(get_text("risk_description", context="app"), key="risk_description_input", value=st.session_state.get('risk_description_input', ''))

            selected_type_impact = st.selectbox(get_text("risk_type_impact", context="app"), tabla_tipo_impacto_global['Tipo de Impacto'], format_func=lambda x: f"{x} (Ponderación Global: {tabla_tipo_impacto_global[tabla_tipo_impacto_global['Tipo de Impacto'] == x]['Ponderación'].iloc[0]})", key="selected_type_impact")
            
            selected_probabilidad_clasificacion = st.selectbox(
                get_text("risk_probability", context="app"),
                factor_probabilidad['Clasificacion'],
                format_func=lambda x: f"{x} ({factor_probabilidad[factor_probabilidad['Clasificacion'] == x]['Definicion'].iloc[0]})",
                key="selected_probabilidad"
            )
            selected_exposicion_clasificacion = st.selectbox(
                get_text("risk_exposure", context="app"),
                factor_exposicion['Clasificacion'],
                format_func=lambda x: f"{x} ({factor_exposicion[factor_exposicion['Clasificacion'] == x]['Definicion'].iloc[0]})",
                key="selected_exposicion"
            )

            impacto_numerico_slider = st.slider(get_text("risk_impact_numeric", context="app"), min_value=0, max_value=100, value=st.session_state.get('impacto_numerico_slider', 50), step=1, help="Severidad general del impacto.", key="impacto_numerico_slider")
            
            # --- Múltiples Severidades de Impacto Dinámicas ---
            impact_inputs_data = {}
            if current_profile_data and selected_category_for_input:
                impacts_config_for_cat = current_profile_data.get("categorias", {}).get(selected_category_for_input, {}).get("impacts", {})
                
                if impacts_config_for_cat:
                    # Renderiza los sliders dinámicos y obtiene sus valores
                    impact_inputs_data = render_impact_sliders(current_profile_data, selected_category_for_input, st.session_state.get('risk_impact_severities', {}), st.session_state.idioma)
                else:
                    st.info(f"No hay tipos de impacto definidos para la categoría '{selected_category_for_input}'. Se usará el slider general.")
            else: # Si no hay perfil o categoría seleccionada
                 impact_inputs_data = {"General": st.session_state.get('impacto_numerico_slider', 50)} # Usar el general como fallback

            control_effectiveness_slider = st.slider(get_text("risk_control_effectiveness", context="app"), min_value=0, max_value=100, value=st.session_state.get('control_effectiveness_slider', 50), step=1, help="Porcentaje de efectividad de los controles existentes para mitigar el riesgo.", key="control_effectiveness_slider")
            deliberate_threat_checkbox = st.checkbox(get_text("risk_deliberate_threat", context="app"), value=st.session_state.get('deliberate_threat_checkbox', False), key="deliberate_threat_checkbox")

            min_loss_input = st.number_input(get_text("min_loss_input_label", context="app"), min_value=0.0, value=st.session_state.get('min_loss_input', 0.0), step=100.0, key="min_loss_input")
            max_loss_input = st.number_input(get_text("max_loss_input_label", context="app"), min_value=0.0, value=st.session_state.get('max_loss_input', 0.0), step=100.0, key="max_loss_input")
            valid_loss_range = (min_loss_input <= max_loss_input)

            submitted = st.form_submit_button(get_text("add_risk_button", context="app"))

            if submitted:
                if not risk_name: st.error(get_text("error_risk_name_empty", context="app"))
                elif not valid_loss_range: st.error("Por favor, verifica el rango de pérdidas (Min Loss USD <= Max Loss USD).")
                else:
                    probabilidad_factor = matriz_probabilidad_vals.get(selected_probabilidad_clasificacion, 0.5)
                    exposicion_factor = factor_exposicion_vals.get(selected_exposicion_clasificacion, 0.6)

                    amenaza_deliberada_factor_val = 1 if deliberate_threat_checkbox else 0
                    
                    # Preparar el diccionario de severidades de impacto para el cálculo
                    severidades_impacto_para_calculo = st.session_state.get('risk_impact_severities', {})
                    if not severidades_impacto_para_calculo: # Si está vacío, usar el slider general
                        severidades_impacto_para_calculo = {"General": impacto_numerico_slider}

                    # Calcular el Riesgo Residual Determinista
                    amenaza_inherente_det, amenaza_residual_det, amenaza_residual_ajustada_det, riesgo_residual_det = \
                        calcular_criticidad(
                            selected_probabilidad_clasificacion,
                            selected_exposicion_clasificacion,
                            amenaza_deliberada_factor_val,
                            control_effectiveness_slider,
                            severidades_impacto_para_calculo # Pasar el diccionario de severidades
                        )
                    
                    clasificacion_det, color_det = clasificar_criticidad(riesgo_residual_det, st.session_state.idioma)

                    # Lógica de Guardar/Actualizar Riesgo
                    if st.session_state.current_edit_index != -1:
                        idx = st.session_state.current_edit_index
                        st.session_state.riesgos.loc[idx] = [
                            st.session_state.riesgos.loc[idx, 'ID'], risk_name, risk_description, selected_type_impact,
                            probabilidad_factor, exposicion_factor, impacto_numerico_slider,
                            control_effectiveness_slider, "Sí" if deliberate_threat_checkbox else "No",
                            min_loss_input, max_loss_input,
                            selected_profile_for_input, selected_category_for_input, selected_subcategory_for_input,
                            severidades_impacto_para_calculo, # Guardar el diccionario de impactos
                            f"{amenaza_inherente_det:.2f}", f"{análisis_residual_det:.2f}", f"{análisis_residual_ajustada_det:.2f}",
                            riesgo_residual_det, clasificacion_det, color_det
                        ]
                        st.success(f"'{risk_name}' actualizado exitosamente.")
                        st.session_state.current_edit_index = -1
                        reset_form_fields()
                    else:
                        new_risk_id = len(st.session_state.riesgos) + 1
                        new_risk = {
                            "ID": new_risk_id, "Nombre del Riesgo": risk_name, "Descripción": risk_description, "Tipo de Impacto": selected_type_impact,
                            "Probabilidad": probabilidad_factor, "Exposición": exposicion_factor, "Impacto Numérico": impacto_numerico_slider,
                            "Efectividad del Control (%)": control_effectiveness_slider, "Amenaza Deliberada": "Sí" if deliberate_threat_checkbox else "No",
                            "Min Loss USD": min_loss_input, "Max Loss USD": max_loss_input,
                            "Perfil": selected_profile_for_input, "Categoria": selected_category_for_input, "Subcategoria": selected_subcategory_for_input,
                            "Impactos Detallados": severidades_impacto_para_calculo,
                            "Amenaza Inherente": f"{amenaza_inherente_det:.2f}", "Amenaza Residual": f"{análisis_residual_det:.2f}",
                            "Amenaza Residual Ajustada": f"{análisis_residual_ajustada_det:.2f}",
                            "Riesgo Residual": riesgo_residual_det, "Clasificación": clasificacion_det, "Color": color_det
                        }
                        st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([new_risk])], ignore_index=True)
                        st.success(get_text("success_risk_added", context="app"))
                        reset_form_fields()
            elif submitted and not valid_loss_range:
                st.error("Por favor, verifica el rango de pérdidas (Min Loss USD <= Max Loss USD).")

    else: st.warning("Por favor, selecciona un perfil para poder agregar riesgos.")

    st.markdown("---")
    st.header(get_text("deterministic_results_title", context="app"))
    if 'riesgo_residual_det' in locals():
        col1_det, col2_det = st.columns(2)
        with col1_det:
            st.markdown(f"<div class='metric-box'><h3>{get_text('inherent_threat', context='app')}</h3><p>{amenaza_inherente_det:.2f}</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-box'><h3>{get_text('residual_threat', context='app')}</h3><p>{análisis_residual_det:.2f}</p></div>", unsafe_allow_html=True)
        with col2_det:
            st.markdown(f"<div class='metric-box'><h3>{get_text('adjusted_residual_threat', context='app')}</h3><p>{análisis_residual_ajustada_det:.2f}</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-box'><h3>{get_text('residual_risk', context='app')}</h3><p>{riesgo_residual_det:.2f}</p></div>", unsafe_allow_html=True)
        
        st.markdown(f"<p style='text-align: center; font-size: 1.2em; font-weight: bold;'>{get_text('classification', context='app')}: <span style='color:{color_det};'>{clasificacion_det}</span></p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-size: 1.2em; font-weight: bold;'>{get_text('risk_residual_percent', context='app')}: <span style='color:black;'>{riesgo_residual_det*100:.1f}%</span></p>", unsafe_allow_html=True)
        
        # Mostrar Máximo Riesgo Teórico
        max_theoretical_risk_val = calcular_max_theoretical_risk(
            selected_probabilidad_clasificacion, selected_exposicion_clasificacion, 1, 0, # Amenaza deliberada SI, Efectividad MÍNIMA (0)
            current_profile_data, selected_category_for_input
        )
        if max_theoretical_risk_val > 0:
            st.markdown(f"<p style='text-align: center; font-size: 1.1em;'>{get_text('max_theoretical_risk', context='app')}: <span style='color:grey;'>{max_theoretical_risk_val*100:.1f}%</span></p>", unsafe_allow_html=True)
            
    else: st.info("Ingresa los datos del riesgo para ver los resultados deterministas aquí.")

    st.markdown("---")
    st.header(get_text("added_risks_title", context="app"))
    if not st.session_state.riesgos.empty:
        df_display = st.session_state.riesgos.copy()
        # Asegurarse de que las columnas necesarias existan
        for col in ["Perfil", "Categoria", "Subcategoria", "Impactos Detallados"]:
            if col not in df_display.columns: df_display[col] = ''
        
        for i, row in df_display.iterrows():
            edit_button_key = f"edit_btn_{row['ID']}"
            delete_button_key = f"del_btn_{row['ID']}"
            col_btns = st.columns([1,1,10])
            with col_btns[0]:
                if st.button(get_text("edit_risk", context="app"), key=edit_button_key):
                    st.session_state.current_edit_index = i
                    st.session_state.risk_name_input = row['Nombre del Riesgo']
                    st.session_state.risk_description_input = row['Descripción']
                    st.session_state.selected_type_impact = row['Tipo de Impacto']
                    st.session_state.selected_probabilidad = row['Probabilidad'] # Factor numérico -> búsqueda de clasificación
                    st.session_state.selected_exposicion = row['Exposición']     # Factor numérico -> búsqueda de clasificación
                    st.session_state.impacto_numerico_slider = row['Impacto Numérico']
                    st.session_state.control_effectiveness_slider = row['Efectividad del Control (%)']
                    st.session_state.deliberate_threat_checkbox = (row['Amenaza Deliberada'] == 'Sí')
                    st.session_state.min_loss_input = row.get('Min Loss USD', 0.0)
                    st.session_state.max_loss_input = row.get('Max Loss USD', 0.0)
                    
                    # Cargar perfil, categoría, subcategoría
                    st.session_state.risk_profile_selector = row.get('Perfil', list(st.session_state.perfiles_usuario.keys())[0])
                    st.session_state.risk_category_selector = row.get('Categoria', '')
                    st.session_state.risk_subcategory_selector = row.get('Subcategoria', '')
                    # Cargar las severidades de impacto guardadas
                    st.session_state['risk_impact_severities'] = row.get('Impactos Detallados', {})
                    
                    st.rerun()
            with col_btns[1]:
                if st.button(get_text("delete_risk", context="app"), key=delete_button_key):
                    if st.warning(get_text("confirm_delete", context="app"), icon="⚠️"):
                        st.session_state.riesgos = st.session_state.riesgos.drop(i).reset_index(drop=True)
                        st.success(get_text("risk_deleted", context="app"))
                        st.rerun()

        st.dataframe(format_risk_dataframe(st.session_state.riesgos, st.session_state.idioma), hide_index=True)
        
        csv_data = st.session_state.riesgos.to_csv(index=False).encode('utf-8')
        st.download_button(label=get_text("download_excel_button", context="app"), data=csv_data, file_name="riesgos_evaluados.csv", mime="text/csv", help="Descargar los datos de los riesgos evaluados en formato CSV.")
    else: st.info(get_text("no_risks_yet", context="app"))

    st.markdown("---")
    st.header(get_text("montecarlo_input_title", context="app"))

    # Selección de riesgos para simular
    risk_names_options = [""] + st.session_state.riesgos['Nombre del Riesgo'].tolist()
    all_risks_option_name = get_text("all_risks_for_simulation", context="app")
    risks_for_multiselect = [{"ID": "all", "Nombre del Riesgo": all_risks_option_name}] + st.session_state.riesgos.to_dict('records')
    risk_names_for_multiselect = [r.get('Nombre del Riesgo', 'N/A') for r in risks_for_multiselect]
    
    default_multiselect = [get_text("all_risks_for_simulation", context="app")] if get_text("all_risks_for_simulation", context="app") in risk_names_for_multiselect else []

    selected_risks_multiselect = st.multiselect(
        get_text("select_risk_to_simulate", context="app"),
        risk_names_for_multiselect,
        default=default_multiselect,
        key="risks_to_simulate_multiselect"
    )

    if st.button(get_text("simulate_button", context="app")) and selected_risks_multiselect:
        risks_to_simulate = []
        if get_text("all_risks_for_simulation", context="app") in selected_risks_multiselect:
            risks_to_simulate = st.session_state.riesgos.to_dict('records')
        else:
            selected_names = selected_risks_multiselect
            risks_to_simulate = [r for r in st.session_state.riesgos.to_dict('records') if r['Nombre del Riesgo'] in selected_names]

        if not risks_to_simulate:
            st.warning(get_text("no_risks_to_simulate", context="app"))
        else:
            valor_economico_global = st.session_state.get('global_economic_value', 100000.0)
            num_iteraciones_mc = st.session_state.get('montecarlo_iterations', 10000)

            with st.spinner('Ejecutando simulación Monte Carlo...'):
                riesgo_residual_sim_data_agg, perdidas_usd_sim_data_agg, correlations_agg, sim_data_per_risk_results = simular_montecarlo(
                    risks_to_simulate, valor_economico_global, num_iteraciones_mc
                )
                
                if perdidas_usd_sim_data_agg is not None and len(perdidas_usd_sim_data_agg) > 0:
                    st.session_state.riesgo_residual_sim_data_agg = riesgo_residual_sim_data_agg
                    st.session_state.perdidas_usd_sim_data_agg = perdidas_usd_sim_data_agg
                    st.session_state.montecarlo_correlations_agg = correlations_agg
                    st.session_state.sim_data_per_risk = sim_data_per_risk_results
                    st.success("Simulación Monte Carlo completada.")
                else:
                    st.error("No se pudieron generar resultados de Monte Carlo. Verifique los valores de entrada.")
    elif st.button(get_text("simulate_button", context="app")) and not selected_risks_multiselect:
        st.warning(get_text("select_at_least_one_risk", context="app"))

    # Configuración global de Monte Carlo
    valor_economico_global = st.number_input(
        get_text("economic_value_asset", context="app"), min_value=0.0, value=st.session_state.get('global_economic_value', 100000.0),
        step=1000.0, format="%.2f", key="global_economic_value",
        help="Valor monetario general para la simulación agregada."
    )
    num_iteraciones_mc = st.slider(
        get_text("num_iterations", context="app"), min_value=1000, max_value=50000, value=st.session_state.get('montecarlo_iterations', 10000),
        step=1000, key="montecarlo_iterations", help="Número de simulaciones para el cálculo Monte Carlo."
    )

    # Histograma de Monte Carlo (Distribución de Pérdida Económica Agregada)
    st.markdown("---")
    if 'perdidas_usd_sim_data_agg' in st.session_state and len(st.session_state.perdidas_usd_sim_data_agg) > 0:
        st.header(get_text("economic_loss_distribution_title", context="app"))
        fig_loss = plot_montecarlo_histogram(st.session_state.perdidas_usd_sim_data_agg, get_text("economic_loss_distribution_title", context="app"), get_text("economic_value_asset", context="app"), st.session_state.idioma)
        if fig_loss:
            col_left_hist, col_center_hist, col_right_hist = st.columns([1,3,1])
            with col_center_hist:
                st.pyplot(fig_loss)
                plt.close(fig_loss)
    else: st.info("Ejecuta la simulación Monte Carlo para ver la distribución de pérdidas económicas.")


with col_graf:
    # --- Dashboard de Riesgos Global ---
    st.header("Dashboard de Riesgos Global")
    if not st.session_state.riesgos.empty:
        df_display = st.session_state.riesgos.copy()
        # Asegurarse de que las columnas necesarias existan
        for col in ["Perfil", "Categoria", "Subcategoria", "Impactos Detallados"]:
            if col not in df_display.columns: df_display[col] = ''
        
        average_risk_residual = df_display['Riesgo Residual'].mean() if 'Riesgo Residual' in df_display.columns else 0.0
        avg_classification, avg_color = clasificar_criticidad(average_risk_residual, st.session_state.idioma)
        
        col_dash1, col_dash2 = st.columns(2)
        with col_dash1:
            st.markdown(f"<div class='metric-box'><h3>Riesgo Residual Promedio</h3><p>{average_risk_residual*100:.1f}%</p></div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; font-size: 1.1em; font-weight: bold;'>Clasificación: <span style='color:{avg_color};'>{avg_classification}</span></p>", unsafe_allow_html=True)
        
        with col_dash2:
            st.subheader("Distribución de Criticidad")
            if 'Clasificacion' in df_display.columns:
                risk_counts = df_display['Clasificacion'].value_counts().to_frame()
                st.dataframe(risk_counts, use_container_width=True)
            else: st.info("No hay suficientes datos para mostrar distribución de criticidad.")
        
        # Mostrar Mapa de Calor y Pareto
        st.markdown("---")
        st.header(get_text("risk_heatmap_title", context="app"))
        fig_heatmap = create_heatmap(st.session_state.riesgos, matriz_probabilidad, matriz_impacto, st.session_state.idioma)
        if fig_heatmap: st.plotly_chart(fig_heatmap, use_container_width=True)
        else: st.info("Agrega riesgos para generar el mapa de calor.")

        st.markdown("---")
        st.header(get_text("risk_pareto_chart_title", context="app"))
        if not st.session_state.riesgos.empty:
            fig_pareto = create_pareto_chart(st.session_state.riesgos, st.session_state.idioma)
            if fig_pareto: st.plotly_chart(fig_pareto, use_container_width=True)
        else: st.info("Agrega riesgos para generar el gráfico de Pareto.")

    else: st.info("Agrega riesgos para ver el dashboard y las visualizaciones.")

    st.markdown("---")
    # Resultados y Métricas de Monte Carlo (Agregado)
    st.header(get_text("montecarlo_results_title", context="app"))
    if 'perdidas_usd_sim_data_agg' in st.session_state and len(st.session_state.perdidas_usd_sim_data_agg) > 0:
        perdidas_agg = st.session_state.perdidas_usd_sim_data_agg
        
        alpha = 0.95
        sorted_losses = np.sort(perdidas_agg)
        index_cvar_float = len(sorted_losses) * alpha
        if index_cvar_float >= len(sorted_losses):
            cvar_95_val = sorted_losses[-1]
        else:
            index_cvar = int(np.floor(index_cvar_float))
            cvar_95_val = sorted_losses[index_cvar:].mean()

        col_mc1, col_mc2 = st.columns(2)
        with col_mc1:
            st.markdown(f"<div class='metric-box'><h3>{get_text('expected_loss', context='app')}</h3><p>${np.mean(perdidas_agg):,.2f}</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-box'><h3>{get_text('median_loss', context='app')}</h3><p>${np.median(perdidas_agg):,.2f}</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-box'><h3>{get_text('p5_loss', context='app')}</h3><p>${np.percentile(perdidas_agg, 5):,.2f}</p></div>", unsafe_allow_html=True)
        with col_mc2:
            st.markdown(f"<div class='metric-box'><h3>{get_text('p90_loss', context='app')}</h3><p>${np.percentile(perdidas_agg, 90):,.2f}</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-box'><h3>{get_text('max_loss', context='app')}</h3><p>${np.max(perdidas_agg):,.2f}</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-box'><h3>{get_text('cvar_95', context='app')}</h3><p>${cvar_95_val:,.2f}</p></div>", unsafe_allow_html=True)

        st.markdown("---")
        st.header(get_text("sensitivity_analysis_title", context="app"))
        if 'montecarlo_correlations_agg' in st.session_state and st.session_state.montecarlo_correlations_agg is not None:
            fig_sensitivity = create_sensitivity_plot(st.session_state.montecarlo_correlations_agg, st.session_state.idioma)
            if fig_sensitivity: st.plotly_chart(fig_sensitivity, use_container_width=True)
        else: st.info("Ejecuta la simulación Monte Carlo para ver el análisis de sensibilidad.")
    else: st.info("Ejecuta la simulación Monte Carlo para ver los resultados aquí.")
