# __init__.py
import os
import streamlit.components.v1 as components

_component_func = components.declare_component(
    "production_planning",
    url="http://localhost:3001",  # URL de développement
)

def st_production_planning(data: dict, edit_mode: bool = False, key=None):
    """
    Crée un composant de planification de production.
    
    Args:
        data: Dictionnaire contenant les données de planification
        edit_mode: Booléen indiquant si le mode édition est actif
        key: Clé unique pour le composant
        
    Returns:
        Les mises à jour envoyées par le composant (type, weekNumber, value)
    """
    component_value = _component_func(
        data=data,
        editMode=edit_mode,
        key=key,
        default=None
    )
    
    return component_value