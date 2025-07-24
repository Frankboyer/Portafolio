import streamlit as st
import pandas as pd
import numpy as np

# Importar desde los módulos locales
from data_config import tabla_tipo_impacto, matriz_probabilidad, matriz_impacto, factor_exposicion, factor_probabilidad, efectividad_controles, criticidad_límites, textos, factores_amenaza_deliberada
from calculations import clasificar_criticidad, calcular_criticidad, simular_montecarlo
from plotting import create_heatmap, create_pareto_chart, plot_montecarlo_histogram, create_sensitivity_plot
from utils import reset_form_fields, format_risk_dataframe

# --- Configuración de la página ---
st.set_page_config(layout="wide", page_title="Calculadora de Riesgos", page_icon="🛡️")

# --- CSS Personalizado ---
st.markdown("""
<style>
    /* Estilos generales */
    .reportview-container {
        background: #f0f2f6;
        color: #333;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #004d99;
    }
    .stButton>button {
        background-color: #007bff;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #0056b3;
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>select {
        border-radius: 5px;
        border: 1px solid #ced4da;
        padding: 8px 12px;
    }
    /* Contenedores de métricas */
    .stMetric {
        background-color: #e9ecef;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #007bff;
        margin-bottom: 10px;
    }
    .stMetric label {
        color: #004d99;
        font-weight: bold;
    }
    /* Estilos para tablas de Streamlit (dataframe) */
    .stDataFrame {
        font-size: 0.9em;
    }
    /* Info/Warning/Error boxes */
    .stAlert {
        border-radius: 8px;
    }
    /* Custom styles for Streamlit columns to add spacing */
    .st-emotion-cache-1jm6hrp { /* This targets the column div directly */
        padding-right: 1rem;
        padding-left: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# --- Inicialización de Session State ---
if 'idioma' not in st.session_state:
    st.session_state.idioma = 'es'
if 'riesgos' not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "ID", "Nombre del Riesgo", "Descripción", "Tipo de Impacto",
        "Probabilidad", "Exposición", "Impacto Numérico",
        "Efectividad del Control (%)", "Amenaza Deliberada (Checkbox)", "Nivel Amenaza Deliberada",
        "Amenaza Inherente", "Amenaza Residual", "Amenaza Residual Ajustada",
        "Riesgo Residual", "Clasificación", "Color"
    ])
if 'current_edit_index' not in st.session_state:
    st.session_state.current_edit_index = -1 # -1 significa que no estamos editando

# --- Inicializaciones Cruciales para Campos del Formulario ---
# Estos valores predeterminados aseguran que los widgets tengan un valor inicial
# y se adapten a los datos configurados.

# Función para obtener el primer valor seguro de un DataFrame
def get_first_value(df, column):
    return df[column].iloc[0] if not df.empty else ""

if 'default_type_impact' not in st.session_state:
    st.session_state['default_type_impact'] = get_first_value(tabla_tipo_impacto, 'Tipo de Impacto')
if 'default_probabilidad' not in st.session_state:
    st.session_state['default_probabilidad'] = get_first_value(factor_probabilidad, 'Clasificacion')
if 'default_exposicion' not in st.session_state:
    st.session_state['default_exposicion'] = get_first_value(factor_exposicion, 'Clasificacion')
if 'default_amenaza_deliberada' not in st.session_state:
    st.session_state['default_amenaza_deliberada'] = get_first_value(factores_amenaza_deliberada, 'Clasificacion')

if 'default_impacto_numerico' not in st.session_state:
    st.session_state['default_impacto_numerico'] = 50
if 'default_control_effectiveness' not in st.session_state:
    st.session_state['default_control_effectiveness'] = 50

# Claves reales de widgets para asegurar persistencia
# Solo inicializar si no están ya en session_state (e.g. después de un rerun causado por un botón)
if 'risk_name_input' not in st.session_state:
    st.session_state['risk_name_input'] = ""
if 'risk_description_input' not in st.session_state:
    st.session_state['risk_description_input'] = ""
if 'selected_type_impact' not in st.session_state:
    st.session_state['selected_type_impact'] = st.session_state['default_type_impact']
if 'selected_probabilidad' not in st.session_state:
    st.session_state['selected_probabilidad'] = st.session_state['default_probabilidad']
if 'selected_exposicion' not in st.session_state:
    st.session_state['selected_exposicion'] = st.session_state['default_exposicion']
if 'impacto_numerico_slider' not in st.session_state:
    st.session_state['impacto_numerico_slider'] = st.session_state['default_impacto_numerico']
if 'control_effectiveness_slider' not in st.session_state:
    st.session_state['control_effectiveness_slider'] = st.session_state['default_control_effectiveness']
if 'deliberate_threat_present_checkbox' not in st.session_state:
    st.session_state['deliberate_threat_present_checkbox'] = False
if 'deliberate_threat_level_selectbox' not in st.session_state:
    st.session_state['deliberate_threat_level_selectbox'] = st.session_state['default_amenaza_deliberada']


# --- Función para obtener textos ---
def get_text(key):
    return textos[st.session_state.idioma].get(key, key)

# --- Callback para enviar formulario ---
def handle_form_submit():
    nombre_riesgo = st.session_state['risk_name_input']
    descripcion_riesgo = st.session_state['risk_description_input']
    tipo_impacto = st.session_state['selected_type_impact']
    probabilidad_str = st.session_state['selected_probabilidad']
    exposicion_str = st.session_state['selected_exposicion']
    impacto_numerico = st.session_state['impacto_numerico_slider']
    efectividad_control = st.session_state['control_effectiveness_slider']

    # Nuevos inputs de amenaza deliberada
    es_amenaza_deliberada_checkbox = st.session_state['deliberate_threat_present_checkbox']
    nivel_amenaza_deliberada_str = st.session_state['deliberate_threat_level_selectbox']

    if not nombre_riesgo:
        st.error(get_text("error_risk_name_empty"))
        return
    else:
        # Asegurarse de que los DataFrames no estén vacíos antes de acceder a .iloc[0]
        probabilidad_val = factor_probabilidad[factor_probabilidad['Clasificacion'] == probabilidad_str]['Factor'].iloc[0] if not factor_probabilidad.empty else 0.0
        exposicion_val = factor_exposicion[factor_exposicion['Clasificacion'] == exposicion_str]['Factor'].iloc[0] if not factor_exposicion.empty else 0.0
        ponderacion_impacto_val = tabla_tipo_impacto[tabla_tipo_impacto['Tipo de Impacto'] == tipo_impacto]['Ponderación'].iloc[0] if not tabla_tipo_impacto.empty else 0.0

        amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual_val = calcular_criticidad(
            probabilidad_val,
            exposicion_val,
            nivel_amenaza_deliberada_str,
            efectividad_control,
            impacto_numerico,
            ponderacion_impacto_val,
            es_amenaza_deliberada_checkbox
        )

        clasificacion, color = clasificar_criticidad(riesgo_residual_val, st.session_state.idioma)

        new_risk_data = {
            "ID": st.session_state.current_edit_index if st.session_state.current_edit_index != -1 else (st.session_state.riesgos['ID'].max() + 1 if not st.session_state.riesgos.empty else 1),
            "Nombre del Riesgo": nombre_riesgo,
            "Descripción": descripcion_riesgo,
            "Tipo de Impacto": tipo_impacto,
            "Probabilidad": probabilidad_val,
            "Exposición": exposicion_val,
            "Impacto Numérico": impacto_numerico,
            "Efectividad del Control (%)": efectividad_control,
            "Amenaza Deliberada (Checkbox)": es_amenaza_deliberada_checkbox,
            "Nivel Amenaza Deliberada": nivel_amenaza_deliberada_str,
            "Amenaza Inherente": amenaza_inherente,
            "Amenaza Residual": amenaza_residual,
            "Amenaza Residual Ajustada": amenaza_residual_ajustada,
            "Riesgo Residual": riesgo_residual_val,
            "Clasificación": clasificacion,
            "Color": color
        }

        if st.session_state.current_edit_index != -1:
            # Encuentra el ID real del riesgo para actualizar
            idx_to_update = st.session_state.riesgos[st.session_state.riesgos['ID'] == st.session_state.current_edit_index].index
            if not idx_to_update.empty:
                st.session_state.riesgos.loc[idx_to_update[0]] = new_risk_data
                st.success(f"Riesgo '{nombre_riesgo}' actualizado exitosamente.")
            else:
                st.error("Error al encontrar el riesgo para actualizar. Añadiendo como nuevo.")
                st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([new_risk_data])], ignore_index=True)
        else:
            st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([new_risk_data])], ignore_index=True)
            st.success(get_text("success_risk_added"))

        st.session_state.current_edit_index = -1 # Salir del modo edición
        reset_form_fields() # Resetear los campos del formulario
        st.experimental_rerun() # Recargar la app para mostrar los cambios


# --- Sidebar ---
with st.sidebar:
    st.header(get_text("language_select"))
    language_options = {'es': 'Español', 'en': 'English'}
    selected_language = st.selectbox("Choose Language", options=list(language_options.keys()), format_func=lambda x: language_options[x], key="language_selector")
    if selected_language != st.session_state.idioma:
        st.session_state.idioma = selected_language
        st.experimental_rerun() # Recargar la página para cambiar el idioma

    st.markdown("---")
    st.header(get_text("matrix_title"))

    # --- Matriz de Probabilidad ---
    st.subheader(get_text("matrix_prob_col"))
    if not matriz_probabilidad.empty:
        df_prob_display = matriz_probabilidad[['Clasificacion', 'Factor', 'Justificacion']].rename(
            columns={'Clasificacion': get_text("matrix_prob_col"), 'Factor': get_text("matrix_factor_col"), 'Justificacion': get_text("matrix_justification_col")}
        )
        st.dataframe(df_prob_display, hide_row_index=True)
    else:
        st.info("La matriz de probabilidad no está disponible.")

    # --- Ponderaciones de Tipo de Impacto ---
    st.subheader(get_text("matrix_impact_type_title"))
    if not tabla_tipo_impacto.empty:
        df_impact_type_display = tabla_tipo_impacto[['Tipo de Impacto', 'Ponderación', 'Justificación Técnica']].rename(
            columns={'Tipo de Impacto': get_text("risk_type_impact"), 'Ponderación': get_text("matrix_factor_col"), 'Justificación Técnica': get_text("matrix_justification_col")}
        )
        st.dataframe(df_impact_type_display, hide_row_index=True)
    else:
        st.info("La tabla de tipos de impacto no está disponible.")

    # --- Factores de Exposición ---
    st.subheader(get_text("matrix_exposure_title"))
    if not factor_exposicion.empty:
        df_exposure_display = factor_exposicion[['Clasificacion', 'Factor']].rename(
            columns={'Clasificacion': get_text("matrix_exposure_title"), 'Factor': get_text("matrix_factor_col")}
        )
        st.dataframe(df_exposure_display, hide_row_index=True)
    else:
        st.info("La tabla de factores de exposición no está disponible.")

    # --- Factores de Amenaza Deliberada ---
    st.subheader(get_text("matrix_threat_title"))
    if not factores_amenaza_deliberada.empty:
        df_threat_display = factores_amenaza_deliberada[['Clasificacion', 'Factor']].rename(
            columns={'Clasificacion': get_text("matrix_threat_title"), 'Factor': get_text("matrix_factor_col")}
        )
        st.dataframe(df_threat_display, hide_row_index=True)
    else:
        st.info("La tabla de factores de amenaza deliberada no está disponible.")

    # --- Factores de Efectividad de Control ---
    st.subheader(get_text("matrix_control_title"))
    if not efectividad_controles.empty:
        df_control_display = efectividad_controles[['Clasificacion', 'Factor']].rename(
            columns={'Clasificacion': get_text("matrix_control_title"), 'Factor': get_text("matrix_factor_col")}
        )
        st.dataframe(df_control_display, hide_row_index=True)
    else:
        st.info("La tabla de efectividad de controles no está disponible.")


# --- Título ---
st.title(get_text("app_title"))

# --- Formulario de entrada ---
st.header(get_text("risk_input_form_title"))
with st.form("risk_form", clear_on_submit=False):
    # Lógica de carga para edición
    if st.session_state.current_edit_index != -1:
        # Asegurarse de que el índice exista en el DataFrame
        risk_to_edit_df = st.session_state.riesgos[st.session_state.riesgos['ID'] == st.session_state.current_edit_index]
        if not risk_to_edit_df.empty:
            risk_to_edit = risk_to_edit_df.iloc[0]
            st.session_state['risk_name_input'] = risk_to_edit["Nombre del Riesgo"]
            st.session_state['risk_description_input'] = risk_to_edit["Descripción"]
            
            # Asegúrate de que los valores para selectbox existan en las opciones
            st.session_state['selected_type_impact'] = risk_to_edit["Tipo de Impacto"] if risk_to_edit["Tipo de Impacto"] in tabla_tipo_impacto['Tipo de Impacto'].tolist() else st.session_state['default_type_impact']
            
            # Para Probabilidad y Exposición, traducir de factor a clasificación para el selectbox
            prob_class_edit = factor_probabilidad[factor_probabilidad['Factor'] == risk_to_edit["Probabilidad"]]['Clasificacion'].iloc[0] if not factor_probabilidad[factor_probabilidad['Factor'] == risk_to_edit["Probabilidad"]].empty else st.session_state['default_probabilidad']
            st.session_state['selected_probabilidad'] = prob_class_edit

            exp_class_edit = factor_exposicion[factor_exposicion['Factor'] == risk_to_edit["Exposición"]]['Clasificacion'].iloc[0] if not factor_exposicion[factor_exposicion['Factor'] == risk_to_edit["Exposición"]].empty else st.session_state['default_exposicion']
            st.session_state['selected_exposicion'] = exp_class_edit

            st.session_state['impacto_numerico_slider'] = int(risk_to_edit["Impacto Numérico"])
            st.session_state['control_effectiveness_slider'] = int(risk_to_edit["Efectividad del Control (%)"])
            st.session_state['deliberate_threat_present_checkbox'] = risk_to_edit["Amenaza Deliberada (Checkbox)"]
            
            delib_threat_level_edit = risk_to_edit["Nivel Amenaza Deliberada"] if risk_to_edit["Nivel Amenaza Deliberada"] in factores_amenaza_deliberada['Clasificacion'].tolist() else st.session_state['default_amenaza_deliberada']
            st.session_state['deliberate_threat_level_selectbox'] = delib_threat_level_edit

            st.write(f"**{get_text('editing_risk')}**: {risk_to_edit['Nombre del Riesgo']}")
            st.info(get_text('edit_in_form'))
        else:
            st.session_state.current_edit_index = -1 # Reset si el riesgo a editar no se encuentra

    col1, col2 = st.columns(2)
    with col1:
        st.text_input(get_text("risk_name"), key="risk_name_input")
        st.selectbox(
            get_text("risk_type_impact"),
            tabla_tipo_impacto['Tipo de Impacto'].tolist(),
            key="selected_type_impact",
            index=tabla_tipo_impacto['Tipo de Impacto'].tolist().index(st.session_state['selected_type_impact']) if st.session_state['selected_type_impact'] in tabla_tipo_impacto['Tipo de Impacto'].tolist() else 0
        )
        st.selectbox(
            get_text("risk_probability"),
            factor_probabilidad['Clasificacion'].tolist(),
            key="selected_probabilidad",
            index=factor_probabilidad['Clasificacion'].tolist().index(st.session_state['selected_probabilidad']) if st.session_state['selected_probabilidad'] in factor_probabilidad['Clasificacion'].tolist() else 0
        )
        st.selectbox(
            get_text("risk_exposure"),
            factor_exposicion['Clasificacion'].tolist(),
            key="selected_exposicion",
            index=factor_exposicion['Clasificacion'].tolist().index(st.session_state['selected_exposicion']) if st.session_state['selected_exposicion'] in factor_exposicion['Clasificacion'].tolist() else 0
        )
    with col2:
        st.text_area(get_text("risk_description"), height=100, key="risk_description_input")
        st.slider(get_text("risk_impact_numeric"), 0, 100, value=st.session_state['impacto_numerico_slider'], key="impacto_numerico_slider")
        st.slider(get_text("risk_control_effectiveness"), 0, 100, value=st.session_state['control_effectiveness_slider'], key="control_effectiveness_slider")

        st.checkbox(get_text("risk_deliberate_threat_present"), key="deliberate_threat_present_checkbox")
        
        deliberate_threat_level_options = factores_amenaza_deliberada['Clasificacion'].tolist()
        
        # Asegurarse de que el valor inicial sea válido para el selectbox
        current_level_index = deliberate_threat_level_options.index(st.session_state['deliberate_threat_level_selectbox']) if st.session_state['deliberate_threat_level_selectbox'] in deliberate_threat_level_options else 0

        if st.session_state['deliberate_threat_present_checkbox']:
            st.selectbox(
                get_text("risk_deliberate_threat_level"),
                deliberate_threat_level_options,
                index=current_level_index,
                key="deliberate_threat_level_selectbox"
            )
        else:
            # Si el checkbox no está marcado, forzamos el selectbox a 'No' y lo deshabilitamos
            # Asegurarse de que 'No' sea una opción válida antes de intentar acceder a su índice
            no_index = deliberate_threat_level_options.index('No') if 'No' in deliberate_threat_level_options else 0
            st.session_state['deliberate_threat_level_selectbox'] = 'No' # Asegura que el valor sea 'No'
            st.selectbox(
                get_text("risk_deliberate_threat_level"),
                deliberate_threat_level_options,
                index=no_index,
                key="deliberate_threat_level_selectbox",
                disabled=True # Deshabilita el selectbox
            )

    submitted = st.form_submit_button(get_text("add_risk_button"))
    if submitted:
        handle_form_submit()


# --- Visualización de riesgos ---
st.markdown("---")
st.header(get_text("risk_table_title"))
if st.session_state.riesgos.empty:
    st.info(get_text("no_risks_added"))
else:
    # Asegúrate de que los IDs sean únicos y se puedan usar como clave
    if 'ID' not in st.session_state.riesgos.columns:
        st.session_state.riesgos['ID'] = range(1, len(st.session_state.riesgos) + 1)
    
    # Ordenar por ID para consistencia, o por Riesgo Residual
    df_display = st.session_state.riesgos.sort_values(by="Riesgo Residual", ascending=False).reset_index(drop=True)

    # Formatear el DataFrame para visualización
    styled_df = format_risk_dataframe(df_display)
    st.dataframe(styled_df, use_container_width=True, hide_row_index=True)

    # Botones de Editar y Eliminar para cada riesgo
    st.markdown("<br>", unsafe_allow_html=True) # Espaciado
    for i, row in df_display.iterrows():
        unique_id = row['ID']
        cols_buttons = st.columns([1, 1, 4]) # Dos columnas para botones, una para espacio
        with cols_buttons[0]:
            if st.button(get_text("edit_button"), key=f"edit_{unique_id}"):
                st.session_state.current_edit_index = unique_id
                st.experimental_rerun()
        with cols_buttons[1]:
            # Lógica de confirmación de eliminación
            if st.session_state.get(f'confirm_delete_{unique_id}', False):
                st.warning(f"{get_text('confirm_delete')} '{row['Nombre del Riesgo']}'?")
                col_confirm_yes, col_confirm_no = st.columns(2)
                with col_confirm_yes:
                    if st.button("Sí", key=f"confirm_yes_{unique_id}"):
                        st.session_state.riesgos = st.session_state.riesgos[st.session_state.riesgos['ID'] != unique_id].reset_index(drop=True)
                        st.session_state[f'confirm_delete_{unique_id}'] = False
                        st.success(f"Riesgo '{row['Nombre del Riesgo']}' eliminado.")
                        st.experimental_rerun()
                with col_confirm_no:
                    if st.button("No", key=
