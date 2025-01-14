import streamlit as st
from models import Projet, TypeDocument, StatutProjet
from Others.documents import sauvegarder_document
from datetime import datetime

def Page_projets_afficher():
    if not hasattr(st.session_state, 'projets'):
        st.session_state.projets = st.session_state.db.charger_tous_projets()
    
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
            
            # Avant l'upload
            if 'document_list' not in st.session_state:
                st.session_state.document_list = []

            # Nouvelle gestion des documents
            documents_data = []  # Liste pour stocker les tuples (document, type)

            # Fonction callback pour l'upload
            def on_file_upload():
                print("on_file_upload")
                st.session_state.document_list = st.session_state.uploaded_files

            documents = st.file_uploader(
                "Documents du projet",
                accept_multiple_files=True,
                key="uploaded_files",
                on_change=on_file_upload
            )

            if st.session_state.document_list:
                st.write("Documents sélectionnés:")
                for idx, doc in enumerate(st.session_state.document_list):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.write(f"📄 {doc.name}")
                    with col2:
                        type_doc = st.selectbox(
                            "Type",
                            options=list(TypeDocument),
                            key=f"doc_type_{idx}",
                            format_func=lambda x: x.value
                        )
                        documents_data.append((doc, type_doc))
                    with col3:
                        if st.button("Retirer", key=f"remove_doc_{idx}"):
                            new_docs = list(st.session_state.document_list)
                            new_docs.pop(idx)
                            st.session_state.document_list = new_docs
                            st.rerun()

            # Lors de la soumission du formulaire
            if submit and nom:
                projet = Projet(nom, description)
                projet.statut = statut
                projet.adresse_postale = adresse_postale
                projet.code_postal = code_postal
                projet.ville = ville
                
                # Sauvegarder le projet
                projet = projet.sauvegarder(st.session_state.db)
                
                # Sauvegarder les documents avec leurs types
                if documents_data:
                    for doc, type_doc in documents_data:
                        document = sauvegarder_document(doc, type_doc)
                        document.sauvegarder(st.session_state.db, projet_id=projet.id)
                
                st.session_state.projets = st.session_state.db.charger_tous_projets()
                st.session_state.document_list = []  # Réinitialiser la liste
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
            st.subheader(f"Projets \"{statut.value}\"")
            for projet in projets:
                with st.expander(f"Projet: {projet.nom}", expanded=False):
                    projet_id = f"projet_{projet.id}"
                    mode_edition = st.session_state.get(f"edit_mode_{projet_id}", False)
                    
                    if mode_edition:
                        with st.form(f"edit_project_form_{projet.id}"):
                            nouveau_nom = st.text_input("Nom du projet", value=projet.nom)
                            nouvelle_description = st.text_area("Description", value=projet.description)
                            nouveau_statut = st.selectbox(
                                "Statut", 
                                options=list(StatutProjet),
                                format_func=lambda x: x.value,
                                index=list(StatutProjet).index(projet.statut)
                            )
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                nouvelle_adresse = st.text_area("Adresse postale", value=projet.adresse_postale)
                                nouveau_code_postal = st.text_input("Code postal", value=projet.code_postal)
                            with col2:
                                nouvelle_ville = st.text_input("Ville", value=projet.ville)

                            # Gestion des documents
                            st.write("---")
                            st.write("Documents du projet")
                            
                            # Initialiser la liste des documents à supprimer
                            docs_a_supprimer = []
                            
                            # Documents existants
                            if projet.documents:
                                st.write("Documents existants :")
                                for doc in projet.documents:
                                    col1, col2, col3 = st.columns([3, 2, 1])
                                    with col1:
                                        st.write(f"📄 {doc.nom}")
                                    with col2:
                                        st.write(f"Type: {doc.type.value}")
                                    with col3:
                                        if st.checkbox("Supprimer", key=f"del_doc_{doc.id}_{projet.id}"):
                                            docs_a_supprimer.append(doc)
                                st.write("---")

                            # Nouveaux documents
                            nouveaux_documents = st.file_uploader(
                                "Ajouter de nouveaux documents",
                                accept_multiple_files=True,
                                key=f"new_docs_{projet.id}"
                            )
                            
                            # Types pour les nouveaux documents
                            types_docs = []
                            if nouveaux_documents:
                                st.write("Sélectionnez le type pour chaque nouveau document :")
                                for i, doc in enumerate(nouveaux_documents):
                                    col1, col2 = st.columns([3, 1])
                                    with col1:
                                        st.write(f"📄 {doc.name}")
                                    with col2:
                                        type_doc = st.selectbox(
                                            "Type",
                                            options=list(TypeDocument),
                                            format_func=lambda x: x.value,
                                            key=f"edit_doc_type_{projet.id}_{i}"
                                        )
                                        types_docs.append(type_doc)
                            
                            st.write("---")

                            # Boutons de formulaire
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                save = st.form_submit_button("Enregistrer")
                            with col2:
                                cancel = st.form_submit_button("Annuler")
                            with col3:
                                delete = st.form_submit_button("Supprimer")

                            if save:
                                projet.nom = nouveau_nom
                                projet.description = nouvelle_description
                                projet.statut = nouveau_statut
                                projet.adresse_postale = nouvelle_adresse
                                projet.code_postal = nouveau_code_postal
                                projet.ville = nouvelle_ville

                                # Supprimer les documents marqués pour suppression
                                for doc in docs_a_supprimer:
                                    doc.supprimer(st.session_state.db)
                                    projet.documents.remove(doc)

                                # Ajouter les nouveaux documents
                                if nouveaux_documents:
                                    for doc, type_doc in zip(nouveaux_documents, types_docs):
                                        document = sauvegarder_document(doc, type_doc)
                                        document.sauvegarder(st.session_state.db, projet_id=projet.id)

                                projet.modifier(st.session_state.db)
                                st.session_state.projets = st.session_state.db.charger_tous_projets()
                                st.session_state[f"edit_mode_{projet_id}"] = False
                                st.success("Projet modifié avec succès!")
                                st.rerun()

                            if cancel:
                                st.session_state[f"edit_mode_{projet_id}"] = False
                                st.rerun()
                                
                            if delete:
                                projet.supprimer(st.session_state.db)
                                st.session_state.projets = st.session_state.db.charger_tous_projets()
                                st.success("Projet supprimé avec succès!")
                                st.rerun()
                    
                    else:
                        st.write("**Description:**", projet.description)
                        st.write("**Date de création:**", projet.date_creation.strftime("%d/%m/%Y"))
                        
                        if projet.adresse_postale or projet.code_postal or projet.ville:
                            st.write(f"**Adresse:**  \n{projet.adresse_postale}   \n{projet.code_postal} {projet.ville}")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button("Configurer", key=f"config_{projet.id}"):
                                st.session_state[f"edit_mode_{projet_id}"] = True
                                st.rerun()
                        with col2:
                            if st.button("Afficher les détails", key=f"details_{projet.id}"):
                                st.session_state.projet_details = projet.id
                                st.rerun()
                        with col3:
                            if st.button("Supprimer", key=f"delete_{projet.id}"):
                                projet.supprimer(st.session_state.db)
                                st.session_state.projets = st.session_state.db.charger_tous_projets()
                                st.success("Projet supprimé avec succès!")
                                st.rerun()