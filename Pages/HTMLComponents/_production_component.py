def st_kanban_board(walls: list, current_week: int, key=None):
    """Create a Kanban board component for production planning
    
    Args:
        walls: List of wall instances with their data
        current_week: Current week number
        key: Optional unique key for the component
        
    Returns:
        Dict with wallId and targetWeek when a wall is moved
    """
    # Créer le composant
    component_value = components.declare_component(
        "production_kanban",
        path="Production KANBAN"  # Assurez-vous que ce chemin est correct
    )(walls=walls, current_week=current_week, key=key)
    
    return component_value