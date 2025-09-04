import { useUserContext } from '../contexts/UserContext';

/**
 * Hook simplificado para manejo de datos del vendedor
 *
 * Proporciona interfaz limpia para componentes que necesitan datos del vendedor
 */
export const useVendor = () => {
  // Datos históricos para gráficos de ventas
  const salesHistory = [
    { date: '2024-01', sales: 125, revenue: 15600 },
    { date: '2024-02', sales: 142, revenue: 18400 },
    { date: '2024-03', sales: 108, revenue: 13200 },
    { date: '2024-04', sales: 176, revenue: 22800 },
    { date: '2024-05', sales: 198, revenue: 26400 },
    { date: '2024-06', sales: 165, revenue: 21000 },
    { date: '2024-07', sales: 187, revenue: 24200 },
    { date: '2024-08', sales: 203, revenue: 27800 },
  ];

  const monthlySales = [
    { month: 'Ene', sales: 125, target: 150 },
    { month: 'Feb', sales: 142, target: 150 },
    { month: 'Mar', sales: 108, target: 150 },
    { month: 'Abr', sales: 176, target: 150 },
    { month: 'May', sales: 198, target: 180 },
    { month: 'Jun', sales: 165, target: 180 },
    { month: 'Jul', sales: 187, target: 180 },
    { month: 'Ago', sales: 203, target: 200 },
  ];
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
    isFieldComplete,
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
    totalCommissions: 0,
    stockLevel: 0,
    lowStockItems: 0,
    activeProducts: 0,
    totalOrders: 0,
    averageRating: 0,
    joinDate: new Date().toISOString(),
    lastActivity: new Date().toISOString(),
  };

  // Configuraciones simplificadas
  const notifications = vendorProfile?.settings.notifications || {
    email: true,
    push: true,
    orderUpdates: true,
    promotions: false,
  };

  const preferences = vendorProfile?.settings.preferences || {
    theme: 'light' as const,
    language: 'es',
    currency: 'USD',
    timezone: 'America/Mexico_City',
  };

  // Información de contacto
  const contactInfo = vendorProfile?.contactInfo || {
    phone: '',
    address: '',
    city: '',
    state: '',
    zipCode: '',
  };

  // Métodos de conveniencia
  const updateStoreName = async (name: string): Promise<boolean> => {
    return await updateVendorProfile({ storeName: name });
  };

  const updateStoreDescription = async (
    description: string
  ): Promise<boolean> => {
    return await updateVendorProfile({ storeDescription: description });
  };

  const toggleNotification = async (
    type: keyof typeof notifications
  ): Promise<boolean> => {
    const newNotifications = {
      ...notifications,
      [type]: !notifications[type],
    };
    return await updateSettings({ notifications: newNotifications });
  };

  const updateTheme = async (
    theme: 'light' | 'dark' | 'auto'
  ): Promise<boolean> => {
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
      canPublish: completionPercentage >= 60,
    };
  };

  const getBusinessSummary = () => {
    return {
      totalSales: metrics.totalSales,
      revenue: '$' + metrics.totalRevenue.toLocaleString(),
      products: metrics.activeProducts,
      orders: metrics.totalOrders,
      rating: metrics.averageRating.toFixed(1),
      growth: '+5%',
    };
  };

  return {
    // Estado básico
    // Datos de productos más vendidos
    topProducts: [
      {
        id: '1',
        name: 'Smartphone Pro Max',
        price: 899,
        thumbnail: 'https://picsum.photos/64/64?random=1',
        salesCount: 150,
        category: 'Electrónicos',
        rating: 4.8,
        rank: 1,
        salesGrowth: '+15%',
      },
      {
        id: '2',
        name: 'Laptop Gaming RGB',
        price: 1299,
        thumbnail: 'https://picsum.photos/64/64?random=2',
        salesCount: 89,
        category: 'Computadoras',
        rating: 4.6,
        rank: 2,
        salesGrowth: '+8%',
      },
      {
        id: '3',
        name: 'Auriculares Inalámbricos',
        price: 199,
        thumbnail: 'https://picsum.photos/64/64?random=3',
        salesCount: 245,
        category: 'Audio',
        rating: 4.7,
        rank: 3,
        salesGrowth: '+22%',
      },
      {
        id: '4',
        name: 'Smartwatch Deportivo',
        price: 299,
        thumbnail: 'https://picsum.photos/64/64?random=4',
        salesCount: 134,
        category: 'Wearables',
        rating: 4.5,
        rank: 4,
        salesGrowth: '+12%',
      },
      {
        id: '5',
        name: 'Tablet Pro 12 pulgadas',
        price: 699,
        thumbnail: 'https://picsum.photos/64/64?random=5',
        salesCount: 78,
        category: 'Tablets',
        rating: 4.9,
        rank: 5,
        salesGrowth: '+5%',
      },
    ],
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
    isFieldComplete,
    salesHistory,
    monthlySales,
  };
};

export type UseVendorReturn = ReturnType<typeof useVendor>;
