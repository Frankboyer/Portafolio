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

def format_risk_dataframe(df_riesgos, idioma='es', estilizado=True):
    """
    Formatea el DataFrame de riesgos para una mejor visualización en Streamlit,
    incluyendo la traducción de columnas, formato numérico y estilos condicionales si se desea.

    Parámetros:
    - df_riesgos: DataFrame original con los datos de riesgo
    - idioma: 'es' o 'en' para mostrar los encabezados traducidos
    - estilizado: bool. Si True, aplica formato condicional de color; si False, devuelve solo DataFrame limpio
    """
    if df_riesgos.empty:
        return pd.DataFrame()  # Retorna un DataFrame vacío si no hay datos

    df_display = df_riesgos.copy()

    # Mapear valores numéricos a nombres de clasificación si es necesario para Probabilidad y Exposición
    prob_map = factor_probabilidad.set_index('Factor')['Clasificacion'].to_dict()
    exp_map = factor_exposicion.set_index('Factor')['Clasificacion'].to_dict()

    df_display['Probabilidad'] = df_display['Probabilidad'].map(prob_map).fillna(df_display['Probabilidad']).astype(str)
    df_display['Exposición'] = df_display['Exposición'].map(exp_map).fillna(df_display['Exposición']).astype(str)

    # Definir nombres de columnas según idioma
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
        "Color": "Color"
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

    # Selección de nombres según idioma
    nombre_columnas = column_names_es if idioma == 'es' else column_names_en
    df_display = df_display.rename(columns=nombre_columnas)

    # Formatear la columna "Amenaza Deliberada" como texto Sí/No o Yes/No
    ad_col = nombre_columnas["Amenaza Deliberada"]
    df_display[ad_col] = df_display[ad_col].apply(lambda x: "Sí" if x == 1.0 else ("No" if idioma == 'es' else "No" if x == 0.0 else x)) if idioma == 'es' else df_display[ad_col].apply(lambda x: "Yes" if x == 1.0 else "No")

    # Columnas numéricas para redondear
    numeric_cols = [nombre_columnas[c] for c in [
        "Impacto Numérico", "Efectividad del Control (%)",
        "Amenaza Inherente", "Amenaza Residual",
        "Amenaza Residual Ajustada", "Riesgo Residual"
    ] if nombre_columnas[c] in df_display.columns]

    for col in numeric_cols:
        df_display[col] = df_display[col].apply(lambda x: f"{x:.2f}" if isinstance(x, (int, float, float)) else x)

    # Columnas visibles (sin 'ID' ni 'Color')
    cols_to_show = [
        nombre_columnas["Nombre del Riesgo"],
        nombre_columnas["Descripción"],
        nombre_columnas["Tipo de Impacto"],
        nombre_columnas["Probabilidad"],
        nombre_columnas["Exposición"],
        nombre_columnas["Impacto Numérico"],
        nombre_columnas["Efectividad del Control (%)"],
        nombre_columnas["Amenaza Deliberada"],
        nombre_columnas["Amenaza Inherente"],
        nombre_columnas["Amenaza Residual"],
        nombre_columnas["Amenaza Residual Ajustada"],
        nombre_columnas["Riesgo Residual"],
        nombre_columnas["Clasificación"]
    ]

    # Si se solicita sin estilo, solo devolver el DataFrame limpio
    if not estilizado:
        df_display = df_display.drop(columns=['Color'], errors='ignore')
        df_display = df_display[[col for col in cols_to_show if col in df_display.columns]]
        return df_display

    # Estilo condicional por color de fondo
    def color_rows(row):
        color = row.get('Color', '#FFFFFF')
        return [f'background-color: {color}' for _ in row]

    # Aplicar estilo y ocultar columna "Color"
    styled_df = df_display.style.apply(color_rows, axis=1)
    if 'Color' in df_display.columns:
        styled_df = styled_df.hide_columns(['Color'])

    return styled_df
