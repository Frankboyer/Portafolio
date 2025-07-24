# utils.py

import streamlit as st
import pandas as pd # Asegúrate de importar pandas

def reset_form_fields():
    """Resetea los campos del formulario de entrada de riesgo."""
    st.session_state['risk_name_input'] = ""
    st.session_state['risk_description_input'] = ""
    # Puedes obtener los valores por defecto de data_config si los necesitas
    # o simplemente resetear a los primeros elementos de las listas
    st.session_state['selected_type_impact'] = pd.DataFrame({'Tipo de Impacto':['Financiero']})['Tipo de Impacto'].iloc[0] # Ejemplo, ajusta con tu data_config real
    st.session_state['selected_probabilidad'] = pd.DataFrame({'Clasificacion':['Muy Bajo']})['Clasificacion'].iloc[0] # Ejemplo
    st.session_state['selected_exposicion'] = pd.DataFrame({'Clasificacion':['Diaria']})['Clasificacion'].iloc[0] # Ejemplo
    st.session_state['impacto_numerico_slider'] = 50
    st.session_state['control_effectiveness_slider'] = 50
    st.session_state['deliberate_threat_present_checkbox'] = False # Resetea el checkbox
    st.session_state['deliberate_threat_level_selectbox'] = pd.DataFrame({'Clasificacion':['No']})['Clasificacion'].iloc[0] # Resetea el selectbox a 'No'
    st.session_state.current_edit_index = -1

# ... (resto de tus funciones en utils.py) ...
# Asegúrate de que color_clasificacion incluya 'critico'/'critical' como te comenté antes:
def color_clasificacion(val):
    if isinstance(val, str):
        val_lower = val.lower()
        if val_lower in ['bajo', 'low']:
            return 'background-color: #d4edda' # Verde claro
        elif val_lower in ['medio', 'medium']:
            return 'background-color: #ffc107' # Amarillo
        elif val_lower in ['alto', 'high']:
            return 'background-color: #fd7e14; color: white' # Naranja
        elif val_lower in ['crítico', 'critical']: # ¡Añadido!
            return 'background-color: #dc3545; color: white' # Rojo
    return '' # Default
