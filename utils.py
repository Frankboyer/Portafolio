import pandas as pd

def format_risk_dataframe(df, idioma, estilizado=True):
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

    # Columnas que quieres mostrar (sin 'Color')
    cols_to_show = [
        "Nombre del Riesgo", "Descripción", "Tipo de Impacto",
        "Probabilidad", "Exposición", "Impacto Numérico",
        "Efectividad del Control (%)", "Amenaza Deliberada",
        "Amenaza Inherente", "Amenaza Residual", "Amenaza Residual Ajustada",
        "Riesgo Residual", "Clasificación"
    ]

    # Verifica que esas columnas existan en df para evitar errores
    cols_existentes = [col for col in cols_to_show if col in df.columns]
    df_to_show = df[cols_existentes]

    if estilizado:
        # Función para aplicar color de fondo basado en la clasificación (ejemplo)
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

        # Aplica estilo a la columna 'Clasificación'
        styled_df = df_to_show.style.applymap(color_clasificacion, subset=['Clasificación'])

        # Puedes agregar más estilos si quieres

        return styled_df

    else:
        return df_to_show
