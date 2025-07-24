import streamlit as st
import pandas as pd
import polars as pl
from utils import load_sample_data, load_risk_for_edit

def main():
    st.set_page_config(page_title="Risk App", layout="wide")
    
    # Carga de datos
    df = load_sample_data()
    
    # Interfaz
    st.title("📊 Risk Management Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Data Preview")
        st.dataframe(df.to_pandas() if isinstance(df, pl.DataFrame) else df)
    
    with col2:
        st.header("Risk Editor")
        risk_id = st.selectbox(
            "Select Risk ID",
            df["risk_id"].to_list() if isinstance(df, pl.DataFrame) else df["risk_id"].tolist()
        )
        
        if risk_data := load_risk_for_edit(risk_id, df):
            st.json(risk_data)
            risk_score = risk_data["impact"] * risk_data["probability"]
            st.metric("Risk Score", f"{risk_score:.0%}")
            
            # Gráfico de ejemplo
            st.altair_chart(create_risk_chart(risk_data))

def create_risk_chart(data: dict) -> "alt.Chart":
    import altair as alt
    source = pd.DataFrame({
        'Metric': ['Impact', 'Probability'],
        'Value': [data['impact'], data['probability']]
    })
    return alt.Chart(source).mark_bar().encode(
        x='Metric',
        y='Value',
        color='Metric'
    ).properties(height=200)

if __name__ == "__main__":
    main()
    
