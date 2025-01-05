import streamlit as st
from models import Projet, TypeDocument, StatutProjet
from Others.documents import sauvegarder_document
from datetime import datetime
from Pages.page_projet_details import Page_projet_details

def Page_projets_afficher():
    if not hasattr(st.session_state, 'projets'):
        st.session_state.projets = st.session_state.db.charger_projets()
    
    st.header("Gestion des Projets")
    
    # Grouper les projets par statut
    projets_par_statut = {statut: [] for statut in StatutProjet}
    for projet in st.session_state.projets:
        projets_par_statut[projet.statut].append(projet)
    
    # Initialisation des états si nécessaire
    if 'afficher_form_projet' not in st.session_state:
        st.session_state.afficher_form_projet = False

    # Bouton Nouveau Projet
    if st.button("+ Nouveau Projet"):
        st.session_state.afficher_form_projet = True
        st.rerun()

    # Formulaire de création de projet
    if st.session_state.afficher_form_projet:
        with st.form("new_project_form"):
            st.subheader("Nouveau Projet")
            nom = st.text_input("Nom du projet")
            description = st.text_area("Description")
            statut = st.selectbox("Statut", options=list(StatutProjet), format_func=lambda x: x.value)
            
            col1, col2 = st.columns(2)
            with col1:
                adresse_postale = st.text_area("Adresse postale")
                code_postal = st.text_input("Code postal")
            with col2:
                ville = st.text_input("Ville")
            
            documents = st.file_uploader("Documents du projet", accept_multiple_files=True)
            types_docs = []
            for i in range(len(documents)):
                types_docs.append(st.selectbox(f"Type du document {i+1}", 
                                             options=list(TypeDocument), 
                                             key=f"doc_type_{i}"))
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("Enregistrer")
            with col2:
                cancel = st.form_submit_button("Annuler")
            
            if submit and nom:
                projet = Projet(nom, description)
                projet.statut = statut
                projet.adresse_postale = adresse_postale
                projet.code_postal = code_postal
                projet.ville = ville
                
                # Créer d'abord le projet
                projet = st.session_state.db.creer_projet(projet)
                
                # Puis ajouter les documents
                if documents:
                    for doc, type_doc in zip(documents, types_docs):
                        document = sauvegarder_document(doc, type_doc)
                        st.session_state.db.creer_document(document, projet_id=projet.id)
                
                st.session_state.projets = st.session_state.db.charger_projets()
                st.session_state.afficher_form_projet = False
                st.success("Projet créé avec succès!")
                st.rerun()
            
            if cancel:
                st.session_state.afficher_form_projet = False
                st.rerun()

    # Affichage des projets par statut
    for statut in StatutProjet:
        projets = projets_par_statut[statut]
        if projets:
            st.subheader(f"Projets {statut.value}")
            for idx, projet in enumerate(projets):
                with st.expander(f"Projet: {projet.nom}", expanded=False):
                    st.write("**Description:**", projet.description)
                    st.write("**Date de création:**", projet.date_creation.strftime("%d/%m/%Y"))
                    
                    if projet.adresse_postale or projet.code_postal or projet.ville:
                        st.write(f"**Adresse:**  \n{projet.adresse_postale}   \n{projet.code_postal} {projet.ville}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("Configurer", key=f"config_{projet.id}"):
                            st.session_state.projet_a_modifier = projet.id
                            st.rerun()
                    with col2:
                        if st.button("Afficher les détails", key=f"details_{projet.id}"):
                            st.session_state.projet_details = projet.id
                            st.rerun()
                    with col3:
                        if st.button("Supprimer", key=f"delete_{projet.id}"):
                            st.session_state.db.supprimer_projet(projet.id)
                            st.session_state.projets = st.session_state.db.charger_projets()
                            st.success("Projet supprimé avec succès!")
                            st.rerun()

    # Formulaire de modification
    if hasattr(st.session_state, 'projet_a_modifier'):
        projet = next((p for p in st.session_state.projets 
                      if p.id == st.session_state.projet_a_modifier), None)
        if projet:
            with st.form("modify_project_form"):
                st.subheader(f"Modifier le projet : {projet.nom}")
                nouveau_nom = st.text_input("Nom du projet", value=projet.nom)
                nouvelle_description = st.text_area("Description", value=projet.description)
                nouveau_statut = st.selectbox("Statut", options=list(StatutProjet), 
                                            format_func=lambda x: x.value,
                                            index=list(StatutProjet).index(projet.statut))
                
                col1, col2 = st.columns(2)
                with col1:
                    nouvelle_adresse = st.text_area("Adresse postale", value=projet.adresse_postale)
                    nouveau_code_postal = st.text_input("Code postal", value=projet.code_postal)
                with col2:
                    nouvelle_ville = st.text_input("Ville", value=projet.ville)

                nouveaux_documents = st.file_uploader("Nouveaux documents", accept_multiple_files=True)
                types_docs = []
                for i in range(len(nouveaux_documents)):
                    types_docs.append(st.selectbox(f"Type du document {i+1}", 
                                                 options=list(TypeDocument), 
                                                 key=f"mod_doc_type_{i}"))
                
                if projet.documents:
                    st.write("Documents existants :")
                    for doc in projet.documents:
                        st.write(f"- {doc.nom} ({doc.type.value})")
                
                col1, col2 = st.columns(2)
                with col1:
                    submit = st.form_submit_button("Enregistrer")
                with col2:
                    cancel = st.form_submit_button("Annuler")
                
                if submit:
                    projet.nom = nouveau_nom
                    projet.description = nouvelle_description
                    projet.statut = nouveau_statut
                    projet.adresse_postale = nouvelle_adresse
                    projet.code_postal = nouveau_code_postal
                    projet.ville = nouvelle_ville
                    
                    if nouveaux_documents:
                        for doc, type_doc in zip(nouveaux_documents, types_docs):
                            document = sauvegarder_document(doc, type_doc)
                            st.session_state.db.creer_document(document, projet_id=projet.id)
                    
                    st.session_state.db.modifier_projet(projet)
                    st.session_state.projets = st.session_state.db.charger_projets()
                    del st.session_state.projet_a_modifier
                    st.success("Projet modifié avec succès!")
                    st.rerun()
                
                if cancel:
                    del st.session_state.projet_a_modifier
                    st.rerun()