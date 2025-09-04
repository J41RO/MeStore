import React, { useState, useMemo } from 'react';
import { Package, Warehouse, Navigation, Archive } from 'lucide-react';

// Enums para las zonas del almacén (basados en inventory.types.ts)
enum LocationZone {
  WAREHOUSE_A = 'WAREHOUSE_A',
  WAREHOUSE_B = 'WAREHOUSE_B',
  DISPLAY_AREA = 'DISPLAY_AREA',
  STORAGE_ROOM = 'STORAGE_ROOM',
}

// Interfaces basadas en los tipos existentes del proyecto
interface LocationInfo {
  zone: LocationZone;
  aisle: string;
  shelf: string;
  position: string;
}

interface InventoryItem {
  id: string;
  name: string;
  sku: string;
  quantity: number;
  status: 'IN_STOCK' | 'LOW_STOCK' | 'OUT_OF_STOCK';
  location: LocationInfo;
}

interface LocationMapProps {
  items: InventoryItem[];
  onLocationClick?: (location: LocationInfo) => void;
  highlightedItems?: string[];
  showLegend?: boolean;
  showStatistics?: boolean;
  filterByZone?: LocationZone;
  filterByStatus?: 'IN_STOCK' | 'LOW_STOCK' | 'OUT_OF_STOCK';
  searchTerm?: string;
  className?: string;
}

