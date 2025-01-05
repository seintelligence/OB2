import streamlit as st
from models import StatutProjet, TypeDocument, TypeIsolant
from Others.generer_pdf_projet import generer_pdf_projet  # Ajout de l'import

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
        st.session_state.projets = st.session_state.db.charger_projets()
    
    projet = next((p for p in st.session_state.projets if p.id == st.session_state.projet_details), None)
    if not projet:
        st.error("Projet non trouvé")
        return
        
    # Génération du PDF si demandée
    if hasattr(st.session_state, 'generer_pdf') and st.session_state.generer_pdf:
        st.write("Génération du PDF en cours...")  # Debug
        try:
            pdf = generer_pdf_projet(projet)
            st.success("PDF généré avec succès")  # Debug
            st.download_button(
                label="📥 Télécharger le PDF",
                data=pdf,
                file_name=f"projet_{projet.nom}_{projet.date_creation.strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Erreur lors de la génération du PDF: {str(e)}")
        del st.session_state.generer_pdf
    
    # Menu latéral
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
    
    # Contenu principal
    st.title(f"Projet: {projet.nom}", anchor="projet")
    st.write(f"**État actuel:** {projet.statut.value}")
    st.write(f"**Date de création:** {projet.date_creation.strftime('%d/%m/%Y')}")
    
    # Affichage de l'adresse complète
    if projet.adresse_postale or projet.code_postal or projet.ville:
        st.write(f"**Adresse:**  \n{projet.adresse_postale}   \n{projet.code_postal} {projet.ville}")
    else:
        st.write("**Adresse:**  \nNon spécifiée")
    
    # Section Documents
    st.header("Documents", anchor="documents")
    col_upload, col_filter = st.columns([0.7, 0.3])
    with col_upload:
        nouveaux_docs = st.file_uploader("Ajouter des documents", accept_multiple_files=True)
    with col_filter:
        filtre_type = st.selectbox("Filtrer par type", ["Tous"] + [t.value for t in TypeDocument])
    
    # [Reste du code pour la section Documents]
    
    # Section Parties Prenantes
    st.header("Parties Prenantes", anchor="parties-prenantes")
    st.info("Fonctionnalité à venir")

    # Section Coût
    st.header("Coût", anchor="cout")
    cout_total = sum(round(modele.cout * len(modele.instances), 2) for modele in projet.modeles_mur) if projet.modeles_mur else 0
    st.metric("Coût total estimé", f"{cout_total}€")
    if projet.modeles_mur:
        st.write("**Détail des coûts:**")
        for modele in projet.modeles_mur:
            st.write(f"- Modèle {modele.reference}: {modele.cout}€ × {len(modele.instances)} instances = {modele.cout * len(modele.instances)}€")

    # Section Murs
    from models import TypeIsolant, ModeleMur, InstanceMur  # Ajout de l'import

    # Section Murs
    st.header("Murs", anchor="murs")
    if projet.statut == StatutProjet.EN_CONCEPTION:
        if not hasattr(st.session_state, 'modele_a_modifier') and st.button("+ Nouveau modèle de mur"):
            st.session_state.nouveau_modele = True
            
        # Formulaire de création/modification
        if hasattr(st.session_state, 'nouveau_modele') or hasattr(st.session_state, 'modele_a_modifier'):
            # Au début de la section formulaire
            st.markdown('<form id="model-edit-form"></form>', unsafe_allow_html=True)
            with st.form("form_modele"):
                modele = None
                if hasattr(st.session_state, 'modele_a_modifier'):
                    modele = next((m for m in projet.modeles_mur if m.id == st.session_state.modele_a_modifier), None)
                
                reference = st.text_input("Référence", value=modele.reference if modele else "")
                col1, col2, col3 = st.columns(3)
                with col1:
                    longueur = st.number_input("Longueur (cm)", min_value=0, value=int(modele.longueur) if modele else 0)
                with col2:
                    hauteur = st.number_input("Hauteur (cm)", min_value=0, value=int(modele.hauteur) if modele else 0)
                with col3:
                    epaisseur = st.number_input("Épaisseur (cm)", min_value=0, value=int(modele.epaisseur) if modele else 0)
                    
                isolant = st.selectbox(
                    "Type d'isolant", 
                    options=list(TypeIsolant),
                    index=list(TypeIsolant).index(modele.isolant) if modele else 0
                )
                
                if not modele:  # Seulement pour nouveau modèle
                    nb_instances = st.number_input("Nombre d'instances", min_value=1, value=1)
                
                st.write(f"Coût total estimé: {cout_total:.2f}€")
                
                # Nombre d'instances - disponible pour création et modification
                nb_instances = st.number_input("Nombre d'instances", min_value=1, 
                    value=len(modele.instances) if modele and len(modele.instances)>0 else 1)
                
                submitted = st.form_submit_button("Enregistrer")
                if submitted:
                    if modele:
                        # Modification
                        modele.reference = reference
                        modele.longueur = longueur
                        modele.hauteur = hauteur
                        modele.epaisseur = epaisseur
                        modele.isolant = isolant
                        
                        # Ajuster le nombre d'instances
                        current_instances = len(modele.instances)
                        if nb_instances > current_instances:
                            # Ajouter des instances
                            for i in range(current_instances, nb_instances):
                                instance = InstanceMur(i+1, modele)
                                instance = st.session_state.db.creer_instance_mur(instance, projet.id, modele.id)
                                modele.instances.append(instance)
                        elif nb_instances < current_instances:
                            # Supprimer des instances
                            for instance in modele.instances[nb_instances:]:
                                st.session_state.db.supprimer_instance_mur(instance.id)
                            modele.instances = modele.instances[:nb_instances]
                            
                        st.session_state.db.modifier_modele_mur(modele)
                        del st.session_state.modele_a_modifier
                    else:
                        # Création
                        new_modele = ModeleMur(reference, longueur, hauteur, epaisseur, isolant)
                        new_modele = st.session_state.db.creer_modele_mur(new_modele, projet.id)
                        
                        # Créer les instances
                        for i in range(nb_instances):
                            instance = InstanceMur(i+1, new_modele)
                            instance = st.session_state.db.creer_instance_mur(instance, projet.id, new_modele.id)
                            new_modele.instances.append(instance)
                        
                        del st.session_state.nouveau_modele
                    
                    st.session_state.projets = st.session_state.db.charger_projets()
                    st.success("Modèle " + ("modifié" if modele else "créé") + " avec succès!")
                    st.rerun()

                if st.form_submit_button("Annuler"):
                    if modele:
                        del st.session_state.modele_a_modifier
                    else:
                        del st.session_state.nouveau_modele
                    st.rerun()

        # Affichage des modèles existants# Dans la section d'affichage des modèles
        if projet.modeles_mur:
            for modele in projet.modeles_mur:
                with st.expander(f"Modèle {modele.reference} --> {len(modele.instances)}"):
                    st.write(f"**Dimensions:** {modele.longueur}×{modele.hauteur}×{modele.epaisseur}cm")
                    st.write(f"**Type d'isolant:** {modele.isolant.value}")
                    st.write(f"**Nombre d'instances:** {len(modele.instances)}")
                    if modele.cout : st.write(f"**Coût au m²:** {modele.cout/((modele.longueur*modele.hauteur)/10000):.2f}€/m²")
                    st.write(f"**Coût total:** {modele.cout:.2f}€")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Modifier", key=f"mod_{modele.id}"):
                            st.session_state.modele_a_modifier = modele.id
                            auto_scroll_to_form()
                            st.success("Modèle modifié!")
                            st.rerun()
                    with col2:
                        if st.button("Supprimer", key=f"del_{modele.id}"):
                            st.session_state.db.supprimer_modele_mur(modele.id)
                            st.session_state.projets = st.session_state.db.charger_projets()
                            st.success("Modèle supprimé!")
                            st.rerun()