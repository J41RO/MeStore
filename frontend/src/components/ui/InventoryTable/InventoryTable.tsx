import React from 'react';
import {
  InventoryItem,
  InventoryStatus,
  LocationZone,
} from '../../../types/inventory.types';

// Datos mock para testing
const mockInventoryData: InventoryItem[] = [
  {
    id: '1',
    productId: 'PROD001',
    productName: 'Laptop Dell XPS',
    sku: 'LT-DELL-001',
    quantity: 25,
    minStock: 10,
    maxStock: 50,
    status: InventoryStatus.IN_STOCK,
    location: {
      zone: LocationZone.WAREHOUSE_A,
      aisle: 'A1',
      shelf: 'S1',
      position: 'P1',
    },
    lastUpdated: new Date(),
    cost: 1200,
  },
  {
    id: '2',
    productId: 'PROD002',
    productName: 'Mouse Logitech',
    sku: 'MS-LOG-002',
    quantity: 5,
    minStock: 15,
    maxStock: 100,
    status: InventoryStatus.LOW_STOCK,
    location: {
      zone: LocationZone.DISPLAY_AREA,
      aisle: 'B2',
      shelf: 'S3',
      position: 'P2',
    },
    lastUpdated: new Date(),
    cost: 45,
  },
];

interface InventoryTableProps {
  data?: InventoryItem[];
}

export const InventoryTable: React.FC<InventoryTableProps> = ({
  data = mockInventoryData,
}) => {
  return (
    <div className='w-full overflow-x-auto'>
      <table className='min-w-full bg-white border border-gray-200 rounded-lg'>
        <thead className='bg-gray-50'>
          <tr>
            <th className='px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase'>
              Producto
            </th>
            <th className='px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase'>
              SKU
            </th>
            <th className='px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase'>
              Cantidad
            </th>
            <th className='px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase'>
              Estado
            </th>
            <th className='px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase'>
              Ubicación
            </th>
          </tr>
        </thead>
        <tbody className='divide-y divide-gray-200'>
          {data.map(item => (
            <tr key={item.id} className='hover:bg-gray-50'>
              <td className='px-4 py-4 text-sm text-gray-900'>
                {item.productName}
              </td>
              <td className='px-4 py-4 text-sm text-gray-500'>{item.sku}</td>
              <td className='px-4 py-4 text-sm text-gray-900'>
                {item.quantity}
              </td>
              <td className='px-4 py-4 text-sm'>
                <span
                  className={`px-2 py-1 text-xs rounded-full ${
                    item.status === InventoryStatus.IN_STOCK
                      ? 'bg-green-100 text-green-800'
                      : item.status === InventoryStatus.LOW_STOCK
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-red-100 text-red-800'
                  }`}
                >
                  {item.status.replace('_', ' ').toUpperCase()}
                </span>
              </td>
              <td className='px-4 py-4 text-sm text-gray-500'>
                {item.location.zone} - {item.location.aisle}
                {item.location.shelf}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default InventoryTable;