const LocationMap: React.FC<LocationMapProps> = ({
  items = [],
  onLocationClick,
  showLegend = true,
  showStatistics = true,
  filterByZone,
  filterByStatus,
  searchTerm = '',
  className = '',
}) => {
  const [selectedLocation, setSelectedLocation] = useState<LocationInfo | null>(
    null
  );

  // Configuración de zonas con colores y layouts
  const zoneConfig = {
    [LocationZone.WAREHOUSE_A]: {
      name: 'Almacén A',
      color: 'bg-blue-50 border-blue-200',
      hoverColor: 'hover:bg-blue-100',
      rows: 4,
      cols: 6,
    },
    [LocationZone.WAREHOUSE_B]: {
      name: 'Almacén B',
      color: 'bg-green-50 border-green-200',
      hoverColor: 'hover:bg-green-100',
      rows: 4,
      cols: 6,
    },
    [LocationZone.DISPLAY_AREA]: {
      name: 'Área de Exhibición',
      color: 'bg-purple-50 border-purple-200',
      hoverColor: 'hover:bg-purple-100',
      rows: 2,
      cols: 8,
    },
    [LocationZone.STORAGE_ROOM]: {
      name: 'Sala de Almacenamiento',
      color: 'bg-orange-50 border-orange-200',
      hoverColor: 'hover:bg-orange-100',
      rows: 2,
      cols: 4,
    },
  };

  // Aplicar filtros
  const filteredItems = useMemo(() => {
    let filtered = items;

    if (filterByZone) {
      filtered = filtered.filter(item => item.location.zone === filterByZone);
    }

    if (filterByStatus) {
      filtered = filtered.filter(item => item.status === filterByStatus);
    }

    if (searchTerm) {
      filtered = filtered.filter(
        item =>
          item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          item.sku.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    return filtered;
  }, [items, filterByZone, filterByStatus, searchTerm]);

  // Procesar items por zona
  const itemsByZone = useMemo(() => {
    const zones = new Map<LocationZone, InventoryItem[]>();
    Object.values(LocationZone).forEach(zone => {
      zones.set(zone, []);
    });

    filteredItems.forEach(item => {
      const zoneItems = zones.get(item.location.zone) || [];
      zoneItems.push(item);
      zones.set(item.location.zone, zoneItems);
    });
    return zones;
  }, [filteredItems]);

  // Función para renderizar una zona específica
  const renderZone = (zone: LocationZone) => {
    const config = zoneConfig[zone];
    const zoneItems = itemsByZone.get(zone) || [];

    return (
      <div
        key={zone}
        className={`
          border-2 rounded-lg p-3 ${config.color}
          transition-all duration-200 ${config.hoverColor}
        `}
        style={{
          gridColumn: `span ${config.cols}`,
          gridRow: `span ${config.rows}`,
        }}
      >
        <div className='flex items-center justify-between mb-2'>
          <h4 className='font-semibold text-sm text-gray-700'>{config.name}</h4>
          <span className='text-xs bg-white px-2 py-1 rounded-full'>
            {zoneItems.length} productos
          </span>
        </div>

        {showStatistics && (
          <div className='flex items-center gap-3 text-xs text-gray-600 mb-1'>
            <span>
              Ocupación:{' '}
              {Math.round(
                (zoneItems.length /
                  (config.rows * Math.floor(config.cols / 2))) *
                  100
              )}
              %
            </span>
            <span>•</span>
            <span className='text-green-600'>
              {zoneItems.filter(i => i.status === 'IN_STOCK').length} En Stock
            </span>
            <span className='text-yellow-600'>
              {zoneItems.filter(i => i.status === 'LOW_STOCK').length} Bajo
            </span>
            <span className='text-red-600'>
              {zoneItems.filter(i => i.status === 'OUT_OF_STOCK').length}{' '}
              Agotado
            </span>
          </div>
        )}

        <div className='space-y-1'>
          {Array.from({ length: config.rows }, (_, aisleIdx) => (
            <div key={`aisle-${aisleIdx}`} className='flex items-center gap-1'>
              <div className='w-6 h-6 bg-gray-200 rounded text-xs flex items-center justify-center font-medium'>
                {String.fromCharCode(65 + aisleIdx)}
              </div>

              <div className='flex gap-1'>
                {Array.from(
                  { length: Math.floor(config.cols / 2) },
                  (_, shelfIdx) => {
                    const position = `${String.fromCharCode(65 + aisleIdx)}-${shelfIdx + 1}`;
                    const item = zoneItems.find(
                      item =>
                        item.location.aisle ===
                          String.fromCharCode(65 + aisleIdx) &&
                        item.location.shelf === (shelfIdx + 1).toString()
                    );

                    return (
                      <div
                        key={position}
                        className={`
                        w-8 h-6 border border-gray-300 rounded cursor-pointer
                        flex items-center justify-center text-xs transition-all duration-200
                        ${
                          item
                            ? item.status === 'IN_STOCK'
                              ? 'bg-green-100 border-green-300'
                              : item.status === 'LOW_STOCK'
                                ? 'bg-yellow-100 border-yellow-300'
                                : 'bg-red-100 border-red-300'
                            : 'bg-gray-50 hover:bg-gray-100'
                        }
                        hover:scale-110 hover:shadow-sm
                      `}
                        onClick={() => {
                          if (item) {
                            setSelectedLocation(item.location);
                            onLocationClick?.(item.location);
                          } else {
                            const emptyLocation: LocationInfo = {
                              zone,
                              aisle: String.fromCharCode(65 + aisleIdx),
                              shelf: (shelfIdx + 1).toString(),
                              position: position,
                            };
                            setSelectedLocation(emptyLocation);
                          }
                        }}
                        title={
                          item
                            ? `${item.name}\nStock: ${item.quantity}\nPasillo: ${item.location.aisle}\nEstante: ${item.location.shelf}`
                            : `Posición ${position} - Libre`
                        }
                      >
                        {item ? (
                          <Package className='w-3 h-3' />
                        ) : (
                          <span className='text-gray-400 text-xs'>
                            {shelfIdx + 1}
                          </span>
                        )}
                      </div>
                    );
                  }
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className={`p-4 ${className}`}>
      <div className='flex items-center justify-between mb-4'>
        <div className='flex items-center gap-2'>
          <Warehouse className='w-6 h-6 text-blue-600' />
          <h3 className='text-xl font-bold text-gray-800'>Mapa del Almacén</h3>
          <Navigation className='w-5 h-5 text-gray-500' />
        </div>
        <div className='flex items-center gap-2 text-sm text-gray-600'>
          <Archive className='w-4 h-4' />
          <span>{items.length} productos totales</span>
        </div>
      </div>

      {showLegend && (
        <div className='grid grid-cols-2 md:grid-cols-4 gap-3 mb-4 text-sm'>
          <div className='flex items-center gap-2'>
            <div className='w-4 h-4 bg-blue-50 border-2 border-blue-200 rounded'></div>
            <span>Almacén A</span>
          </div>
          <div className='flex items-center gap-2'>
            <div className='w-4 h-4 bg-green-50 border-2 border-green-200 rounded'></div>
            <span>Almacén B</span>
          </div>
          <div className='flex items-center gap-2'>
            <div className='w-4 h-4 bg-purple-50 border-2 border-purple-200 rounded'></div>
            <span>Área Exhibición</span>
          </div>
          <div className='flex items-center gap-2'>
            <div className='w-4 h-4 bg-orange-50 border-2 border-orange-200 rounded'></div>
            <span>Sala Almacén</span>
          </div>
        </div>
      )}

      <div className='bg-white p-4 rounded-lg shadow-sm border-2 border-gray-300'>
        <div className='grid grid-cols-12 grid-rows-6 gap-2 min-h-[400px]'>
          {Object.values(LocationZone).map(zone => renderZone(zone))}
        </div>
      </div>

      {selectedLocation && (
        <div className='mt-4 p-4 bg-white border-2 border-blue-200 rounded-lg shadow-sm'>
          <div className='flex items-center justify-between mb-2'>
            <h4 className='font-semibold text-gray-800'>
              Información de Ubicación
            </h4>
            <button
              onClick={() => setSelectedLocation(null)}
              className='text-gray-500 hover:text-gray-700'
            >
              ✕
            </button>
          </div>
          <div className='grid grid-cols-2 gap-4 text-sm'>
            <div>
              <span className='font-medium'>Zona:</span>
              <span className='ml-2'>{selectedLocation.zone}</span>
            </div>
            <div>
              <span className='font-medium'>Pasillo:</span>
              <span className='ml-2'>{selectedLocation.aisle}</span>
            </div>
            <div>
              <span className='font-medium'>Estante:</span>
              <span className='ml-2'>{selectedLocation.shelf}</span>
            </div>
            <div>
              <span className='font-medium'>Posición:</span>
              <span className='ml-2'>{selectedLocation.position}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LocationMap;
