import streamlit as st
import pandas as pd
import numpy as np
from data_config import textos, tabla_tipo_impacto, factor_probabilidad, factor_exposicion, factores_amenaza_deliberada
from calculations import clasificar_criticidad, calcular_criticidad, simular_montecarlo
from plotting import create_heatmap, create_pareto_chart, plot_montecarlo_histogram, create_sensitivity_plot
from utils import get_text, get_first_value, get_factor_value, validate_impact_value, load_risk_for_edit
from logger import setup_logger

# ======================
# 1. CONFIGURACIÓN INICIAL
# ======================
def setup_page_config():
    """Configuración inicial de la página"""
    st.set_page_config(
        layout="wide",
        page_title=get_text("app_title"),
        page_icon="🛡️",
        initial_sidebar_state="expanded"
    )
    apply_custom_styles()
    setup_logger("risk_app", "risk_app.log")

def apply_custom_styles():
    """Aplica estilos CSS personalizados"""
    st.markdown(f"""
    <style>
        .main .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
        }}
        h1, h2, h3 {{
            color: #003366;
            border-bottom: 1px solid #eee;
            padding-bottom: 0.3rem;
        }}
        .stButton>button {{
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            font-weight: bold;
        }}
        .stDataFrame {{
            font-size: 0.9rem;
        }}
        .risk-high {{
            background-color: #ffcccc !important;
        }}
        .risk-medium {{
            background-color: #fff3cd !important;
        }}
    </style>
    """, unsafe_allow_html=True)

# ======================
# 2. MANEJO DEL ESTADO
# ======================
def initialize_session_state():
    """Inicializa el estado de la sesión"""
    if 'riesgos' not in st.session_state:
        st.session_state.riesgos = pd.DataFrame(columns=[
            "ID", "Nombre del Riesgo", "Descripción", "Tipo de Impacto",
            "Probabilidad", "Exposición", "Impacto Numérico",
            "Efectividad del Control (%)", "Amenaza Deliberada (Checkbox)", 
            "Nivel Amenaza Deliberada", "Amenaza Inherente", "Amenaza Residual",
            "Amenaza Residual Ajustada", "Riesgo Residual", "Clasificación", "Color"
        ])
    
    if 'form_fields' not in st.session_state:
        st.session_state.form_fields = {
            'risk_name_input': "",
            'risk_description_input': "",
            'selected_type_impact': get_first_value(tabla_tipo_impacto, 'Tipo de Impacto'),
            'selected_probabilidad': get_first_value(factor_probabilidad, 'Clasificacion'),
            'selected_exposicion': get_first_value(factor_exposicion, 'Clasificacion'),
            'impacto_numerico_slider': 50,
            'control_effectiveness_slider': 50,
            'deliberate_threat_present_checkbox': False,
            'deliberate_threat_level_selectbox': get_first_value(factores_amenaza_deliberada, 'Clasificacion')
        }
    
    if 'current_edit_index' not in st.session_state:
        st.session_state.current_edit_index = -1

