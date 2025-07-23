import streamlit as st
import pandas as pd
# Asegúrate de que esta importación sea correcta y la ruta a data_config.py sea accesible
from data_config import criticidad_límites

def reset_form_fields():
    """
    Reinicia los campos de entrada del formulario de riesgo a sus valores por defecto.
    Esto se usa comúnmente después de agregar o editar un riesgo para limpiar la UI.
    También asegura que el estado de edición actual se reinicie.
    
    Esta función asume que las claves de st.session_state que corresponden a los
    campos del formulario ya han sido inicializadas al inicio de riskapp.py
    con un valor por defecto.
    """
    st.session_state['risk_name_input'] = ""
    st.session_state['risk_description_input'] = ""
    st.session_state['selected_type_impact'] = st.session_state['default_type_impact']
    st.session_state['selected_probabilidad'] = st.session_state['default_probabilidad']
    st.session_state['selected_exposicion'] = st.session_state['default_exposicion']
    st.session_state['impacto_numerico_slider'] = st.session_state['default_impacto_numerico']
    st.session_state['control_effectiveness_slider'] = st.session_state['default_control_effectiveness']
    st.session_state['deliberate_threat_checkbox'] = False
    st.session_state['current_edit_index'] = -1 # Asegurarse de que no estamos en modo edición


def format_risk_dataframe(df_risks, idioma="es"):
    """
    Formatea el DataFrame de riesgos para una mejor visualización en Streamlit,
    aplicando colores de criticidad al 'Riesgo Residual'.

    Args:
        df_risks (pd.DataFrame): El DataFrame de riesgos a formatear.
        idioma (str, optional): El idioma para la clasificación de criticidad (no usado directamente aquí
                                 para la función de color, pero pasado para consistencia si se usara la clasificación).
                                 Por defecto es 'es'.

    Returns:
        pandas.io.formats.style.Styler: Un objeto Styler de Pandas con los estilos aplicados,
                                         o el DataFrame original si está vacío.
    """
    if df_risks.empty:
        return df_risks

    def get_color(val):
        """Función interna para obtener el color de fondo basado en el valor de riesgo residual."""
        # Itera sobre los límites de criticidad definidos en data_config.py
        for v_min, v_max, _, color, _ in criticidad_límites:
            if v_min <= val <= v_max:
                return f'background-color: {color};'
        return '' # Retorna vacío si no hay color asociado

    # Aplica la función get_color a la columna 'Riesgo Residual'
    styled_df = df_risks.style.applymap(get_color, subset=['Riesgo Residual'])

    return styled_df
