import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Stage, Layer, Rect, Text, Group, Line } from 'react-konva';
import { Save, Trash2, Move, Square, Settings, Grid } from 'lucide-react';

interface CustomZone {
  id: string;
  name: string;
  x: number;
  y: number;
  width: number;
  height: number;
  color: string;
  capacity: number;
  type: 'storage' | 'processing' | 'shipping' | 'receiving' | 'display' | 'custom';
}

interface WarehouseEditorProps {
  initialZones?: CustomZone[];
  canvasWidth?: number;
  canvasHeight?: number;
  onSave?: (zones: CustomZone[]) => void;
}

const ZONE_COLORS = [
  '#e3f2fd', // Azul claro
  '#f3e5f5', // Morado claro
  '#e8f5e8', // Verde claro
  '#fff3e0', // Naranja claro
  '#ffeb3b', // Amarillo
  '#fce4ec', // Rosa claro
  '#e0f2f1', // Verde agua
  '#f1f8e9'  // Verde lima
];

const ZONE_TYPES = [
  { value: 'storage', label: 'Almacenamiento', color: '#e3f2fd' },
  { value: 'processing', label: 'Procesamiento', color: '#e8f5e8' },
  { value: 'shipping', label: 'Envío', color: '#fff3e0' },
  { value: 'receiving', label: 'Recepción', color: '#ffeb3b' },
  { value: 'display', label: 'Exhibición', color: '#f1f8e9' },
  { value: 'custom', label: 'Personalizada', color: '#f3e5f5' }
];

