import React, { createContext, useContext, ReactNode, useState, useEffect } from 'react';
import { useAuthContext } from './AuthContext';
import { VendorProfile, UserContextState, VendorUpdateData } from '../types/user.types';

interface UserContextType extends UserContextState {
  loadVendorProfile: () => Promise<void>;
  updateVendorProfile: (data: VendorUpdateData) => Promise<boolean>;
  refreshMetrics: () => Promise<void>;
  updateSettings: (settings: Partial<VendorProfile['settings']>) => Promise<boolean>;
  updateContactInfo: (contactInfo: Partial<VendorProfile['contactInfo']>) => Promise<boolean>;
  calculateCompletionPercentage: () => number;
  getProfileMissingFields: () => string[];
  isFieldComplete: (fieldPath: string) => boolean;
}

interface UserProviderProps {
  children: ReactNode;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider: React.FC<UserProviderProps> = ({ children }) => {
  const [vendorProfile, setVendorProfile] = useState<VendorProfile | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recentActivity, setRecentActivity] = useState<any[]>([]);

  const { user, isAuthenticated } = useAuthContext();

  useEffect(() => {
    if (isAuthenticated && user && vendorProfile === null) {
      loadVendorProfile();
    }
  }, [isAuthenticated, user, vendorProfile]);

  const generateMockVendorProfile = (userId: string, email: string, name?: string): VendorProfile => {
    const storeName = name ? 'Tienda de ' + name : 'Tienda de ' + email.split('@')[0];
    
    return {
      userId,
      storeName,
      storeDescription: 'Bienvenido a ' + storeName + '. Aquí encontrarás los mejores productos.',
      storeSlug: email.split('@')[0]?.toLowerCase().replace(/[^a-z0-9]/g, '') || 'tienda',
      
      contactInfo: {
        phone: '',
        address: '',
        city: '',
        state: '',
        zipCode: ''
      },
      
      businessMetrics: {
        totalSales: Math.floor(Math.random() * 100),
        totalRevenue: Math.floor(Math.random() * 10000),
        totalCommissions: Math.floor(Math.random() * 1000),
        stockLevel: Math.floor(Math.random() * 100),
        lowStockItems: Math.floor(Math.random() * 10),
        activeProducts: Math.floor(Math.random() * 50),
        totalOrders: Math.floor(Math.random() * 200),
        averageRating: 4.5,
        joinDate: new Date().toISOString(),
        lastActivity: new Date().toISOString()
      },
      
      settings: {
        notifications: {
          email: true,
          push: true,
          orderUpdates: true,
          promotions: false
        },
        preferences: {
          theme: 'light' as const,
          language: 'es',
          currency: 'USD',
          timezone: 'America/Mexico_City'
        },
        business: {
          autoAcceptOrders: false,
          minimumOrderAmount: 0,
          processingTime: '1-2 días',
          returnPolicy: 'Devoluciones aceptadas dentro de 30 días'
        }
      },
      
      profileStatus: {
        isVerified: false,
        isActive: true,
        completionPercentage: 0,
        lastUpdated: new Date().toISOString()
      }
    };
  };

