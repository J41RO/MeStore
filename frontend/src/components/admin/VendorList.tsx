import React, { useState, useEffect } from 'react';

// Interfaces TypeScript
interface VendorListProps {
  onVendorSelect?: (vendor: Vendor) => void;
}

interface Vendor {
  id: number;
  name: string;
  email: string;
  user_type: 'VENDEDOR' | 'ADMIN' | 'SUPERUSER' | 'COMPRADOR';
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

interface FilterState {
  status: 'todos' | 'activo' | 'inactivo' | 'verificado';
  userType: 'todos' | 'VENDEDOR' | 'ADMIN' | 'SUPERUSER' | 'COMPRADOR';
}

interface BulkActionModal {
  type: 'approve' | 'suspend' | 'email' | null;
  isOpen: boolean;
}

interface BulkEmailData {
  subject: string;
  message: string;
}

// Datos mock de vendedores para testing
const mockVendors: Vendor[] = [
  {
    id: 1,
    name: 'Carlos Rodríguez',
    email: 'carlos.rodriguez@gmail.com',
    user_type: 'VENDEDOR',
    is_active: true,
    is_verified: true,
    created_at: '2024-08-15T10:30:00Z'
  },
  {
    id: 2,
    name: 'María González',
    email: 'maria.gonzalez@hotmail.com',
    user_type: 'VENDEDOR',
    is_active: true,
    is_verified: false,
    created_at: '2024-08-20T14:15:00Z'
  },
  {
    id: 3,
    name: 'Admin Sistema',
    email: 'admin@mestocker.com',
    user_type: 'ADMIN',
    is_active: true,
    is_verified: true,
    created_at: '2024-07-01T08:00:00Z'
  },
  {
    id: 4,
    name: 'Ana Martínez',
    email: 'ana.martinez@yahoo.com',
    user_type: 'COMPRADOR',
    is_active: false,
    is_verified: true,
    created_at: '2024-08-25T16:45:00Z'
  },
  {
    id: 5,
    name: 'Super Usuario',
    email: 'super@mestocker.com',
    user_type: 'SUPERUSER',
    is_active: true,
    is_verified: true,
    created_at: '2024-06-15T12:00:00Z'
  },
  {
    id: 6,
    name: 'Luis Pérez',
    email: 'luis.perez@empresa.co',
    user_type: 'VENDEDOR',
    is_active: true,
    is_verified: false,
    created_at: '2024-09-01T09:20:00Z'
  }
];

const VendorList: React.FC<VendorListProps> = ({ onVendorSelect }) => {
  // Estados básicos
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [filteredVendors, setFilteredVendors] = useState<Vendor[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<FilterState>({
    status: 'todos',
    userType: 'todos'
  });

  // Estado para selección múltiple de vendedores
  const [selectedVendors, setSelectedVendors] = useState<Set<number>>(new Set());
  const [selectAll, setSelectAll] = useState(false);

  // Estados para modales de acciones bulk
  const [bulkModal, setBulkModal] = useState<BulkActionModal>({ type: null, isOpen: false });
  const [suspendReason, setSuspendReason] = useState('');
  const [emailData, setEmailData] = useState<BulkEmailData>({ subject: '', message: '' });
  const [bulkLoading, setBulkLoading] = useState(false);

  // Estados de paginación
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // Calcular vendedores para la página actual
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentVendors = filteredVendors.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(filteredVendors.length / itemsPerPage);

  // Funciones para manejo de selección múltiple
  const handleSelectVendor = (vendorId: number) => {
    const newSelected = new Set(selectedVendors);
    if (newSelected.has(vendorId)) {
      newSelected.delete(vendorId);
    } else {
      newSelected.add(vendorId);
    }
    setSelectedVendors(newSelected);
    setSelectAll(newSelected.size === filteredVendors.length && filteredVendors.length > 0);
  };

  const handleSelectAll = () => {
    if (selectAll) {
      setSelectedVendors(new Set());
      setSelectAll(false);
    } else {
      const allIds = new Set(filteredVendors.map(vendor => vendor.id));
      setSelectedVendors(allIds);
      setSelectAll(true);
    }
  };

  const clearSelection = () => {
    setSelectedVendors(new Set());
    setSelectAll(false);
  };

  // Funciones para acciones bulk
  const openBulkModal = (type: 'approve' | 'suspend' | 'email') => {
    setBulkModal({ type, isOpen: true });
  };

  const closeBulkModal = () => {
    setBulkModal({ type: null, isOpen: false });
    setSuspendReason('');
    setEmailData({ subject: '', message: '' });
  };

  const executeBulkAction = async () => {
    setBulkLoading(true);
    const selectedIds = Array.from(selectedVendors);
    
    try {
      // Simular llamadas API
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      if (bulkModal.type === 'approve') {
        // Actualizar vendors aprobados
        setVendors(prev => prev.map(vendor => 
          selectedIds.includes(vendor.id) 
            ? { ...vendor, is_verified: true }
            : vendor
        ));
        alert(`✅ ${selectedIds.length} vendedores aprobados exitosamente`);
      } else if (bulkModal.type === 'suspend') {
        // Actualizar vendors suspendidos
        setVendors(prev => prev.map(vendor => 
          selectedIds.includes(vendor.id) 
            ? { ...vendor, is_active: false }
            : vendor
        ));
        alert(`✅ ${selectedIds.length} vendedores suspendidos exitosamente`);
      } else if (bulkModal.type === 'email') {
        alert(`✅ Email enviado a ${selectedIds.length} vendedores exitosamente`);
      }
      
      clearSelection();
      closeBulkModal();
    } catch (error) {
      alert('❌ Error en la operación bulk');
    } finally {
      setBulkLoading(false);
    }
  };

  // useEffect para inicialización
  useEffect(() => {
    loadVendors();
  }, []);

  // useEffect para filtrado automático
  useEffect(() => {
    filterVendors();
  }, [filters, vendors]);

  // useEffect para resetear página cuando cambian los filtros
  useEffect(() => {
    setCurrentPage(1);
  }, [filters]);

  // Función para cargar vendedores
  const loadVendors = async () => {
    setLoading(true);
    // Simular carga de API con datos mock
    setTimeout(() => {
      setVendors(mockVendors);
      setFilteredVendors(mockVendors);
      setLoading(false);
    }, 1000);
  };

  // Función para filtrar vendedores
  const filterVendors = () => {
    let filtered = vendors.filter(vendor => {
      // Filtro por estado
      if (filters.status === 'activo' && !vendor.is_active) return false;
      if (filters.status === 'inactivo' && vendor.is_active) return false;
      if (filters.status === 'verificado' && !vendor.is_verified) return false;
      
      // Filtro por tipo de usuario
      if (filters.userType !== 'todos' && vendor.user_type !== filters.userType) return false;
      
      return true;
    });
    
    setFilteredVendors(filtered);
  };

  // Función para obtener clases CSS dinámicas por tipo de usuario
  const getUserTypeClasses = (userType: string) => {
    switch (userType) {
      case 'VENDEDOR':
        return 'bg-blue-100 text-blue-800';
      case 'ADMIN':
        return 'bg-purple-100 text-purple-800';
      case 'SUPERUSER':
        return 'bg-red-100 text-red-800';
      case 'COMPRADOR':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Función para obtener clases CSS dinámicas por estado
  const getStatusClasses = (isActive: boolean) => {
    return isActive 
      ? 'bg-green-100 text-green-800' 
      : 'bg-red-100 text-red-800';
  };

  // Función para obtener clases CSS dinámicas por verificación
  const getVerifiedClasses = (isVerified: boolean) => {
    return isVerified 
      ? 'bg-green-100 text-green-800' 
      : 'bg-yellow-100 text-yellow-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Cargando vendedores...</span>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-2">
          Lista de Vendedores
        </h2>
        <p className="text-gray-600 text-sm">
          Gestiona y filtra la lista de vendedores registrados
        </p>
      </div>

      {/* Barra de acciones bulk */}
      {selectedVendors.size > 0 && (
        <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <span className="text-sm font-medium text-blue-800">
                {selectedVendors.size} vendedor{selectedVendors.size !== 1 ? 'es' : ''} seleccionado{selectedVendors.size !== 1 ? 's' : ''}
              </span>
              <div className="flex space-x-2">
                <button
                  onClick={() => openBulkModal('approve')}
                  className="px-3 py-1 text-sm font-medium text-green-700 bg-green-100 border border-green-300 rounded-md hover:bg-green-200 transition-colors"
                >
                  Aprobar Seleccionados
                </button>
                <button
                  onClick={() => openBulkModal('suspend')}
                  className="px-3 py-1 text-sm font-medium text-red-700 bg-red-100 border border-red-300 rounded-md hover:bg-red-200 transition-colors"
                >
                  Suspender
                </button>
                <button
                  onClick={() => openBulkModal('email')}
                  className="px-3 py-1 text-sm font-medium text-blue-700 bg-blue-100 border border-blue-300 rounded-md hover:bg-blue-200 transition-colors"
                >
                  Enviar Email
                </button>
              </div>
            </div>
            <button
              onClick={clearSelection}
              className="px-3 py-1 text-sm font-medium text-gray-600 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 transition-colors"
            >
              Limpiar Selección
            </button>
          </div>
        </div>
      )}

      {/* Panel de filtros */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg border">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Filtro por Estado */}
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filtrar por Estado
            </label>
            <select
              value={filters.status}
              onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value as FilterState['status'] }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
            >
              <option value="todos">Todos los estados</option>
              <option value="activo">Activos</option>
              <option value="inactivo">Inactivos</option>
              <option value="verificado">Verificados</option>
            </select>
          </div>

          {/* Filtro por Tipo de Usuario */}
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filtrar por Tipo de Cuenta
            </label>
            <select
              value={filters.userType}
              onChange={(e) => setFilters(prev => ({ ...prev, userType: e.target.value as FilterState['userType'] }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
            >
              <option value="todos">Todos los tipos</option>
              <option value="VENDEDOR">Vendedores</option>
              <option value="ADMIN">Administradores</option>
              <option value="SUPERUSER">Super Usuarios</option>
              <option value="COMPRADOR">Compradores</option>
            </select>
          </div>

          {/* Botón limpiar filtros */}
          <div className="flex items-end">
            <button
              onClick={() => setFilters({ status: 'todos', userType: 'todos' })}
              className="px-4 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            >
              Limpiar Filtros
            </button>
          </div>
        </div>

        {/* Indicador de filtros activos */}
        {(filters.status !== 'todos' || filters.userType !== 'todos') && (
          <div className="mt-3 flex flex-wrap gap-2">
            <span className="text-xs text-gray-600">Filtros activos:</span>
            {filters.status !== 'todos' && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                Estado: {filters.status}
              </span>
            )}
            {filters.userType !== 'todos' && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                Tipo: {filters.userType}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Tabla de vendedores */}
      <div className="bg-white border rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <input
                    type="checkbox"
                    checked={selectAll}
                    onChange={handleSelectAll}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Vendedor
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tipo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Verificado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {currentVendors.map((vendor, index) => (
                <tr 
                  key={vendor.id} 
                  className={`${
                    selectedVendors.has(vendor.id) 
                      ? 'bg-blue-50 border-l-4 border-blue-500' 
                      : index % 2 === 0 
                        ? 'bg-white hover:bg-gray-50' 
                        : 'bg-gray-50 hover:bg-gray-100'
                  } transition-colors`}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <input
                      type="checkbox"
                      checked={selectedVendors.has(vendor.id)}
                      onChange={() => handleSelectVendor(vendor.id)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{vendor.name}</div>
                    <div className="text-sm text-gray-500">ID: {vendor.id}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{vendor.email}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getUserTypeClasses(vendor.user_type)}`}>
                      {vendor.user_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${getStatusClasses(vendor.is_active)}`}>
                      {vendor.is_active ? '🟢 Activo' : '🔴 Inactivo'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${getVerifiedClasses(vendor.is_verified)}`}>
                      {vendor.is_verified ? '✅ Verificado' : '⏳ Pendiente'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => onVendorSelect?.(vendor)}
                        className="text-blue-600 hover:text-blue-900 transition-colors"
                      >
                        Ver
                      </button>
                      <button className="text-green-600 hover:text-green-900 transition-colors">
                        Editar
                      </button>
                      <button className="text-red-600 hover:text-red-900 transition-colors">
                        {vendor.is_active ? 'Suspender' : 'Activar'}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Controles de paginación */}
      {totalPages > 1 && (
        <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6 mt-4">
          <div className="flex-1 flex justify-between sm:hidden">
            <button
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
              className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Anterior
            </button>
            <button
              onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Siguiente
            </button>
          </div>
          <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-gray-700">
                Mostrando{' '}
                <span className="font-medium">{indexOfFirstItem + 1}</span>
                {' '}a{' '}
                <span className="font-medium">
                  {Math.min(indexOfLastItem, filteredVendors.length)}
                </span>
                {' '}de{' '}
                <span className="font-medium">{filteredVendors.length}</span>
                {' '}vendedores
              </p>
            </div>
            <div>
              <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                <button
                  onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                  disabled={currentPage === 1}
                  className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Anterior
                </button>
                {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                  <button
                    key={page}
                    onClick={() => setCurrentPage(page)}
                    className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                      page === currentPage
                        ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                        : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                    }`}
                  >
                    {page}
                  </button>
                ))}
                <button
                  onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                  disabled={currentPage === totalPages}
                  className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Siguiente
                </button>
              </nav>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Confirmación para Aprobar */}
      {bulkModal.type === 'approve' && bulkModal.isOpen && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
                <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                </svg>
              </div>
              <div className="mt-3 text-center">
                <h3 className="text-lg leading-6 font-medium text-gray-900">Aprobar Vendedores</h3>
                <div className="mt-2 px-7 py-3">
                  <p className="text-sm text-gray-500">
                    ¿Estás seguro de que deseas aprobar {selectedVendors.size} vendedor{selectedVendors.size !== 1 ? 'es' : ''}?
                    Esta acción los marcará como verificados.
                  </p>
                </div>
                <div className="items-center px-4 py-3">
                  <button
                    onClick={executeBulkAction}
                    disabled={bulkLoading}
                    className="px-4 py-2 bg-green-500 text-white text-base font-medium rounded-md w-24 mr-2 hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-300 disabled:opacity-50"
                  >
                    {bulkLoading ? '...' : 'Aprobar'}
                  </button>
                  <button
                    onClick={closeBulkModal}
                    disabled={bulkLoading}
                    className="px-4 py-2 bg-gray-500 text-white text-base font-medium rounded-md w-24 hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-300"
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Confirmación para Suspender */}
      {bulkModal.type === 'suspend' && bulkModal.isOpen && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
                <svg className="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                </svg>
              </div>
              <div className="mt-3 text-center">
                <h3 className="text-lg leading-6 font-medium text-gray-900">Suspender Vendedores</h3>
                <div className="mt-2 px-7 py-3">
                  <p className="text-sm text-gray-500 mb-4">
                    ¿Estás seguro de que deseas suspender {selectedVendors.size} vendedor{selectedVendors.size !== 1 ? 'es' : ''}?
                  </p>
                  <textarea
                    value={suspendReason}
                    onChange={(e) => setSuspendReason(e.target.value)}
                    placeholder="Razón de la suspensión (obligatorio)"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                    rows={3}
                    required
                  />
                </div>
                <div className="items-center px-4 py-3">
                  <button
                    onClick={executeBulkAction}
                    disabled={bulkLoading || !suspendReason.trim()}
                    className="px-4 py-2 bg-red-500 text-white text-base font-medium rounded-md w-24 mr-2 hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-300 disabled:opacity-50"
                  >
                    {bulkLoading ? '...' : 'Suspender'}
                  </button>
                  <button
                    onClick={closeBulkModal}
                    disabled={bulkLoading}
                    className="px-4 py-2 bg-gray-500 text-white text-base font-medium rounded-md w-24 hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-300"
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Email Bulk */}
      {bulkModal.type === 'email' && bulkModal.isOpen && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-blue-100">
                <svg className="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                </svg>
              </div>
              <div className="mt-3 text-center">
                <h3 className="text-lg leading-6 font-medium text-gray-900">Enviar Email Masivo</h3>
                <div className="mt-2 px-7 py-3">
                  <p className="text-sm text-gray-500 mb-4">
                    Enviar email a {selectedVendors.size} vendedor{selectedVendors.size !== 1 ? 'es' : ''}
                  </p>
                  <input
                    type="text"
                    value={emailData.subject}
                    onChange={(e) => setEmailData(prev => ({ ...prev, subject: e.target.value }))}
                    placeholder="Asunto del email"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 mb-3"
                    required
                  />
                  <textarea
                    value={emailData.message}
                    onChange={(e) => setEmailData(prev => ({ ...prev, message: e.target.value }))}
                    placeholder="Mensaje del email"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={4}
                    required
                  />
                </div>
                <div className="items-center px-4 py-3">
                  <button
                    onClick={executeBulkAction}
                    disabled={bulkLoading || !emailData.subject.trim() || !emailData.message.trim()}
                    className="px-4 py-2 bg-blue-500 text-white text-base font-medium rounded-md w-24 mr-2 hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-300 disabled:opacity-50"
                  >
                    {bulkLoading ? '...' : 'Enviar'}
                  </button>
                  <button
                    onClick={closeBulkModal}
                    disabled={bulkLoading}
                    className="px-4 py-2 bg-gray-500 text-white text-base font-medium rounded-md w-24 hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-300"
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VendorList;