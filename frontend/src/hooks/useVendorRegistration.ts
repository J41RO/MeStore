import { useState, useCallback } from 'react';
import { UserType } from '../types/auth.types';

export interface VendorRegistrationData {
  businessName: string;
  email: string;
  phone: string;
  businessType: 'persona_juridica' | 'persona_natural';
  nit?: string;
  address: string;
  city: string;
  department: string;
  userType: UserType;
  phoneVerified: boolean;
  emailVerified: boolean;
  documents: File[];
}

interface UseVendorRegistrationReturn {
  submitRegistration: (data: VendorRegistrationData) => Promise<boolean>;
  isLoading: boolean;
  error: string | null;
  progress: number;
}

export const useVendorRegistration = (): UseVendorRegistrationReturn => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);

  const submitRegistration = useCallback(async (data: VendorRegistrationData): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    setProgress(0);

    try {
      // Simulate registration steps with progress updates
      setProgress(10);
      await new Promise(resolve => setTimeout(resolve, 200));

      // Step 1: Validate business data
      setProgress(25);
      const businessValidation = await validateBusinessData(data);
      if (!businessValidation.isValid) {
        throw new Error(businessValidation.error);
      }

      // Step 2: Create user account
      setProgress(50);
      const userResult = await createUserAccount(data);
      if (!userResult.success) {
        throw new Error(userResult.error);
      }

      // Step 3: Setup vendor profile
      setProgress(75);
      const profileResult = await setupVendorProfile(data, userResult.userId);
      if (!profileResult.success) {
        throw new Error(profileResult.error);
      }

      // Step 4: Upload documents (if any)
      if (data.documents.length > 0) {
        setProgress(90);
        const documentsResult = await uploadDocuments(data.documents, userResult.userId);
        if (!documentsResult.success) {
          throw new Error(documentsResult.error);
        }
      }

      // Step 5: Send welcome email
      setProgress(95);
      await sendWelcomeEmail(data.email);

      setProgress(100);
      await new Promise(resolve => setTimeout(resolve, 500)); // Show completion

      return true;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error en el registro';
      setError(errorMessage);
      console.error('Registration failed:', err);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    submitRegistration,
    isLoading,
    error,
    progress
  };
};

// Helper functions for registration steps
async function validateBusinessData(data: VendorRegistrationData) {
  // Simulate API call for business validation
  await new Promise(resolve => setTimeout(resolve, 100));

  // Basic validation
  if (!data.businessName || data.businessName.length < 3) {
    return { isValid: false, error: 'Nombre de empresa muy corto' };
  }

  if (!data.email || !data.email.includes('@')) {
    return { isValid: false, error: 'Email inválido' };
  }

  if (!data.phone || data.phone.length !== 10) {
    return { isValid: false, error: 'Teléfono inválido' };
  }

  if (data.businessType === 'persona_juridica' && (!data.nit || !data.nit.match(/^\d{9}-\d$/))) {
    return { isValid: false, error: 'NIT inválido para persona jurídica' };
  }

  return { isValid: true };
}

async function createUserAccount(data: VendorRegistrationData) {
  try {
    const response = await fetch('/api/v1/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: data.email,
        password: 'temp_password_' + Date.now(), // In production, collect password from user
        nombre: data.businessName,
        telefono: data.phone,
        user_type: data.userType,
        is_active: true
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Error creando usuario');
    }

    const result = await response.json();
    return { success: true, userId: result.id || result.user_id };
  } catch (error) {
    console.error('Create user account failed:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Error de conexión'
    };
  }
}

async function setupVendorProfile(data: VendorRegistrationData, userId: string) {
  try {
    const response = await fetch('/api/v1/vendors', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify({
        user_id: userId,
        nombre_empresa: data.businessName,
        tipo_persona: data.businessType,
        nit: data.nit,
        direccion: data.address,
        ciudad: data.city,
        departamento: data.department,
        telefono: data.phone,
        email: data.email,
        is_active: true,
        verificado: false
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Error configurando perfil de vendedor');
    }

    return { success: true };
  } catch (error) {
    console.error('Setup vendor profile failed:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Error configurando perfil'
    };
  }
}

async function uploadDocuments(documents: File[], userId: string) {
  try {
    const formData = new FormData();
    documents.forEach((file, index) => {
      formData.append(`document_${index}`, file);
    });
    formData.append('user_id', userId);

    const response = await fetch('/api/v1/vendors/documentos', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Error subiendo documentos');
    }

    return { success: true };
  } catch (error) {
    console.error('Upload documents failed:', error);
    return {
      success: false,
      error: 'Error subiendo documentos'
    };
  }
}

async function sendWelcomeEmail(email: string) {
  try {
    await fetch('/api/v1/notifications/welcome-vendor', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify({ email }),
    });
  } catch (error) {
    console.warn('Welcome email failed, but registration continues:', error);
  }
}