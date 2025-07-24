import pandas as pd
import streamlit as st

def reset_form_fields():
    """
    Limpia los campos del formulario guardados en session_state.
    """
    keys_to_reset = [
        'risk_name_input',
        'risk_description_input',
        'selected_type_impact',
        'selected_probabilidad',
        'selected_exposicion',
        'impacto_numerico_slider',
        'control_effectiveness_slider',
        'deliberate_threat_checkbox'
    ]
    for key in keys_to_reset:
        if key in st.session_state:
            if isinstance(st.session_state[key], bool):
                st.session_state[key] = False
            elif isinstance(st.session_state[key], int):
                st.session_state[key] = 0
            else:
                st.session_state[key] = ''

def format_risk_dataframe(df: pd.DataFrame, idioma: str, estilizado=True):
    """
    Formatea el DataFrame de riesgos para mostrarlo en Streamlit,
    ocultando la columna 'Color' y aplicando estilos condicionales.

    Args:
        df (pd.DataFrame): DataFrame con los riesgos.
        idioma (str): Código de idioma ('es' o 'en').
        estilizado (bool): Si es True, devuelve un DataFrame con estilos para Streamlit.

    Returns:
        pd.DataFrame o pd.Styler: DataFrame formateado y/o estilizado.
    """
    if df.empty:
        return df

    # Excluir la columna 'Color'
    cols_to_show = [col for col in df.columns if col != 'Color']

    # Asegurar que la columna 'Clasificación' exista para aplicar estilo
    if 'Clasificación' not in df.columns:
        return df[cols_to_show]

    df_to_show = df[cols_to_show]

    if estilizado:
        def color_clasificacion(val):
            if isinstance(val, str):
                val_lower = val.lower()
                if val_lower in ['alto', 'high']:
                    return 'background-color: #f44336; color: white'  # rojo
                elif val_lower in ['medio', 'medium', 'moderado']:
                    return 'background-color: #ffeb3b; color: black'  # amarillo
                elif val_lower in ['bajo', 'low']:
                    return 'background-color: #4caf50; color: white'  # verde
            return ''

        styled_df = df_to_show.style.applymap(color_clasificacion, subset=['Clasificación'])

        return styled_df
    else:
        return df_to_show
