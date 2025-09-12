import React, { useState, useEffect } from 'react';
import { useNotifications } from '../contexts/NotificationContext';
import { useAuthStore } from '../stores/authStore';

// Icons
const UserIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
  </svg>
);

const CreditCardIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
  </svg>
);

const BellIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5v-5z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.97 4.97a.235.235 0 0 0-.02 0l-4.24 4.24a.235.235 0 0 0-.02 0L2.46 13.46a.235.235 0 0 0 0 .33L6.7 17.3a.235.235 0 0 0 .33 0l4.24-4.24a.235.235 0 0 0 0-.02L15.46 8.8a.235.235 0 0 0 0-.33L11.3 4.3a.235.235 0 0 0-.33 0z" />
  </svg>
);

const CameraIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
  </svg>
);

const SpinnerIcon = () => (
  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
  </svg>
);

// Interfaces
interface VendorProfile {
  id: string;
  email: string;
  nombre?: string;
  apellido?: string;
  avatar_url?: string;
  business_name?: string;
  business_description?: string;
  website_url?: string;
  social_media_links?: Record<string, string>;
  business_hours?: Record<string, string>;
  shipping_policy?: string;
  return_policy?: string;
  bank_name?: string;
  account_holder_name?: string;
  account_number?: string;
  tipo_cuenta?: string;
  notification_preferences?: {
    email_new_orders: boolean;
    email_low_stock: boolean;
    sms_urgent_orders: boolean;
    push_daily_summary: boolean;
  };
}

interface ProfileTabProps {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
}

const ProfileTab: React.FC<ProfileTabProps> = ({ active, onClick, icon, label }) => (
  <button
    onClick={onClick}
    className={`flex items-center px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
      active
        ? 'border-blue-500 text-blue-600'
        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
    }`}
  >
    {icon}
    <span className="ml-2">{label}</span>
  </button>
);

