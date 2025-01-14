import streamlit as st
import streamlit.components.v1 as stc
from models import Statut, StatutProjet, PlanificationProduction
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from datetime import datetime
from Pages._production_component import st_production_planning

def Page_plan_production():
    st.markdown("""
        <style>
            .overload {
                background-color: #fee2e2 !important;
                color: #991b1b !important;
            }
            .underload {
                background-color: #dbeafe !important;
                color: #1e40af !important;
            }
            .optimal {
                background-color: #d1fae5 !important;
                color: #065f46 !important;
            }
            .capacity-edit {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }
            .capacity-edit input[type="number"] {
                width: 60px;
                padding: 4px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            .capacity-edit input[type="checkbox"] {
                width: 16px;
                height: 16px;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialisation
    if not hasattr(st.session_state, 'projets'):
        st.session_state.projets = st.session_state.db.charger_tous_projets()
    
    planification = PlanificationProduction(st.session_state.db)
    
    # Section Plan de Production
    st.title("Plan de Production")
    
    # Get the planning data once
    project_list, manuf_plan = planification.get_all_production_data()
    semaines = planification.obtenir_semaines(True)[:12]
    capacites = [s.capacite for s in semaines[:12]]
    
    # Afficher le plan de production
    display_table_production_schedule(planification)

    # Afficher le graphique de production
    display_graph_production_schedule(12, project_list, manuf_plan, capacites)
    
    # Section Réallocation des Murs
    display_allocation_murs(planification, project_list)

def display_table_production_schedule(planification):
    """Display the production planning table with edit capabilities"""
    # Mode édition
    edit_mode = st.checkbox("Mode édition", key="edit_mode_table")
    
    # Calcul des semaines
    current_week = datetime.now().isocalendar()[1]
    week_range = 26  # semaine actuelle + 25 semaines
    
    # Année courante
    annee = datetime.now().year
    
    # Récupérer les données dans l'ordre
    semaines = planification.obtenir_semaines(
        seulementTravaillees=True,
        debutSemaine=current_week,
        maxSemaines=week_range
    )
    
    project_list, manuf_plan = planification.get_all_production_data()
    
    # Préparer les données pour le composant
    projects_data = []
    for i, project in enumerate(project_list):
        if project not in ["Total", "Capacité"]:
            projects_data.append({
                "name": project,
                "values": manuf_plan[i]
            })
    
    # Obtenir les capacités des semaines
    capacites = [s.capacite for s in semaines]
    
    # Calculer les totaux par semaine
    total_par_semaine = [0] * len(manuf_plan[0]) if manuf_plan else [0] * week_range
    for projet_data in manuf_plan:
        for i, val in enumerate(projet_data):
            total_par_semaine[i] += val
    
    component_data = {
        "projects": projects_data,
        "totalPerWeek": total_par_semaine,
        "capacities": capacites
    }
    
    # Utiliser le composant
    update_value = st_production_planning(
        data=component_data,
        edit_mode=edit_mode
    )

    # Traiter les mises à jour
    if isinstance(update_value, dict):
        try:
            if 'type' in update_value and 'weekNumber' in update_value and 'value' in update_value:
                update_type = update_value['type']
                week_num = update_value['weekNumber']
                value = update_value['value']
                
                if update_type == "capacity":
                    planification.definir_capacite_semaine(annee, week_num, int(value))
                    st.rerun()
                elif update_type == "worked":
                    planification.definir_semaine_travaillee(annee, week_num, bool(value))
                    st.rerun()
                    
        except Exception as e:
            st.error(f"Erreur lors de la mise à jour : {str(e)}")

def display_graph_production_schedule(num_weeks, projects, manuf_plan, capacites):
    """
    Affiche le graphique de production avec tous les projets
    
    Args:
        num_weeks: Nombre de semaines à afficher
        projects: Liste des noms de projets
        manuf_plan: Matrice [projet x semaine] avec le nombre de murs prévus
        capacites: Liste des capacités par semaine
    """
    # Créer les étiquettes des semaines
    week_labels = [f'Sem {i+1}' for i in range(num_weeks)]
    
    # Créer le graphique avec Plotly
    fig = go.Figure()
    
    # Filtrer pour exclure uniquement la ligne "Total" et "Capacité"
    real_projects = [p for p in projects if p not in ['Total', 'Capacité']]
    real_project_indices = [i for i, p in enumerate(projects) if p in real_projects]
    
    print("Debug - Projets:", real_projects)  # Debug
    print("Debug - Indices:", real_project_indices)  # Debug
    
    # Ajouter les barres empilées pour chaque projet
    for proj_idx, project in zip(real_project_indices, real_projects):
        print(f"Debug - Ajout projet {project} avec données: {manuf_plan[proj_idx]}")  # Debug
        fig.add_trace(go.Bar(
            name=project,
            x=week_labels,
            y=manuf_plan[proj_idx],
            hovertemplate="Projet: %{fullData.name}<br>" +
                         "Semaine: %{x}<br>" +
                         "Murs: %{y}<br>"
        ))
    
    # Ajouter la ligne de capacité
    fig.add_trace(go.Scatter(
        name='Capacité',
        x=week_labels,
        y=capacites,
        mode='lines+markers',
        line=dict(color='red', width=2, dash='dash'),
        marker=dict(symbol='circle', size=8)
    ))
    
    # Configurer la mise en page
    fig.update_layout(
        title='Plan de production et capacité par semaine',
        xaxis_title='Semaine',
        yaxis_title='Nombre de murs',
        barmode='stack',
        height=500,
        showlegend=True,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True)

def display_allocation_murs(planification, project_list):
    """
    Display and manage wall allocation to production weeks
    """
    st.subheader("Allocation des murs aux semaines de production")
    
    instances_allocations = st.session_state.db.charger_allocations_instances()
    projets_filtres = [p for p in project_list if p not in ['Total', 'Capacité']]
    
    projet_nom = st.selectbox(
        "Sélectionner un projet",
        projets_filtres,
        key="projet_realloc"
    )
    
    if projet_nom:
        projet = next((p for p in st.session_state.projets if p.nom == projet_nom), None)
        if projet and projet.instances_mur:
            semaines = planification.obtenir_semaines(True)[:12]
            options_semaines = [(None, "Non allouée")] + [
                (s.numero, f"Semaine {s.numero} ({s.capacite} murs max)") 
                for s in semaines
            ]
            
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write("**Mur**")
            with col2:
                st.write("**Semaine allouée**")
            
            annee = datetime.now().year
            
            for instance in projet.instances_mur:
                key_selectbox = f"alloc_{instance.id}"
                key_previous = f"prev_{instance.id}"
                key_success = f"success_{instance.id}"
                
                semaine_actuelle = instances_allocations.get(instance.id)
                
                if key_previous not in st.session_state:
                    st.session_state[key_previous] = semaine_actuelle
                
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"Mur n°{instance.numero} - {instance.modele.reference}")
                with col2:
                    nouvelle_semaine = st.selectbox(
                        "Semaine",
                        [s[0] for s in options_semaines],
                        format_func=lambda x: "Non allouée" if x is None else f"Semaine {x}",
                        key=key_selectbox,
                        index=next((i for i, s in enumerate(options_semaines) if s[0] == semaine_actuelle), 0)
                    )
                with col3:
                    if nouvelle_semaine != st.session_state[key_previous]:
                        if st.button("Sauvegarder", key=f"save_{instance.id}"):
                            try:
                                if st.session_state[key_previous] is not None:
                                    ancienne_semaine = planification.obtenir_semaine(
                                        annee, st.session_state[key_previous])
                                    if ancienne_semaine:
                                        ancienne_semaine.retirer_instance_mur(instance, st.session_state.db)
                                
                                if nouvelle_semaine is not None:
                                    nouvelle_sem = planification.obtenir_semaine(
                                        annee, nouvelle_semaine)
                                    if nouvelle_sem:
                                        nouvelle_sem.allouer_instance_mur(instance, st.session_state.db)
                                
                                st.session_state[key_previous] = nouvelle_semaine
                                st.session_state[key_success] = True
                                st.rerun()
                            except ValueError as e:
                                st.error(str(e))
                    elif key_success in st.session_state and st.session_state[key_success]:
                        st.success("✓")
                        del st.session_state[key_success]
        else:
            st.info("Aucune instance de mur à afficher pour ce projet")

def st_kanban_board(walls: list, current_week: int) -> dict:
    """Crée un tableau Kanban pour la planification de production"""
    from jinja2 import Template
    import os

    # Lire le template HTML depuis le fichier
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'kanban_board.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        template = Template(f.read())

    # Rendre le HTML
    rendered_html = template.render(
        walls=walls,
        current_week=current_week
    )
    
    # Calculer la hauteur
    max_walls_per_column = max(
        len([w for w in walls if not w['allocation']]),  # Non alloués
        len([w for w in walls if w['status'] == 'EN_FABRICATION' and w['allocation'] and w['allocation'] < current_week]),  # Retard
        max(len([w for w in walls if w['allocation'] == week]) for week in range(current_week, current_week + 12))  # Semaines
    )
    height = max(100, 100 + (max_walls_per_column * 80))
    
    return stc.html(rendered_html, height=height)

def display_allocation_murs2(planification, project_list):
    """Display and manage wall allocation to production weeks using Kanban board"""
    st.subheader("Allocation des murs aux semaines de production")
    
    projets_filtres = [p for p in project_list if p not in ['Total', 'Capacité']]
    
    projet_nom = st.selectbox(
        "Sélectionner un projet",
        projets_filtres,
        key="projet_realloc"
    )
    
    if projet_nom:
        projet = next((p for p in st.session_state.projets if p.nom == projet_nom), None)
        if projet and projet.instances_mur:
            # Préparer les données
            current_week = datetime.now().isocalendar()[1]
            instances_allocations = st.session_state.db.charger_allocations_instances()
            
            # Convertir les instances en format attendu par le Kanban
            walls_data = [
                {
                    "id": instance.id,
                    "numero": instance.numero,
                    "modele": {
                        "reference": instance.modele.reference
                    },
                    "status": instance.statut.value,
                    "allocation": instances_allocations.get(instance.id)
                }
                for instance in projet.instances_mur
            ]
            
            # Afficher le Kanban
            result = st_kanban_board(walls=walls_data, current_week=current_week)
            
            # Gérer les mises à jour d'allocation
            if result:
                try:
                    wall_id = result.get('wallId')
                    target_week = result.get('targetWeek')
                    
                    instance = next(
                        (inst for inst in projet.instances_mur if inst.id == wall_id), 
                        None
                    )
                    
                    if instance:
                        annee = datetime.now().year
                        # Cas où le mur est déplacé vers une semaine
                        if target_week is not None:
                            nouvelle_sem = planification.obtenir_semaine(annee, target_week)
                            if nouvelle_sem:
                                nouvelle_sem.allouer_instance_mur(instance, st.session_state.db)
                        # Cas où le mur est déplacé vers "Non alloué" ou "Retard"
                        else:
                            current_allocation = instances_allocations.get(instance.id)
                            if current_allocation:
                                current_sem = planification.obtenir_semaine(annee, current_allocation)
                                if current_sem:
                                    current_sem.retirer_instance_mur(instance, st.session_state.db)
                        
                        st.rerun()
                except Exception as e:
                    st.error(f"Erreur lors de l'allocation : {str(e)}")
        else:
            st.info("Aucune instance de mur à afficher pour ce projet")