import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import streamlit as st
from typing import List, Dict

def create_heatmap(df: pd.DataFrame, x_col: str, y_col: str, value_col: str, title: str) -> None:
    """Crea un mapa de calor interactivo"""
    try:
        pivot = df.pivot_table(index=y_col, columns=x_col, values=value_col, aggfunc='mean')
        plt.figure(figsize=(10, 6))
        sns.heatmap(pivot, annot=True, fmt=".2f", cmap="YlOrRd", linewidths=.5)
        plt.title(title)
        plt.xticks(rotation=45)
        plt.yticks(rotation=0)
        st.pyplot(plt)
        plt.clf()
    except Exception as e:
        st.error(f"Error generando mapa de calor: {str(e)}")

def create_pareto_chart(df: pd.DataFrame, value_col: str, label_col: str, title: str) -> None:
    """Crea un diagrama de Pareto"""
    try:
        df_sorted = df.sort_values(value_col, ascending=False)
        df_sorted['cumulative'] = df_sorted[value_col].cumsum() / df_sorted[value_col].sum()
        
        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax1.bar(df_sorted[label_col], df_sorted[value_col], color='b')
        ax1.set_ylabel('Valor', color='b')
        ax1.tick_params('y', colors='b')
        
        ax2 = ax1.twinx()
        ax2.plot(df_sorted[label_col], df_sorted['cumulative'], 'r-')
        ax2.set_ylabel('Porcentaje Acumulado', color='r')
        ax2.tick_params('y', colors='r')
        
        plt.title(title)
        plt.xticks(rotation=45)
        st.pyplot(fig)
        plt.clf()
    except Exception as e:
        st.error(f"Error generando Pareto: {str(e)}")

def plot_montecarlo_histogram(data: List[float], title: str) -> None:
    """Grafica histograma de simulación Monte Carlo"""
    try:
        plt.figure(figsize=(10, 6))
        sns.histplot(data, kde=True, bins=50, color='skyblue')
        plt.title(title)
        plt.xlabel('Nivel de Riesgo')
        plt.ylabel('Frecuencia')
        st.pyplot(plt)
        plt.clf()
    except Exception as e:
        st.error(f"Error generando histograma: {str(e)}")

def create_sensitivity_plot(sensitivity_data: Dict[str, float], title: str) -> None:
    """Crea gráfico de barras para análisis de sensibilidad"""
    try:
        names = list(sensitivity_data.keys())
        values = list(sensitivity_data.values())
        
        plt.figure(figsize=(10, 6))
        y_pos = np.arange(len(names))
        plt.barh(y_pos, values, align='center', color='green')
        plt.yticks(y_pos, names)
        plt.title(title)
        plt.xlabel('Impacto en Riesgo')
        st.pyplot(plt)
        plt.clf()
    except Exception as e:
        st.error(f"Error generando gráfico de sensibilidad: {str(e)}")
