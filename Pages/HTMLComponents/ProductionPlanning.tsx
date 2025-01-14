// ProductionPlanning.tsx
import React, { useEffect } from "react"
import {
  ComponentProps,
  Streamlit,
  withStreamlitConnection,
} from "streamlit-component-lib"

interface Week {
  number: number
  capacity: number
  worked: boolean
}

interface Project {
  name: string
  values: number[]
}

interface PlanningData {
  projects: Project[]
  totalPerWeek: number[]
  capacities: number[]
}

const ProductionPlanning = (props: ComponentProps) => {
  const { data, editMode } = props.args
  
  useEffect(() => {
    // Ajuster la hauteur du composant
    Streamlit.setFrameHeight()
  })

  const handleCapacityChange = (weekNum: number, value: number) => {
    Streamlit.setComponentValue({
      type: 'capacity',
      weekNumber: weekNum,
      value: value
    })
  }

  const handleWorkedChange = (weekNum: number, value: boolean) => {
    Streamlit.setComponentValue({
      type: 'worked',
      weekNumber: weekNum,
      value: value
    })
  }

  return (
    <div className="production-planning">
      <table className="production-table">
        <thead>
          <tr>
            <th>Projet</th>
            {Array.from({length: 12}, (_, i) => (
              <th key={i}>S{i + 1}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.projects.map((project: Project, idx: number) => (
            <tr key={idx}>
              <td>{project.name}</td>
              {project.values.map((value: number, weekIdx: number) => (
                <td key={weekIdx}>{value > 0 ? value : ''}</td>
              ))}
            </tr>
          ))}
          <tr>
            <td><strong>Total</strong></td>
            {data.totalPerWeek.map((total: number, idx: number) => (
              <td key={idx}><strong>{total}</strong></td>
            ))}
          </tr>
          <tr>
            <td><strong>Capacité</strong></td>
            {data.capacities.map((capacity: number, idx: number) => (
              <td key={idx}>
                {editMode ? (
                  <div className="capacity-cell">
                    <input
                      type="number"
                      value={capacity}
                      min={0}
                      max={20}
                      onChange={(e) => handleCapacityChange(idx + 1, parseInt(e.target.value))}
                    />
                    <input
                      type="checkbox"
                      defaultChecked={true}
                      onChange={(e) => handleWorkedChange(idx + 1, e.target.checked)}
                    />
                  </div>
                ) : (
                  capacity
                )}
              </td>
            ))}
          </tr>
        </tbody>
      </table>

      <style jsx>{`
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
        
        input[type="number"] {
          width: 50px;
          text-align: center;
          padding: 2px;
        }

        input[type="checkbox"] {
          width: 16px;
          height: 16px;
        }
      `}</style>
    </div>
  )
}

export default withStreamlitConnection(ProductionPlanning)