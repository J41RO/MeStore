import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, Clock, User, Building, AlertCircle, Loader2, Mail, Phone, MapPin, Calendar } from 'lucide-react';
import axios from 'axios';
import { useAuthStore } from '../../stores/authStore';

// ============================================================================
// TYPES
// ============================================================================
interface PendingVendor {
  id: string;
  email: string;
  nombre_display: string | null;
  tipo_vendedor: 'persona_natural' | 'persona_juridica';
  vendor_status: string;
  created_at: string;
  telefono: string | null;
  identificacion: string | null;
  direccion_fiscal: string | null;
  ciudad_fiscal: string | null;
  departamento_fiscal: string | null;
  representante_legal?: string;
  email_representante?: string;
}

interface APIResponse {
  success: boolean;
  count: number;
  sellers: PendingVendor[];
}

interface ApproveResponse {
  success: boolean;
  message: string;
  seller_id: string;
  vendor_status: string;
}

interface RejectResponse {
  success: boolean;
  message: string;
  seller_id: string;
  vendor_status: string;
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================
const VendorManagement: React.FC = () => {
  const { token } = useAuthStore();

  // State
  const [vendors, setVendors] = useState<PendingVendor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Action state
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [selectedVendor, setSelectedVendor] = useState<PendingVendor | null>(null);

  // Modal states
  const [showApproveModal, setShowApproveModal] = useState(false);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [rejectReason, setRejectReason] = useState('');
  const [rejectError, setRejectError] = useState('');

  // Toast notification
  const [toast, setToast] = useState<{show: boolean; message: string; type: 'success' | 'error'}>({
    show: false,
    message: '',
    type: 'success'
  });

  // ========== FETCH VENDORS ==========
  const fetchVendors = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.get<APIResponse>(
        `${import.meta.env.VITE_API_URL}/api/v1/auth/admin/pending-sellers`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      if (response.data.success) {
        setVendors(response.data.sellers);
      }
    } catch (err: any) {
      console.error('Error fetching vendors:', err);
      setError(err.response?.data?.detail || 'Error al cargar vendedores pendientes');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVendors();
  }, [token]);