  const loadVendorProfile = async (): Promise<void> => {
    if (user === null) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const mockProfile = generateMockVendorProfile(user.id, user.email, user.name);
      mockProfile.profileStatus.completionPercentage = calculateCompletionPercentage(mockProfile);
      
      setVendorProfile(mockProfile);
      
      setRecentActivity([
        { type: 'login', timestamp: new Date().toISOString(), description: 'Inicio de sesión' },
        { type: 'profile_view', timestamp: new Date(Date.now() - 3600000).toISOString(), description: 'Perfil visualizado' }
      ]);
      
      console.log('Perfil de vendedor cargado:', mockProfile.storeName);
    } catch (error) {
      console.error('Error cargando perfil de vendedor:', error);
      setError('Error al cargar el perfil del vendedor');
    } finally {
      setIsLoading(false);
    }
  };

  const updateVendorProfile = async (data: VendorUpdateData): Promise<boolean> => {
    if (vendorProfile === null) return false;
    
    setIsLoading(true);
    setError(null);
    
    try {
      await new Promise(resolve => setTimeout(resolve, 300));
      
      const updatedProfile = {
        ...vendorProfile,
        ...data,
        profileStatus: {
          ...vendorProfile.profileStatus,
          lastUpdated: new Date().toISOString(),
          completionPercentage: 0
        }
      };
      
      updatedProfile.profileStatus.completionPercentage = calculateCompletionPercentage(updatedProfile);
      setVendorProfile(updatedProfile);
      
      console.log('Perfil actualizado exitosamente');
      return true;
    } catch (error) {
      console.error('Error actualizando perfil:', error);
      setError('Error al actualizar el perfil');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const updateSettings = async (settings: Partial<VendorProfile['settings']>): Promise<boolean> => {
    if (vendorProfile === null) return false;
    
    const updatedSettings = {
      ...vendorProfile.settings,
      ...settings
    };
    
    return await updateVendorProfile({ settings: updatedSettings });
  };

  const updateContactInfo = async (contactInfo: Partial<VendorProfile['contactInfo']>): Promise<boolean> => {
    if (vendorProfile === null) return false;
    
    const updatedContactInfo = {
      ...vendorProfile.contactInfo,
      ...contactInfo
    };
    
    return await updateVendorProfile({ contactInfo: updatedContactInfo });
  };

  const refreshMetrics = async (): Promise<void> => {
    if (vendorProfile === null) return;
    
    setIsLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 200));
      
      const updatedMetrics = {
        ...vendorProfile.businessMetrics,
        lastActivity: new Date().toISOString(),
        totalSales: vendorProfile.businessMetrics.totalSales + Math.floor(Math.random() * 5)
      };
      
      setVendorProfile(prev => prev !== null ? {
        ...prev,
        businessMetrics: updatedMetrics
      } : null);
      
    } catch (error) {
      console.error('Error refrescando métricas:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const calculateCompletionPercentage = (profile?: VendorProfile): number => {
    const targetProfile = profile || vendorProfile;
    if (!targetProfile) return 0;
    
    const fields = [
      targetProfile.storeName,
      targetProfile.storeDescription,
      targetProfile.contactInfo.phone,
      targetProfile.contactInfo.address,
      targetProfile.contactInfo.city,
      targetProfile.settings.business.returnPolicy
    ];
    
    const completedFields = fields.filter(field => field !== undefined && field !== null && field.trim() !== '').length;
    return Math.round((completedFields / fields.length) * 100);
  };

  const getProfileMissingFields = (): string[] => {
    if (vendorProfile === null) return [];
    
    const missingFields: string[] = [];
    
    if (vendorProfile.contactInfo.phone === undefined || vendorProfile.contactInfo.phone === '') missingFields.push('Teléfono');
    if (vendorProfile.contactInfo.address === undefined || vendorProfile.contactInfo.address === '') missingFields.push('Dirección');
    if (vendorProfile.contactInfo.city === undefined || vendorProfile.contactInfo.city === '') missingFields.push('Ciudad');
    if (vendorProfile.storeDescription === undefined || vendorProfile.storeDescription.length < 10) {
      missingFields.push('Descripción de tienda');
    }
    
    return missingFields;
  };

  const isFieldComplete = (fieldPath: string): boolean => {
    if (vendorProfile === null) return false;
    
    const getValue = (obj: any, path: string) => {
      return path.split('.').reduce((current, key) => current?.[key], obj);
    };
    
    const value = getValue(vendorProfile, fieldPath);
    return value !== undefined && value !== null && value !== '';
  };

  const completionPercentage = vendorProfile?.profileStatus.completionPercentage || 0;
  const isProfileComplete = completionPercentage >= 80;

  const contextValue: UserContextType = {
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
    calculateCompletionPercentage,
    getProfileMissingFields,
    isFieldComplete
  };

  return (
    <UserContext.Provider value={contextValue}>
      {children}
    </UserContext.Provider>
  );
};

export const useUserContext = (): UserContextType => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUserContext debe usarse dentro de UserProvider');
  }
  return context;
};

export { UserContext };
export type { UserContextType };