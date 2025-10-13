import React, { useState, useEffect } from 'react';
import { Check, X, Clock, Building, User, Mail, Phone, FileText, AlertCircle } from 'lucide-react';
import axios from 'axios';
import { useAuthStore } from '../../../stores/authStore';

interface PendingSeller {
  id: string;
  email: string;
  nombre_display: string;
  identificacion: string;
  tipo_vendedor: 'persona_natural' | 'persona_juridica';
  vendor_status: string;
  telefono: string;
  direccion_fiscal: string;
  ciudad_fiscal: string;
  departamento_fiscal: string;
  created_at: string;
  representante_legal?: string;
  email_representante?: string;
}

const AdminPendingSellers: React.FC = () => {
  const [sellers, setSellers] = useState<PendingSeller[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [selectedSeller, setSelectedSeller] = useState<PendingSeller | null>(null);
  const [rejectionReason, setRejectionReason] = useState('');
  const [rejectionError, setRejectionError] = useState('');

  const token = useAuthStore((state) => state.token);
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchPendingSellers();
  }, []);

  const fetchPendingSellers = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await axios.get(`${API_URL}/api/v1/auth/admin/pending-sellers`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      setSellers(response.data.sellers || []);
    } catch (err: any) {
      console.error('Error fetching pending sellers:', err);
      setError(err.response?.data?.detail || 'Error cargando vendedores pendientes');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (sellerId: string) => {
    if (!window.confirm('¿Estás seguro de aprobar este vendedor?')) {
      return;
    }

    try {
      setActionLoading(sellerId);

      await axios.post(
        `${API_URL}/api/v1/auth/admin/approve-seller/${sellerId}`,
        {},
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      // Refresh list
      await fetchPendingSellers();

      alert('Vendedor aprobado exitosamente');
    } catch (err: any) {
      console.error('Error approving seller:', err);
      alert(err.response?.data?.detail || 'Error aprobando vendedor');
    } finally {
      setActionLoading(null);
    }
  };

  const openRejectModal = (seller: PendingSeller) => {
    setSelectedSeller(seller);
    setRejectionReason('');
    setRejectionError('');
    setShowRejectModal(true);
  };

  const handleReject = async () => {
    if (!selectedSeller) return;

    // Validar razón
    if (rejectionReason.trim().length < 20) {
      setRejectionError('La razón debe tener al menos 20 caracteres');
      return;
    }

    try {
      setActionLoading(selectedSeller.id);

      await axios.post(
        `${API_URL}/api/v1/auth/admin/reject-seller/${selectedSeller.id}`,
        { reason: rejectionReason.trim() },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      setShowRejectModal(false);
      await fetchPendingSellers();

      alert('Vendedor rechazado');
    } catch (err: any) {
      console.error('Error rejecting seller:', err);
      setRejectionError(err.response?.data?.detail || 'Error rechazando vendedor');
    } finally {
      setActionLoading(null);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-CO', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-red-800">Error</h3>
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Vendedores Pendientes</h1>
        <p className="text-gray-600 mt-2">
          Revisa y aprueba las solicitudes de nuevos vendedores
        </p>
      </div>

      {sellers.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <Clock className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-700">No hay vendedores pendientes</h3>
          <p className="text-gray-500 mt-2">Todas las solicitudes han sido procesadas</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Tipo
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Nombre/Razón Social
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Identificación
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Contacto
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ubicación
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Fecha
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {sellers.map((seller) => (
                  <tr key={seller.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {seller.tipo_vendedor === 'persona_natural' ? (
                          <User className="w-8 h-8 text-blue-500" />
                        ) : (
                          <Building className="w-8 h-8 text-purple-500" />
                        )}
                        <span className="ml-2 text-xs text-gray-500">
                          {seller.tipo_vendedor === 'persona_natural' ? 'Natural' : 'Jurídica'}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">
                        {seller.nombre_display}
                      </div>
                      <div className="text-sm text-gray-500">{seller.email}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {seller.identificacion}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center text-sm text-gray-700">
                        <Phone className="w-4 h-4 mr-1 text-gray-400" />
                        {seller.telefono}
                      </div>
                      {seller.email_representante && (
                        <div className="flex items-center text-xs text-gray-500 mt-1">
                          <Mail className="w-3 h-3 mr-1" />
                          {seller.email_representante}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700">
                      <div>{seller.ciudad_fiscal}</div>
                      <div className="text-xs text-gray-500">{seller.departamento_fiscal}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(seller.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleApprove(seller.id)}
                          disabled={actionLoading === seller.id}
                          className="inline-flex items-center px-3 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
                        >
                          {actionLoading === seller.id ? (
                            <span className="animate-spin mr-1">⏳</span>
                          ) : (
                            <Check className="w-4 h-4 mr-1" />
                          )}
                          Aprobar
                        </button>
                        <button
                          onClick={() => openRejectModal(seller)}
                          disabled={actionLoading === seller.id}
                          className="inline-flex items-center px-3 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
                        >
                          <X className="w-4 h-4 mr-1" />
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

      {/* Modal de Rechazo */}
      {showRejectModal && selectedSeller && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Rechazar Vendedor
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              {selectedSeller.nombre_display} - {selectedSeller.email}
            </p>

            <label className="block text-sm font-medium text-gray-700 mb-2">
              Razón del rechazo (mínimo 20 caracteres) *
            </label>
            <textarea
              value={rejectionReason}
              onChange={(e) => {
                setRejectionReason(e.target.value);
                setRejectionError('');
              }}
              placeholder="Ej: Los documentos proporcionados no son legibles. Por favor, sube copias de mejor calidad..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none"
              rows={4}
            />

            <div className="mt-2 text-xs text-gray-500">
              {rejectionReason.length} / 20 caracteres mínimos
            </div>

            {rejectionError && (
              <div className="mt-2 text-sm text-red-600">
                {rejectionError}
              </div>
            )}

            <div className="mt-6 flex justify-end space-x-3">
              <button
                onClick={() => setShowRejectModal(false)}
                disabled={actionLoading !== null}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleReject}
                disabled={actionLoading !== null || rejectionReason.trim().length < 20}
                className="px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
              >
                {actionLoading ? 'Procesando...' : 'Confirmar Rechazo'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPendingSellers;
