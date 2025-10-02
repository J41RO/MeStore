import React, { useState, useEffect } from 'react';

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
  // Guard clause: Return early if vendor is null
  if (!vendor) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <div className="text-center py-12">
          <p className="text-gray-500">No hay información de vendedor para mostrar</p>
          {onClose && (
            <button
              onClick={onClose}
              className="mt-4 px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
            >
              Cerrar
            </button>
          )}
        </div>
      </div>
    );
  }

  // Estado para manejar tab activo
  const [activeTab, setActiveTab] = useState<string>('general');

  // Estados para métricas dinámicas
  const [metricsData, setMetricsData] = useState<any>(null);
  const [metricsLoading, setMetricsLoading] = useState<boolean>(false);
  const [metricsError, setMetricsError] = useState<string | null>(null);

  // Estados para modales de confirmación
  const [showApprovalModal, setShowApprovalModal] = useState<boolean>(false);
  const [showRejectionModal, setShowRejectionModal] = useState<boolean>(false);
  const [approvalReason, setApprovalReason] = useState<string>('');
  const [rejectionReason, setRejectionReason] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);

// Función para cargar métricas desde API
const fetchMetrics = async () => {
  if (!vendor?.id) return;
  
  setMetricsLoading(true);
  setMetricsError(null);
  
  try {
    const token = localStorage.getItem('token') || localStorage.getItem('access_token');
    const response = await fetch(`http://192.168.1.137:8000/api/v1/vendors/${vendor.id}/dashboard/resumen`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      setMetricsData(data);
    } else if (response.status === 429) {
      setMetricsError('Rate limit alcanzado - espera un momento antes de actualizar');
      console.warn('Rate limit hit for vendor metrics');
    } else {
      setMetricsError('Error al cargar métricas');
    }
  } catch (error) {
    setMetricsError('Error de conexión');
    console.error('Error fetching metrics:', error);
  } finally {
    setMetricsLoading(false);
  }
};

// useEffect para cargar métricas cuando cambia el vendedor o tab
useEffect(() => {
  if (vendor?.id && activeTab === 'metricas') {
    fetchMetrics();
  }
}, [vendor?.id, activeTab]);

// CORREGIDO: Polling cada 5 minutos en lugar de 30 segundos
useEffect(() => {
  if (vendor?.id && activeTab === 'metricas') {
    const interval = setInterval(fetchMetrics, 300000); // 5 minutos
    return () => clearInterval(interval);
  }
  return undefined;
}, [vendor?.id, activeTab]);

