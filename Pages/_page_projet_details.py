import streamlit as st
from models import StatutProjet, TypeDocument, TypeIsolant, ModeleMur, InstanceMur
from Others.generer_pdf_projet import generer_pdf_projet

def auto_scroll_to_form():
    scroll_js = """
    <script>
        const form = document.getElementById('model-edit-form');
        if (form) {
            form.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    </script>
    """
    st.markdown(scroll_js, unsafe_allow_html=True)

def Page_projet_details():
    if not hasattr(st.session_state, 'projet_details'):
        st.error("Aucun projet sélectionné")
        return
        
    if not hasattr(st.session_state, 'projets'):
        st.session_state.projets = st.session_state.db.charger_tous_projets()
    
    projet = next((p for p in st.session_state.projets if p.id == st.session_state.projet_details), None)
    if not projet:
        st.error("Projet non trouvé")
        return
        
    if hasattr(st.session_state, 'generer_pdf') and st.session_state.generer_pdf:
        st.write("Génération du PDF en cours...")
        try:
            pdf = generer_pdf_projet(projet)
            st.success("PDF généré avec succès")
            st.download_button(
                label="📥 Télécharger le PDF",
                data=pdf,
                file_name=f"projet_{projet.nom}_{projet.date_creation.strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Erreur lors de la génération du PDF: {str(e)}")
        del st.session_state.generer_pdf
    
    with st.sidebar:
        st.header("Navigation")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Retour à la liste"):
                del st.session_state.projet_details
                st.rerun()
        with col2:
            if st.button("📄 Générer PDF"):
                st.session_state.generer_pdf = True
                st.rerun()
        st.divider()
        
        st.markdown("""
            - [Informations générales](#projet)
            - [Documents](#documents)
            - [Parties Prenantes](#parties-prenantes)
            - [Coût](#cout)
            - [Murs](#murs)
        """)
    
    st.title(f"Projet: {projet.nom}", anchor="projet")
    st.write(f"**État actuel:** {projet.statut.value}")
    st.write(f"**Date de création:** {projet.date_creation.strftime('%d/%m/%Y')}")
    
    if projet.adresse_postale or projet.code_postal or projet.ville:
        st.write(f"**Adresse:**  \n{projet.adresse_postale}   \n{projet.code_postal} {projet.ville}")
    else:
        st.write("**Adresse:**  \nNon spécifiée")
    
    st.header("Documents", anchor="documents")
    col_upload, col_filter = st.columns([0.7, 0.3])
    with col_upload:
        nouveaux_docs = st.file_uploader("Ajouter des documents", accept_multiple_files=True)
        if nouveaux_docs:
            for doc in nouveaux_docs:
                document = sauvegarder_document(doc, TypeDocument.AUTRE)  # Par défaut
                document.sauvegarder(st.session_state.db, projet_id=projet.id)
                projet.documents.append(document)
            st.success("Documents ajoutés avec succès!")
            st.rerun()
    with col_filter:
        filtre_type = st.selectbox("Filtrer par type", ["Tous"] + [t.value for t in TypeDocument])
    
    st.header("Parties Prenantes", anchor="parties-prenantes")
    st.info("Fonctionnalité à venir")

    st.header("Coût", anchor="cout")
    cout_total = sum(round(modele.cout * len(modele.instances), 2) for modele in projet.modeles_mur) if projet.modeles_mur else 0
    st.metric("Coût total estimé", f"{cout_total}€")
    if projet.modeles_mur:
        st.write("**Détail des coûts:**")
        for modele in projet.modeles_mur:
            cout_modele = modele.cout * len(modele.instances)
            st.write(f"- Modèle {modele.reference}: {modele.cout}€ × {len(modele.instances)} instances = {cout_modele}€")

    st.header("Murs", anchor="murs")
    if projet.statut != StatutProjet.EN_CONCEPTION:
        st.error("Le projet n'est plus en conception et il n'est plus possible de modifier les murs")
    if projet.statut == StatutProjet.EN_CONCEPTION:
        if not hasattr(st.session_state, 'modele_a_modifier') and st.button("+ Nouveau modèle de mur"):
            st.session_state.nouveau_modele = True
            
        if hasattr(st.session_state, 'nouveau_modele') or hasattr(st.session_state, 'modele_a_modifier'):
            st.markdown('<form id="model-edit-form"></form>', unsafe_allow_html=True)
            with st.form("form_modele"):
                modele = None
                if hasattr(st.session_state, 'modele_a_modifier'):
                    modele = next((m for m in projet.modeles_mur if m.id == st.session_state.modele_a_modifier), None)
                
                reference = st.text_input("Référence", value=modele.reference if modele else "")
                col1, col2, col3 = st.columns(3)
                with col1:
                    longueur = st.number_input("Longueur (cm)", min_value=0, value=int(modele.longueur) if modele else 0, key="longueur")
                with col2:
                    hauteur = st.number_input("Hauteur (cm)", min_value=0, value=int(modele.hauteur) if modele else 0, key="hauteur")
                with col3:
                    epaisseur = st.number_input("Épaisseur (cm)", min_value=0, value=int(modele.epaisseur) if modele else 0, key="epaisseur")
                    
                isolant = st.selectbox(
                    "Type d'isolant", 
                    options=list(TypeIsolant),
                    index=list(TypeIsolant).index(modele.isolant) if modele else 0,
                    key="isolant"
                )
                
                # Champ nombre d'instances
                nb_instances = st.number_input(
                    "Nombre d'instances", 
                    min_value=1,
                    value=len(modele.instances) if modele and len(modele.instances)>0 else 1,
                    key="nb_instances"
                )
                
                submitted = st.form_submit_button("Enregistrer")
                if submitted:
                    if modele:
                        # Modification
                        modele.reference = reference
                        modele.longueur = longueur
                        modele.hauteur = hauteur
                        modele.epaisseur = epaisseur
                        modele.isolant = isolant
                        
                        current_instances = len(modele.instances)
                        if nb_instances > current_instances:
                            # Ajout de nouvelles instances
                            for i in range(current_instances, nb_instances):
                                instance = InstanceMur(i+1, modele)
                                instance.sauvegarder(st.session_state.db, projet.id, modele.id)
                                modele.instances.append(instance)
                                projet.instances_mur.append(instance)
                        elif nb_instances < current_instances:
                            # Suppression des instances en trop
                            for instance in modele.instances[nb_instances:]:
                                instance.supprimer(st.session_state.db)
                                projet.instances_mur.remove(instance)
                            modele.instances = modele.instances[:nb_instances]
                            
                        modele.modifier(st.session_state.db)
                        del st.session_state.modele_a_modifier
                    else:
                        # Création
                        new_modele = ModeleMur(reference, longueur, hauteur, epaisseur, isolant)
                        new_modele.calculer_cout()  # Calcul du coût avant sauvegarde
                        new_modele.sauvegarder(st.session_state.db, projet.id)
                        
                        # Création des instances
                        for i in range(nb_instances):
                            instance = InstanceMur(i+1, new_modele)
                            instance.sauvegarder(st.session_state.db, projet.id, new_modele.id)
                            new_modele.instances.append(instance)
                            projet.instances_mur.append(instance)
                        
                        projet.modeles_mur.append(new_modele)
                        del st.session_state.nouveau_modele
                    
                    st.success("Modèle " + ("modifié" if modele else "créé") + " avec succès!")
                    st.rerun()

                if st.form_submit_button("Annuler"):
                    if modele:
                        del st.session_state.modele_a_modifier
                    else:
                        del st.session_state.nouveau_modele
                    st.rerun()

        if projet.modeles_mur:
            for modele in projet.modeles_mur:
                with st.expander(f"Modèle {modele.reference} --> {len(modele.instances)} instances"):
                    st.write(f"**Dimensions:** {modele.longueur}×{modele.hauteur}×{modele.epaisseur}cm")
                    st.write(f"**Type d'isolant:** {modele.isolant.value}")
                    st.write(f"**Nombre d'instances:** {len(modele.instances)}")
                    if modele.cout:
                        surface = (modele.longueur * modele.hauteur) / 10000  # conversion en m²
                        cout_m2 = modele.cout / surface if surface > 0 else 0
                        st.write(f"**Coût au m²:** {cout_m2:.2f}€/m²")
                    st.write(f"**Coût total:** {modele.cout:.2f}€")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Modifier", key=f"mod_{modele.id}"):
                            st.session_state.modele_a_modifier = modele.id
                            auto_scroll_to_form()
                            st.rerun()
                    with col2:
                        if st.button("Supprimer", key=f"del_{modele.id}"):
                            modele.supprimer(st.session_state.db)
                            projet.modeles_mur.remove(modele)
                            st.success("Modèle supprimé!")
                            st.rerun()