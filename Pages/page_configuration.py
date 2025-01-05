import streamlit as st
from models import TypeIsolant

def Page_configuration():
    st.title("Configuration")
    
    # Section Modèles de mur
    st.header("Modèles de mur")
    if st.button("Gérer les modèles de mur"):
        st.session_state.page = "Modèles de mur"
        st.rerun()
        
    # Section Instances de mur
    st.header("Instances de mur")
    if st.button("Gérer les instances de mur"):
        st.session_state.page = "Instances de mur"
        st.rerun()
        
    # Section Paramètres globaux
    st.header("Paramètres globaux")
    with st.expander("Types d'isolant"):
        st.write("Types d'isolant disponibles:")
        for isolant in TypeIsolant:
            st.write(f"- {isolant.value}")
