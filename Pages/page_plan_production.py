import streamlit as st
from models import Statut, StatutProjet

def Page_plan_production():
    st.markdown("""
        <style>
            /* Style pour le conteneur Kanban */
            .kanban-container {
                padding: 1rem;
                background-color: #f3f4f6;
                margin: 1rem 0;
                border-radius: 8px;
            }
            
            /* Style pour les colonnes Kanban */
            .kanban-column {
                background-color: #f8f9fa;
                padding: 1rem;
                border-radius: 4px;
            }
            
            /* Style pour les cartes Kanban */
            .kanban-card {
                background-color: white;
                padding: 1rem;
                margin: 0.5rem 0;
                border-radius: 4px;
                border-left: 4px solid #1D252C;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            
            /* Style pour le header du projet */
            .project-header {
                background-color: #1D252C;
                color: white;
                padding: 1rem;
                margin: 2rem 0 1rem 0;
                border-radius: 4px;
            }
            
            /* Ajuster les colonnes Streamlit */
            [data-testid="column"] {
                background-color: #f8f9fa;
                padding: 1rem !important;
                border-radius: 4px;
                margin: 0 0.5rem !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    if not hasattr(st.session_state, 'projets'):
        st.session_state.projets = st.session_state.db.charger_projets()
    
    # Filtrer uniquement les projets en fabrication
    projets_en_fabrication = [p for p in st.session_state.projets 
                             if p.statut == StatutProjet.EN_FABRICATION]
    
    if not projets_en_fabrication:
        st.info("Aucun projet en fabrication actuellement.")
        return
    
    # Titre de la page avec compteurs
    st.title("Plan de Production")
    
    # Pour chaque projet en fabrication
    for projet in projets_en_fabrication:
        # Afficher le header du projet avec style
        st.markdown(f"""
            <div class="project-header">
                <h2>Projet {projet.nom}</h2>
            </div>
        """, unsafe_allow_html=True)
        
        # Créer les colonnes pour le Kanban
        col1, col2, col3 = st.columns(3)
        
        # Colonne "À produire"
        with col1:
            st.markdown("""
                <div style="background-color: #f7d5d5; padding: 0.5rem; border-radius: 4px; margin-bottom: 0.5rem;">
                    <h3 style="margin: 0; color: #991b1b; text-align: center;">À produire</h3>
                </div>
            """, unsafe_allow_html=True)
            
            instances_a_produire = [i for i in projet.instances_mur if i.statut == Statut.EN_COURS]
            for instance in sorted(instances_a_produire, key=lambda x: x.numero):
                st.markdown(f"""
                    <div class="kanban-card">
                        <strong>Mur n°{instance.numero}</strong><br>
                        Modèle: {instance.modele.reference}<br>
                        Dimensions: {instance.modele.longueur}×{instance.modele.hauteur}cm
                    </div>
                """, unsafe_allow_html=True)
        
        # Colonne "En production"
        with col2:
            st.markdown("""
                <div style="background-color: #fef3c7; padding: 0.5rem; border-radius: 4px; margin-bottom: 0.5rem;">
                    <h3 style="margin: 0; color: #92400e; text-align: center;">En production</h3>
                </div>
            """, unsafe_allow_html=True)
            
            instances_en_prod = [i for i in projet.instances_mur if i.statut == Statut.VALIDE]
            for instance in sorted(instances_en_prod, key=lambda x: x.numero):
                st.markdown(f"""
                    <div class="kanban-card">
                        <strong>Mur n°{instance.numero}</strong><br>
                        Modèle: {instance.modele.reference}<br>
                        Dimensions: {instance.modele.longueur}×{instance.modele.hauteur}cm
                    </div>
                """, unsafe_allow_html=True)
        
        # Colonne "Terminé"
        with col3:
            st.markdown("""
                <div style="background-color: #d1fae5; padding: 0.5rem; border-radius: 4px; margin-bottom: 0.5rem;">
                    <h3 style="margin: 0; color: #065f46; text-align: center;">Terminé</h3>
                </div>
            """, unsafe_allow_html=True)
            
            instances_terminees = [i for i in projet.instances_mur if i.statut == Statut.TERMINE]
            for instance in sorted(instances_terminees, key=lambda x: x.numero):
                st.markdown(f"""
                    <div class="kanban-card">
                        <strong>Mur n°{instance.numero}</strong><br>
                        Modèle: {instance.modele.reference}<br>
                        Dimensions: {instance.modele.longueur}×{instance.modele.hauteur}cm
                    </div>
                """, unsafe_allow_html=True)
        
        # Ajouter un séparateur entre les projets
        st.markdown("<hr style='margin: 2rem 0; border: none; border-top: 2px solid #e5e7eb;'>", 
                   unsafe_allow_html=True)