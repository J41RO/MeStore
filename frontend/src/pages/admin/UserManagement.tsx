import React from 'react';

const UserManagement: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          Gestión de Usuarios
        </h1>
        <p className="text-gray-600 mb-6">
          Administra usuarios, roles y permisos del sistema.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-semibold text-blue-900">Total Usuarios</h3>
            <p className="text-2xl font-bold text-blue-700">0</p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="font-semibold text-green-900">Usuarios Activos</h3>
            <p className="text-2xl font-bold text-green-700">0</p>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg">
            <h3 className="font-semibold text-yellow-900">Pendientes</h3>
            <p className="text-2xl font-bold text-yellow-700">0</p>
          </div>
        </div>

        <div className="bg-gray-50 p-4 rounded-lg">
          <p className="text-gray-500 text-center">
            Funcionalidad de gestión de usuarios en desarrollo
          </p>
        </div>
      </div>
    </div>
  );
};

export default UserManagement;