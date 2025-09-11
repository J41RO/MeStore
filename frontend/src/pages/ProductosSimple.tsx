import React from 'react';
import { useNotifications } from '../contexts/NotificationContext';

const ProductosSimple: React.FC = () => {
  const { showNotification } = useNotifications();

  // Datos mock temporales
  const mockProducts = [
    {
      id: '1',
      nombre: 'Smartphone Galaxy A54',
      precio: 450000,
      stock: 25,
      categoria: 'Electrónicos',
      activo: true
    },
    {
      id: '2', 
      nombre: 'Laptop HP Pavilion',
      precio: 1200000,
      stock: 12,
      categoria: 'Computadores',
      activo: true
    },
    {
      id: '3',
      nombre: 'Auriculares Sony',
      precio: 180000,
      stock: 8,
      categoria: 'Audio',
      activo: false
    }
  ];

  const handleTestNotification = () => {
    showNotification({
      title: 'Test',
      message: 'NotificationProvider funcionando correctamente!',
      type: 'success'
    });
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Mis Productos</h1>
        <button
          onClick={handleTestNotification}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Test Notification
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Productos</p>
              <p className="text-2xl font-bold text-gray-900">3</p>
            </div>
            <div className="p-3 rounded-full bg-blue-50">
              📦
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Productos Activos</p>
              <p className="text-2xl font-bold text-green-600">2</p>
            </div>
            <div className="p-3 rounded-full bg-green-50">
              ✅
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Stock Total</p>
              <p className="text-2xl font-bold text-blue-600">45</p>
            </div>
            <div className="p-3 rounded-full bg-blue-50">
              📊
            </div>
          </div>
        </div>
      </div>

      {/* Products Table */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Lista de Productos</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Producto
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Precio
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Stock
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {mockProducts.map((product) => (
                <tr key={product.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{product.nombre}</div>
                      <div className="text-sm text-gray-500">{product.categoria}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${product.precio.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {product.stock} unidades
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      product.activo
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {product.activo ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
        <div className="flex">
          <div className="flex-shrink-0">
            ⚠️
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">
              Versión Temporal
            </h3>
            <div className="mt-2 text-sm text-yellow-700">
              <p>
                Esta es una versión simplificada de la página de productos con datos mock.
                Se activará la versión completa una vez que la API esté funcionando correctamente.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductosSimple;