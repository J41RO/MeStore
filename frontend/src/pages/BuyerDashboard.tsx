import React from 'react';
import { useAuthStore } from '../stores/authStore';

const BuyerDashboard: React.FC = () => {
  const { user } = useAuthStore();

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="md:flex md:items-center md:justify-between mb-8">
          <div className="flex-1 min-w-0">
            <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
              ¡Bienvenido, {user?.name || user?.email?.split('@')[0]}! 👋
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Tu panel de comprador - Explora productos y gestiona tus pedidos
            </p>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {/* Explorar Marketplace */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                    <span className="text-white text-lg">🛒</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Explorar Productos
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      Marketplace
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
            <div className="bg-gray-50 px-5 py-3">
              <div className="text-sm">
                <a
                  href="/marketplace/home"
                  className="font-medium text-blue-600 hover:text-blue-500"
                >
                  Ver todos los productos
                </a>
              </div>
            </div>
          </div>

          {/* Mi Carrito */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                    <span className="text-white text-lg">🛍️</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Mi Carrito
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      Ver Pedidos
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
            <div className="bg-gray-50 px-5 py-3">
              <div className="text-sm">
                <a
                  href="/marketplace/cart"
                  className="font-medium text-green-600 hover:text-green-500"
                >
                  Ver carrito de compras
                </a>
              </div>
            </div>
          </div>

          {/* Mis Compras */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                    <span className="text-white text-lg">📦</span>
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Mis Compras
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      Historial
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
            <div className="bg-gray-50 px-5 py-3">
              <div className="text-sm">
                <a
                  href="/app/mis-compras"
                  className="font-medium text-purple-600 hover:text-purple-500"
                >
                  Ver historial de compras
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Sección de Productos Destacados */}
        <div className="bg-white shadow overflow-hidden sm:rounded-md mb-8">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              🌟 Productos Destacados
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {[1, 2, 3, 4].map((item) => (
                <div key={item} className="border border-gray-200 rounded-lg p-4">
                  <div className="w-full h-32 bg-gray-200 rounded-md mb-3 flex items-center justify-center">
                    <span className="text-gray-400 text-sm">Imagen producto</span>
                  </div>
                  <h4 className="font-medium text-gray-900 text-sm">Producto {item}</h4>
                  <p className="text-gray-500 text-xs mt-1">Descripción del producto...</p>
                  <div className="mt-2 flex justify-between items-center">
                    <span className="text-green-600 font-semibold">$99.999</span>
                    <button className="text-xs bg-blue-600 text-white px-2 py-1 rounded">
                      Ver detalles
                    </button>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4 text-center">
              <a
                href="/marketplace/search"
                className="text-blue-600 hover:text-blue-500 text-sm font-medium"
              >
                Ver más productos →
              </a>
            </div>
          </div>
        </div>

        {/* Información de Contacto y Ayuda */}
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              📞 ¿Necesitas ayuda?
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl mb-2">📧</div>
                <h4 className="font-medium text-gray-900">Email</h4>
                <p className="text-gray-500 text-sm">soporte@mestore.com</p>
              </div>
              <div className="text-center">
                <div className="text-2xl mb-2">📞</div>
                <h4 className="font-medium text-gray-900">Teléfono</h4>
                <p className="text-gray-500 text-sm">(+57) 300 123 4567</p>
              </div>
              <div className="text-center">
                <div className="text-2xl mb-2">💬</div>
                <h4 className="font-medium text-gray-900">Chat en vivo</h4>
                <p className="text-gray-500 text-sm">Lun-Vie 9AM-6PM</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BuyerDashboard;