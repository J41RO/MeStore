



import React, { useState, useMemo } from 'react';
import { StockMovement, StockMovementFilters, MovementType, MovementReason, LocationZone } from '../../../types/inventory.types';

// Datos mock para testing
const mockMovements: StockMovement[] = [
  {
    id: '1',
    productId: 'PROD001',
    productName: 'Laptop Dell XPS',
    sku: 'LT-DELL-001',
    type: MovementType.ENTRADA,
    reason: MovementReason.COMPRA,
    quantity: 10,
    previousStock: 15,
    newStock: 25,
    location: { zone: LocationZone.WAREHOUSE_A, aisle: 'A1', shelf: 'S1', position: 'P1' },
    userId: 'USER001',
    userName: 'Admin Usuario',
    notes: 'Compra de reposición',
    timestamp: new Date(),
    cost: 12000,
    reference: 'ORD-2025-001'
  },
  {
    id: '2',
    productId: 'PROD002',
    productName: 'Mouse Logitech',
    sku: 'MS-LOG-002',
    type: MovementType.SALIDA,
    reason: MovementReason.VENTA,
    quantity: 3,
    previousStock: 8,
    newStock: 5,
    location: { zone: LocationZone.DISPLAY_AREA, aisle: 'B2', shelf: 'S3', position: 'P2' },
    userId: 'USER002',
    userName: 'Vendedor 1',
    timestamp: new Date(),
    reference: 'VT-2025-001'
  }
];

interface StockMovementsProps {
  movements?: StockMovement[];
}

const StockMovements: React.FC<StockMovementsProps> = ({
  movements = mockMovements,
}) => {
  const [filters, setFilters] = useState<StockMovementFilters>({});
  const [_showAddForm, _setShowAddForm] = useState(false);

  const filteredMovements = useMemo(() => {
    return movements.filter(movement => {
      // Filtro por tipo
      if (filters.type && filters.type.length > 0) {
        if (!filters.type.includes(movement.type)) return false;
      }

      // Filtro por razón
      if (filters.reason && filters.reason.length > 0) {
        if (!filters.reason.includes(movement.reason)) return false;
      }

      // Filtro por ubicación
      if (filters.location && filters.location.length > 0) {
        if (!filters.location.includes(movement.location.zone)) return false;
      }

      // Filtro por búsqueda
      if (filters.searchTerm) {
        const searchLower = filters.searchTerm.toLowerCase();
        if (
          movement.productName.toLowerCase().indexOf(searchLower) === -1 &&
          movement.sku.toLowerCase().indexOf(searchLower) === -1 &&
          (movement.reference || '').toLowerCase().indexOf(searchLower) === -1
        ) return false;
      }

      return true;
    });
  }, [movements, filters]);

  return (
    <div className="w-full space-y-4">
      {/* Header con botón agregar */}
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-800">
          Movimientos de Stock
        </h2>
        <button
          onClick={() => _setShowAddForm(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Registrar Movimiento
        </button>
      </div>

      {/* Filtros */}
      <div className="p-4 bg-gray-50 rounded-lg">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tipo
            </label>
            <select
              className="w-full border border-gray-300 rounded-md px-3 py-2"
              onChange={(e) => setFilters({
                ...filters,
                type: e.target.value ? [e.target.value as MovementType] : undefined
              })}
            >
              <option value="">Todos los tipos</option>
              <option value={MovementType.ENTRADA}>Entrada</option>
              <option value={MovementType.SALIDA}>Salida</option>
              <option value={MovementType.AJUSTE}>Ajuste</option>
              <option value={MovementType.TRANSFERENCIA}>Transferencia</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Razón
            </label>
            <select
              className="w-full border border-gray-300 rounded-md px-3 py-2"
              onChange={(e) => setFilters({
                ...filters,
                reason: e.target.value ? [e.target.value as MovementReason] : undefined
              })}
            >
              <option value="">Todas las razones</option>
              <option value={MovementReason.COMPRA}>Compra</option>
              <option value={MovementReason.VENTA}>Venta</option>
              <option value={MovementReason.DEVOLUCION}>Devolución</option>
              <option value={MovementReason.MERMA}>Merma</option>
              <option value={MovementReason.AJUSTE_INVENTARIO}>Ajuste</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Ubicación
            </label>
            <select
              className="w-full border border-gray-300 rounded-md px-3 py-2"
              onChange={(e) => setFilters({
                ...filters,
                location: e.target.value ? [e.target.value as LocationZone] : undefined
              })}
            >
              <option value="">Todas las ubicaciones</option>
              <option value={LocationZone.WAREHOUSE_A}>Almacén A</option>
              <option value={LocationZone.WAREHOUSE_B}>Almacén B</option>
              <option value={LocationZone.DISPLAY_AREA}>Área de Exhibición</option>
              <option value={LocationZone.STORAGE_ROOM}>Sala de Almacenamiento</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Buscar
            </label>
            <input
              type="text"
              placeholder="Producto, SKU o referencia"
              className="w-full border border-gray-300 rounded-md px-3 py-2"
              onChange={(e) => setFilters({
                ...filters,
                searchTerm: e.target.value || undefined
              })}
            />
          </div>
        </div>
      </div>

      {/* Tabla de movimientos */}
      <div className="w-full overflow-x-auto">
        <table className="min-w-full bg-white border border-gray-200 rounded-lg">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Fecha
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Producto
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Tipo
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Cantidad
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Stock
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Usuario
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Referencia
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {filteredMovements.map((movement) => (
              <tr key={movement.id} className="hover:bg-gray-50">
                <td className="px-4 py-4 text-sm text-gray-900">
                  {movement.timestamp.toLocaleDateString()}
                </td>
                <td className="px-4 py-4 text-sm">
                  <div>
                    <div className="text-gray-900">{movement.productName}</div>
                    <div className="text-gray-500 text-xs">{movement.sku}</div>
                  </div>
                </td>
                <td className="px-4 py-4 text-sm">
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    movement.type === MovementType.ENTRADA ? 'bg-green-100 text-green-800' :
                    movement.type === MovementType.SALIDA ? 'bg-red-100 text-red-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {movement.type.toUpperCase()}
                  </span>
                  <div className="text-xs text-gray-500 mt-1">
                    {movement.reason.replace('_', ' ').toUpperCase()}
                  </div>
                </td>
                <td className="px-4 py-4 text-sm">
                  <span className={`font-medium ${
                    movement.type === MovementType.ENTRADA ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {movement.type === MovementType.ENTRADA ? '+' : '-'}{movement.quantity}
                  </span>
                </td>
                <td className="px-4 py-4 text-sm text-gray-900">
                  {movement.previousStock} → {movement.newStock}
                </td>
                <td className="px-4 py-4 text-sm text-gray-500">
                  {movement.userName}
                </td>
                <td className="px-4 py-4 text-sm text-gray-500">
                  {movement.reference || '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredMovements.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No se encontraron movimientos que coincidan con los filtros
        </div>
      )}
    </div>
  );
};

export default StockMovements;