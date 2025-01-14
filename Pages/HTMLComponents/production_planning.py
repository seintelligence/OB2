import streamlit.components.v1 as components
import json
from jinja2 import Template

def production_planning_table(data, edit_mode=False, key=None):
    """Create a production planning table component"""
    
    # HTML du composant
    html = """
        <table class="production-table">
            <thead>
                <tr>
                    <th>Projet</th>
                    {% for week in range(1, num_weeks + 1) %}
                        <th>S{{ week }}</th>
                    {% endfor %}
                </tr>
            </thead>
            <tbody>
                {% for project in projects %}
                    <tr>
                        <td style="text-align: left">{{ project }}</td>
                        {% for value in data[loop.index0] %}
                            <td>{{ value if value > 0 else '' }}</td>
                        {% endfor %}
                    </tr>
                {% endfor %}
                <tr>
                    <td style="text-align: left"><strong>Total</strong></td>
                    {% for total in total_per_week %}
                        <td><strong>{{ total }}</strong></td>
                    {% endfor %}
                </tr>
                <tr>
                    <td style="text-align: left"><strong>Capacité</strong></td>
                    {% for capacity in capacities %}
                        <td>
                            {% if edit_mode %}
                                <div class="capacity-cell">
                                    <input type="number" 
                                           value="{{ capacity }}"
                                           min="0" 
                                           max="20" 
                                           data-week="{{ loop.index }}"
                                           onchange="handleChange(event, 'capacity')"/>
                                    <input type="checkbox" 
                                           data-week="{{ loop.index }}"
                                           checked
                                           onchange="handleChange(event, 'worked')"/>
                                </div>
                            {% else %}
                                {{ capacity }}
                            {% endif %}
                        </td>
                    {% endfor %}
                </tr>
            </tbody>
        </table>

        <script>
            function handleChange(event, type) {
                const weekNum = parseInt(event.target.dataset.week);
                const value = type === 'capacity' ? 
                    parseInt(event.target.value) : event.target.checked;
                
                const componentValue = {
                    type: type,
                    weekNumber: weekNum,
                    value: value
                };
                
                // Envoyer au parent via Streamlit
                window.parent.postMessage({
                    type: "streamlit:setComponentValue",
                    value: componentValue,
                    dataType: "json"
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
                width: 40px;
                text-align: center;
                padding: 2px;
            }
        </style>
    """
    
    # Préparer les données
    template_data = {
        "num_weeks": len(data["data"][0]),
        "projects": [p for p in data["projects"] if p not in ["Total", "Capacité"]],
        "data": [row for i, row in enumerate(data["data"]) 
                if data["projects"][i] not in ["Total", "Capacité"]],
        "total_per_week": data["total_per_week"],
        "capacities": data["capacities"],
        "edit_mode": edit_mode
    }
    
    # Rendre le template
    rendered_html = Template(html).render(**template_data)
    
    # Créer et retourner le composant HTML
    return components.html(
        rendered_html,
        height=(len(template_data["projects"]) + 3) * 35 + 40,
        scrolling=True
    )