# ======================
# 3. FUNCIONES PRINCIPALES
# ======================
def handle_form_submit():
    """Maneja el envío del formulario"""
    logger = setup_logger("form_submit")
    form_data = st.session_state.form_fields
    
    try:
        # Validaciones
        if not form_data['risk_name_input'].strip():
            raise ValueError(get_text("error_risk_name_empty"))
        
        if not validate_impact_value(form_data['impacto_numerico_slider']):
            raise ValueError(get_text("error_invalid_impact_value"))
        
        # Cálculos
        probabilidad_val = get_factor_value(factor_probabilidad, form_data['selected_probabilidad'])
        exposicion_val = get_factor_value(factor_exposicion, form_data['selected_exposicion'])
        ponderacion_impacto_val = get_factor_value(tabla_tipo_impacto, form_data['selected_type_impact'], 'Ponderación')
        
        resultados = calcular_criticidad(
            probabilidad_val, exposicion_val,
            form_data['deliberate_threat_level_selectbox'],
            form_data['control_effectiveness_slider'],
            form_data['impacto_numerico_slider'],
            ponderacion_impacto_val,
            form_data['deliberate_threat_present_checkbox']
        )
        
        clasificacion, color = clasificar_criticidad(resultados[3], st.session_state.get('idioma', 'es'))
        
        # Crear registro
        new_risk = {
            "ID": st.session_state.current_edit_index if st.session_state.current_edit_index != -1 
                  else (st.session_state.riesgos['ID'].max() + 1 if not st.session_state.riesgos.empty else 1),
            "Nombre del Riesgo": form_data['risk_name_input'],
            "Descripción": form_data['risk_description_input'],
            "Tipo de Impacto": form_data['selected_type_impact'],
            "Probabilidad": form_data['selected_probabilidad'],
            "Exposición": form_data['selected_exposicion'],
            "Impacto Numérico": form_data['impacto_numerico_slider'],
            "Efectividad del Control (%)": form_data['control_effectiveness_slider'],
            "Amenaza Deliberada (Checkbox)": form_data['deliberate_threat_present_checkbox'],
            "Nivel Amenaza Deliberada": form_data['deliberate_threat_level_selectbox'],
            "Amenaza Inherente": resultados[0],
            "Amenaza Residual": resultados[1],
            "Amenaza Residual Ajustada": resultados[2],
            "Riesgo Residual": resultados[3],
            "Clasificación": clasificacion,
            "Color": color
        }
        
        # Actualizar DataFrame
        if st.session_state.current_edit_index != -1:
            idx = st.session_state.riesgos[st.session_state.riesgos['ID'] == st.session_state.current_edit_index].index[0]
            st.session_state.riesgos.loc[idx] = new_risk
        else:
            st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([new_risk])], ignore_index=True)
        
        st.success(get_text("success_risk_added"))
        st.session_state.current_edit_index = -1
        logger.info(f"Riesgo {'editado' if st.session_state.current_edit_index != -1 else 'agregado'}: {form_data['risk_name_input']}")
        
    except Exception as e:
        log_error(logger, e, "Error en handle_form_submit")
        st.error(f"{get_text('error_processing_risk')}: {str(e)}")

# ======================
# 4. COMPONENTES DE UI
# ======================
def render_language_selector():
    """Selector de idioma"""
    st.sidebar.header(get_text("language_select"))
    language_options = {'es': 'Español', 'en': 'English'}
    selected_language = st.sidebar.selectbox(
        label="",
        options=list(language_options.keys()),
        format_func=lambda x: language_options[x],
        key="language_selector"
    )
    if selected_language != st.session_state.get('idioma', 'es'):
        st.session_state.idioma = selected_language
        st.rerun()

def render_risk_form():
    """Formulario de ingreso de riesgos"""
    with st.form("risk_form", clear_on_submit=True):
        st.header(get_text("risk_form_title"))
        
        if st.session_state.current_edit_index != -1:
            risk_data = load_risk_for_edit(st.session_state.current_edit_index, st.session_state.riesgos)
            if risk_data:
                for key in st.session_state.form_fields:
                    if key in risk_data:
                        st.session_state.form_fields[key] = risk_data[key]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input(
                label=get_text("risk_name"),
                key="form_fields.risk_name_input",
                max_chars=100
            )
            
            st.selectbox(
                label=get_text("risk_type_impact"),
                options=tabla_tipo_impacto['Tipo de Impacto'].tolist(),
                key="form_fields.selected_type_impact"
            )
            
            st.selectbox(
                label=get_text("probability"),
                options=factor_probabilidad['Clasificacion'].tolist(),
                key="form_fields.selected_probabilidad"
            )
            
        with col2:
            st.text_area(
                label=get_text("risk_description"),
                height=100,
                key="form_fields.risk_description_input",
                max_chars=500
            )
            
            st.slider(
                label=get_text("impact_level"),
                min_value=0,
                max_value=100,
                value=50,
                key="form_fields.impacto_numerico_slider"
            )
            
            st.slider(
                label=get_text("control_effectiveness"),
                min_value=0,
                max_value=100,
                value=50,
                key="form_fields.control_effectiveness_slider"
            )
        
        with st.expander(get_text("deliberate_threat_section_title")):
            st.checkbox(
                label=get_text("deliberate_threat_checkbox"),
                key="form_fields.deliberate_threat_present_checkbox"
            )
            
            if st.session_state.form_fields['deliberate_threat_present_checkbox']:
                st.selectbox(
                    label=get_text("deliberate_threat_level"),
                    options=factores_amenaza_deliberada['Clasificacion'].tolist(),
                    key="form_fields.deliberate_threat_level_selectbox"
                )
        
        submitted = st.form_submit_button(
            label=get_text("add_risk_button"),
            on_click=handle_form_submit
        )

