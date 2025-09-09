import React, { useState } from 'react';
import VendorList from '../../components/admin/VendorList';
import VendorDetail from '../../components/admin/VendorDetail';

// Interface para compatibilidad
interface Vendor {
  id: number;
  name: string;
  email: string;
  user_type: 'VENDEDOR' | 'ADMIN' | 'SUPERUSER' | 'COMPRADOR';
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

const UserManagement: React.FC = () => {
  const [selectedVendor, setSelectedVendor] = useState<Vendor | null>(null);
  const [activeView, setActiveView] = useState<'list' | 'detail'>('list');

  const handleVendorSelect = (vendor: Vendor) => {
    setSelectedVendor(vendor);
    setActiveView('detail');
  };

  const handleBackToList = () => {
    setSelectedVendor(null);
    setActiveView('list');
  };

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Gestión de Usuarios
            </h1>
            <p className="text-gray-600">
              Administra usuarios, roles y permisos del sistema.
            </p>
          </div>
          {activeView === 'detail' && (
            <button
              onClick={handleBackToList}
              className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              ← Volver a la Lista
            </button>
          )}
        </div>

        {activeView === 'list' && (
          <>
            {/* KPIs de usuarios */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-blue-50 p-4 rounded-lg border-l-4 border-blue-500">
                <h3 className="font-semibold text-blue-900">Total Usuarios</h3>
                <p className="text-2xl font-bold text-blue-700">6</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg border-l-4 border-green-500">
                <h3 className="font-semibold text-green-900">Usuarios Activos</h3>
                <p className="text-2xl font-bold text-green-700">5</p>
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg border-l-4 border-yellow-500">
                <h3 className="font-semibold text-yellow-900">Verificados</h3>
                <p className="text-2xl font-bold text-yellow-700">4</p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg border-l-4 border-purple-500">
                <h3 className="font-semibold text-purple-900">Vendedores</h3>
                <p className="text-2xl font-bold text-purple-700">3</p>
              </div>
            </div>

            {/* Lista de vendedores */}
            <VendorList onVendorSelect={handleVendorSelect} />
          </>
        )}

        {activeView === 'detail' && selectedVendor && (
          <VendorDetail vendor={selectedVendor} onClose={handleBackToList} />
        )}
      </div>
    </div>
  );
};

export default UserManagement;