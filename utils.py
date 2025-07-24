import streamlit as st
import pandas as pd
from data_config import textos, criticidad_límites, tabla_tipo_impacto, factor_probabilidad, factor_exposicion

def get_text_utils(key):
    """
    Obtiene el texto correspondiente a una clave en el idioma actual de la sesión.
    Se asume que st.session_state.idioma está definido.
    """
    return textos[st.session_state.idioma].get(key, key)

def reset_form_fields():
    """
    Reinicia los campos del formulario de entrada de riesgo a sus valores predeterminados.
    Esto se hace actualizando los valores en st.session_state.
    """
    st.session_state['risk_name_input'] = ""
    st.session_state['risk_description_input'] = ""
    st.session_state['selected_type_impact'] = st.session_state['default_type_impact']
    st.session_state['selected_probabilidad'] = st.session_state['default_probabilidad']
    st.session_state['selected_exposicion'] = st.session_state['default_exposicion']
    st.session_state['impacto_numerico_slider'] = st.session_state['default_impacto_numerico']
    st.session_state['control_effectiveness_slider'] = st.session_state['default_control_effectiveness']
    st.session_state['deliberate_threat_checkbox'] = False
    st.session_state.current_edit_index = -1 # Asegúrate de que no estamos en modo edición

def format_risk_dataframe(df_riesgos, idioma='es'):
    """
    Formatea el DataFrame de riesgos para una mejor visualización en Streamlit,
    incluyendo la traducción de columnas y la aplicación de estilos.
    """
    if df_riesgos.empty:
        return pd.DataFrame() # Retorna un DataFrame vacío si no hay datos

    df_display = df_riesgos.copy()

    # Mapear valores numéricos a nombres de clasificación si es necesario para Probabilidad y Exposición
    # Asegúrate de que estos mapeos existen en data_config
    prob_map = factor_probabilidad.set_index('Factor')['Clasificacion'].to_dict()
    exp_map = factor_exposicion.set_index('Factor')['Clasificacion'].to_dict()

    df_display['Probabilidad'] = df_display['Probabilidad'].map(prob_map).fillna(df_display['Probabilidad']).astype(str)
    df_display['Exposición'] = df_display['Exposición'].map(exp_map).fillna(df_display['Exposición']).astype(str)


    # Definir nombres de columnas para mostrar según el idioma
    column_names_es = {
        "ID": "ID",
        "Nombre del Riesgo": "Nombre del Riesgo",
        "Descripción": "Descripción",
        "Tipo de Impacto": "Tipo de Impacto",
        "Probabilidad": "Probabilidad",
        "Exposición": "Exposición",
        "Impacto Numérico": "Impacto Numérico",
        "Efectividad del Control (%)": "Efectividad del Control (%)",
        "Amenaza Deliberada": "Amenaza Deliberada",
        "Amenaza Inherente": "Amenaza Inherente",
        "Amenaza Residual": "Amenaza Residual",
        "Amenaza Residual Ajustada": "Amenaza Residual Ajustada",
        "Riesgo Residual": "Riesgo Residual",
        "Clasificación": "Clasificación",
        "Color": "Color" # Mantener para el estilo, luego se oculta
    }

    column_names_en = {
        "ID": "ID",
        "Nombre del Riesgo": "Risk Name",
        "Descripción": "Description",
        "Tipo de Impacto": "Impact Type",
        "Probabilidad": "Probability",
        "Exposición": "Exposure",
        "Impacto Numérico": "Numeric Impact",
        "Efectividad del Control (%)": "Control Effectiveness (%)",
        "Amenaza Deliberada": "Deliberate Threat",
        "Amenaza Inherente": "Inherent Threat",
        "Amenaza Residual": "Residual Threat",
        "Amenaza Residual Ajustada": "Adjusted Residual Threat",
        "Riesgo Residual": "Residual Risk",
        "Clasificación": "Classification",
        "Color": "Color"
    }

    if idioma == 'es':
        df_display = df_display.rename(columns=column_names_es)
        # Formatear 'Amenaza Deliberada' a Sí/No
        df_display['Amenaza Deliberada'] = df_display['Amenaza Deliberada'].apply(lambda x: "Sí" if x == 1.0 else "No")
    else:
        df_display = df_display.rename(columns=column_names_en)
        # Formatear 'Deliberate Threat' a Yes/No
        df_display['Deliberate Threat'] = df_display['Deliberate Threat'].apply(lambda x: "Yes" if x == 1.0 else "No")


    # Columnas numéricas para formato
    numeric_cols = [col_name for col_name in [
        column_names_es["Impacto Numérico"] if idioma == 'es' else column_names_en["Impacto Numérico"],
        column_names_es["Efectividad del Control (%)"] if idioma == 'es' else column_names_en["Efectividad del Control (%)"],
        column_names_es["Amenaza Inherente"] if idioma == 'es' else column_names_en["Amenaza Inherente"],
        column_names_es["Amenaza Residual"] if idioma == 'es' else column_names_en["Amenaza Residual"],
        column_names_es["Amenaza Residual Ajustada"] if idioma == 'es' else column_names_en["Amenaza Residual Ajustada"],
        column_names_es["Riesgo Residual"] if idioma == 'es' else column_names_en["Riesgo Residual"]
    ] if col_name in df_display.columns] # Asegurarse de que la columna exista

    # Aplicar formato de dos decimales a las columnas numéricas relevantes
    for col in numeric_cols:
        df_display[col] = df_display[col].apply(lambda x: f"{x:.2f}")

    # Estilo condicional para la columna 'Riesgo Residual' basada en 'Color'
    def color_rows(row):
        color = row['Color']
        return [f'background-color: {color}' for _ in row]

    # Columnas a mostrar (excluir 'ID' y 'Color' para el usuario final)
    cols_to_show_es = [
        "Nombre del Riesgo", "Descripción", "Tipo de Impacto", "Probabilidad",
        "Exposición", "Impacto Numérico", "Efectividad del Control (%)",
        "Amenaza Deliberada", "Amenaza Inherente", "Amenaza Residual",
        "Amenaza Residual Ajustada", "Riesgo Residual", "Clasificación"
    ]
    cols_to_show_en = [
        "Risk Name", "Description", "Impact Type", "Probability",
        "Exposure", "Numeric Impact", "Control Effectiveness (%)",
        "Deliberate Threat", "Inherent Threat", "Residual Threat",
        "Adjusted Residual Threat", "Residual Risk", "Classification"
    ]
    display_cols = cols_to_show_es if idioma == 'es' else cols_to_show_en

    # Aplicar el estilo y luego seleccionar las columnas a mostrar
    styled_df = df_display.style.apply(color_rows, axis=1)

    return styled_df.hide(axis="columns", subset=['Color']).reindex(columns=display_cols, fill_value='')