const WarehouseEditor: React.FC<WarehouseEditorProps> = ({
  initialZones = [],
  canvasWidth = 800,
  canvasHeight = 600,
  onSave
}) => {
  const [zones, setZones] = useState<CustomZone[]>(initialZones);
  const [selectedZone, setSelectedZone] = useState<string | null>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [drawingStart, setDrawingStart] = useState<{x: number, y: number} | null>(null);
  const [mode, setMode] = useState<'select' | 'draw'>('select');
  const [showGrid, setShowGrid] = useState(true);
  const [selectedColor, setSelectedColor] = useState('#e3f2fd');
  const [selectedType, setSelectedType] = useState<CustomZone['type']>('storage');
  const [editingZone, setEditingZone] = useState<CustomZone | null>(null);
  
  const stageRef = useRef<any>(null);

  const generateId = () => Date.now().toString();

  const handleMouseDown = useCallback((e: any) => {
    if (mode === 'draw') {
      // Solo dibujar si hacemos click en el fondo del stage, no en una zona existente
      if (e.target === e.target.getStage()) {
        const pos = e.target.getStage().getPointerPosition();
        setDrawingStart(pos);
        setIsDrawing(true);
      }
    }
  }, [mode]);

  const handleMouseUp = useCallback((e: any) => {
    if (mode === 'draw' && isDrawing && drawingStart) {
      const pos = e.target.getStage().getPointerPosition();
      const width = Math.abs(pos.x - drawingStart.x);
      const height = Math.abs(pos.y - drawingStart.y);
      
      if (width > 30 && height > 30) {
        const zonesCount = zones.length + 1;
        const newZone: CustomZone = {
          id: generateId(),
          name: `Zona ${zonesCount}`,
          x: Math.min(pos.x, drawingStart.x),
          y: Math.min(pos.y, drawingStart.y),
          width,
          height,
          color: selectedColor,
          capacity: Math.floor((width * height) / 1000),
          type: selectedType
        };
        setZones(prev => [...prev, newZone]);
      }
      setIsDrawing(false);
      setDrawingStart(null);
    }
  }, [mode, isDrawing, drawingStart, zones.length, selectedColor, selectedType]);

  const handleZoneClick = (zoneId: string, e: any) => {
    if (mode === 'select') {
      e.cancelBubble = true; // Prevenir que el click se propague al stage
      setSelectedZone(zoneId);
      const zone = zones.find(z => z.id === zoneId);
      if (zone) {
        setEditingZone(zone);
      }
    }
  };

  const handleZoneDragEnd = (zoneId: string, e: any) => {
    const newX = e.target.x();
    const newY = e.target.y();
    
    setZones(prev => prev.map(z => 
      z.id === zoneId 
        ? {...z, x: newX, y: newY}
        : z
    ));
    
    // Actualizar también la zona en edición si es la misma
    if (editingZone && editingZone.id === zoneId) {
      setEditingZone(prev => prev ? {...prev, x: newX, y: newY} : null);
    }
  };

  const updateZone = (updatedZone: CustomZone) => {
    setZones(prev => prev.map(z => z.id === updatedZone.id ? updatedZone : z));
    setEditingZone(updatedZone);
  };

  const deleteZone = (zoneId: string) => {
    setZones(prev => prev.filter(z => z.id !== zoneId));
    setSelectedZone(null);
    setEditingZone(null);
  };

  const saveLayout = () => {
    if (onSave) {
      onSave(zones);
    }
    // Guardar en localStorage también
    localStorage.setItem('custom-warehouse-layout', JSON.stringify(zones));
    alert('Layout guardado exitosamente');
  };

  const loadLayout = () => {
    const saved = localStorage.getItem('custom-warehouse-layout');
    if (saved) {
      try {
        const loadedZones = JSON.parse(saved);
        setZones(loadedZones);
        alert('Layout cargado exitosamente');
      } catch (error) {
        alert('Error al cargar el layout guardado');
      }
    }
  };

  const clearCanvas = () => {
    if (confirm('¿Estás seguro de que quieres limpiar todo el canvas?')) {
      setZones([]);
      setSelectedZone(null);
      setEditingZone(null);
    }
  };

  // useEffect para eliminación con teclado
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Delete' || e.key === 'Backspace') {
        if (selectedZone && editingZone) {
          deleteZone(selectedZone);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedZone, editingZone]);

  // useEffect para mejorar cursores
  useEffect(() => {
    if (stageRef.current) {
      const stage = stageRef.current;
      const container = stage.container();
      if (container) {
        container.style.cursor = mode === 'draw' ? 'crosshair' : 'default';
      }
    }
  }, [mode]);

  return (
    <div className="warehouse-editor p-6 bg-gray-50 min-h-screen">
      <div className="header mb-6">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">
          Editor Personalizado del Almacén
        </h2>
        <p className="text-gray-600">
          Diseña tu layout exactamente como lo necesitas. Dibuja zonas, muévelas, personalízalas.
        </p>
      </div>

      {/* Toolbar Principal */}
      <div className="toolbar mb-6 p-4 bg-white rounded-lg shadow">
        <div className="flex flex-wrap gap-4 items-center">
          {/* Modo de trabajo */}
          <div className="mode-selector flex gap-2">
            <button
              onClick={() => setMode('select')}
              className={`btn px-4 py-2 rounded flex items-center gap-2 transition-all ${
                mode === 'select' ? 'bg-blue-500 text-white' : 'bg-gray-200 hover:bg-gray-300'
              }`}
            >
              <Move size={16} />
              Seleccionar
            </button>
            <button
              onClick={() => setMode('draw')}
              className={`btn px-4 py-2 rounded flex items-center gap-2 transition-all ${
                mode === 'draw' ? 'bg-green-500 text-white' : 'bg-gray-200 hover:bg-gray-300'
              }`}
            >
              <Square size={16} />
              Dibujar Zona
            </button>
          </div>

          <div className="w-px h-6 bg-gray-300"></div>

          {/* Tipo de zona */}
          <div className="zone-type">
            <label className="text-sm font-medium mr-2">Tipo:</label>
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value as CustomZone['type'])}
              className="px-3 py-1 border rounded text-sm"
            >
              {ZONE_TYPES.map(type => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Selector de color */}
          <div className="color-picker flex items-center gap-2">
            <label className="text-sm font-medium">Color:</label>
            <div className="flex gap-1">
              {ZONE_COLORS.map(color => (
                <button
                  key={color}
                  onClick={() => setSelectedColor(color)}
                  className={`w-6 h-6 rounded border-2 ${
                    selectedColor === color ? 'border-gray-800' : 'border-gray-300'
                  }`}
                  style={{ backgroundColor: color }}
                />
              ))}
            </div>
          </div>

          <div className="w-px h-6 bg-gray-300"></div>

          {/* Controles de canvas */}
          <div className="canvas-controls flex gap-2">
            <button
              onClick={() => setShowGrid(!showGrid)}
              className={`btn px-3 py-2 rounded flex items-center gap-2 ${
                showGrid ? 'bg-indigo-500 text-white' : 'bg-gray-200'
              }`}
            >
              <Grid size={16} />
              Grid
            </button>
          </div>

          <div className="w-px h-6 bg-gray-300"></div>

          {/* Acciones principales */}
          <div className="main-actions flex gap-2">
            <button
              onClick={saveLayout}
              className="btn bg-green-600 text-white px-4 py-2 rounded flex items-center gap-2 hover:bg-green-700"
            >
              <Save size={16} />
              Guardar
            </button>
            <button
              onClick={loadLayout}
              className="btn bg-blue-600 text-white px-4 py-2 rounded flex items-center gap-2 hover:bg-blue-700"
            >
              <Settings size={16} />
              Cargar
            </button>
            <button
              onClick={clearCanvas}
              className="btn bg-red-600 text-white px-4 py-2 rounded flex items-center gap-2 hover:bg-red-700"
            >
              <Trash2 size={16} />
              Limpiar
            </button>
          </div>
        </div>
      </div>

      {/* Área principal con canvas y panel de propiedades */}
      <div className="main-area grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Canvas */}
        <div className="canvas-section lg:col-span-3">
          <div className="canvas-container bg-white rounded-lg shadow-lg p-4">
            <div className="canvas-header mb-4">
              <h3 className="text-lg font-semibold">
                Canvas del Almacén ({canvasWidth}x{canvasHeight}px)
              </h3>
              <p className="text-sm text-gray-600">
                {mode === 'draw' 
                  ? 'Haz clic y arrastra para dibujar una nueva zona' 
                  : 'Haz clic en una zona para seleccionarla y editarla'
                }
              </p>
            </div>

            <div className="canvas-wrapper border-2 border-gray-200 rounded overflow-auto">
              <Stage
                ref={stageRef}
                width={canvasWidth}
                height={canvasHeight}
                onMouseDown={handleMouseDown}
                onMouseUp={handleMouseUp}
              >
                <Layer>
                  {/* Grid de fondo */}
                  {showGrid && (
                    <>
                      {Array.from({length: Math.floor(canvasWidth/50)}).map((_, i) => (
                        <Line
                          key={`vline-${i}`}
                          points={[i * 50, 0, i * 50, canvasHeight]}
                          stroke="#f0f0f0"
                          strokeWidth={1}
                          listening={false}
                        />
                      ))}
                      {Array.from({length: Math.floor(canvasHeight/50)}).map((_, i) => (
                        <Line
                          key={`hline-${i}`}
                          points={[0, i * 50, canvasWidth, i * 50]}
                          stroke="#f0f0f0"
                          strokeWidth={1}
                          listening={false}
                        />
                      ))}
                    </>
                  )}
                  
                  {/* Zonas dibujadas */}
                  {zones.map(zone => (
                    <Group key={zone.id}>
                      <Rect
                        x={zone.x}
                        y={zone.y}
                        width={zone.width}
                        height={zone.height}
                        fill={zone.color}
                        stroke={selectedZone === zone.id ? '#3b82f6' : '#666'}
                        strokeWidth={selectedZone === zone.id ? 3 : 1}
                        draggable={mode === 'select'}
                        onClick={(e) => handleZoneClick(zone.id, e)}
                        onDragEnd={(e) => handleZoneDragEnd(zone.id, e)}
                        shadowBlur={selectedZone === zone.id ? 10 : 0}
                        shadowColor="rgba(59, 130, 246, 0.3)"
                        onMouseEnter={(e) => {
                          if (mode === 'select') {
                            const stage = e.target.getStage();
                            const container = stage?.container();
                            if (container) container.style.cursor = 'move';
                          }
                        }}
                        onMouseLeave={(e) => {
                          const stage = e.target.getStage();
                          const container = stage?.container();
                          if (container) container.style.cursor = mode === 'draw' ? 'crosshair' : 'default';
                        }}
                      />
                      <Text
                        x={zone.x + 5}
                        y={zone.y + 5}
                        text={zone.name}
                        fontSize={12}
                        fill="#333"
                        fontStyle="bold"
                        listening={false}
                      />
                      <Text
                        x={zone.x + 5}
                        y={zone.y + zone.height - 35}
                        text={`Cap: ${zone.capacity}`}
                        fontSize={10}
                        fill="#666"
                        listening={false}
                      />
                      <Text
                        x={zone.x + 5}
                        y={zone.y + zone.height - 20}
                        text={`${zone.width}x${zone.height}`}
                        fontSize={9}
                        fill="#888"
                        listening={false}
                      />
                    </Group>
                  ))}
                </Layer>
              </Stage>
            </div>
          </div>
        </div>

        {/* Panel de propiedades */}
        <div className="properties-panel">
          <div className="bg-white rounded-lg shadow-lg p-4">
            <h3 className="text-lg font-semibold mb-4">Propiedades</h3>
            
            {editingZone ? (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Nombre</label>
                  <input
                    type="text"
                    value={editingZone.name}
                    onChange={(e) => updateZone({...editingZone, name: e.target.value})}
                    className="w-full p-2 border rounded text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Tipo</label>
                  <select
                    value={editingZone.type}
                    onChange={(e) => updateZone({...editingZone, type: e.target.value as CustomZone['type']})}
                    className="w-full p-2 border rounded text-sm"
                  >
                    {ZONE_TYPES.map(type => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Capacidad</label>
                  <input
                    type="number"
                    value={editingZone.capacity}
                    onChange={(e) => updateZone({...editingZone, capacity: parseInt(e.target.value) || 0})}
                    className="w-full p-2 border rounded text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Color</label>
                  <div className="grid grid-cols-4 gap-1">
                    {ZONE_COLORS.map(color => (
                      <button
                        key={color}
                        onClick={() => updateZone({...editingZone, color})}
                        className={`w-8 h-8 rounded border-2 ${
                          editingZone.color === color ? 'border-gray-800' : 'border-gray-300'
                        }`}
                        style={{ backgroundColor: color }}
                      />
                    ))}
                  </div>
                </div>

                <div className="pt-4 border-t">
                  <h4 className="font-medium mb-2">Dimensiones</h4>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-gray-600">X:</span> {Math.round(editingZone.x)}px
                    </div>
                    <div>
                      <span className="text-gray-600">Y:</span> {Math.round(editingZone.y)}px
                    </div>
                    <div>
                      <span className="text-gray-600">Ancho:</span> {Math.round(editingZone.width)}px
                    </div>
                    <div>
                      <span className="text-gray-600">Alto:</span> {Math.round(editingZone.height)}px
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => deleteZone(editingZone.id)}
                  className="w-full bg-red-500 text-white py-2 px-4 rounded flex items-center justify-center gap-2 hover:bg-red-600"
                >
                  <Trash2 size={16} />
                  Eliminar Zona
                </button>
              </div>
            ) : (
              <div className="text-center text-gray-500 py-8">
                <Square size={48} className="mx-auto mb-4 opacity-50" />
                <p>Selecciona una zona para editar sus propiedades</p>
              </div>
            )}
          </div>

          {/* Estadísticas */}
          <div className="mt-6 bg-white rounded-lg shadow-lg p-4">
            <h3 className="text-lg font-semibold mb-4">Estadísticas</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Zonas totales:</span>
                <span className="font-medium">{zones.length}</span>
              </div>
              <div className="flex justify-between">
                <span>Capacidad total:</span>
                <span className="font-medium">
                  {zones.reduce((sum, zone) => sum + zone.capacity, 0)} productos
                </span>
              </div>
              <div className="flex justify-between">
                <span>Área total:</span>
                <span className="font-medium">
                  {Math.round(zones.reduce((sum, zone) => sum + (zone.width * zone.height), 0) / 1000)} m²
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WarehouseEditor;