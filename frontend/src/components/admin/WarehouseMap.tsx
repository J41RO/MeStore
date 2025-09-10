import React, { useState, useRef, useEffect } from 'react';
import { Stage, Layer, Rect, Text, Group } from 'react-konva';
import { Home, Building, Factory, Settings, ZoomIn, ZoomOut, RotateCcw, Save, MapPin } from 'lucide-react';
import WarehouseEditor from './WarehouseEditor';
import LocationManager from './LocationManager';

// Interfaces para el sistema escalable
interface WarehouseTemplate {
  id: string;
  name: string;
  description: string;
  dimensions: { width: number; height: number };
  zones: WarehouseZone[];
  icon: React.ReactNode;
  recommendedFor: string;
  businessPhase: 'startup' | 'growth' | 'expansion';
}

interface WarehouseZone {
  id: string;
  name: string;
  x: number;
  y: number;
  width: number;
  height: number;
  color: string;
  capacity: number;
  type: 'storage' | 'processing' | 'shipping' | 'receiving' | 'display';
  currentOccupancy?: number;
}

interface WarehouseConfig {
  currentTemplate: string;
  customZones: WarehouseZone[];
  businessInfo: {
    currentPhase: 'startup' | 'growth' | 'expansion';
    location: string;
    plannedGrowth: string;
    startDate: string;
  };
  lastModified: string;
}

// Templates escalables para diferentes fases del negocio
const WAREHOUSE_TEMPLATES: WarehouseTemplate[] = [
  {
    id: 'room',
    name: 'Habitación',
    description: 'Espacio inicial - habitación de apartamento',
    dimensions: { width: 500, height: 350 },
    icon: <Home size={20} />,
    recommendedFor: 'Inicio del negocio, 1-50 productos',
    businessPhase: 'startup',
    zones: [
      {
        id: 'main-storage',
        name: 'Área Principal',
        x: 50, y: 50, width: 220, height: 150,
        color: '#e3f2fd', capacity: 30, type: 'storage'
      },
      {
        id: 'corner-storage',
        name: 'Rincón Almacenaje',
        x: 300, y: 50, width: 150, height: 120,
        color: '#f3e5f5', capacity: 20, type: 'storage'
      },
      {
        id: 'packing-desk',
        name: 'Mesa Empaque',
        x: 50, y: 220, width: 180, height: 80,
        color: '#e8f5e8', capacity: 10, type: 'processing'
      },
      {
        id: 'display-area',
        name: 'Área Exhibición',
        x: 300, y: 190, width: 150, height: 110,
        color: '#fff3e0', capacity: 15, type: 'display'
      }
    ]
  },
  {
    id: 'small-warehouse',
    name: 'Depósito Pequeño',
    description: 'Depósito comercial 50-100 m²',
    dimensions: { width: 700, height: 500 },
    icon: <Building size={20} />,
    recommendedFor: 'Crecimiento medio, 100-500 productos',
    businessPhase: 'growth',
    zones: [
      {
        id: 'receiving-dock',
        name: 'Área Recepción',
        x: 50, y: 50, width: 180, height: 100,
        color: '#ffeb3b', capacity: 50, type: 'receiving'
      },
      {
        id: 'storage-section-a',
        name: 'Almacén A',
        x: 260, y: 50, width: 180, height: 180,
        color: '#e3f2fd', capacity: 200, type: 'storage'
      },
      {
        id: 'storage-section-b',
        name: 'Almacén B',
        x: 470, y: 50, width: 180, height: 180,
        color: '#f3e5f5', capacity: 200, type: 'storage'
      },
      {
        id: 'processing-zone',
        name: 'Área Empaque',
        x: 50, y: 180, width: 180, height: 120,
        color: '#e8f5e8', capacity: 40, type: 'processing'
      },
      {
        id: 'shipping-dock',
        name: 'Área Envío',
        x: 50, y: 330, width: 180, height: 120,
        color: '#fff3e0', capacity: 60, type: 'shipping'
      },
      {
        id: 'display-showroom',
        name: 'Sala Exhibición',
        x: 260, y: 260, width: 390, height: 190,
        color: '#f1f8e9', capacity: 80, type: 'display'
      }
    ]
  },
  {
    id: 'large-warehouse',
    name: 'Almacén Industrial',
    description: 'Almacén grande 200+ m²',
    dimensions: { width: 900, height: 650 },
    icon: <Factory size={20} />,
    recommendedFor: 'Expansión completa, 1000+ productos',
    businessPhase: 'expansion',
    zones: [
      {
        id: 'main-receiving',
        name: 'Recepción Principal',
        x: 50, y: 50, width: 200, height: 120,
        color: '#ffeb3b', capacity: 100, type: 'receiving'
      },
      {
        id: 'bulk-storage-1',
        name: 'Almacén Masivo 1',
        x: 280, y: 50, width: 250, height: 200,
        color: '#e3f2fd', capacity: 500, type: 'storage'
      },
      {
        id: 'bulk-storage-2',
        name: 'Almacén Masivo 2',
        x: 560, y: 50, width: 250, height: 200,
        color: '#f3e5f5', capacity: 500, type: 'storage'
      },
      {
        id: 'processing-center',
        name: 'Centro Procesamiento',
        x: 50, y: 200, width: 200, height: 150,
        color: '#e8f5e8', capacity: 80, type: 'processing'
      },
      {
        id: 'quality-control',
        name: 'Control Calidad',
        x: 280, y: 280, width: 150, height: 100,
        color: '#fce4ec', capacity: 30, type: 'processing'
      },
      {
        id: 'main-shipping',
        name: 'Envío Principal',
        x: 50, y: 380, width: 200, height: 120,
        color: '#fff3e0', capacity: 120, type: 'shipping'
      },
      {
        id: 'showroom-large',
        name: 'Showroom Grande',
        x: 280, y: 410, width: 530, height: 190,
        color: '#f1f8e9', capacity: 200, type: 'display'
      }
    ]
  }
];

