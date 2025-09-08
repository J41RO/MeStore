import React from 'react';

const Marketplace: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            🛒 Marketplace - Área de Compradores
          </h1>
          <p className="text-gray-600 mb-6">
            Bienvenido al marketplace de MeStore. Aquí puedes explorar y comprar productos.
          </p>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h2 className="text-lg font-semibold text-blue-900 mb-2">
              Funcionalidades del Marketplace:
            </h2>
            <ul className="list-disc list-inside text-blue-800 space-y-1">
              <li>Explorar catálogo de productos</li>
              <li>Buscar y filtrar productos</li>
              <li>Ver detalles de productos</li>
              <li>Agregar al carrito</li>
              <li>Gestionar pedidos</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Marketplace;