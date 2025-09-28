import React, { useState, useEffect } from 'react';
import { Users, UserCheck, UserX, Shield, Plus, Edit, Trash2, UserMinus, CheckCircle } from 'lucide-react';

interface User {
  id: string;
  email: string;
  nombre: string;
  apellido: string;
  user_type: string;
  vendor_status: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

interface UserStats {
  total_users: number;
  total_vendors: number;
  total_admins: number;
  verified_users: number;
  pending_vendors: number;
  recent_registrations: number;
}

const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');

      if (!token) {
        setError('No authentication token found');
        return;
      }

      // Cargar estadísticas
      try {
        const statsResponse = await fetch('http://192.168.1.137:8000/api/v1/superuser-admin/users/stats', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (statsResponse.ok) {
          const statsData = await statsResponse.json();
          setStats(statsData);
        }
      } catch (err) {
        console.warn('Stats endpoint failed, using defaults');
        setStats({
          totalUsers: 2,
          totalVendors: 1,
          totalAdmins: 1,
          verifiedUsers: 2,
          activeUsers: 2,
          inactiveUsers: 0
        });
      }

      // Cargar lista de usuarios
      const usersResponse = await fetch('http://192.168.1.137:8000/api/v1/superuser-admin/users?limit=50', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (usersResponse.ok) {
        const usersData = await usersResponse.json();
        setUsers(usersData.users || []);
      } else {
        setError('Failed to load users');
      }

    } catch (err) {
      setError('Error loading user data: ' + (err instanceof Error ? err.message : 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const performUserAction = async (userId: string, action: string, reason?: string) => {
    try {
      setActionLoading(userId);
      const token = localStorage.getItem('access_token');

      const response = await fetch(`http://192.168.1.137:8000/api/v1/superuser-admin/users/${userId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action, reason })
      });

      if (response.ok) {
        const result = await response.json();
        alert(`✅ ${result.message}`);
        await loadUserData(); // Recargar datos
      } else {
        const error = await response.json();
        alert(`❌ Error: ${error.detail || 'Action failed'}`);
      }
    } catch (err) {
      alert(`❌ Error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setActionLoading(null);
    }
  };

  const handleActivateUser = (userId: string) => {
    if (confirm('¿Confirmas que quieres activar este usuario?')) {
      performUserAction(userId, 'activate', 'Activado por administrador');
    }
  };

  const handleSuspendUser = (userId: string) => {
    const reason = prompt('Motivo de la suspensión (opcional):');
    if (confirm('¿Confirmas que quieres suspender este usuario?')) {
      performUserAction(userId, 'suspend', reason || 'Suspendido por administrador');
    }
  };

  const handleVerifyUser = (userId: string) => {
    if (confirm('¿Confirmas que quieres verificar este usuario?')) {
      performUserAction(userId, 'verify', 'Verificado por administrador');
    }
  };

  const handleDeleteUser = (userId: string) => {
    const reason = prompt('Motivo de la eliminación (obligatorio):');
    if (reason && confirm('¿CONFIRMAS que quieres ELIMINAR este usuario? Esta acción no se puede deshacer.')) {
      performUserAction(userId, 'delete', reason);
    }
  };

  const getUserActions = (user: User) => {
    const actions = [];

    // No permitir acciones en SUPERUSER
    if (user.user_type === 'SUPERUSER') {
      return (
        <span className="text-xs text-gray-500 italic">
          Protegido
        </span>
      );
    }

    // Activar/Suspender
    if (user.is_active) {
      actions.push(
        <button
          key="suspend"
          onClick={() => handleSuspendUser(user.id)}
          disabled={actionLoading === user.id}
          className="text-orange-600 hover:text-orange-800 text-xs px-2 py-1 border border-orange-300 rounded hover:bg-orange-50 transition-colors"
          title="Suspender usuario"
        >
          <UserMinus className="h-3 w-3 inline mr-1" />
          Suspender
        </button>
      );
    } else {
      actions.push(
        <button
          key="activate"
          onClick={() => handleActivateUser(user.id)}
          disabled={actionLoading === user.id}
          className="text-green-600 hover:text-green-800 text-xs px-2 py-1 border border-green-300 rounded hover:bg-green-50 transition-colors"
          title="Activar usuario"
        >
          <CheckCircle className="h-3 w-3 inline mr-1" />
          Activar
        </button>
      );
    }

    // Verificar
    if (!user.is_verified) {
      actions.push(
        <button
          key="verify"
          onClick={() => handleVerifyUser(user.id)}
          disabled={actionLoading === user.id}
          className="text-blue-600 hover:text-blue-800 text-xs px-2 py-1 border border-blue-300 rounded hover:bg-blue-50 transition-colors"
          title="Verificar usuario"
        >
          <UserCheck className="h-3 w-3 inline mr-1" />
          Verificar
        </button>
      );
    }

    // Eliminar
    actions.push(
      <button
        key="delete"
        onClick={() => handleDeleteUser(user.id)}
        disabled={actionLoading === user.id}
        className="text-red-600 hover:text-red-800 text-xs px-2 py-1 border border-red-300 rounded hover:bg-red-50 transition-colors"
        title="Eliminar usuario"
      >
        <Trash2 className="h-3 w-3 inline mr-1" />
        Eliminar
      </button>
    );

    return (
      <div className="flex space-x-1 flex-wrap">
        {actionLoading === user.id ? (
          <span className="text-xs text-gray-500">Procesando...</span>
        ) : (
          actions
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Cargando usuarios...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          Error: {error}
          <button
            onClick={loadUserData}
            className="ml-4 bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 pb-4">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Gestión de Usuarios</h1>
            <p className="text-gray-600">Administra todos los usuarios del sistema</p>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={loadUserData}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
            >
              🔄 Actualizar
            </button>
            <button
              onClick={() => alert('Función de agregar usuario disponible próximamente')}
              className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
            >
              <Plus className="h-4 w-4 inline mr-1" />
              Nuevo Usuario
            </button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-lg shadow border">
            <div className="flex items-center">
              <Users className="h-8 w-8 text-blue-500" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Total Usuarios</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_users}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow border">
            <div className="flex items-center">
              <UserCheck className="h-8 w-8 text-green-500" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Verificados</p>
                <p className="text-2xl font-bold text-gray-900">{stats.verified_users}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow border">
            <div className="flex items-center">
              <Shield className="h-8 w-8 text-purple-500" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Vendedores</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_vendors}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg shadow border">
            <div className="flex items-center">
              <UserX className="h-8 w-8 text-red-500" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Vendedores Pendientes</p>
                <p className="text-2xl font-bold text-gray-900">{stats.pending_vendors}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Users Table */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Lista de Usuarios ({users.length})</h2>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Usuario
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tipo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Fecha Registro
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{user.email}</div>
                      <div className="text-sm text-gray-500">
                        {user.nombre} {user.apellido}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      user.user_type === 'SUPERUSER' ? 'bg-purple-100 text-purple-800' :
                      user.user_type === 'ADMIN' ? 'bg-blue-100 text-blue-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {user.user_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex space-x-2">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {user.is_active ? 'Activo' : 'Inactivo'}
                      </span>
                      {user.is_verified && (
                        <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                          Verificado
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {getUserActions(user)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {users.length === 0 && (
          <div className="text-center py-8">
            <Users className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No hay usuarios</h3>
            <p className="mt-1 text-sm text-gray-500">No se encontraron usuarios en el sistema.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserManagement;