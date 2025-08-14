import { useUserContext } from '../contexts/UserContext';

/**
 * Hook simplificado para manejo de datos del vendedor
 * 
 * Proporciona interfaz limpia para componentes que necesitan datos del vendedor
 */
export const useVendor = () => {
  const {
    vendorProfile,
    isLoading,
    error,
    completionPercentage,
    isProfileComplete,
    recentActivity,
    loadVendorProfile,
    updateVendorProfile,
    refreshMetrics,
    updateSettings,
    updateContactInfo,
    getProfileMissingFields,
    isFieldComplete
  } = useUserContext();

  // Datos computados del vendedor
  const storeName = vendorProfile?.storeName || 'Mi Tienda';
  const storeSlug = vendorProfile?.storeSlug || 'mi-tienda';
  const isVerified = vendorProfile?.profileStatus.isVerified || false;
  const isActive = vendorProfile?.profileStatus.isActive || false;
  
  // Métricas de negocio simplificadas
  const metrics = vendorProfile?.businessMetrics || {
    totalSales: 0,
    totalRevenue: 0,
    activeProducts: 0,
    totalOrders: 0,
    averageRating: 0,
    joinDate: new Date().toISOString(),
    lastActivity: new Date().toISOString()
  };

  // Configuraciones simplificadas
  const notifications = vendorProfile?.settings.notifications || {
    email: true,
    push: true,
    orderUpdates: true,
    promotions: false
  };

  const preferences = vendorProfile?.settings.preferences || {
    theme: 'light' as const,
    language: 'es',
    currency: 'USD',
    timezone: 'America/Mexico_City'
  };

  // Información de contacto
  const contactInfo = vendorProfile?.contactInfo || {
    phone: '',
    address: '',
    city: '',
    state: '',
    zipCode: ''
  };

  // Métodos de conveniencia
  const updateStoreName = async (name: string): Promise<boolean> => {
    return await updateVendorProfile({ storeName: name });
  };

  const updateStoreDescription = async (description: string): Promise<boolean> => {
    return await updateVendorProfile({ storeDescription: description });
  };

  const toggleNotification = async (type: keyof typeof notifications): Promise<boolean> => {
    const newNotifications = {
      ...notifications,
      [type]: !notifications[type]
    };
    return await updateSettings({ notifications: newNotifications });
  };

  const updateTheme = async (theme: 'light' | 'dark' | 'auto'): Promise<boolean> => {
    const newPreferences = { ...preferences, theme };
    return await updateSettings({ preferences: newPreferences });
  };

  // Métodos de análisis
  const getCompletionStatus = () => {
    const missingFields = getProfileMissingFields();
    return {
      percentage: completionPercentage,
      isComplete: isProfileComplete,
      missingFields,
      canPublish: completionPercentage >= 60
    };
  };

  const getBusinessSummary = () => {
    return {
      totalSales: metrics.totalSales,
      revenue: '$' + metrics.totalRevenue.toLocaleString(),
      products: metrics.activeProducts,
      orders: metrics.totalOrders,
      rating: metrics.averageRating.toFixed(1),
      growth: '+5%'
    };
  };

  return {
    // Estado básico
    vendorProfile,
    isLoading,
    error,
    
    // Datos del vendedor
    storeName,
    storeSlug,
    isVerified,
    isActive,
    
    // Métricas y configuraciones
    metrics,
    notifications,
    preferences,
    contactInfo,
    
    // Estado del perfil
    completionPercentage,
    isProfileComplete,
    recentActivity,
    
    // Métodos principales
    loadVendorProfile,
    updateVendorProfile,
    refreshMetrics,
    
    // Métodos específicos
    updateStoreName,
    updateStoreDescription,
    updateContactInfo,
    toggleNotification,
    updateTheme,
    
    // Métodos de análisis
    getCompletionStatus,
    getBusinessSummary,
    getProfileMissingFields,
    isFieldComplete
  };
};

export type UseVendorReturn = ReturnType<typeof useVendor>;