// Componente principal
const VendorProfile: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'profile' | 'banking' | 'notifications'>('profile');
  const [vendorData, setVendorData] = useState<VendorProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving] = useState(false);
  const { showNotification } = useNotifications();
  const { user } = useAuthStore();

  // Cargar datos del vendor
  useEffect(() => {
    const loadVendorData = async () => {
      try {
        setLoading(true);
        
        // Simular datos para desarrollo (reemplazar con API call)
        const mockData: VendorProfile = {
          id: user?.id || 'test-vendor-001',
          email: user?.email || 'vendedor.test@mestore.com',
          nombre: user?.name || 'Vendedor',
          apellido: 'Test',
          avatar_url: undefined,
          business_name: 'Mi Tienda Online',
          business_description: 'Especialistas en productos de calidad para el hogar y la oficina.',
          website_url: 'https://mitienda.com',
          social_media_links: {
            facebook: 'https://facebook.com/mitienda',
            instagram: 'https://instagram.com/mitienda'
          },
          business_hours: {
            monday: '9:00-18:00',
            tuesday: '9:00-18:00',
            wednesday: '9:00-18:00',
            thursday: '9:00-18:00',
            friday: '9:00-18:00',
            saturday: '10:00-16:00',
            sunday: 'closed'
          },
          shipping_policy: 'Envíos gratuitos por compras superiores a $100,000. Tiempo de entrega: 2-5 días hábiles.',
          return_policy: 'Aceptamos devoluciones dentro de los primeros 30 días con producto en perfecto estado.',
          bank_name: 'Bancolombia',
          account_holder_name: 'Vendedor Test',
          account_number: '1234567890',
          tipo_cuenta: 'AHORROS',
          notification_preferences: {
            email_new_orders: true,
            email_low_stock: true,
            sms_urgent_orders: false,
            push_daily_summary: true
          }
        };
        
        setVendorData(mockData);
        
      } catch (error) {
        console.error('Error loading vendor data:', error);
        showNotification({
          title: 'Error',
          message: 'Error al cargar datos del perfil',
          type: 'error'
        });
      } finally {
        setLoading(false);
      }
    };

    loadVendorData();
  }, [user, showNotification]);

  // const _handleAvatarUpdate = (avatarUrl: string) => {
  //   setVendorData(prev => prev ? { ...prev, avatar_url: avatarUrl } : null);
  //   showNotification({
  //     title: 'Éxito',
  //     message: 'Avatar actualizado correctamente',
  //     type: 'success'
  //   });
  // };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-center">
          <SpinnerIcon />
          <p className="mt-2 text-gray-600">Cargando perfil...</p>
        </div>
      </div>
    );
  }

  if (!vendorData) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Error al cargar datos del perfil</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header con avatar y nombre */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <div className="flex items-center space-x-6">
          <div className="relative">
            <img 
              src={vendorData.avatar_url || '/default-avatar.png'} 
              alt="Avatar"
              className="w-24 h-24 rounded-full object-cover bg-gray-200 border-2 border-gray-300"
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(vendorData.business_name || vendorData.nombre || 'Vendor')}&size=96&background=3B82F6&color=white`;
              }}
            />
            <div className="absolute -bottom-2 -right-2">
              <button
                className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white hover:bg-blue-700 transition-colors"
                title="Cambiar avatar"
              >
                <CameraIcon />
              </button>
            </div>
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {vendorData.business_name || `${vendorData.nombre} ${vendorData.apellido}`.trim()}
            </h1>
            <p className="text-gray-600">{vendorData.email}</p>
            {vendorData.business_name && (
              <p className="text-sm text-gray-500 mt-1">
                {vendorData.nombre} {vendorData.apellido}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Navegación por tabs */}
      <div className="border-b border-gray-200 mb-8">
        <nav className="-mb-px flex space-x-0">
          <ProfileTab 
            active={activeTab === 'profile'} 
            onClick={() => setActiveTab('profile')}
            icon={<UserIcon />}
            label="Información del Negocio"
          />
          <ProfileTab 
            active={activeTab === 'banking'} 
            onClick={() => setActiveTab('banking')}
            icon={<CreditCardIcon />}
            label="Información Bancaria"
          />
          <ProfileTab 
            active={activeTab === 'notifications'} 
            onClick={() => setActiveTab('notifications')}
            icon={<BellIcon />}
            label="Notificaciones"
          />
        </nav>
      </div>

      {/* Contenido por tab */}
      <div className="mt-8">
        {activeTab === 'profile' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Información del Negocio</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nombre Comercial
                </label>
                <input
                  type="text"
                  value={vendorData.business_name || ''}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Nombre de tu negocio"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Sitio Web
                </label>
                <input
                  type="url"
                  value={vendorData.website_url || ''}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="https://..."
                />
              </div>
            </div>

            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Descripción del Negocio
              </label>
              <textarea
                rows={4}
                value={vendorData.business_description || ''}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Describe tu negocio..."
              />
            </div>

            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Política de Envíos
                </label>
                <textarea
                  rows={3}
                  value={vendorData.shipping_policy || ''}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Describe tu política de envíos..."
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Política de Devoluciones
                </label>
                <textarea
                  rows={3}
                  value={vendorData.return_policy || ''}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Describe tu política de devoluciones..."
                />
              </div>
            </div>

            <div className="mt-8 flex justify-end">
              <button
                disabled={saving}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center"
              >
                {saving && <SpinnerIcon />}
                <span className={saving ? 'ml-2' : ''}>
                  {saving ? 'Guardando...' : 'Guardar Cambios'}
                </span>
              </button>
            </div>
          </div>
        )}

        {activeTab === 'banking' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Información Bancaria</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nombre del Banco
                </label>
                <input
                  type="text"
                  value={vendorData.bank_name || ''}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Ej: Bancolombia"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Titular de la Cuenta
                </label>
                <input
                  type="text"
                  value={vendorData.account_holder_name || ''}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Nombre completo del titular"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Número de Cuenta
                </label>
                <input
                  type="text"
                  value={vendorData.account_number || ''}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="1234567890"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tipo de Cuenta
                </label>
                <select
                  value={vendorData.tipo_cuenta || 'AHORROS'}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="AHORROS">Ahorros</option>
                  <option value="CORRIENTE">Corriente</option>
                </select>
              </div>
            </div>

            <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
              <div className="flex">
                <div className="flex-shrink-0">
                  ⚠️
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-yellow-800">
                    Información Importante
                  </h3>
                  <div className="mt-2 text-sm text-yellow-700">
                    <p>
                      Esta información será utilizada para procesar tus pagos y retiros.
                      Asegúrate de que los datos sean correctos.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-8 flex justify-end">
              <button
                disabled={saving}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center"
              >
                {saving && <SpinnerIcon />}
                <span className={saving ? 'ml-2' : ''}>
                  {saving ? 'Guardando...' : 'Guardar Información Bancaria'}
                </span>
              </button>
            </div>
          </div>
        )}

        {activeTab === 'notifications' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Preferencias de Notificaciones</h3>
            
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-medium text-gray-900">Nuevas Órdenes por Email</h4>
                  <p className="text-sm text-gray-500">Recibir notificación cuando llegue una nueva orden</p>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={vendorData.notification_preferences?.email_new_orders || false}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-medium text-gray-900">Stock Bajo por Email</h4>
                  <p className="text-sm text-gray-500">Recibir alerta cuando el stock de un producto esté bajo</p>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={vendorData.notification_preferences?.email_low_stock || false}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-medium text-gray-900">SMS para Órdenes Urgentes</h4>
                  <p className="text-sm text-gray-500">Recibir SMS para órdenes marcadas como urgentes</p>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={vendorData.notification_preferences?.sms_urgent_orders || false}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-medium text-gray-900">Resumen Diario</h4>
                  <p className="text-sm text-gray-500">Recibir resumen diario de ventas y actividad</p>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={vendorData.notification_preferences?.push_daily_summary || false}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                </div>
              </div>
            </div>

            <div className="mt-8 flex justify-end">
              <button
                disabled={saving}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center"
              >
                {saving && <SpinnerIcon />}
                <span className={saving ? 'ml-2' : ''}>
                  {saving ? 'Guardando...' : 'Guardar Preferencias'}
                </span>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Estado temporal */}
      <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-md">
        <div className="flex">
          <div className="flex-shrink-0">
            ℹ️
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">
              Versión de Desarrollo
            </h3>
            <div className="mt-2 text-sm text-blue-700">
              <p>
                Esta página está usando datos simulados. La funcionalidad de guardado se integrará
                con la API una vez que esté disponible.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VendorProfile;