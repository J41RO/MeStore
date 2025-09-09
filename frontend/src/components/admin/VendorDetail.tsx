import React, { useState } from 'react';

// Interfaces TypeScript
interface VendorDetailProps {
  vendor: VendorDetail | null;
  onClose?: () => void;
}

// Interface básica (compatible con VendorList)
interface Vendor {
  id: number;
  name: string;
  email: string;
  user_type: 'VENDEDOR' | 'ADMIN' | 'SUPERUSER' | 'COMPRADOR';
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

// Interface extendida para detalles completos
interface VendorDetail extends Vendor {
  telefono?: string;
  cedula?: string;
  ciudad?: string;
  direccion?: string;
  updated_at?: string;
  // Campos de negocio
  comision_rate?: number;
  productos_activos?: number;
  ventas_totales?: number;
  // Documentos y verificaciones
  documentos?: VendorDocument[];
}

// Interface para documentos
interface VendorDocument {
  id: number;
  tipo: 'cedula' | 'rut' | 'camara_comercio' | 'cuenta_bancaria';
  nombre: string;
  estado: 'pendiente' | 'aprobado' | 'rechazado';
  fecha_subida: string;
  url?: string;
}

const VendorDetail: React.FC<VendorDetailProps> = ({ vendor, onClose }) => {
  // Estado para manejar tab activo
  const [activeTab, setActiveTab] = useState<string>('general');

  if (vendor === null) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <p className="text-gray-500 text-center">Selecciona un vendedor para ver los detalles</p>
      </div>
    );
  }

  // Función para obtener clases CSS de tabs
  const getTabClasses = (tabId: string) => {
    const baseClasses = "px-4 py-2 text-sm font-medium rounded-lg transition-colors";
    if (activeTab === tabId) {
      return `${baseClasses} bg-blue-100 text-blue-700 border-b-2 border-blue-500`;
    }
    return `${baseClasses} text-gray-500 hover:text-gray-700 hover:bg-gray-100`;
  };

  return (
    <div className="bg-white shadow rounded-lg p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-semibold text-gray-800">
            Detalles del Vendedor
          </h2>
          {onClose && (
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              ×
            </button>
          )}
        </div>
        <p className="text-gray-600 text-sm">
          Información completa de {vendor.name}
        </p>
      </div>

      {/* Sistema de Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-2 mb-4">
            <button
              onClick={() => setActiveTab('general')}
              className={getTabClasses('general')}
            >
              Información General
            </button>
            <button
              onClick={() => setActiveTab('documentos')}
              className={getTabClasses('documentos')}
            >
              Documentos
            </button>
            <button
              onClick={() => setActiveTab('metricas')}
              className={getTabClasses('metricas')}
            >
              Métricas
            </button>
            <button
              onClick={() => setActiveTab('historial')}
              className={getTabClasses('historial')}
            >
              Historial
            </button>
          </nav>
        </div>
      </div>

      {/* Contenido de Tabs */}
      <div className="min-h-96">
        {activeTab === 'general' && (
          <div className="space-y-8">
            <h3 className="text-lg font-medium text-gray-900 mb-6">Información General</h3>
            
            {/* Sección: Información Personal */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h4 className="text-md font-medium text-gray-800 mb-4">Información Personal</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Nombre Completo</label>
                  <p className="text-gray-900 font-medium">{vendor.name}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Cédula</label>
                  <p className="text-gray-900">{vendor.cedula || 'No registrada'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Usuario</label>
                  <span className={`inline-flex px-3 py-1 text-xs font-semibold rounded-full ${
                    vendor.user_type === 'VENDEDOR' ? 'bg-blue-100 text-blue-800' :
                    vendor.user_type === 'ADMIN' ? 'bg-purple-100 text-purple-800' :
                    vendor.user_type === 'SUPERUSER' ? 'bg-red-100 text-red-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    {vendor.user_type}
                  </span>
                </div>
              </div>
            </div>

            {/* Sección: Información de Contacto */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h4 className="text-md font-medium text-gray-800 mb-4">Información de Contacto</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <p className="text-gray-900">{vendor.email}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Teléfono</label>
                  <p className="text-gray-900">{vendor.telefono || 'No registrado'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Ciudad</label>
                  <p className="text-gray-900">{vendor.ciudad || 'No registrada'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Dirección</label>
                  <p className="text-gray-900">{vendor.direccion || 'No registrada'}</p>
                </div>
              </div>
            </div>

            {/* Sección: Estado y Verificación */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h4 className="text-md font-medium text-gray-800 mb-4">Estado y Verificación</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Estado de Cuenta</label>
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                    vendor.is_active 
                      ? 'bg-green-100 text-green-800 border border-green-200' 
                      : 'bg-red-100 text-red-800 border border-red-200'
                  }`}>
                    <span className={`w-2 h-2 rounded-full mr-2 ${
                      vendor.is_active ? 'bg-green-400' : 'bg-red-400'
                    }`}></span>
                    {vendor.is_active ? 'Activo' : 'Inactivo'}
                  </span>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Verificación</label>
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                    vendor.is_verified 
                      ? 'bg-green-100 text-green-800 border border-green-200' 
                      : 'bg-yellow-100 text-yellow-800 border border-yellow-200'
                  }`}>
                    <span className={`w-2 h-2 rounded-full mr-2 ${
                      vendor.is_verified ? 'bg-green-400' : 'bg-yellow-400'
                    }`}></span>
                    {vendor.is_verified ? 'Verificado' : 'Pendiente'}
                  </span>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Fecha de Registro</label>
                  <p className="text-gray-900 text-sm">{new Date(vendor.created_at).toLocaleDateString('es-ES', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Última Actualización</label>
                  <p className="text-gray-900 text-sm">{vendor.updated_at ? 
                    new Date(vendor.updated_at).toLocaleDateString('es-ES', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    }) : 'No disponible'}</p>
                </div>
              </div>
            </div>

            {/* Sección: Información de Negocio */}
            {vendor.user_type === 'VENDEDOR' && (
              <div className="bg-gray-50 rounded-lg p-6">
                <h4 className="text-md font-medium text-gray-800 mb-4">Información de Negocio</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center p-4 bg-white rounded-lg border">
                    <p className="text-2xl font-bold text-blue-600">{vendor.productos_activos || 0}</p>
                    <p className="text-sm text-gray-600">Productos Activos</p>
                  </div>
                  <div className="text-center p-4 bg-white rounded-lg border">
                    <p className="text-2xl font-bold text-green-600">${vendor.ventas_totales || 0}</p>
                    <p className="text-sm text-gray-600">Ventas Totales</p>
                  </div>
                  <div className="text-center p-4 bg-white rounded-lg border">
                    <p className="text-2xl font-bold text-purple-600">{vendor.comision_rate || 0}%</p>
                    <p className="text-sm text-gray-600">Comisión</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'documentos' && (
          <div className="space-y-6">
            <h3 className="text-lg font-medium text-gray-900 mb-6">Documentos</h3>
            
            <div className="bg-gray-50 rounded-lg p-6">
              <div className="grid gap-4">
                {[
                  {
                    id: 1,
                    tipo: 'cedula',
                    nombre: 'Cédula de Ciudadanía',
                    estado: 'aprobado',
                    fecha_subida: '2024-08-20T10:30:00Z'
                  },
                  {
                    id: 2,
                    tipo: 'rut',
                    nombre: 'RUT Persona Natural',
                    estado: 'aprobado',
                    fecha_subida: '2024-08-20T10:35:00Z'
                  },
                  {
                    id: 3,
                    tipo: 'cuenta_bancaria',
                    nombre: 'Certificación Bancaria',
                    estado: 'pendiente',
                    fecha_subida: '2024-09-01T14:20:00Z'
                  }
                ].map((doc) => (
                  <div key={doc.id} className="bg-white rounded-lg border p-4 flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="bg-blue-100 rounded-lg p-2">
                        <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-900">{doc.nombre}</h4>
                        <p className="text-sm text-gray-500">
                          Subido el {new Date(doc.fecha_subida).toLocaleDateString('es-ES')}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        doc.estado === 'aprobado' ? 'bg-green-100 text-green-800' :
                        doc.estado === 'pendiente' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {doc.estado === 'aprobado' ? 'Aprobado' :
                         doc.estado === 'pendiente' ? 'Pendiente' : 'Rechazado'}
                      </span>
                      <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                        Ver
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'metricas' && (
          <div className="space-y-6">
            <h3 className="text-lg font-medium text-gray-900 mb-6">Métricas y KPIs</h3>
            
            {/* KPIs Principales */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white border rounded-lg p-6 text-center">
                <div className="text-3xl font-bold text-blue-600 mb-2">
                  {vendor.productos_activos || 12}
                </div>
                <div className="text-sm text-gray-600 mb-1">Productos Activos</div>
                <div className="text-xs text-green-600">+2 este mes</div>
              </div>
              
              <div className="bg-white border rounded-lg p-6 text-center">
                <div className="text-3xl font-bold text-green-600 mb-2">
                  ${(vendor.ventas_totales || 45680).toLocaleString()}
                </div>
                <div className="text-sm text-gray-600 mb-1">Ventas Totales</div>
                <div className="text-xs text-green-600">+15% vs mes anterior</div>
              </div>
              
              <div className="bg-white border rounded-lg p-6 text-center">
                <div className="text-3xl font-bold text-purple-600 mb-2">
                  {vendor.comision_rate || 8}%
                </div>
                <div className="text-sm text-gray-600 mb-1">Comisión Actual</div>
                <div className="text-xs text-gray-500">Fijo</div>
              </div>
              
              <div className="bg-white border rounded-lg p-6 text-center">
                <div className="text-3xl font-bold text-orange-600 mb-2">
                  4.8
                </div>
                <div className="text-sm text-gray-600 mb-1">Calificación</div>
                <div className="text-xs text-green-600">Excelente</div>
              </div>
            </div>

            {/* Gráficos Mock */}
            <div className="bg-white border rounded-lg p-6">
              <h4 className="font-medium text-gray-900 mb-4">Ventas por Mes</h4>
              <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                <div className="text-center text-gray-500">
                  <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <p>Gráfico de ventas mensuales</p>
                  <p className="text-sm">(Implementación futura)</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'historial' && (
          <div className="space-y-6">
            <h3 className="text-lg font-medium text-gray-900 mb-6">Historial de Actividades</h3>
            
            <div className="bg-gray-50 rounded-lg p-6">
              <div className="flow-root">
                <ul className="-mb-8">
                  {[
                    {
                      id: 1,
                      actividad: 'Cuenta creada',
                      descripcion: 'Se registró en la plataforma',
                      fecha: vendor.created_at,
                      tipo: 'registro'
                    },
                    {
                      id: 2,
                      actividad: 'Documentos subidos',
                      descripcion: 'Subió cédula y RUT para verificación',
                      fecha: '2024-08-20T10:30:00Z',
                      tipo: 'documento'
                    },
                    {
                      id: 3,
                      actividad: 'Cuenta verificada',
                      descripcion: 'Documentos aprobados por administrador',
                      fecha: '2024-08-21T15:45:00Z',
                      tipo: 'verificacion'
                    },
                    {
                      id: 4,
                      actividad: 'Primer producto publicado',
                      descripcion: 'Publicó "Smartphone Samsung Galaxy"',
                      fecha: '2024-08-25T09:15:00Z',
                      tipo: 'producto'
                    },
                    {
                      id: 5,
                      actividad: 'Primera venta realizada',
                      descripcion: 'Vendió producto por $850.000',
                      fecha: '2024-08-28T14:30:00Z',
                      tipo: 'venta'
                    }
                  ].map((item, itemIdx, array) => (
                    <li key={item.id}>
                      <div className="relative pb-8">
                        {itemIdx !== array.length - 1 ? (
                          <span className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200" aria-hidden="true" />
                        ) : null}
                        <div className="relative flex space-x-3">
                          <div>
                            <span className={`h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white ${
                              item.tipo === 'registro' ? 'bg-blue-500' :
                              item.tipo === 'documento' ? 'bg-yellow-500' :
                              item.tipo === 'verificacion' ? 'bg-green-500' :
                              item.tipo === 'producto' ? 'bg-purple-500' :
                              'bg-orange-500'
                            }`}>
                              <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                              </svg>
                            </span>
                          </div>
                          <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                            <div>
                              <p className="text-sm font-medium text-gray-900">{item.actividad}</p>
                              <p className="text-sm text-gray-500">{item.descripcion}</p>
                            </div>
                            <div className="text-right text-sm whitespace-nowrap text-gray-500">
                              {new Date(item.fecha).toLocaleDateString('es-ES', {
                                month: 'short',
                                day: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </div>
                          </div>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VendorDetail;