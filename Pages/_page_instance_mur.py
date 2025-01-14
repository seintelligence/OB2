import streamlit as st
from models import InstanceMur, Document, TypeDocument, Statut
from Others.documents import sauvegarder_document

def Page_instance_mur_afficher():
    if not hasattr(st.session_state, 'projets'):
        st.session_state.projets = st.session_state.db.charger_tous_projets()
    
    st.header("Gestion des Instances de Mur")
    
    projets_avec_modeles = [p for p in st.session_state.projets if p.modeles_mur]
    
    if not projets_avec_modeles:
        st.warning("Aucun projet avec des modèles de mur n'est disponible.")
        return
    
    if st.button("+ Nouvelle(s) Instance(s) de Mur"):
        st.session_state.afficher_form_instance = True
        
    # Formulaire de création
    if hasattr(st.session_state, 'afficher_form_instance') and st.session_state.afficher_form_instance:
        with st.form("form_instance"):
            projet = st.selectbox("Projet", projets_avec_modeles, format_func=lambda x: x.nom)
            modele = st.selectbox("Modèle de mur", projet.modeles_mur,
                                format_func=lambda x: f"{x.reference} ({x.longueur}×{x.hauteur}cm)")
            nb_instances = st.number_input("Nombre d'instances à créer", min_value=1, value=1, step=1)
            
            numeros_existants = [inst.numero for inst in modele.instances]
            prochain_numero = 1 if not numeros_existants else max(numeros_existants) + 1
            st.write(f"La numérotation commencera à : {prochain_numero}")
            
            documents = st.file_uploader("Documents communs aux instances", accept_multiple_files=True)
            types_docs = [st.selectbox(f"Type du document {i+1}", options=list(TypeDocument), key=f"type_doc_instance_{i}") 
                         for i in range(len(documents))] if documents else []
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Enregistrer")
            with col2:
                if st.form_submit_button("Annuler"):
                    st.session_state.afficher_form_instance = False
                    st.rerun()
            
            if submitted:
                try:
                    for i in range(nb_instances):
                        instance = InstanceMur(prochain_numero + i, modele)
                        instance.sauvegarder(st.session_state.db, projet.id, modele.id)
                        
                        if documents:
                            for doc, type_doc in zip(documents, types_docs):
                                document = sauvegarder_document(doc, type_doc)
                                document.sauvegarder(st.session_state.db, instance_id=instance.id)
                                instance.documents.append(document)
                        
                        modele.instances.append(instance)
                        projet.instances_mur.append(instance)
                    
                    st.session_state.afficher_form_instance = False
                    st.session_state.projets = st.session_state.db.charger_tous_projets()
                    st.success(f"{nb_instances} instance(s) de mur créée(s) avec succès!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur lors de la création des instances : {str(e)}")

    # Affichage des instances existantes
    for projet in projets_avec_modeles:
        if projet.instances_mur:
            st.subheader(f"Projet : {projet.nom}")
            for modele in projet.modeles_mur:
                instances_du_modele = [inst for inst in projet.instances_mur if inst.modele == modele]
                if instances_du_modele:
                    st.write(f"**Modèle : {modele.reference}** ({modele.longueur}×{modele.hauteur}cm)")
                    for instance in sorted(instances_du_modele, key=lambda x: x.numero):
                        with st.expander(f"Instance n°{instance.numero}"):
                            st.write(f"**Statut:** {instance.statut.value}")
                            if instance.documents:
                                st.write("**Documents:**")
                                for doc in instance.documents:
                                    st.write(f"- {doc.nom} ({doc.type.value})")
                            
                            # Formulaire de modification du statut
                            nouveau_statut = st.selectbox(
                                "Nouveau statut", 
                                options=list(Statut), 
                                index=list(Statut).index(instance.statut),
                                key=f"statut_{instance.id}"
                            )
                            
                            if nouveau_statut != instance.statut:
                                instance.statut = nouveau_statut
                                instance.modifier(st.session_state.db)
                                st.success("Statut mis à jour")
                                st.rerun()

                            if st.button("Supprimer", key=f"del_inst_{instance.id}"):
                                instance.supprimer(st.session_state.db)
                                modele.instances.remove(instance)
                                projet.instances_mur.remove(instance)
                                st.success("Instance supprimée avec succès!")
                                st.rerun()