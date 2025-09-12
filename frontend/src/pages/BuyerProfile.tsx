import React, { useState } from 'react';
import { useAuthStore } from '../stores/authStore';

const BuyerProfile: React.FC = () => {
  const { user } = useAuthStore();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    nombre: user?.name || '',
    email: user?.email || '',
    telefono: '',
    direccion: '',
    ciudad: '',
    codigoPostal: ''
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSave = () => {
    // Aquí iría la lógica para guardar los datos
    console.log('Guardando datos del perfil:', formData);
    setIsEditing(false);
    // TODO: Implementar API call para guardar datos
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="md:flex md:items-center md:justify-between mb-8">
          <div className="flex-1 min-w-0">
            <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
              Mi Perfil de Comprador
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Gestiona tu información personal y preferencias de compra
            </p>
          </div>
          <div className="mt-4 flex md:mt-0 md:ml-4">
            {!isEditing ? (
              <button
                onClick={() => setIsEditing(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                ✏️ Editar Perfil
              </button>
            ) : (
              <div className="flex space-x-2">
                <button
                  onClick={handleSave}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
                >
                  💾 Guardar
                </button>
                <button
                  onClick={() => setIsEditing(false)}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                >
                  ❌ Cancelar
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Información Personal */}
          <div className="lg:col-span-2">
            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Información Personal
                </h3>
                
                <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Nombre Completo
                    </label>
                    <input
                      type="text"
                      name="nombre"
                      value={formData.nombre}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      className={`mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 ${
                        isEditing 
                          ? 'bg-white focus:outline-none focus:ring-blue-500 focus:border-blue-500' 
                          : 'bg-gray-50 cursor-not-allowed'
                      }`}
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Email
                    </label>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      disabled={true} // Email no debería ser editable
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 bg-gray-50 cursor-not-allowed"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Teléfono
                    </label>
                    <input
                      type="tel"
                      name="telefono"
                      value={formData.telefono}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      className={`mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 ${
                        isEditing 
                          ? 'bg-white focus:outline-none focus:ring-blue-500 focus:border-blue-500' 
                          : 'bg-gray-50 cursor-not-allowed'
                      }`}
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Ciudad
                    </label>
                    <input
                      type="text"
                      name="ciudad"
                      value={formData.ciudad}
                      onChange={handleInputChange}
                      disabled={!isEditing}
                      className={`mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 ${
                        isEditing 
                          ? 'bg-white focus:outline-none focus:ring-blue-500 focus:border-blue-500' 
                          : 'bg-gray-50 cursor-not-allowed'
                      }`}
                    />
                  </div>
                </div>
                
                <div className="mt-6">
                  <label className="block text-sm font-medium text-gray-700">
                    Dirección de Envío
                  </label>
                  <textarea
                    name="direccion"
                    rows={3}
                    value={formData.direccion}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className={`mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 ${
                      isEditing 
                        ? 'bg-white focus:outline-none focus:ring-blue-500 focus:border-blue-500' 
                        : 'bg-gray-50 cursor-not-allowed'
                    }`}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Panel Lateral */}
          <div className="space-y-6">
            {/* Estado de la cuenta */}
            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Estado de la Cuenta
                </h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Tipo de Usuario:</span>
                    <span className="text-sm font-medium text-blue-600">
                      {user?.user_type || 'COMPRADOR'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Estado:</span>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Activo
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Email Verificado:</span>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      ✓ Verificado
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Estadísticas de Compras */}
            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Mis Estadísticas
                </h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Total Compras:</span>
                    <span className="text-sm font-medium text-gray-900">0</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Total Gastado:</span>
                    <span className="text-sm font-medium text-gray-900">$0 COP</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">Productos Favoritos:</span>
                    <span className="text-sm font-medium text-gray-900">0</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Acciones Rápidas */}
            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Acciones Rápidas
                </h3>
                <div className="space-y-2">
                  <a
                    href="/marketplace/home"
                    className="block w-full text-center px-4 py-2 border border-blue-600 text-sm font-medium rounded-md text-blue-600 bg-white hover:bg-blue-50"
                  >
                    🛒 Explorar Productos
                  </a>
                  <a
                    href="/marketplace/cart"
                    className="block w-full text-center px-4 py-2 border border-green-600 text-sm font-medium rounded-md text-green-600 bg-white hover:bg-green-50"
                  >
                    🛍️ Ver Mi Carrito
                  </a>
                  <a
                    href="/app/mis-compras"
                    className="block w-full text-center px-4 py-2 border border-purple-600 text-sm font-medium rounded-md text-purple-600 bg-white hover:bg-purple-50"
                  >
                    📦 Mis Compras
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BuyerProfile;