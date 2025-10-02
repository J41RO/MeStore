import axios, { AxiosError } from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://192.168.1.137:8000';

export interface VendorRegistrationData {
  email: string;
  password: string;
  full_name: string;
  phone: string;
  business_name: string;
  city: string;
  business_type: 'persona_natural' | 'empresa';
  primary_category: string;
  terms_accepted: boolean;
}

export interface VendorRegistrationResponse {
  vendor_id: string;
  email: string;
  full_name: string;
  business_name: string;
  status: string;
  message: string;
  next_steps: {
    add_products: string;
    view_dashboard: string;
  };
  created_at: string;
}

export interface ApiError {
  error_code?: string;
  error_message?: string;
  detail?: string;
  details?: Array<{
    field: string;
    message: string;
  }>;
}

export const vendorApiService = {
  /**
   * Registrar nuevo vendor usando el endpoint específico
   * POST /api/v1/vendors/register
   */
  register: async (data: VendorRegistrationData): Promise<VendorRegistrationResponse> => {
    try {
      const response = await axios.post<VendorRegistrationResponse>(
        `${API_BASE}/api/v1/vendors/register`,
        data,
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<ApiError>;
        throw {
          message: axiosError.response?.data?.error_message ||
                   axiosError.response?.data?.detail ||
                   'Error al registrar vendor',
          status: axiosError.response?.status,
          details: axiosError.response?.data?.details || [],
        };
      }
      throw error;
    }
  },
};
