import streamlit as st
import pandas as pd
from data_config import criticidad_límites # Asegúrate de importar esto

def reset_form_fields():
    """
    Reinicia los campos de entrada del formulario de riesgo a sus valores por defecto.
    Esto se usa comúnmente después de agregar o editar un riesgo para limpiar la UI.
    También asegura que el estado de edición actual se reinicie.
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
        """Función interna para obtener el color basado en el valor de riesgo residual."""
        for v_min, v_max, _, color, _ in criticidad_límites:
            if v_min <= val <= v_max:
                return f'background-color: {color};'
        return ''

    # Aplicar el estilo a la columna 'Riesgo Residual'
    styled_df = df_risks.style.applymap(get_color, subset=['Riesgo Residual'])

    return styled_df
