import streamlit as st
import pandas as pd
from data_config import criticidad_límites, textos, tabla_tipo_impacto, factor_probabilidad, factor_exposicion, factores_amenaza_deliberada

# Función auxiliar para obtener textos específicos de este módulo
def get_text_utils(key, idioma='es'):
    return textos[idioma].get(key, key)

def reset_form_fields():
    """Resetea los campos del formulario de entrada de riesgo a sus valores por defecto."""
    st.session_state['risk_name_input'] = ""
    st.session_state['risk_description_input'] = ""

    # Asegúrate de que los valores por defecto existan en los DataFrames
    st.session_state['selected_type_impact'] = tabla_tipo_impacto['Tipo de Impacto'].iloc[0] if not tabla_tipo_impacto.empty else ""
    st.session_state['selected_probabilidad'] = factor_probabilidad['Clasificacion'].iloc[0] if not factor_probabilidad.empty else ""
    st.session_state['selected_exposicion'] = factor_exposicion['Clasificacion'].iloc[0] if not factor_exposicion.empty else ""

    st.session_state['impacto_numerico_slider'] = 50
    st.session_state['control_effectiveness_slider'] = 50
    st.session_state['deliberate_threat_present_checkbox'] = False
    st.session_state['deliberate_threat_level_selectbox'] = factores_amenaza_deliberada['Clasificacion'].iloc[0] if not factores_amenaza_deliberada.empty else ""

    st.session_state.current_edit_index = -1 # Asegura que no estemos en modo edición

def color_clasificacion(val):
    """
    Función de ayuda para aplicar colores de fondo basados en la clasificación del riesgo.
    """
    if isinstance(val, str):
        val_lower = val.lower()
        if val_lower in ['bajo', 'low']:
            return 'background-color: #d4edda' # Verde claro
        elif val_lower in ['medio', 'medium']:
            return 'background-color: #ffc107' # Amarillo
        elif val_lower in ['alto', 'high']:
            return 'background-color: #fd7e14; color: white' # Naranja
        elif val_lower in ['crítico', 'critical']:
            return 'background-color: #dc3545; color: white' # Rojo
    return '' # Default

def format_risk_dataframe(df):
    """
    Aplica formato condicional al DataFrame de riesgos para Streamlit.
    """
    if df.empty:
        return df
    # Columnas a las que se aplica el estilo de color
    columns_to_style = ['Clasificación']
    # Aplica el estilo a las columnas seleccionadas
    styled_df = df.style.applymap(color_clasificacion, subset=columns_to_style)
    return styled_df
