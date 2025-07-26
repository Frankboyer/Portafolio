# modules/utils.py
"""
Utilidades para la interfaz de usuario, formateo de datos, y gestión de estado.
Incluye funciones para gestionar perfiles, resetear campos, obtener textos traducidos,
y renderizar sliders de impacto dinámicos.
"""
import streamlit as st
import pandas as pd
import json
import os
from modules.data_config import criticidad_límites, PERFILES_BASE # Importar datos necesarios
from modules.data_config import matriz_probabilidad_vals, factor_exposicion_vals # Mapeos
from modules.data_config import textos # Diccionario de textos generales

# --- Funciones de Utilidad para la UI ---

def reset_form_fields():
    """Reinicia los campos del formulario de entrada de riesgo a sus valores por defecto."""
    st.session_state['risk_name_input'] = ""
    st.session_state['risk_description_input'] = ""
    st.session_state['selected_type_impact'] = st.session_state['default_type_impact']
    st.session_state['selected_probabilidad'] = st.session_state['default_probabilidad']
    st.session_state['selected_exposicion'] = st.session_state['default_exposicion']
    st.session_state['impacto_numerico_slider'] = st.session_state['default_impacto_numerico']
    st.session_state['control_effectiveness_slider'] = st.session_state['default_control_effectiveness']
    st.session_state['deliberate_threat_checkbox'] = False
    st.session_state['current_edit_index'] = -1
    st.session_state['min_loss_input'] = st.session_state.get('default_min_loss', 0.0)
    st.session_state['max_loss_input'] = st.session_state.get('default_max_loss', 0.0)
    # Resetear selectores de perfil de riesgo
    st.session_state['risk_profile_selector'] = list(st.session_state.perfiles_usuario.keys())[0] if st.session_state.perfiles_usuario else ""
    st.session_state['risk_category_selector'] = ""
    st.session_state['risk_subcategory_selector'] = ""
    # Limpiar los inputs de severidad de impacto dinámicos
    st.session_state['risk_impact_severities'] = {}

def format_risk_dataframe(df_risks, idioma="es"):
    """Formatea el DataFrame de riesgos aplicando colores a la columna 'Riesgo Residual'."""
    if df_risks.empty: return df_risks
    def get_color(val):
        for v_min, v_max, _, color, _ in criticidad_límites:
            if v_min <= val <= v_max: return f'background-color: {color};'
        return ''
    styled_df = df_risks.style.applymap(get_color, subset=['Riesgo Residual'])
    return styled_df

# --- Funciones para Gestión de Perfiles (deben estar definidas o importadas) ---
# Las funciones de profile_manager se importan en app.py
# Si las quieres tener aquí también, descomenta las siguientes líneas y ajústalas:
# from modules.profile_manager import load_profiles, save_profiles, get_profile_data, delete_profile, update_profile, add_profile

# --- Funciones para obtener Textos Traducidos ---
def get_text(key, context="app"):
    """
    Obtiene el texto traducido.
    Contexto: 'app' para textos generales, 'hierarchy' para perfiles, categorías, subcategorías.
    """
    lang = st.session_state.get('idioma', 'es')
    
    if context == "app":
        return textos.get(lang, {}).get(key, key)
    elif context == "hierarchy":
        # Acceder a HIERARCHY_TRANSLATIONS importado desde data_config
        try:
            from modules.data_config import HIERARCHY_TRANSLATIONS # Asegura la importación
            return HIERARCHY_TRANSLATIONS.get(lang, {}).get(key, HIERARCHY_TRANSLATIONS.get('es', {}).get(key, key))
        except ImportError:
            return key # Fallback si no se importa
    return key # Fallback general

def render_impact_sliders(profile_data, selected_category, current_severities_state, idioma="es"):
    """
    Renderiza los sliders de severidad de impacto basados en la categoría seleccionada
    dentro de un perfil.
    """
    impact_inputs_data = {}
    if not profile_data or not selected_category: return impact_inputs_data

    impacts_config_for_cat = profile_data.get("categorias", {}).get(selected_category, {}).get("impacts", {})
    
    if impacts_config_for_cat:
        st.subheader(get_text("Impactos Detallados", context="app"))
        for tipo_impacto, ponderacion_perfil in impacts_config_for_cat.items():
            current_severidad = current_severities_state.get(tipo_impacto, 50)
            impact_severity = st.slider(
                f"{get_text('impact_type_label', context='app')}: {tipo_impacto} (Ponderación Perfil: {ponderacion_perfil}%)",
                min_value=0, max_value=100, value=current_severidad, step=1,
                key=f"impact_severity_{tipo_impacto}",
                help=f"Severidad del impacto '{tipo_impacto}' para este riesgo."
            )
            impact_inputs_data[tipo_impacto] = impact_severity
    else:
        pass

    return impact_inputs_data
