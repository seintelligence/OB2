import React, { useState, useEffect } from 'react';
import { AlertCircle, Clock } from 'lucide-react';

const KanbanBoard = ({ walls, currentWeek, onWallMove }) => {
  const [columns, setColumns] = useState([]);
  const [draggedWall, setDraggedWall] = useState(null);

  useEffect(() => {
    // Organise les murs dans les colonnes appropriées
    const unallocated = walls.filter(wall => !wall.allocation);
    const delayed = walls.filter(wall => {
      return wall.status === "EN_FABRICATION" && 
             wall.allocation && 
             wall.allocation < currentWeek;
    });
    
    // Créer les colonnes futures (12 semaines)
    const futureColumns = Array.from({ length: 12 }, (_, i) => ({
      id: currentWeek + i,
      title: `Semaine ${currentWeek + i}`,
      walls: walls.filter(w => w.allocation === currentWeek + i)
    }));

    setColumns([
      {
        id: 'unallocated',
        title: 'Non alloué',
        walls: unallocated
      },
      {
        id: 'delayed',
        title: 'Retard',
        walls: delayed
      },
      ...futureColumns
    ]);
  }, [walls, currentWeek]);

  const handleDragStart = (wall) => {
    setDraggedWall(wall);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (columnId) => {
    if (!draggedWall) return;

    // Convert columnId to number for week columns
    const targetWeek = columnId === 'unallocated' ? null : 
                      columnId === 'delayed' ? null : 
                      parseInt(columnId);

    onWallMove(draggedWall.id, targetWeek);
    setDraggedWall(null);
  };

  return (
    <div className="flex gap-4 overflow-x-auto p-4">
      {columns.map(column => (
        <div
          key={column.id}
          className="flex-none w-64 bg-gray-50 rounded-lg p-4"
          onDragOver={handleDragOver}
          onDrop={() => handleDrop(column.id)}
        >
          <div className="flex items-center gap-2 mb-4">
            {column.id === 'delayed' && <AlertCircle className="text-red-500" size={20} />}
            {column.id !== 'unallocated' && column.id !== 'delayed' && 
              <Clock className="text-blue-500" size={20} />}
            <h3 className="font-medium">{column.title}</h3>
          </div>

          <div className="space-y-2">
            {column.walls.map(wall => (
              <div
                key={wall.id}
                draggable
                onDragStart={() => handleDragStart(wall)}
                className="p-3 bg-white rounded shadow-sm cursor-move hover:shadow-md transition-shadow"
              >
                <div className="text-sm font-medium">
                  Mur n°{wall.numero} - {wall.modele.reference}
                </div>
                <div className="text-xs text-gray-500">
                  Status: {wall.status}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default KanbanBoard;