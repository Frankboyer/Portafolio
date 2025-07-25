# modules/profile_manager.py
"""
Módulo para gestionar perfiles de riesgo personalizados: carga, guardado,
creación, edición y eliminación, interactuando con el estado de sesión y archivos JSON.
"""
import streamlit as st
import pandas as pd
import json
import os
from modules.data_config import PERFILES_BASE # Importar perfiles base

# --- Rutas de Archivos y Constantes ---
PROFILE_FILE = "user_profiles.json"

# --- Funciones de Gestión de Perfiles ---

def load_profiles():
    """Carga perfiles de un archivo JSON o devuelve los perfiles base si no existe."""
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                if "perfiles_usuario" in loaded_data and isinstance(loaded_data["perfiles_usuario"], dict):
                    return loaded_data["perfiles_usuario"]
                else:
                    st.warning("Archivo de perfiles inválido. Usando perfiles base.")
                    return PERFILES_BASE.copy()
        except json.JSONDecodeError:
            st.warning("Error al decodificar el archivo de perfiles. Usando perfiles base.")
            return PERFILES_BASE.copy()
        except Exception as e:
            st.warning(f"Error al leer el archivo de perfiles: {e}. Usando perfiles base.")
            return PERFILES_BASE.copy()
    else:
        return PERFILES_BASE.copy()

def save_profiles(profiles_data):
    """Guarda los perfiles en un archivo JSON."""
    try:
        with open(PROFILE_FILE, 'w', encoding='utf-8') as f:
            json.dump({"perfiles_usuario": profiles_data}, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error al guardar perfiles: {e}")
        return False

def get_profile_data(profile_name):
    """Devuelve los datos de un perfil específico del almacenamiento (session_state)."""
    return st.session_state.perfiles_usuario.get(profile_name)

def delete_profile(profile_name):
    """Elimina un perfil del estado y del archivo (si no es base)."""
    if profile_name in st.session_state.perfiles_usuario and profile_name not in PERFILES_BASE:
        del st.session_state.perfiles_usuario[profile_name]
        save_profiles(st.session_state.perfiles_usuario)
        return True
    return False

def update_profile(profile_name, new_data):
    """Actualiza un perfil existente en el estado y lo guarda."""
    if profile_name in st.session_state.perfiles_usuario:
        st.session_state.perfiles_usuario[profile_name] = new_data
        save_profiles(st.session_state.perfiles_usuario)
        return True
    return False

def add_profile(profile_name, profile_data):
    """Agrega un nuevo perfil al estado si no existe y lo guarda."""
    if profile_name in st.session_state.perfiles_usuario:
        return False # Ya existe
    st.session_state.perfiles_usuario[profile_name] = profile_data
    save_profiles(st.session_state.perfiles_usuario)
    return True