  // ========== APPROVE VENDOR ==========
  const handleApprove = async () => {
    if (!selectedVendor) return;

    setActionLoading(selectedVendor.id);

    try {
      const response = await axios.post<ApproveResponse>(
        `${import.meta.env.VITE_API_URL}/api/v1/auth/admin/approve-seller/${selectedVendor.id}`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      if (response.data.success) {
        showToast(response.data.message, 'success');
        setShowApproveModal(false);
        setSelectedVendor(null);
        // Refresh list
        await fetchVendors();
      }
    } catch (err: any) {
      console.error('Error approving vendor:', err);
      showToast(err.response?.data?.detail || 'Error al aprobar vendedor', 'error');
    } finally {
      setActionLoading(null);
    }
  };

  // ========== REJECT VENDOR ==========
  const handleReject = async () => {
    if (!selectedVendor || !rejectReason.trim()) return;

    if (rejectReason.trim().length < 20) {
      setRejectError('La razón debe tener al menos 20 caracteres');
      return;
    }

    setActionLoading(selectedVendor.id);
    setRejectError('');

    try {
      const response = await axios.post<RejectResponse>(
        `${import.meta.env.VITE_API_URL}/api/v1/auth/admin/reject-seller/${selectedVendor.id}`,
        { reason: rejectReason.trim() },
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      if (response.data.success) {
        showToast(response.data.message, 'success');
        setShowRejectModal(false);
        setSelectedVendor(null);
        setRejectReason('');
        // Refresh list
        await fetchVendors();
      }
    } catch (err: any) {
      console.error('Error rejecting vendor:', err);
      setRejectError(err.response?.data?.detail || 'Error al rechazar vendedor');
    } finally {
      setActionLoading(null);
    }
  };

  // ========== TOAST NOTIFICATION ==========
  const showToast = (message: string, type: 'success' | 'error') => {
    setToast({ show: true, message, type });
    setTimeout(() => {
      setToast({ show: false, message: '', type: 'success' });
    }, 5000);
  };

  // ========== FORMAT DATE ==========
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-CO', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // ========== RENDER ==========
  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-50 via-orange-50 to-purple-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-orange-500 to-purple-600 p-8 text-white shadow-xl">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center space-x-4 mb-2">
            <Building className="w-10 h-10" />
            <h1 className="text-3xl font-bold">Gestión de Vendedores Pendientes</h1>
          </div>
          <p className="text-orange-100 text-sm">
            Aprobar o rechazar solicitudes de registro de vendedores
          </p>
        </div>
      </div>

      {/* Toast Notification */}
      {toast.show && (
        <div className="fixed top-4 right-4 z-50 animate-slide-in-right">
          <div className={`max-w-md rounded-lg shadow-lg p-4 flex items-start space-x-3 ${
            toast.type === 'success' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
          }`}>
            {toast.type === 'success' ? (
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            ) : (
              <XCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            )}
            <p className={`text-sm font-medium ${toast.type === 'success' ? 'text-green-800' : 'text-red-800'}`}>
              {toast.message}
            </p>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto p-8">
        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
            <span className="ml-3 text-gray-600">Cargando vendedores...</span>
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 flex items-start space-x-3">
            <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-red-900 font-semibold mb-1">Error</h3>
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && vendors.length === 0 && (
          <div className="bg-white rounded-2xl shadow-xl p-12 text-center">
            <Clock className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No hay vendedores pendientes
            </h3>
            <p className="text-gray-600">
              Todas las solicitudes han sido procesadas
            </p>
          </div>
        )}

        {/* Vendors Table */}
        {!loading && !error && vendors.length > 0 && (
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
            <div className="px-6 py-4 bg-gradient-to-r from-orange-50 to-purple-50 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">
                Vendedores Pendientes ({vendors.length})
              </h2>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Vendedor
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Tipo
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Estado
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Registro
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {vendors.map((vendor) => (
                    <tr key={vendor.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-start space-x-3">
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                            vendor.tipo_vendedor === 'persona_natural'
                              ? 'bg-blue-100'
                              : 'bg-purple-100'
                          }`}>
                            {vendor.tipo_vendedor === 'persona_natural' ? (
                              <User className="w-5 h-5 text-blue-600" />
                            ) : (
                              <Building className="w-5 h-5 text-purple-600" />
                            )}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900 truncate">
                              {vendor.nombre_display || 'Sin nombre'}
                            </p>
                            <div className="flex items-center space-x-1 text-xs text-gray-500 mt-1">
                              <Mail className="w-3 h-3" />
                              <span className="truncate">{vendor.email}</span>
                            </div>
                            {vendor.telefono && (
                              <div className="flex items-center space-x-1 text-xs text-gray-500 mt-0.5">
                                <Phone className="w-3 h-3" />
                                <span>{vendor.telefono}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            vendor.tipo_vendedor === 'persona_natural'
                              ? 'bg-blue-100 text-blue-800'
                              : 'bg-purple-100 text-purple-800'
                          }`}>
                            {vendor.tipo_vendedor === 'persona_natural' ? 'Natural' : 'Jurídica'}
                          </span>
                          {vendor.identificacion && (
                            <p className="text-xs text-gray-500 mt-1">
                              {vendor.tipo_vendedor === 'persona_natural' ? 'CC' : 'NIT'}: {vendor.identificacion}
                            </p>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          <Clock className="w-3 h-3 mr-1" />
                          {vendor.vendor_status}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center space-x-1 text-xs text-gray-500">
                          <Calendar className="w-3 h-3" />
                          <span>{formatDate(vendor.created_at)}</span>
                        </div>
                        {vendor.direccion_fiscal && (
                          <div className="flex items-center space-x-1 text-xs text-gray-500 mt-1">
                            <MapPin className="w-3 h-3" />
                            <span className="truncate">
                              {vendor.ciudad_fiscal}, {vendor.departamento_fiscal}
                            </span>
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end space-x-2">
                          <button
                            onClick={() => {
                              setSelectedVendor(vendor);
                              setShowApproveModal(true);
                            }}
                            disabled={actionLoading === vendor.id}
                            className="inline-flex items-center px-3 py-1.5 bg-green-600 text-white text-xs font-medium rounded-lg hover:bg-green-700 disabled:bg-gray-400 transition-colors"
                          >
                            <CheckCircle className="w-4 h-4 mr-1" />
                            Aprobar
                          </button>
                          <button
                            onClick={() => {
                              setSelectedVendor(vendor);
                              setShowRejectModal(true);
                              setRejectReason('');
                              setRejectError('');
                            }}
                            disabled={actionLoading === vendor.id}
                            className="inline-flex items-center px-3 py-1.5 bg-red-600 text-white text-xs font-medium rounded-lg hover:bg-red-700 disabled:bg-gray-400 transition-colors"
                          >
                            <XCircle className="w-4 h-4 mr-1" />
                            Rechazar
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Approve Modal */}
      {showApproveModal && selectedVendor && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 animate-scale-in">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900">Aprobar Vendedor</h3>
            </div>

            <p className="text-gray-600 mb-6">
              ¿Confirmas que quieres aprobar a <strong>{selectedVendor.nombre_display}</strong>?
            </p>

            <div className="bg-gray-50 rounded-lg p-4 mb-6 space-y-2 text-sm">
              <p className="text-gray-700">
                <strong>Email:</strong> {selectedVendor.email}
              </p>
              <p className="text-gray-700">
                <strong>Tipo:</strong> {selectedVendor.tipo_vendedor === 'persona_natural' ? 'Persona Natural' : 'Persona Jurídica'}
              </p>
              {selectedVendor.identificacion && (
                <p className="text-gray-700">
                  <strong>{selectedVendor.tipo_vendedor === 'persona_natural' ? 'Cédula' : 'NIT'}:</strong> {selectedVendor.identificacion}
                </p>
              )}
            </div>

            <div className="flex space-x-3">
              <button
                onClick={() => {
                  setShowApproveModal(false);
                  setSelectedVendor(null);
                }}
                disabled={actionLoading === selectedVendor.id}
                className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200 disabled:opacity-50 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleApprove}
                disabled={actionLoading === selectedVendor.id}
                className="flex-1 px-4 py-2 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 disabled:bg-gray-400 transition-colors flex items-center justify-center"
              >
                {actionLoading === selectedVendor.id ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                    Aprobando...
                  </>
                ) : (
                  'Aprobar'
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Reject Modal */}
      {showRejectModal && selectedVendor && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 animate-scale-in">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                <XCircle className="w-6 h-6 text-red-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900">Rechazar Vendedor</h3>
            </div>

            <p className="text-gray-600 mb-4">
              Proporciona una razón para rechazar a <strong>{selectedVendor.nombre_display}</strong>
            </p>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Razón del rechazo (mínimo 20 caracteres) *
              </label>
              <textarea
                value={rejectReason}
                onChange={(e) => {
                  setRejectReason(e.target.value);
                  if (e.target.value.trim().length >= 20) {
                    setRejectError('');
                  }
                }}
                placeholder="Ej: La documentación proporcionada no cumple con los requisitos necesarios para la aprobación..."
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none ${
                  rejectError ? 'border-red-300' : 'border-gray-300'
                }`}
                rows={4}
                maxLength={500}
              />
              <div className="flex items-center justify-between mt-2">
                {rejectError ? (
                  <p className="text-xs text-red-600">{rejectError}</p>
                ) : (
                  <p className="text-xs text-gray-500">
                    {rejectReason.trim().length} / 500 caracteres
                  </p>
                )}
                {rejectReason.trim().length >= 20 && (
                  <p className="text-xs text-green-600 flex items-center">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    Válido
                  </p>
                )}
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={() => {
                  setShowRejectModal(false);
                  setSelectedVendor(null);
                  setRejectReason('');
                  setRejectError('');
                }}
                disabled={actionLoading === selectedVendor.id}
                className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200 disabled:opacity-50 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleReject}
                disabled={actionLoading === selectedVendor.id || rejectReason.trim().length < 20}
                className="flex-1 px-4 py-2 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 disabled:bg-gray-400 transition-colors flex items-center justify-center"
              >
                {actionLoading === selectedVendor.id ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                    Rechazando...
                  </>
                ) : (
                  'Rechazar'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VendorManagement;
