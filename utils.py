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

    # Excluir la columna 'Color' para que no aparezca
    cols_to_show = [col for col in df.columns if col != 'Color']

    # Asegurarse que existan las columnas
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
