import streamlit as st
from bdd.database import DatabaseManager
from Pages._page_projets_afficher import Page_projets_afficher
from Pages._page_projet_details import Page_projet_details
from Pages._page_plan_production import Page_plan_production
from Pages._page_configuration import Page_configuration
import base64

st.set_page_config(
    page_title="Gestionnaire OB2",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={}, 
)

def main():
    # Initialisation des états
    if 'db' not in st.session_state:
        st.session_state.db = DatabaseManager()
        st.session_state.projets = []
        st.session_state.page = 'projets'
    
    # Utilisation de charger_tous_projets au lieu de charger_projets
    st.session_state.projets = st.session_state.db.charger_tous_projets()
    
    # Logo et en-tête
    file_ = open("assets/ob2-logo.png", "rb")
    contents = file_.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    file_.close()
    
    st.markdown(f"""
        <div style="background-color: #1D252C; padding: 1rem; margin-bottom: 0; display: flex; align-items: center; gap: 1rem;">
            <img src="data:image/png;base64,{data_url}" style="width: 80px; height: auto;">
            <h1 style="color: white; margin: 0; font-size: 2rem;">Gestionnaire OB2</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Navigation principale avec gestion de l'URL
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("Projets", key="nav_projets_main", use_container_width=True):
            st.session_state.page = 'projets'
            if 'projet_details' in st.session_state:
                del st.session_state.projet_details
            st.query_params['page'] = 'projets'
            st.rerun()
    with col2:
        if st.button("Plan de production", key="nav_production_main", use_container_width=True):
            st.session_state.page = 'production'
            st.query_params['page'] = 'production'
            st.rerun()
    with col3:
        if st.button("Configuration", key="nav_config_main", use_container_width=True):
            st.session_state.page = 'configuration'
            st.query_params['page'] = 'configuration'
            st.rerun()

    # Récupération du paramètre de l'URL
    page_param = st.query_params.get('page')
    if page_param:
        st.session_state.page = page_param

    # Affichage de la page sélectionnée
    if hasattr(st.session_state, 'projet_details'):
        st.query_params['page'] = 'projets'
        st.query_params['projet'] = str(st.session_state.projet_details)
        Page_projet_details()
    elif st.session_state.page == "projets":
        st.query_params['page'] = 'projets'
        if 'projet' in st.query_params:
            del st.query_params['projet']
        Page_projets_afficher()
    elif st.session_state.page == "production":
        st.query_params['page'] = 'production'
        Page_plan_production()
    elif st.session_state.page == "configuration":
        st.query_params['page'] = 'configuration'
        Page_configuration()

if __name__ == "__main__":
    main()