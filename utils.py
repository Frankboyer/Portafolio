import pandas as pd
from typing import Any, Optional

def get_text(key: str, idioma: str = 'es') -> str:
    """Obtiene texto traducido según clave e idioma"""
    from data_config import textos
    return textos.get(idioma, {}).get(key, f"[{key} no encontrado]")

def get_first_value(df: pd.DataFrame, column: str) -> Any:
    """Obtiene el primer valor de una columna de DataFrame"""
    return df[column].iloc[0] if not df.empty and column in df.columns else None

def get_factor_value(df: pd.DataFrame, lookup_value: str, factor_column: str = 'Factor') -> float:
    """Obtiene valor numérico de factor a partir de su clasificación"""
    filtered = df[df['Clasificacion'] == lookup_value]
    if filtered.empty:
        raise ValueError(f"Clasificación '{lookup_value}' no encontrada")
    return float(filtered[factor_column].iloc[0])

def validate_impact_value(value: float) -> bool:
    """Valida que el valor de impacto esté en rango correcto"""
    return 0 <= value <= 100

def load_risk_for_edit(risk_id: int, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """Carga datos de un riesgo existente para edición"""
    risk_data = df[df['ID'] == risk_id]
    if not risk_data.empty:
        return risk_data.iloc[0].to_dict()
    return None