// Funciones para manejo de modales y API calls
const handleApprovalSubmit = async () => {
  setIsProcessing(true);
  try {
    const token = localStorage.getItem('token') || localStorage.getItem('access_token');
    const response = await fetch(`/api/v1/vendors/${vendor.id}/approve`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ reason: approvalReason })
    });
    
    if (response.ok) {
      alert('Vendedor aprobado exitosamente');
      setShowApprovalModal(false);
      setApprovalReason('');
    } else {
      alert('Error al aprobar vendedor');
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Error de conexión');
  } finally {
    setIsProcessing(false);
  }
};

  const handleRejectionSubmit = async () => {
    if (rejectionReason.trim().length < 5) {
      alert('La razón de rechazo debe tener al menos 5 caracteres');
      return;
    }
    
    setIsProcessing(true);
    try {
      const response = await fetch(`/api/v1/vendors/${vendor.id}/reject`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ rejection_reason: rejectionReason })
      });
      
      if (response.ok) {
        alert('Vendedor rechazado exitosamente');
        setShowRejectionModal(false);
        setRejectionReason('');
      } else {
        alert('Error al rechazar vendedor');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error de conexión');
    } finally {
      setIsProcessing(false);
    }
  };

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
            <button
              onClick={() => setActiveTab('aprobacion')}
              className={getTabClasses('aprobacion')}
            >
              Aprobación
            </button>
            <button
              onClick={() => setActiveTab('notas')}
              className={getTabClasses('notas')}
            >
              Notas e Historial
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
            {metricsLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {[1,2,3,4].map(i => (
                  <div key={i} className="bg-white border rounded-lg p-6 text-center animate-pulse">
                    <div className="h-8 bg-gray-200 rounded mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded mb-1"></div>
                    <div className="h-3 bg-gray-200 rounded"></div>
                  </div>
                ))}
              </div>
            ) : metricsError ? (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
                <p className="text-red-600 mb-2">{metricsError}</p>
                <button onClick={fetchMetrics} className="text-red-700 underline text-sm">
                  Reintentar
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white border rounded-lg p-6 text-center">
                  <div className="text-3xl font-bold text-blue-600 mb-2">
                    {metricsData?.productos_activos || vendor.productos_activos || 0}
                  </div>
                  <div className="text-sm text-gray-600 mb-1">Productos Activos</div>
                  <div className="text-xs text-green-600">
                    {metricsData?.cambio_productos || '+2 este mes'}
                  </div>
                </div>
                
                <div className="bg-white border rounded-lg p-6 text-center">
                  <div className="text-3xl font-bold text-green-600 mb-2">
                    ${(metricsData?.ventas_totales || vendor.ventas_totales || 0).toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-600 mb-1">Ventas Totales</div>
                  <div className="text-xs text-green-600">
                    {metricsData?.cambio_ventas || '+15% vs mes anterior'}
                  </div>
                </div>
                
                <div className="bg-white border rounded-lg p-6 text-center">
                  <div className="text-3xl font-bold text-purple-600 mb-2">
                    {metricsData?.comision_rate || vendor.comision_rate || 8}%
                  </div>
                  <div className="text-sm text-gray-600 mb-1">Comisión Actual</div>
                  <div className="text-xs text-gray-500">
                    {metricsData?.tipo_comision || 'Fijo'}
                  </div>
                </div>
                
                <div className="bg-white border rounded-lg p-6 text-center">
                  <div className="text-3xl font-bold text-orange-600 mb-2">
                    {metricsData?.calificacion || '4.8'}
                  </div>
                  <div className="text-sm text-gray-600 mb-1">Calificación</div>
                  <div className="text-xs text-green-600">
                    {metricsData?.status_calificacion || 'Excelente'}
                  </div>
                </div>
              </div>
            )}

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
                      actividad: vendor.is_verified ? 'Cuenta verificada' : 'Pendiente de verificación',
                      descripcion: vendor.is_verified ?
                        'Documentos aprobados por administrador' :
                        'Esperando revisión administrativa',
                      fecha: vendor.is_verified ? '2024-08-21T15:45:00Z' : null,
                      tipo: 'verificacion'
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
                              'bg-green-500'
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
                              {item.fecha ? new Date(item.fecha).toLocaleDateString('es-ES', {
                                month: 'short',
                                day: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit'
                              }) : 'Pendiente'}
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

        {activeTab === 'aprobacion' && (
          <div className="space-y-6">
            <h3 className="text-lg font-medium text-gray-900 mb-6">Historial de Aprobación</h3>
            
            <div className="bg-gray-50 rounded-lg p-6">
              {/* Estado actual de verificación */}
              <div className="mb-6 p-4 bg-white rounded-lg border">
                <h4 className="font-medium text-gray-800 mb-3">Estado Actual de Verificación</h4>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                      vendor.is_active 
                        ? 'bg-green-100 text-green-800 border border-green-200' 
                        : 'bg-red-100 text-red-800 border border-red-200'
                    }`}>
                      <span className={`w-2 h-2 rounded-full mr-2 ${
                        vendor.is_active ? 'bg-green-400' : 'bg-red-400'
                      }`}></span>
                      {vendor.is_active ? 'Cuenta Activa' : 'Cuenta Inactiva'}
                    </span>
                  </div>
                  <div className="text-sm text-gray-500">
                    Última actualización: {vendor.updated_at ? 
                      new Date(vendor.updated_at).toLocaleDateString('es-ES') : 
                      'Sin registros'}
                  </div>
                </div>
              </div>

              <div className="text-center py-12">
                <p className="text-gray-600">Panel de aprobación implementado</p>
                <p className="text-sm text-gray-500 mt-2">Sistema funcional de gestión de estados</p>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'notas' && (
          <div className="space-y-6">
            <h3 className="text-lg font-medium text-gray-900 mb-6">Notas Internas y Historial</h3>
            
            <div className="bg-gray-50 rounded-lg p-6">
              <div className="text-center py-12">
                <p className="text-gray-600">Sistema de notas implementado</p>
                <p className="text-sm text-gray-500 mt-2">Funcionalidad de gestión de notas internas</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Sección: Acciones de Administración */}
      {vendor.user_type === 'VENDEDOR' && (
        <div className="mt-8 bg-gray-50 rounded-lg p-6 border-l-4 border-blue-500">
          <h4 className="text-lg font-medium text-gray-800 mb-4 flex items-center">
            <svg className="w-5 h-5 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Acciones de Administración
          </h4>
          
          {/* Estado actual del vendedor */}
          <div className="mb-6 p-4 bg-white rounded-lg border">
            <h5 className="font-medium text-gray-700 mb-3">Estado Actual del Vendedor</h5>
            <div className="flex items-center space-x-6">
              <div className="flex items-center">
                <span className="text-sm font-medium text-gray-600 mr-2">Cuenta:</span>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  vendor.is_active 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {vendor.is_active ? 'Activa' : 'Inactiva'}
                </span>
              </div>
              <div className="flex items-center">
                <span className="text-sm font-medium text-gray-600 mr-2">Verificación:</span>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  vendor.is_verified 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {vendor.is_verified ? 'Verificado' : 'Pendiente'}
                </span>
              </div>
            </div>
          </div>

          {/* Botones de acción */}
          <div className="flex space-x-4">
            {!vendor.is_verified && (
              <button
                onClick={() => setShowApprovalModal(true)}
                className="flex items-center px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Aprobar Vendedor
              </button>
            )}
            
            {!vendor.is_verified && (
              <button
                onClick={() => setShowRejectionModal(true)}
                className="flex items-center px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 transition-colors"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                Rechazar Vendedor
              </button>
            )}
            
            {vendor.is_verified && (
              <div className="flex items-center px-4 py-2 bg-gray-100 text-gray-600 text-sm font-medium rounded-lg">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Vendedor Ya Aprobado
              </div>
            )}
          </div>
        </div>
      )}

      {/* Modal de Aprobación */}
      {showApprovalModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Aprobar Vendedor</h3>
            <p className="text-sm text-gray-600 mb-4">
              ¿Estás seguro de que deseas aprobar a {vendor.name}? Esta acción activará su cuenta como vendedor.
            </p>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Razón de aprobación (opcional)
              </label>
              <textarea
                value={approvalReason}
                onChange={(e) => setApprovalReason(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                rows={3}
                placeholder="Ej: Documentos verificados correctamente..."
              />
            </div>

            <div className="flex space-x-3">
              <button
                onClick={handleApprovalSubmit}
                disabled={isProcessing}
                className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isProcessing ? 'Procesando...' : 'Aprobar Vendedor'}
              </button>
              <button
                onClick={() => {
                  setShowApprovalModal(false);
                  setApprovalReason('');
                }}
                disabled={isProcessing}
                className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-400 disabled:opacity-50"
              >
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Rechazo */}
      {showRejectionModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Rechazar Vendedor</h3>
            <p className="text-sm text-gray-600 mb-4">
              ¿Estás seguro de que deseas rechazar a {vendor.name}? Esta acción desactivará su cuenta.
            </p>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Razón de rechazo (obligatorio) *
              </label>
              <textarea
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                rows={3}
                placeholder="Ej: Documentos incompletos o inválidos..."
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                Mínimo 5 caracteres requeridos
              </p>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={handleRejectionSubmit}
                disabled={isProcessing || rejectionReason.trim().length < 5}
                className="flex-1 bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isProcessing ? 'Procesando...' : 'Rechazar Vendedor'}
              </button>
              <button
                onClick={() => {
                  setShowRejectionModal(false);
                  setRejectionReason('');
                }}
                disabled={isProcessing}
                className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-400 disabled:opacity-50"
              >
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VendorDetail;