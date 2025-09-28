import React, { useState, useEffect } from 'react';
import { User, UpdateUserData, superuserService } from '../../services/superuserService';

interface UserDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  user: User;
  onUserUpdated: (updatedUser: User) => void;
  mode: 'view' | 'edit';
}

interface AuditLogEntry {
  id: string;
  action_name: string;
  timestamp: string;
  performed_by: string;
  target_id: string;
  details: any;
}

const UserDetailsModal: React.FC<UserDetailsModalProps> = ({
  isOpen,
  onClose,
  user,
  onUserUpdated,
  mode,
}) => {
  const [currentMode, setCurrentMode] = useState<'view' | 'edit'>(mode);
  const [formData, setFormData] = useState<UpdateUserData>({});
  const [auditLog, setAuditLog] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'details' | 'security' | 'activity'>('details');

  useEffect(() => {
    if (isOpen && user) {
      setCurrentMode(mode);
      setFormData({
        nombre: user.nombre,
        apellido: user.apellido,
        user_type: user.user_type,
        security_clearance_level: user.security_clearance_level,
        is_active: user.is_active,
        is_verified: user.is_verified,
        telefono: user.telefono,
        cedula: user.cedula,
      });
      loadAuditLog();
    }
  }, [isOpen, user, mode]);

  const loadAuditLog = async () => {
    try {
      setLoading(true);
      const logs = await superuserService.getUserAuditLog(user.id);
      setAuditLog(logs);
    } catch (error) {
      console.error('Error loading audit log:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      const updatedUser = await superuserService.updateUser(user.id, formData);
      onUserUpdated(updatedUser);
      setCurrentMode('view');
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Error updating user');
    } finally {
      setSaving(false);
    }
  };

  const handleInputChange = (key: keyof UpdateUserData, value: any) => {
    setFormData(prev => ({ ...prev, [key]: value }));
  };

  const resetPassword = async () => {
    if (confirm('¿Confirmas que quieres forzar el cambio de contraseña para este usuario? El usuario deberá cambiar su contraseña en el próximo login.')) {
      try {
        setSaving(true);
        await superuserService.resetUserPassword(user.id);
        alert('✅ Password reset scheduled - User will be required to change password on next login');
      } catch (error: any) {
        alert('❌ Error scheduling password reset: ' + (error.response?.data?.detail || error.message));
      } finally {
        setSaving(false);
      }
    }
  };

  const resendVerification = async () => {
    try {
      setSaving(true);
      await superuserService.resendVerificationEmail(user.id);
      alert('Verification email sent successfully');
    } catch (error: any) {
      alert('Error sending verification: ' + (error.response?.data?.detail || error.message));
    } finally {
      setSaving(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getUserTypeIcon = (type: string) => {
    switch (type) {
      case 'BUYER': return '🛒';
      case 'VENDOR': return '🏪';
      case 'ADMIN': return '⚙';
      case 'SUPERUSER': return '👑';
      default: return '👤';
    }
  };

  const getSecurityLevelColor = (level: number) => {
    if (level >= 5) return 'bg-red-100 text-red-800 border-red-200';
    if (level >= 3) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    return 'bg-green-100 text-green-800 border-green-200';
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div
          className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
          onClick={onClose}
        ></div>

        {/* Modal panel */}
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
          {/* Header */}
          <div className="bg-white px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  <div className="h-12 w-12 rounded-full bg-gradient-to-r from-blue-400 to-blue-600 flex items-center justify-center text-white font-semibold text-lg">
                    {user.nombre?.charAt(0)?.toUpperCase() || 'U'}
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-medium text-gray-900">
                    {user.nombre} {user.apellido}
                  </h3>
                  <p className="text-sm text-gray-500">
                    {getUserTypeIcon(user.user_type)} {user.user_type} • ID: {user.id.slice(0, 8)}...
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {currentMode === 'view' && (
                  <button
                    onClick={() => setCurrentMode('edit')}
                    className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
                  >
                    Edit User
                  </button>
                )}
                {currentMode === 'edit' && (
                  <>
                    <button
                      onClick={() => setCurrentMode('view')}
                      className="px-4 py-2 bg-gray-300 text-gray-700 text-sm rounded-md hover:bg-gray-400"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSave}
                      disabled={saving}
                      className="px-4 py-2 bg-green-600 text-white text-sm rounded-md hover:bg-green-700 disabled:opacity-50"
                    >
                      {saving ? 'Saving...' : 'Save Changes'}
                    </button>
                  </>
                )}
                <button
                  onClick={onClose}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex">
              <button
                onClick={() => setActiveTab('details')}
                className={`px-6 py-3 border-b-2 font-medium text-sm ${
                  activeTab === 'details'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                👤 User Details
              </button>
              <button
                onClick={() => setActiveTab('security')}
                className={`px-6 py-3 border-b-2 font-medium text-sm ${
                  activeTab === 'security'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                🔒 Security
              </button>
              <button
                onClick={() => setActiveTab('activity')}
                className={`px-6 py-3 border-b-2 font-medium text-sm ${
                  activeTab === 'activity'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                📊 Activity Log
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {error && (
              <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                {error}
              </div>
            )}

            {/* User Details Tab */}
            {activeTab === 'details' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Basic Information */}
                  <div>
                    <h4 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h4>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          First Name
                        </label>
                        {currentMode === 'edit' ? (
                          <input
                            type="text"
                            value={formData.nombre || ''}
                            onChange={(e) => handleInputChange('nombre', e.target.value)}
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                          />
                        ) : (
                          <p className="mt-1 text-sm text-gray-900">{user.nombre}</p>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Last Name
                        </label>
                        {currentMode === 'edit' ? (
                          <input
                            type="text"
                            value={formData.apellido || ''}
                            onChange={(e) => handleInputChange('apellido', e.target.value)}
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                          />
                        ) : (
                          <p className="mt-1 text-sm text-gray-900">{user.apellido}</p>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Email
                        </label>
                        <p className="mt-1 text-sm text-gray-900">{user.email}</p>
                        <p className="text-xs text-gray-500">Email cannot be changed</p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Phone
                        </label>
                        {currentMode === 'edit' ? (
                          <input
                            type="text"
                            value={formData.telefono || ''}
                            onChange={(e) => handleInputChange('telefono', e.target.value)}
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                          />
                        ) : (
                          <p className="mt-1 text-sm text-gray-900">{user.telefono || 'Not provided'}</p>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Document (Cédula)
                        </label>
                        {currentMode === 'edit' ? (
                          <input
                            type="text"
                            value={formData.cedula || ''}
                            onChange={(e) => handleInputChange('cedula', e.target.value)}
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                          />
                        ) : (
                          <p className="mt-1 text-sm text-gray-900">{user.cedula || 'Not provided'}</p>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Account Information */}
                  <div>
                    <h4 className="text-lg font-medium text-gray-900 mb-4">Account Information</h4>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          User Type
                        </label>
                        {currentMode === 'edit' ? (
                          <select
                            value={formData.user_type || user.user_type}
                            onChange={(e) => handleInputChange('user_type', e.target.value as any)}
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                          >
                            <option value="BUYER">🛒 Buyer</option>
                            <option value="VENDOR">🏪 Vendor</option>
                            <option value="ADMIN">⚙ Admin</option>
                            <option value="SUPERUSER">👑 Superuser</option>
                          </select>
                        ) : (
                          <div className="mt-1">
                            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${
                              user.user_type === 'BUYER' ? 'bg-blue-100 text-blue-800 border-blue-200' :
                              user.user_type === 'VENDOR' ? 'bg-green-100 text-green-800 border-green-200' :
                              user.user_type === 'ADMIN' ? 'bg-purple-100 text-purple-800 border-purple-200' :
                              'bg-red-100 text-red-800 border-red-200'
                            }`}>
                              {getUserTypeIcon(user.user_type)} {user.user_type}
                            </span>
                          </div>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Security Clearance Level
                        </label>
                        {currentMode === 'edit' ? (
                          <select
                            value={formData.security_clearance_level || user.security_clearance_level}
                            onChange={(e) => handleInputChange('security_clearance_level', parseInt(e.target.value))}
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                          >
                            <option value={1}>Level 1 (Standard)</option>
                            <option value={2}>Level 2 (Standard+)</option>
                            <option value={3}>Level 3 (Medium)</option>
                            <option value={4}>Level 4 (Medium+)</option>
                            <option value={5}>Level 5 (High)</option>
                            <option value={6}>Level 6 (High+)</option>
                            <option value={7}>Level 7 (Critical)</option>
                          </select>
                        ) : (
                          <div className="mt-1">
                            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getSecurityLevelColor(user.security_clearance_level)}`}>
                              Level {user.security_clearance_level}
                            </span>
                          </div>
                        )}
                      </div>

                      <div className="flex items-center space-x-6">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Account Status
                          </label>
                          {currentMode === 'edit' ? (
                            <label className="flex items-center">
                              <input
                                type="checkbox"
                                checked={formData.is_active ?? user.is_active}
                                onChange={(e) => handleInputChange('is_active', e.target.checked)}
                                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                              />
                              <span className="ml-2 text-sm text-gray-900">Active</span>
                            </label>
                          ) : (
                            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                              user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                            }`}>
                              {user.is_active ? '✅ Active' : '❌ Inactive'}
                            </span>
                          )}
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Verification Status
                          </label>
                          {currentMode === 'edit' ? (
                            <label className="flex items-center">
                              <input
                                type="checkbox"
                                checked={formData.is_verified ?? user.is_verified}
                                onChange={(e) => handleInputChange('is_verified', e.target.checked)}
                                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                              />
                              <span className="ml-2 text-sm text-gray-900">Verified</span>
                            </label>
                          ) : (
                            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                              user.is_verified ? 'bg-blue-100 text-blue-800' : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {user.is_verified ? '🔒 Verified' : '⏳ Unverified'}
                            </span>
                          )}
                        </div>
                      </div>

                      <div className="pt-4 border-t border-gray-200">
                        <p className="text-sm text-gray-500">
                          <strong>Registered:</strong> {formatDate(user.created_at)}
                        </p>
                        {user.updated_at && (
                          <p className="text-sm text-gray-500">
                            <strong>Last Updated:</strong> {formatDate(user.updated_at)}
                          </p>
                        )}
                        {user.last_login && (
                          <p className="text-sm text-gray-500">
                            <strong>Last Login:</strong> {formatDate(user.last_login)}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Security Tab */}
            {activeTab === 'security' && (
              <div className="space-y-6">
                <h4 className="text-lg font-medium text-gray-900">Security Actions</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="p-4 border border-gray-200 rounded-lg">
                      <h5 className="font-medium text-gray-900 mb-2">Password Management</h5>
                      <p className="text-sm text-gray-600 mb-3">
                        Force user to change password on next login. Current password will remain valid until next login.
                      </p>
                      <button
                        onClick={resetPassword}
                        disabled={saving}
                        className="px-4 py-2 bg-yellow-600 text-white text-sm rounded-md hover:bg-yellow-700 disabled:opacity-50"
                      >
                        🔑 Force Password Change
                      </button>
                    </div>

                    <div className="p-4 border border-gray-200 rounded-lg">
                      <h5 className="font-medium text-gray-900 mb-2">Email Verification</h5>
                      <p className="text-sm text-gray-600 mb-3">
                        Send a new verification email to the user.
                      </p>
                      <button
                        onClick={resendVerification}
                        disabled={saving}
                        className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:opacity-50"
                      >
                        📧 Resend Verification
                      </button>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="p-4 border border-gray-200 rounded-lg">
                      <h5 className="font-medium text-gray-900 mb-2">Account Security</h5>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Security Level:</span>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getSecurityLevelColor(user.security_clearance_level)}`}>
                            Level {user.security_clearance_level}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Two-Factor Auth:</span>
                          <span className="text-red-600">Not Enabled</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Last Password Change:</span>
                          <span className="text-gray-900">Unknown</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Activity Log Tab */}
            {activeTab === 'activity' && (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h4 className="text-lg font-medium text-gray-900">Activity Log</h4>
                  <button
                    onClick={loadAuditLog}
                    className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                  >
                    🔄 Refresh
                  </button>
                </div>

                {loading ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                    <span className="ml-2 text-gray-600">Loading activity...</span>
                  </div>
                ) : auditLog.length > 0 ? (
                  <div className="space-y-3">
                    {auditLog.map((entry) => (
                      <div key={entry.id} className="p-4 border border-gray-200 rounded-lg">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2">
                              <span className="font-medium text-gray-900">
                                {entry.action_name.replace('_', ' ').toUpperCase()}
                              </span>
                              <span className="text-sm text-gray-500">
                                {formatDate(entry.timestamp)}
                              </span>
                            </div>
                            <p className="text-sm text-gray-600 mt-1">
                              Performed by: {entry.performed_by}
                            </p>
                            {entry.details && (
                              <pre className="text-xs text-gray-500 mt-2 bg-gray-50 p-2 rounded overflow-x-auto">
                                {JSON.stringify(entry.details, null, 2)}
                              </pre>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <div className="text-4xl mb-2">📝</div>
                    <p>No activity log entries found</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserDetailsModal;