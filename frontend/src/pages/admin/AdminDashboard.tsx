import React from 'react';

const AdminDashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          Dashboard Administrativo
        </h1>
        <p className="text-gray-600 mb-6">
          Panel de control general para administradores del sistema.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-red-50 p-4 rounded-lg border-l-4 border-red-500">
            <h3 className="font-semibold text-red-900">Sistema</h3>
            <p className="text-lg font-bold text-red-700">Operativo</p>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg border-l-4 border-blue-500">
            <h3 className="font-semibold text-blue-900">Usuarios Online</h3>
            <p className="text-lg font-bold text-blue-700">0</p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg border-l-4 border-green-500">
            <h3 className="font-semibold text-green-900">Transacciones</h3>
            <p className="text-lg font-bold text-green-700">0</p>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg border-l-4 border-yellow-500">
            <h3 className="font-semibold text-yellow-900">Alertas</h3>
            <p className="text-lg font-bold text-yellow-700">0</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="border rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-2">Acceso Rápido</h3>
            <div className="space-y-2">
              <button className="w-full text-left px-3 py-2 bg-gray-100 rounded hover:bg-gray-200">
                Gestión de Usuarios
              </button>
              <button className="w-full text-left px-3 py-2 bg-gray-100 rounded hover:bg-gray-200">
                Configuración del Sistema
              </button>
              <button className="w-full text-left px-3 py-2 bg-gray-100 rounded hover:bg-gray-200">
                Reportes
              </button>
            </div>
          </div>
          
          <div className="border rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-2">Actividad Reciente</h3>
            <div className="text-sm text-gray-600 space-y-2">
              <p>• Sistema iniciado correctamente</p>
              <p>• AdminLayout configurado</p>
              <p>• Rutas administrativas listas</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;