# ======================
# 5. VISTAS PRINCIPALES
# ======================
def render_risk_matrix():
    """Muestra la matriz de riesgos"""
    st.header(get_text("risk_matrix_title"))
    
    if not st.session_state.riesgos.empty:
        # Aplicar estilo según criticidad
        def color_row(row):
            color = row['Color']
            return [f'background-color: {color}'] * len(row)
        
        st.dataframe(
            st.session_state.riesgos.style.apply(color_row, axis=1),
            use_container_width=True,
            height=400
        )
        
        # Botones de acción
        col1, col2, _ = st.columns([1,1,3])
        with col1:
            if st.button(get_text("export_risks")):
                export_risks()
        with col2:
            if st.button(get_text("clear_risks")):
                clear_risks()
    else:
        st.info(get_text("no_risks_added"))

def render_monte_carlo_section():
    """Sección de simulación Monte Carlo"""
    st.header(get_text("monte_carlo_simulation_title"))
    
    if st.session_state.riesgos.empty:
        st.info(get_text("add_risks_for_montecarlo"))
        return
    
    selected_risk = st.selectbox(
        label=get_text("select_risk_for_mc"),
        options=st.session_state.riesgos["Nombre del Riesgo"].tolist()
    )
    
    if selected_risk:
        risk_data = st.session_state.riesgos[st.session_state.riesgos["Nombre del Riesgo"] == selected_risk].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            iterations = st.slider("Iteraciones", 1000, 50000, 10000)
        with col2:
            variability = st.slider("Variabilidad", 0.05, 0.3, 0.15)
        
        if st.button("Ejecutar Simulación"):
            with st.spinner("Simulando..."):
                results = simular_montecarlo(
                    risk_data["Riesgo Residual"],
                    iterations,
                    variability,
                    variability
                )
                
                st.subheader("Resultados")
                st.metric("Riesgo Promedio", f"{results['mean']:.4f}")
                
                tab1, tab2 = st.tabs(["Histograma", "Sensibilidad"])
                with tab1:
                    plot_montecarlo_histogram(results['data'], "Distribución de Riesgo")
                with tab2:
                    sensitivity = {
                        "Probabilidad": risk_data["Probabilidad"],
                        "Exposición": risk_data["Exposición"],
                        "Impacto": risk_data["Impacto Numérico"],
                        "Controles": risk_data["Efectividad del Control (%)"]
                    }
                    create_sensitivity_plot(sensitivity, "Análisis de Sensibilidad")

# ======================
# 6. FUNCIÓN PRINCIPAL
# ======================
def main():
    setup_page_config()
    initialize_session_state()
    render_language_selector()
    
    st.title(get_text("app_title"))
    
    tab1, tab2, tab3 = st.tabs([
        get_text("risk_register"),
        get_text("risk_matrix"),
        get_text("simulation")
    ])
    
    with tab1:
        render_risk_form()
    
    with tab2:
        render_risk_matrix()
    
    with tab3:
        render_monte_carlo_section()

if __name__ == "__main__":
    main()
