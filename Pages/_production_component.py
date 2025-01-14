import streamlit.components.v1 as components
from jinja2 import Template
from datetime import datetime

def st_production_planning(data: dict, edit_mode: bool = False, key=None):
    """Create a production planning table component"""
    # Calcul des semaines à afficher
    current_week = datetime.now().isocalendar()[1]
    end_week = current_week + 25
    weeks = list(range(current_week, end_week + 1))
    
    # HTML du composant
    html = """
        <script src="streamlit-component-lib.js"></script>
        <div id="production-planning">
            <table class="production-table">
                <thead>
                    <tr>
                        <th>Projet</th>
                        {% for week in weeks %}
                            <th>S{{ week }}</th>
                        {% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for project in data['projects'] %}
                        <tr>
                            <td style="text-align: left">{{ project['name'] }}</td>
                            {% for value in project['values'] %}
                                <td>{{ value if value > 0 else '' }}</td>
                            {% endfor %}
                        </tr>
                    {% endfor %}
                    <tr>
                        <td style="text-align: left"><strong>Total</strong></td>
                        {% for total in data['totalPerWeek'] %}
                            <td><strong>{{ total }}</strong></td>
                        {% endfor %}
                    </tr>
                    <tr>
                        <td style="text-align: left"><strong>Capacité</strong></td>
                        {% for capacity in data['capacities'] %}
                            <td>
                                {% if edit_mode %}
                                    <div class="capacity-cell">
                                        <input type="number" 
                                               value="{{ capacity }}"
                                               min="0" 
                                               max="20" 
                                               data-week="{{ weeks[loop.index0] }}"
                                               class="capacity-input"
                                               onchange="handleCapacityChange(event)"/>
                                        <input type="checkbox" 
                                               data-week="{{ weeks[loop.index0] }}"
                                               checked
                                               class="worked-checkbox"
                                               onchange="handleWorkedChange(event)"/>
                                    </div>
                                {% else %}
                                    {{ capacity }}
                                {% endif %}
                            </td>
                        {% endfor %}
                    </tr>
                </tbody>
            </table>
        </div>

        <script>
            function handleCapacityChange(event) {
                const weekNum = parseInt(event.target.dataset.week);
                const value = parseInt(event.target.value);
                
                parent.postMessage({
                    type: "streamlit:setComponentValue",
                    value: {
                        type: 'capacity',
                        weekNumber: weekNum,
                        value: value
                    }
                }, "*");
            }
            
            function handleWorkedChange(event) {
                const weekNum = parseInt(event.target.dataset.week);
                const value = event.target.checked;
                
                parent.postMessage({
                    type: "streamlit:setComponentValue",
                    value: {
                        type: 'worked',
                        weekNumber: weekNum,
                        value: value
                    }
                }, "*");
            }
        </script>

        <style>
            .production-table {
                width: 100%;
                border-collapse: collapse;
                text-align: center;
                font-size: 0.9rem;
            }
            
            .production-table th {
                background-color: #f8fafc;
                color: #334155;
                font-weight: 600;
                padding: 6px 4px;
                border: 1px solid #e2e8f0;
            }
            
            .production-table td {
                padding: 4px;
                border: 1px solid #e2e8f0;
            }
            
            .capacity-cell {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 4px;
            }
            
            .capacity-input {
                width: 50px;
                text-align: center;
                padding: 2px;
            }
            
            .worked-checkbox {
                width: 16px;
                height: 16px;
            }
        </style>
    """
    
    # Rendre le template
    template = Template(html)
    rendered_html = template.render(data=data, edit_mode=edit_mode, weeks=weeks)

    # Créer et retourner le composant HTML
    return components.html(
        rendered_html,
        height=(len(data["projects"]) + 3) * 35 + 40
    )