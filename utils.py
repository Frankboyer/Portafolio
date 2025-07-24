from typing import Optional, Any, Union  # Solo lo esencial de typing
import pandas as pd
import polars as pl
import streamlit as st
from loguru import logger  # Opcional

@st.cache_data
def get_text(key: str) -> str:
    """Obtiene texto traducido o marcado"""
    translations = {"welcome": "Bienvenido", "error": "Error"}
    return translations.get(key, key)

@st.cache_data
def get_first_value(series: Union[pd.Series, pl.Series]) -> Any:
    """Obtiene el primer valor de una serie"""
    if isinstance(series, pd.Series):
        return series.iloc[0]
    return series[0]

@st.cache_data
def get_factor_value(factor: str) -> float:
    """Obtiene factor numérico de un mapeo"""
    factors = {"high": 1.0, "medium": 0.5, "low": 0.1}
    return factors.get(factor.lower(), 0.0)

def validate_impact_value(value: Union[int, float]) -> bool:
    """Valida que el impacto esté en rango permitido"""
    return 0 <= value <= 1.0

@st.cache_data
def load_risk_for_edit(
    risk_id: int, 
    df: Union[pd.DataFrame, pl.DataFrame]
) -> Optional[dict[str, Any]]:  # ¡Cambiado a dict en lugar de Dict!
    """
    Carga un riesgo específico para edición
    """
    try:
        if isinstance(df, pd.DataFrame):
            record = df[df["risk_id"] == risk_id].iloc[0].to_dict()
        else:
            record = df.filter(pl.col("risk_id") == risk_id).to_dicts()[0]
            
        return {
            "id": record.get("risk_id"),
            "name": record.get("risk_name"),
            "impact": float(record.get("impact", 0)),
            "probability": float(record.get("probability", 0))
        }
    except (IndexError, KeyError) as e:
        logger.error(f"Error loading risk {risk_id}: {str(e)}")
        return None
