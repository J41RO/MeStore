import React from 'react';
import { Commission } from '../../types/commission.types';

interface CommissionTableProps {
  commissions: Commission[];
  onRowClick?: (commission: Commission) => void;
}

const CommissionTable: React.FC<CommissionTableProps> = ({
  commissions,
  onRowClick
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid':
        return 'bg-green-100 text-green-800';
      case 'confirmed':
        return 'bg-blue-100 text-blue-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-red-100 text-red-800';
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Producto
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Cliente
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Venta
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Comisión
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Estado
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Fecha
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {commissions.map((commission) => (
            <tr
              key={commission.id}
              onClick={() => onRowClick?.(commission)}
              className={onRowClick ? 'hover:bg-gray-50 cursor-pointer' : ''}
            >
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm font-medium text-gray-900">{commission.productName}</div>
                <div className="text-sm text-gray-500">{commission.productCategory}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-900">{commission.customerName || 'N/A'}</div>
                <div className="text-sm text-gray-500">ID: {commission.orderId}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${commission.saleAmount.toFixed(2)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm font-medium text-green-600">
                  ${commission.commissionAmount.toFixed(2)}
                </div>
                <div className="text-sm text-gray-500">
                  {(commission.commissionRate * 100).toFixed(1)}%
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(commission.status)}`}>
                  {commission.status}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {commission.saleDate.toLocaleDateString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      
      {commissions.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          No se encontraron comisiones con los filtros aplicados
        </div>
      )}
    </div>
  );
};

export default CommissionTable;