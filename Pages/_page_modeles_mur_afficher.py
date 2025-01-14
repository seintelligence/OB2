import streamlit as st
from models import ModeleMur, TypeDocument, TypeIsolant, Ouverture, Statut
from Others.documents import sauvegarder_document

def Page_modeles_mur_afficher():
    if not hasattr(st.session_state, 'projets'):
        st.session_state.projets = st.session_state.db.charger_tous_projets()
    
    st.header("Gestion des Modèles de Mur")
    
    is_modification = hasattr(st.session_state, 'modele_a_modifier')
    
    if not is_modification and st.button("+ Nouveau Modèle de Mur"):
        st.session_state.afficher_form_modele = True
        
    # Formulaire de création/modification
    if (hasattr(st.session_state, 'afficher_form_modele') and st.session_state.afficher_form_modele) or is_modification:
        with st.form("form_modele"):
            modele = None
            projet_selectbox_index = 0
            
            if is_modification:
                modele_id = st.session_state.modele_a_modifier
                modele = next((m for p in st.session_state.projets for m in p.modeles_mur if m.id == modele_id), None)
                if modele:
                    projet = next(p for p in st.session_state.projets if modele in p.modeles_mur)
                    projet_selectbox_index = st.session_state.projets.index(projet)
            
            projet = st.selectbox("Projet", st.session_state.projets, 
                                index=projet_selectbox_index, 
                                format_func=lambda x: x.nom)
            
            # Champs du formulaire
            reference = st.text_input("Référence", value=modele.reference if modele else "")
            longueur = st.number_input("Longueur (cm)", min_value=0, step=1, 
                                     value=int(modele.longueur) if modele else 0)
            hauteur = st.number_input("Hauteur (cm)", min_value=0, step=1, 
                                    value=int(modele.hauteur) if modele else 0)
            epaisseur = st.number_input("Épaisseur (cm)", min_value=0, step=1, 
                                      value=int(modele.epaisseur) if modele else 0)
            isolant = st.selectbox("Type d'isolant", options=list(TypeIsolant), key="type_isolant",
                               format_func=lambda x: x.value,
                               index=list(TypeIsolant).index(modele.isolant) if modele else 0)
            
            # Ouvertures
            nb_ouvertures = st.number_input("Nombre d'ouvertures", min_value=0, step=1, 
                                          value=len(modele.ouvertures) if modele else 0)
            
            ouvertures = []
            for i in range(nb_ouvertures):
                st.write(f"Ouverture {i+1}")
                ouv_existante = modele.ouvertures[i] if modele and i < len(modele.ouvertures) else None
                
                type_ouv = st.selectbox(f"Type", ["Fenêtre", "Porte", "Autre"], key=f"type_ouv_{i}",
                                      index=["Fenêtre", "Porte", "Autre"].index(ouv_existante.type) if ouv_existante else 0)
                col1, col2 = st.columns(2)
                with col1:
                    larg = st.number_input("Largeur (cm)", min_value=0, step=1, key=f"larg_{i}", 
                                         value=int(ouv_existante.largeur) if ouv_existante else 90)
                    pos_x = st.number_input("Position X (cm)", min_value=0, step=1, key=f"pos_x_{i}", 
                                          value=int(ouv_existante.position_x) if ouv_existante else 0)
                with col2:
                    haut = st.number_input("Hauteur (cm)", min_value=0, step=1, key=f"haut_{i}", 
                                         value=int(ouv_existante.hauteur) if ouv_existante else 210)
                    pos_y = st.number_input("Position Y (cm)", min_value=0, step=1, key=f"pos_y_{i}", 
                                          value=int(ouv_existante.position_y) if ouv_existante else 0)
                
                ouvertures.append(Ouverture(type_ouv, larg, haut, pos_x, pos_y))
            
            # Documents
            nouveaux_docs = st.file_uploader("Nouveaux documents", accept_multiple_files=True)
            types_docs = [st.selectbox(f"Type du document {i+1}", options=list(TypeDocument), key=f"type_doc_{i}") 
                         for i in range(len(nouveaux_docs))] if nouveaux_docs else []
            
            if modele and modele.documents:
                st.write("Documents existants:")
                for doc in modele.documents:
                    st.write(f"- {doc.nom} ({doc.type.value})")
            
            # Boutons du formulaire
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Enregistrer")
            with col2:
                if st.form_submit_button("Annuler"):
                    if is_modification:
                        del st.session_state.modele_a_modifier
                    else:
                        st.session_state.afficher_form_modele = False
                    st.rerun()
            
            if submitted:
                try:
                    if not modele:
                        modele = ModeleMur(reference, longueur, hauteur, epaisseur, isolant)
                        modele.ouvertures = ouvertures
                        modele.sauvegarder(st.session_state.db, projet.id)
                    else:
                        modele.reference = reference
                        modele.longueur = longueur
                        modele.hauteur = hauteur
                        modele.epaisseur = epaisseur
                        modele.isolant = isolant
                        modele.ouvertures = ouvertures
                        modele.modifier(st.session_state.db)
                    
                    # Ajout des nouveaux documents
                    if nouveaux_docs:
                        for doc, type_doc in zip(nouveaux_docs, types_docs):
                            document = sauvegarder_document(doc, type_doc)
                            document.sauvegarder(st.session_state.db, modele_id=modele.id)
                    
                    # Mise à jour de l'interface
                    st.session_state.projets = st.session_state.db.charger_tous_projets()
                    if is_modification:
                        del st.session_state.modele_a_modifier
                    else:
                        st.session_state.afficher_form_modele = False
                    st.success("Modèle de mur enregistré avec succès!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Erreur lors de l'enregistrement : {str(e)}")
    
    # Affichage des modèles existants
    for projet in st.session_state.projets:
        if projet.modeles_mur:
            st.subheader(f"Modèles du projet : {projet.nom}")
            for modele in projet.modeles_mur:
                with st.expander(f"Modèle : {modele.reference}"):
                    st.write(f"**ID:** {modele.id}")
                    st.write(f"**Dimensions:** {modele.longueur}×{modele.hauteur}×{modele.epaisseur}cm")
                    st.write(f"**Coût:** {modele.cout}€")
                    st.write(f"**Statut:** {modele.statut.value}")
                    st.write(f"**Isolant:** {modele.isolant.value}")
                    
                    if modele.ouvertures:
                        st.write("**Ouvertures:**")
                        for ouv in modele.ouvertures:
                            st.write(f"- {ouv.type}: {ouv.largeur}×{ouv.hauteur}cm @ ({ouv.position_x}, {ouv.position_y})")
                    
                    if modele.documents:
                        st.write("**Documents:**")
                        for doc in modele.documents:
                            st.write(f"- {doc.nom} ({doc.type.value})")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Modifier", key=f"mod_model_{projet.nom}_{modele.id}"):
                            st.session_state.modele_a_modifier = modele.id
                            st.session_state.afficher_form_modele = True
                            st.rerun()
                    with col2:
                        if st.button("Supprimer", key=f"del_model_{projet.nom}_{modele.id}"):
                            modele.supprimer(st.session_state.db)
                            st.session_state.projets = st.session_state.db.charger_tous_projets()
                            st.success("Modèle supprimé avec succès!")
                            st.rerun()