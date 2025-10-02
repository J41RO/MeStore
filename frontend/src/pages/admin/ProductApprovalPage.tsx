import React, { useState, useEffect, useCallback } from 'react';
import {
  CheckCircle, XCircle, Clock, Package, RefreshCw,
  Eye, User, Calendar, AlertCircle, Filter
} from 'lucide-react';
import axios from 'axios';

interface Product {
  id: string;
  name: string;
  sku: string;
  description: string;
  precio_venta: number;
  stock_quantity: number;
  category: string;
  status: string;
  vendedor_id: string;
  created_at: string;
  main_image_url?: string;
  images?: Array<{ public_url: string }>;
}

interface ProductApprovalStats {
  total_pending: number;
  total_approved: number;
  total_rejected: number;
}

const ProductApprovalPage: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [stats, setStats] = useState<ProductApprovalStats>({
    total_pending: 0,
    total_approved: 0,
    total_rejected: 0
  });
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>('PENDING');
  const [processing, setProcessing] = useState<string | null>(null);

  const API_BASE = 'http://192.168.1.137:8000';

  const fetchProducts = useCallback(async (showRefresh = false) => {
    if (showRefresh) setRefreshing(true);
    else setLoading(true);

    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_BASE}/api/v1/products`, {
        headers: { Authorization: `Bearer ${token}` },
        params: { status: filterStatus, limit: 100 }
      });

      // Handle PaginatedResponse structure: response.data.data contains the products array
      const productsData = response.data.data || response.data.items || response.data || [];
      setProducts(Array.isArray(productsData) ? productsData : []);
    } catch (error) {
      console.error('Error fetching products:', error);
      setProducts([]); // Set empty array on error
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [filterStatus]);

  const fetchStats = useCallback(async () => {
    try {
      const token = localStorage.getItem('access_token');

      const [pending, approved, rejected] = await Promise.all([
        axios.get(`${API_BASE}/api/v1/products`, {
          headers: { Authorization: `Bearer ${token}` },
          params: { status: 'PENDING', limit: 1000 }
        }),
        axios.get(`${API_BASE}/api/v1/products`, {
          headers: { Authorization: `Bearer ${token}` },
          params: { status: 'APPROVED', limit: 1000 }
        }),
        axios.get(`${API_BASE}/api/v1/products`, {
          headers: { Authorization: `Bearer ${token}` },
          params: { status: 'REJECTED', limit: 1000 }
        })
      ]);

      // Extract from PaginatedResponse: response.data.pagination.total
      setStats({
        total_pending: pending.data.pagination?.total || pending.data.data?.length || 0,
        total_approved: approved.data.pagination?.total || approved.data.data?.length || 0,
        total_rejected: rejected.data.pagination?.total || rejected.data.data?.length || 0
      });
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  }, []);

  useEffect(() => {
    fetchProducts();
    fetchStats();
  }, [fetchProducts, fetchStats]);

  const handleApprove = async (productId: string) => {
    setProcessing(productId);
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        `${API_BASE}/api/v1/products/${productId}/approve`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Update stats optimistically
      setStats(prev => ({
        total_pending: Math.max(0, prev.total_pending - 1),
        total_approved: prev.total_approved + 1,
        total_rejected: prev.total_rejected
      }));

      // Refresh data from server
      await fetchProducts();
      await fetchStats();

      alert('Producto aprobado exitosamente');
    } catch (error: any) {
      console.error('Error approving product:', error);
      alert(error.response?.data?.detail || 'Error al aprobar producto');
      // Revert optimistic update on error
      await fetchStats();
    } finally {
      setProcessing(null);
    }
  };

  const handleReject = async (productId: string) => {
    setProcessing(productId);
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        `${API_BASE}/api/v1/products/${productId}/reject`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Update stats optimistically
      setStats(prev => ({
        total_pending: Math.max(0, prev.total_pending - 1),
        total_approved: prev.total_approved,
        total_rejected: prev.total_rejected + 1
      }));

      // Refresh data from server
      await fetchProducts();
      await fetchStats();

      alert('Producto rechazado exitosamente');
    } catch (error: any) {
      console.error('Error rejecting product:', error);
      alert(error.response?.data?.detail || 'Error al rechazar producto');
      // Revert optimistic update on error
      await fetchStats();
    } finally {
      setProcessing(null);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PENDING':
        return <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">Pendiente</span>;
      case 'APPROVED':
        return <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">Aprobado</span>;
      case 'REJECTED':
        return <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">Rechazado</span>;
      default:
        return <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">{status}</span>;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Aprobación de Productos</h1>
            <p className="text-gray-600 mt-2">Gestión de productos pendientes de revisión</p>
          </div>
          <button
            onClick={() => { fetchProducts(true); fetchStats(); }}
            disabled={refreshing}
            className="flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Actualizar
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Pendientes</p>
              <p className="text-3xl font-bold text-yellow-600">{stats.total_pending}</p>
            </div>
            <Clock className="w-12 h-12 text-yellow-500" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Aprobados</p>
              <p className="text-3xl font-bold text-green-600">{stats.total_approved}</p>
            </div>
            <CheckCircle className="w-12 h-12 text-green-500" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Rechazados</p>
              <p className="text-3xl font-bold text-red-600">{stats.total_rejected}</p>
            </div>
            <XCircle className="w-12 h-12 text-red-500" />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex items-center space-x-4">
          <Filter className="w-5 h-5 text-gray-500" />
          <span className="text-sm font-medium text-gray-700">Filtrar por estado:</span>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="PENDING">Pendientes</option>
            <option value="APPROVED">Aprobados</option>
            <option value="REJECTED">Rechazados</option>
            <option value="">Todos</option>
          </select>
        </div>
      </div>

      {/* Products Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          {loading ? (
            <div className="flex justify-center items-center py-12">
              <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
              <span className="ml-3">Cargando productos...</span>
            </div>
          ) : products.length === 0 ? (
            <div className="text-center py-12">
              <Package className="w-16 h-16 mx-auto text-gray-300 mb-4" />
              <p className="text-gray-500 text-lg">No hay productos {filterStatus ? filterStatus.toLowerCase() : ''}</p>
            </div>
          ) : (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Producto</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Categoría</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Precio</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stock</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha Creación</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {products.map((product) => (
                  <tr key={product.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          {product.main_image_url || (product.images && product.images[0]) ? (
                            <img
                              className="h-10 w-10 rounded object-cover"
                              src={product.main_image_url || product.images![0].public_url}
                              alt={product.name}
                            />
                          ) : (
                            <div className="h-10 w-10 rounded bg-gray-200 flex items-center justify-center">
                              <Package className="w-5 h-5 text-gray-400" />
                            </div>
                          )}
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{product.name}</div>
                          <div className="text-sm text-gray-500">SKU: {product.sku}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{product.category || product.categoria || '-'}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${(product.price || product.precio_venta || 0).toLocaleString()}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{product.stock || product.stock_quantity || 0} unidades</td>
                    <td className="px-6 py-4 whitespace-nowrap">{getStatusBadge(product.status)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{formatDate(product.created_at)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => { setSelectedProduct(product); setShowDetails(true); }}
                          className="text-blue-600 hover:text-blue-900"
                          title="Ver detalles"
                        >
                          <Eye className="w-5 h-5" />
                        </button>
                        {product.status === 'PENDING' && (
                          <>
                            <button
                              onClick={() => handleApprove(product.id)}
                              disabled={processing === product.id}
                              className="text-green-600 hover:text-green-900 disabled:opacity-50"
                              title="Aprobar"
                            >
                              <CheckCircle className="w-5 h-5" />
                            </button>
                            <button
                              onClick={() => handleReject(product.id)}
                              disabled={processing === product.id}
                              className="text-red-600 hover:text-red-900 disabled:opacity-50"
                              title="Rechazar"
                            >
                              <XCircle className="w-5 h-5" />
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Details Modal */}
      {showDetails && selectedProduct && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold text-gray-900">Detalles del Producto</h2>
                <button
                  onClick={() => setShowDetails(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-6">
                {/* Image */}
                {(selectedProduct.main_image_url || selectedProduct.images) && (
                  <div className="flex justify-center">
                    <img
                      className="h-48 w-48 object-cover rounded-lg"
                      src={selectedProduct.main_image_url || selectedProduct.images![0].public_url}
                      alt={selectedProduct.name}
                    />
                  </div>
                )}

                {/* Info Grid */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Nombre</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedProduct.name}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">SKU</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedProduct.sku}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Categoría</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedProduct.category || selectedProduct.categoria || '-'}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Precio</label>
                    <p className="mt-1 text-sm text-gray-900">${(selectedProduct.price || selectedProduct.precio_venta || 0).toLocaleString()}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Stock</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedProduct.stock || selectedProduct.stock_quantity || 0} unidades</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Estado</label>
                    <div className="mt-1">{getStatusBadge(selectedProduct.status)}</div>
                  </div>
                </div>

                {/* Description */}
                <div>
                  <label className="text-sm font-medium text-gray-500">Descripción</label>
                  <p className="mt-1 text-sm text-gray-900">{selectedProduct.description}</p>
                </div>

                {/* Actions */}
                {selectedProduct.status === 'PENDING' && (
                  <div className="flex space-x-4 pt-4 border-t">
                    <button
                      onClick={() => {
                        handleApprove(selectedProduct.id);
                        setShowDetails(false);
                      }}
                      disabled={processing === selectedProduct.id}
                      className="flex-1 flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
                    >
                      <CheckCircle className="w-5 h-5 mr-2" />
                      Aprobar Producto
                    </button>
                    <button
                      onClick={() => {
                        handleReject(selectedProduct.id);
                        setShowDetails(false);
                      }}
                      disabled={processing === selectedProduct.id}
                      className="flex-1 flex items-center justify-center px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
                    >
                      <XCircle className="w-5 h-5 mr-2" />
                      Rechazar Producto
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductApprovalPage;