from __future__ import annotations
from typing import Optional, Any, Union
import pandas as pd
import polars as pl
import numpy as np
import streamlit as st
from pydantic import BaseModel  # Para validación de datos

class RiskModel(BaseModel):
    id: int
    name: str
    impact: float
    probability: float

@st.cache_data
def load_sample_data() -> Union[pd.DataFrame, pl.DataFrame]:
    """Carga datos de ejemplo en formato Pandas o Polars"""
    data = {
        "risk_id": [1, 2, 3],
        "risk_name": ["Security Risk", "Financial Risk", "Operational Risk"],
        "impact": [0.8, 0.5, 0.3],
        "probability": [0.7, 0.4, 0.2]
    }
    return pl.DataFrame(data)  # Cambiar a pd.DataFrame() si prefieres Pandas

@st.cache_data
def load_risk_for_edit(
    risk_id: int, 
    df: Union[pd.DataFrame, pl.DataFrame]
) -> Optional[dict[str, Any]]:
    """
    Versión robusta que maneja ambos DataFrames:
    - Usa .loc para Pandas
    - Usa .filter para Polars
    """
    try:
        if isinstance(df, pd.DataFrame):
            record = df.loc[df["risk_id"] == risk_id].iloc[0].to_dict()
        else:
            record = df.filter(pl.col("risk_id") == risk_id).to_dicts()[0]
        
        validated = RiskModel(
            id=int(record["risk_id"]),
            name=str(record["risk_name"]),
            impact=float(record["impact"]),
            probability=float(record["probability"])
        )
        return validated.dict()
    
    except Exception as e:
        st.error(f"Error loading risk {risk_id}: {str(e)}")
        return None
