import React, { useState } from 'react';
import { useAuthStore } from '../stores/authStore';

interface Order {
  id: string;
  date: string;
  total: number;
  status: 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
  items: {
    id: string;
    name: string;
    quantity: number;
    price: number;
    image?: string;
  }[];
}

const BuyerOrders: React.FC = () => {
  const { } = useAuthStore();
  const [activeTab, setActiveTab] = useState<'all' | 'pending' | 'delivered' | 'cancelled'>('all');

  // Datos de ejemplo - en producción vendrían del API
  const sampleOrders: Order[] = [
    {
      id: 'ORD-001',
      date: '2024-01-15',
      total: 299999,
      status: 'delivered',
      items: [
        { id: '1', name: 'Smartphone Samsung Galaxy', quantity: 1, price: 299999 }
      ]
    },
    {
      id: 'ORD-002', 
      date: '2024-01-10',
      total: 150000,
      status: 'shipped',
      items: [
        { id: '2', name: 'Auriculares Bluetooth', quantity: 2, price: 75000 }
      ]
    }
  ];

  const getStatusColor = (status: Order['status']): string => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      shipped: 'bg-purple-100 text-purple-800',
      delivered: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800'
    };
    return colors[status];
  };

  const getStatusText = (status: Order['status']): string => {
    const texts = {
      pending: 'Pendiente',
      processing: 'Procesando',
      shipped: 'Enviado',
      delivered: 'Entregado',
      cancelled: 'Cancelado'
    };
    return texts[status];
  };

  const filteredOrders = activeTab === 'all' 
    ? sampleOrders 
    : sampleOrders.filter(order => order.status === activeTab);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="md:flex md:items-center md:justify-between mb-8">
          <div className="flex-1 min-w-0">
            <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
              📦 Mis Compras
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Historial completo de tus pedidos y compras
            </p>
          </div>
          <div className="mt-4 flex md:mt-0 md:ml-4">
            <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
              🛒 Seguir Comprando
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <nav className="-mb-px flex space-x-8">
            {[
              { key: 'all', label: 'Todas', count: sampleOrders.length },
              { key: 'pending', label: 'Pendientes', count: sampleOrders.filter(o => o.status === 'pending').length },
              { key: 'delivered', label: 'Entregadas', count: sampleOrders.filter(o => o.status === 'delivered').length },
              { key: 'cancelled', label: 'Canceladas', count: sampleOrders.filter(o => o.status === 'cancelled').length }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.key
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label} ({tab.count})
              </button>
            ))}
          </nav>
        </div>

        {/* Orders List */}
        {filteredOrders.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🛒</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No tienes compras aún
            </h3>
            <p className="text-gray-500 mb-6">
              ¡Explora nuestro marketplace y encuentra productos increíbles!
            </p>
            <a
              href="/marketplace/home"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
            >
              Explorar Productos
            </a>
          </div>
        ) : (
          <div className="space-y-6">
            {filteredOrders.map((order) => (
              <div key={order.id} className="bg-white shadow overflow-hidden sm:rounded-lg">
                {/* Order Header */}
                <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">
                      Pedido #{order.id}
                    </h3>
                    <p className="text-sm text-gray-500">
                      Realizado el {new Date(order.date).toLocaleDateString('es-CO', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </p>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(order.status)}`}>
                      {getStatusText(order.status)}
                    </span>
                    <span className="text-lg font-semibold text-gray-900">
                      ${order.total.toLocaleString()} COP
                    </span>
                  </div>
                </div>

                {/* Order Items */}
                <div className="px-6 py-4">
                  <div className="space-y-3">
                    {order.items.map((item) => (
                      <div key={item.id} className="flex items-center space-x-4">
                        <div className="w-16 h-16 bg-gray-200 rounded-md flex items-center justify-center">
                          <span className="text-gray-400 text-xs">IMG</span>
                        </div>
                        <div className="flex-1">
                          <h4 className="text-sm font-medium text-gray-900">{item.name}</h4>
                          <p className="text-sm text-gray-500">
                            Cantidad: {item.quantity} | Precio unitario: ${item.price.toLocaleString()} COP
                          </p>
                        </div>
                        <div className="text-sm font-medium text-gray-900">
                          ${(item.quantity * item.price).toLocaleString()} COP
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Order Actions */}
                <div className="px-6 py-3 bg-gray-50 flex justify-between items-center">
                  <div className="flex space-x-2">
                    {order.status === 'delivered' && (
                      <button className="text-sm text-blue-600 hover:text-blue-500">
                        📝 Escribir reseña
                      </button>
                    )}
                    {order.status === 'pending' && (
                      <button className="text-sm text-red-600 hover:text-red-500">
                        ❌ Cancelar pedido
                      </button>
                    )}
                  </div>
                  <div className="flex space-x-2">
                    <button className="text-sm text-gray-600 hover:text-gray-500">
                      📋 Ver detalles
                    </button>
                    <button className="text-sm text-gray-600 hover:text-gray-500">
                      🔄 Comprar de nuevo
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Summary Stats */}
        {filteredOrders.length > 0 && (
          <div className="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                      <span className="text-white text-sm">📦</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Total de Pedidos
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {sampleOrders.length}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                      <span className="text-white text-sm">💰</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Total Gastado
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        ${sampleOrders.reduce((sum, order) => sum + order.total, 0).toLocaleString()} COP
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                      <span className="text-white text-sm">⭐</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Entregados
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {sampleOrders.filter(o => o.status === 'delivered').length}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                      <span className="text-white text-sm">⏳</span>
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Pendientes
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {sampleOrders.filter(o => o.status === 'pending').length}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BuyerOrders;