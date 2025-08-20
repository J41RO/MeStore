import React from 'react';
import InventoryTableWithFilters from '../components/ui/InventoryTable/InventoryTableWithFilters';
import { useInventory } from '../hooks/useInventory';

const TestInventory: React.FC = () => {
  const { 
    totalItems, 
    lowStockItems, 
    outOfStockItems,
    isLoading 
  } = useInventory();

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-lg">Cargando inventario...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Sistema de Control de Inventario
        </h1>
        <p className="text-gray-600">
          Prueba del componente InventoryTable con filtros funcionales
        </p>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <h3 className="text-sm font-medium text-blue-600">Total Items</h3>
          <p className="text-2xl font-bold text-blue-900">{totalItems}</p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg border border-green-200">
          <h3 className="text-sm font-medium text-green-600">En Stock</h3>
          <p className="text-2xl font-bold text-green-900">
            {totalItems - lowStockItems - outOfStockItems}
          </p>
        </div>
        <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
          <h3 className="text-sm font-medium text-yellow-600">Stock Bajo</h3>
          <p className="text-2xl font-bold text-yellow-900">{lowStockItems}</p>
        </div>
        <div className="bg-red-50 p-4 rounded-lg border border-red-200">
          <h3 className="text-sm font-medium text-red-600">Sin Stock</h3>
          <p className="text-2xl font-bold text-red-900">{outOfStockItems}</p>
        </div>
      </div>

      {/* Tabla de inventario con filtros */}
      <div className="bg-white rounded-lg shadow">
        <InventoryTableWithFilters />
      </div>

      {/* Información de desarrollo */}
      <div className="mt-8 p-4 bg-gray-50 rounded-lg">
        <h3 className="text-lg font-semibold mb-2">Estado de Desarrollo</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium">Componentes:</span>
            <ul className="ml-4">
              <li>✅ InventoryTable - Tabla básica</li>
              <li>✅ InventoryTableWithFilters - Con filtros</li>
              <li>✅ useInventory - Hook personalizado</li>
            </ul>
          </div>
          <div>
            <span className="font-medium">Filtros Activos:</span>
            <ul className="ml-4">
              <li>✅ Filtro por estado</li>
              <li>✅ Filtro por ubicación</li>
              <li>✅ Búsqueda por texto</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TestInventory;