const WarehouseMap: React.FC = () => {
  const [selectedTemplate, setSelectedTemplate] = useState<string>('room');
  const [scale, setScale] = useState(1);
  const [editMode, setEditMode] = useState(false);
  const [activeTab, setActiveTab] = useState<'templates' | 'custom' | 'locations'>('templates');
  // Removed unused selectedInventoryForLocation state
  const [showLocationManager, setShowLocationManager] = useState(false);
  const [config, setConfig] = useState<WarehouseConfig>({
    currentTemplate: 'room',
    customZones: [],
    businessInfo: {
      currentPhase: 'startup',
      location: '',
      plannedGrowth: '',
      startDate: new Date().toISOString().split('T')[0] || ''
    },
    lastModified: new Date().toISOString()
  });

  const stageRef = useRef<any>(null);
  
  const currentTemplate = WAREHOUSE_TEMPLATES.find(t => t.id === selectedTemplate);
  
  // Cargar configuración guardada al inicializar
  useEffect(() => {
    const savedConfig = localStorage.getItem('mestocker-warehouse-config');
    if (savedConfig) {
      try {
        const parsed = JSON.parse(savedConfig);
        setConfig(parsed);
        setSelectedTemplate(parsed.currentTemplate);
      } catch (error) {
        console.error('Error loading saved config:', error);
      }
    }
  }, []);

  // Funciones de control de vista
  const resetView = () => {
    setScale(1);
    if (stageRef.current) {
      stageRef.current.position({ x: 0, y: 0 });
      stageRef.current.batchDraw();
    }
  };

  const zoomIn = () => setScale(s => Math.min(s * 1.2, 3));
  const zoomOut = () => setScale(s => Math.max(s / 1.2, 0.3));

  // Guardar configuración
  const saveConfiguration = () => {
    const updatedConfig = {
      ...config,
      currentTemplate: selectedTemplate,
      lastModified: new Date().toISOString()
    };
    setConfig(updatedConfig);
    localStorage.setItem('mestocker-warehouse-config', JSON.stringify(updatedConfig));
    alert('Configuración guardada exitosamente');
  };

  // Cambiar template y actualizar configuración
  const handleTemplateChange = (templateId: string) => {
    setSelectedTemplate(templateId);
    const template = WAREHOUSE_TEMPLATES.find(t => t.id === templateId);
    if (template) {
      setConfig(prev => ({
        ...prev,
        currentTemplate: templateId,
        businessInfo: {
          ...prev.businessInfo,
          currentPhase: template.businessPhase
        }
      }));
    }
  };

  // Calcular estadísticas del almacén
  const totalCapacity = currentTemplate?.zones.reduce((total, zone) => total + zone.capacity, 0) || 0;
  const storageZones = currentTemplate?.zones.filter(zone => zone.type === 'storage') || [];
  const storageCapacity = storageZones.reduce((total, zone) => total + zone.capacity, 0);

  return (
    <div className="warehouse-map-container p-6 bg-gray-50 min-h-screen">
      <div className="header mb-6">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">
          Mapa del Almacén - Sistema Escalable
        </h2>
        <p className="text-gray-600">
          Diseña y gestiona tu espacio de almacenamiento desde habitación hasta almacén industrial
        </p>
      </div>

      {/* Sistema de Pestañas */}
      <div className="tabs-container mb-6">
        <div className="flex border-b border-gray-200 bg-white rounded-t-lg">
          <button
            onClick={() => setActiveTab('templates')}
            className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'templates'
                ? 'border-blue-500 text-blue-600 bg-blue-50'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Templates Predefinidos
          </button>
          <button
            onClick={() => setActiveTab('custom')}
            className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'custom'
                ? 'border-green-500 text-green-600 bg-green-50'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Editor Personalizado
          </button>
          <button
            onClick={() => setActiveTab('locations')}
            className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'locations'
                ? 'border-purple-500 text-purple-600 bg-purple-50'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <MapPin size={16} className="inline mr-1" />
            Gestión de Ubicaciones
          </button>
        </div>
      </div>

      {/* Contenido condicional según pestaña activa */}
      {activeTab === 'templates' ? (
        <>
          {/* Configuración del Negocio */}
          <div className="business-config mb-6 p-4 bg-white rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-3">Configuración del Negocio</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Ubicación Actual</label>
                <input
                  type="text"
                  value={config.businessInfo.location}
                  onChange={(e) => setConfig(prev => ({
                    ...prev,
                    businessInfo: { ...prev.businessInfo, location: e.target.value }
                  }))}
                  placeholder="Ej: Habitación en Bucaramanga"
                  className="w-full p-2 border rounded text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Fase del Negocio</label>
                <select
                  value={config.businessInfo.currentPhase}
                  onChange={(e) => setConfig(prev => ({
                    ...prev,
                    businessInfo: { ...prev.businessInfo, currentPhase: e.target.value as any }
                  }))}
                  className="w-full p-2 border rounded text-sm"
                >
                  <option value="startup">Inicio (Habitación)</option>
                  <option value="growth">Crecimiento (Depósito)</option>
                  <option value="expansion">Expansión (Industrial)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Plan de Crecimiento</label>
                <input
                  type="text"
                  value={config.businessInfo.plannedGrowth}
                  onChange={(e) => setConfig(prev => ({
                    ...prev,
                    businessInfo: { ...prev.businessInfo, plannedGrowth: e.target.value }
                  }))}
                  placeholder="Ej: Depósito en 6 meses"
                  className="w-full p-2 border rounded text-sm"
                />
              </div>
            </div>
          </div>

          {/* Selector de Templates */}
          <div className="template-selector mb-6 p-4 bg-white rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-3">Selecciona tu Espacio de Almacenamiento</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {WAREHOUSE_TEMPLATES.map(template => (
                <button
                  key={template.id}
                  onClick={() => handleTemplateChange(template.id)}
                  className={`p-4 rounded-lg border-2 transition-all text-left ${
                    selectedTemplate === template.id 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    {template.icon}
                    <span className="font-medium">{template.name}</span>
                  </div>
                  <p className="text-sm text-gray-600 mb-1">{template.description}</p>
                  <p className="text-xs text-blue-600 font-medium">{template.recommendedFor}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Estadísticas del Almacén */}
          <div className="stats-panel mb-6 grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="stat-card p-3 bg-white rounded-lg shadow text-center">
              <h4 className="text-sm font-medium text-gray-600">Capacidad Total</h4>
              <p className="text-2xl font-bold text-blue-600">{totalCapacity}</p>
              <p className="text-xs text-gray-500">productos</p>
            </div>
            <div className="stat-card p-3 bg-white rounded-lg shadow text-center">
              <h4 className="text-sm font-medium text-gray-600">Zonas de Almacén</h4>
              <p className="text-2xl font-bold text-green-600">{storageZones.length}</p>
              <p className="text-xs text-gray-500">áreas</p>
            </div>
            <div className="stat-card p-3 bg-white rounded-lg shadow text-center">
              <h4 className="text-sm font-medium text-gray-600">Cap. Almacenamiento</h4>
              <p className="text-2xl font-bold text-purple-600">{storageCapacity}</p>
              <p className="text-xs text-gray-500">productos</p>
            </div>
            <div className="stat-card p-3 bg-white rounded-lg shadow text-center">
              <h4 className="text-sm font-medium text-gray-600">Zonas Totales</h4>
              <p className="text-2xl font-bold text-orange-600">{currentTemplate?.zones.length || 0}</p>
              <p className="text-xs text-gray-500">áreas</p>
            </div>
          </div>

          {/* Área del Canvas - SOLO para templates */}
          <div className="canvas-container bg-white rounded-lg shadow-lg p-4">
            {/* Controles */}
            <div className="controls mb-4 flex gap-2 flex-wrap items-center">
              <button 
                onClick={zoomIn}
                className="btn bg-blue-500 text-white px-3 py-2 rounded flex items-center gap-1 hover:bg-blue-600"
              >
                <ZoomIn size={16} />
                Zoom +
              </button>
              <button 
                onClick={zoomOut}
                className="btn bg-blue-500 text-white px-3 py-2 rounded flex items-center gap-1 hover:bg-blue-600"
              >
                <ZoomOut size={16} />
                Zoom -
              </button>
              <button 
                onClick={resetView}
                className="btn bg-gray-500 text-white px-3 py-2 rounded flex items-center gap-1 hover:bg-gray-600"
              >
                <RotateCcw size={16} />
                Reset Vista
              </button>
              <button 
                onClick={() => setEditMode(!editMode)}
                className="btn bg-green-500 text-white px-3 py-2 rounded flex items-center gap-1 hover:bg-green-600"
              >
                <Settings size={16} />
                {editMode ? 'Modo Vista' : 'Modo Edición'}
              </button>
              <button 
                onClick={saveConfiguration}
                className="btn bg-indigo-500 text-white px-3 py-2 rounded flex items-center gap-1 hover:bg-indigo-600"
              >
                <Save size={16} />
                Guardar Config
              </button>
              <div className="ml-auto text-sm text-gray-500">
                Escala: {Math.round(scale * 100)}%
              </div>
            </div>

            {/* Canvas */}
            <div className="canvas-wrapper border-2 border-gray-200 rounded overflow-auto">
              <Stage 
                ref={stageRef}
                width={Math.max(currentTemplate?.dimensions.width || 500, 600)} 
                height={Math.max(currentTemplate?.dimensions.height || 350, 400)}
                scaleX={scale}
                scaleY={scale}
                draggable={!editMode}
              >
                <Layer>
                  {/* Fondo del almacén */}
                  <Rect
                    x={0} y={0}
                    width={currentTemplate?.dimensions.width || 500}
                    height={currentTemplate?.dimensions.height || 350}
                    fill="#f8f9fa"
                    stroke="#dee2e6"
                    strokeWidth={2}
                  />
                  
                  {/* Título del almacén */}
                  <Text
                    x={20} y={15}
                    text={`${currentTemplate?.name} - MeStocker Bucaramanga`}
                    fontSize={16}
                    fill="#495057"
                    fontStyle="bold"
                  />

                  {/* Renderizar zonas */}
                  {currentTemplate?.zones.map(zone => (
                    <Group key={zone.id}>
                      <Rect
                        x={zone.x} y={zone.y}
                        width={zone.width} height={zone.height}
                        fill={zone.color}
                        stroke="#666"
                        strokeWidth={1}
                        draggable={editMode}
                        shadowBlur={editMode ? 5 : 0}
                        shadowColor="gray"
                      />
                      <Text
                        x={zone.x + 5} y={zone.y + 5}
                        text={zone.name}
                        fontSize={12}
                        fill="#333"
                        fontStyle="bold"
                      />
                      <Text
                        x={zone.x + 5} y={zone.y + zone.height - 45}
                        text={`Capacidad: ${zone.capacity}`}
                        fontSize={10}
                        fill="#666"
                      />
                      <Text
                        x={zone.x + 5} y={zone.y + zone.height - 30}
                        text={`Tipo: ${zone.type}`}
                        fontSize={9}
                        fill="#888"
                      />
                      <Text
                        x={zone.x + 5} y={zone.y + zone.height - 15}
                        text={`${zone.width}x${zone.height}px`}
                        fontSize={8}
                        fill="#aaa"
                      />
                    </Group>
                  ))}
                </Layer>
              </Stage>
            </div>
          </div>

          {/* Detalles de las Zonas */}
          <div className="zone-details mt-6">
            <h3 className="text-lg font-semibold mb-4">Detalles de las Zonas</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {currentTemplate?.zones.map(zone => (
                <div key={zone.id} className="zone-card p-4 bg-white rounded-lg shadow hover:shadow-md transition-shadow">
                  <div className="flex items-center gap-3 mb-3">
                    <div 
                      className="zone-color w-6 h-6 rounded" 
                      style={{ backgroundColor: zone.color }}
                    ></div>
                    <h5 className="font-semibold text-gray-800">{zone.name}</h5>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Capacidad:</span>
                      <span className="font-medium">{zone.capacity} productos</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Tipo:</span>
                      <span className="font-medium capitalize">{zone.type}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Dimensiones:</span>
                      <span className="font-medium">{zone.width}x{zone.height}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Posición:</span>
                      <span className="font-medium">({zone.x}, {zone.y})</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Roadmap de Crecimiento */}
          <div className="growth-roadmap mt-6 p-4 bg-white rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Roadmap de Crecimiento</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {WAREHOUSE_TEMPLATES.map((template, index) => (
                <div key={template.id} className={`roadmap-step p-3 rounded border-2 ${
                  selectedTemplate === template.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                }`}>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-lg font-bold text-gray-500">#{index + 1}</span>
                    {template.icon}
                    <span className="font-medium">{template.name}</span>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{template.description}</p>
                  <div className="text-xs text-gray-500">
                    <div>Capacidad: {template.zones.reduce((sum, zone) => sum + zone.capacity, 0)} productos</div>
                    <div>Zonas: {template.zones.length} áreas</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      ) : activeTab === 'custom' ? (
        /* Editor Personalizado */
        <WarehouseEditor
          canvasWidth={800}
          canvasHeight={600}
          onSave={(zones) => {
            setConfig(prev => ({
              ...prev,
              customZones: zones as WarehouseZone[],
              lastModified: new Date().toISOString()
            }));
          }}
        />
      ) : (
        /* Gestión de Ubicaciones */
        <div className="locations-management">
          <div className="mb-6 p-4 bg-white rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <MapPin size={20} />
              Gestión de Ubicaciones de Inventario
            </h3>
            <p className="text-gray-600 mb-4">
              Asigna y reasigna ubicaciones específicas de productos en el almacén. 
              Selecciona un producto del inventario para cambiar su ubicación.
            </p>
            
            {!showLocationManager ? (
              <div className="text-center py-8">
                <MapPin size={48} className="mx-auto text-gray-400 mb-4" />
                <p className="text-gray-500 mb-4">
                  Selecciona un producto del inventario para gestionar su ubicación
                </p>
                <button 
                  onClick={() => setShowLocationManager(true)}
                  className="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600 flex items-center gap-2 mx-auto"
                >
                  <MapPin size={16} />
                  Abrir Selector de Inventario
                </button>
              </div>
            ) : (
              <LocationManager
                inventoryItem={{
                  id: '1',
                  productId: '1',
                  productName: 'Producto de Ejemplo',
                  sku: 'SKU-001',
                  quantity: 10,
                  minStock: 5,
                  maxStock: 50,
                  status: 'IN_STOCK' as any,
                  location: {
                    zone: 'WAREHOUSE_A' as any,
                    aisle: 'A1',
                    shelf: '01',
                    position: '01'
                  },
                  lastUpdated: new Date(),
                  cost: 100
                }}
                availableLocations={[]}
                onLocationUpdate={async (itemId: string, newLocation: any, observaciones?: string) => {
                  console.log('Ubicación actualizada:', itemId, newLocation, observaciones);
                  setShowLocationManager(false);
                  return true;
                }}
                onClose={() => setShowLocationManager(false)}
              />
            )}
          </div>
          
          {/* Mapa Visual de Ubicaciones */}
          <div className="location-visual-map bg-white rounded-lg shadow p-4">
            <h4 className="text-md font-semibold mb-4">Mapa Visual de Ubicaciones</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {currentTemplate?.zones
                .filter(zone => zone.type === 'storage')
                .map(zone => (
                  <div key={zone.id} className="zone-location-card p-4 border rounded-lg hover:shadow-md">
                    <div className="flex items-center gap-2 mb-2">
                      <div 
                        className="w-4 h-4 rounded" 
                        style={{ backgroundColor: zone.color }}
                      ></div>
                      <h5 className="font-medium">{zone.name}</h5>
                    </div>
                    <div className="text-sm text-gray-600 space-y-1">
                      <div>Capacidad: {zone.capacity} productos</div>
                      <div>Ocupación: 0 productos (0%)</div>
                      <div>Ubicaciones disponibles: {zone.capacity}</div>
                    </div>
                    <div className="mt-3">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-500 h-2 rounded-full" 
                          style={{ width: '0%' }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WarehouseMap;