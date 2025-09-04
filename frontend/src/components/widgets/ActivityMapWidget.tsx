import React, { useState, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';

// Fix para iconos de Leaflet en React
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Interfaces TypeScript para los datos
interface CityActivity {
  id: string;
  name: string;
  region: string;
  latitude: number;
  longitude: number;
  sales: number;
  activeUsers: number;
  orders: number;
  activityLevel: 'high' | 'medium' | 'low';
}

// Datos mock de principales ciudades de Colombia
const COLOMBIA_CITIES: CityActivity[] = [
  {
    id: 'bogota',
    name: 'Bogotá',
    region: 'Cundinamarca',
    latitude: 4.7110,
    longitude: -74.0721,
    sales: 2500000,
    activeUsers: 45000,
    orders: 12500,
    activityLevel: 'high'
  },
  {
    id: 'medellin',
    name: 'Medellín',
    region: 'Antioquia',
    latitude: 6.2442,
    longitude: -75.5812,
    sales: 1800000,
    activeUsers: 32000,
    orders: 8900,
    activityLevel: 'high'
  },
  {
    id: 'cali',
    name: 'Cali',
    region: 'Valle del Cauca',
    latitude: 3.4516,
    longitude: -76.5320,
    sales: 1200000,
    activeUsers: 25000,
    orders: 6800,
    activityLevel: 'medium'
  },
  {
    id: 'barranquilla',
    name: 'Barranquilla',
    region: 'Atlántico',
    latitude: 10.9639,
    longitude: -74.7964,
    sales: 950000,
    activeUsers: 18500,
    orders: 5200,
    activityLevel: 'medium'
  },
  {
    id: 'cartagena',
    name: 'Cartagena',
    region: 'Bolívar',
    latitude: 10.4236,
    longitude: -75.5378,
    sales: 650000,
    activeUsers: 12000,
    orders: 3400,
    activityLevel: 'low'
  }
];

const ActivityMapWidget: React.FC = React.memo(() => {
  const [selectedCity, setSelectedCity] = useState<CityActivity | null>(null);
  const [activityFilter, setActivityFilter] = useState<'all' | 'sales' | 'users' | 'orders'>('all');
  const [periodFilter, setPeriodFilter] = useState<'week' | 'month' | 'quarter'>('month');
  
  // Centro de Colombia
  const colombiaCenter: [number, number] = [4.570868, -74.297333];
  
  // Calcular métricas totales
  const totalMetrics = useMemo(() => {
    return COLOMBIA_CITIES.reduce(
      (acc, city) => ({
        totalSales: acc.totalSales + city.sales,
        totalUsers: acc.totalUsers + city.activeUsers,
        totalOrders: acc.totalOrders + city.orders,
      }),
      { totalSales: 0, totalUsers: 0, totalOrders: 0 }
    );
  }, []);

  // Formatear números
  const formatNumber = (num: number): string => {
    return new Intl.NumberFormat('es-CO').format(num);
  };

  const formatCurrency = (num: number): string => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0
    }).format(num);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">
        Actividad por Región - Colombia
      </h2>
      
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Panel de métricas */}
        <div className="lg:w-1/3 space-y-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-medium text-blue-800 mb-2">Métricas Nacionales</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Ventas Totales:</span>
                <span className="font-medium">{formatCurrency(totalMetrics.totalSales)}</span>
              </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-medium text-gray-800 mb-3">Filtros</h3>
            
            <div className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Tipo de Actividad</label>
                <select 
                  value={activityFilter} 
                  onChange={(e) => setActivityFilter(e.target.value as any)}
                  className="w-full text-xs border rounded px-2 py-1 bg-white"
                >
                  <option value="all">Todas las Actividades</option>
                  <option value="sales">Solo Ventas</option>
                  <option value="users">Solo Usuarios</option>
                  <option value="orders">Solo Pedidos</option>
                </select>
              </div>
              
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Período</label>
                <select 
                  value={periodFilter} 
                  onChange={(e) => setPeriodFilter(e.target.value as any)}
                  className="w-full text-xs border rounded px-2 py-1 bg-white"
                >
                  <option value="week">Última Semana</option>
                  <option value="month">Último Mes</option>
                  <option value="quarter">Último Trimestre</option>
                </select>
              </div>
            </div>
          </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Usuarios Activos:</span>
                <span className="font-medium">{formatNumber(totalMetrics.totalUsers)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Pedidos:</span>
                <span className="font-medium">{formatNumber(totalMetrics.totalOrders)}</span>
              </div>
            </div>
          </div>

          {selectedCity && (
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="font-medium text-green-800 mb-2">{selectedCity.name}</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Región:</span>
                  <span className="font-medium">{selectedCity.region}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Ventas:</span>
                  <span className="font-medium">{formatCurrency(selectedCity.sales)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Usuarios:</span>
                  <span className="font-medium">{formatNumber(selectedCity.activeUsers)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Pedidos:</span>
                  <span className="font-medium">{formatNumber(selectedCity.orders)}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Contenedor del mapa */}
        <div className="lg:w-2/3">
          <div className="h-96 rounded-lg overflow-hidden border">
            <MapContainer
              center={colombiaCenter}
              zoom={6}
              className="h-full w-full"
            >
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              />
              
              {COLOMBIA_CITIES.map((city) => (
                <Marker
                  key={city.id}
                  position={[city.latitude, city.longitude]}
                  eventHandlers={{
                    click: () => setSelectedCity(city),
                  }}
                >
                  <Popup>
                    <div className="p-2">
                      <h3 className="font-semibold text-lg">{city.name}</h3>
                      <p className="text-sm text-gray-600 mb-2">{city.region}</p>
                      <div className="space-y-1 text-xs">
                        <div className="flex justify-between">
                          <span>Ventas:</span>
                          <span className="font-medium">{formatCurrency(city.sales)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Usuarios:</span>
                          <span className="font-medium">{formatNumber(city.activeUsers)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Pedidos:</span>
                          <span className="font-medium">{formatNumber(city.orders)}</span>
                        </div>
                      </div>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </div>
        </div>
      </div>
    </div>
  );
});

export default ActivityMapWidget;