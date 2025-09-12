interface LeadFormData {
  email: string;
  nombre: string;
  tipo_negocio: 'vendedor' | 'comprador' | 'ambos';
  telefono?: string;
  empresa?: string;
  source?: string;
}

interface LeadResponse {
  message: string;
  lead_id: number;
  email_sent: boolean;
}

interface ApiErrorResponse {
  detail: string;
  status_code?: number;
}

class LeadService {
  private baseURL = '/api/v1';

  async createLead(leadData: LeadFormData): Promise<LeadResponse> {
    try {
      const response = await fetch(`${this.baseURL}/leads`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          ...leadData,
          source: leadData.source || 'landing'
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        // Handle specific error cases
        if (response.status === 409) {
          throw new Error('Este email ya está registrado en nuestra lista de espera');
        } else if (response.status === 422) {
          // Validation error
          const errorMsg = data?.detail?.[0]?.msg || 'Datos inválidos. Verifica la información.';
          throw new Error(errorMsg);
        } else if (response.status >= 500) {
          throw new Error('Error del servidor. Inténtalo de nuevo en unos minutos.');
        } else {
          throw new Error(data?.detail || 'Error desconocido al procesar la solicitud');
        }
      }

      return data;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      
      // Network or other errors
      throw new Error('Error de conexión. Verifica tu internet e inténtalo de nuevo.');
    }
  }

  async createQuickLead(email: string, source: string = 'quick-capture'): Promise<LeadResponse> {
    return this.createLead({
      email,
      nombre: 'Lead Rápido',
      tipo_negocio: 'vendedor',
      source
    });
  }

  // Admin methods (require authentication)
  async getLeads(skip: number = 0, limit: number = 100): Promise<any[]> {
    try {
      const response = await fetch(`${this.baseURL}/leads?skip=${skip}&limit=${limit}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Error obteniendo lista de leads');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching leads:', error);
      throw error;
    }
  }

  async getLeadStats(): Promise<any> {
    try {
      const response = await fetch(`${this.baseURL}/leads/stats`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Error obteniendo estadísticas');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching lead stats:', error);
      throw error;
    }
  }

  async testWelcomeEmail(email: string, nombre: string = 'Usuario Test'): Promise<any> {
    try {
      const response = await fetch(`${this.baseURL}/leads/test-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          email,
          nombre,
          tipo_negocio: 'vendedor'
        }),
      });

      if (!response.ok) {
        throw new Error('Error enviando email de prueba');
      }

      return await response.json();
    } catch (error) {
      console.error('Error sending test email:', error);
      throw error;
    }
  }

  // Utility methods
  validateEmail(email: string): boolean {
    const emailRegex = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i;
    return emailRegex.test(email);
  }

  validatePhone(phone: string): boolean {
    const phoneRegex = /^[+]?[0-9\s\-()]{7,15}$/;
    return phoneRegex.test(phone.trim());
  }

  formatErrorMessage(error: unknown): string {
    if (error instanceof Error) {
      return error.message;
    }
    return 'Error desconocido';
  }

  // Analytics helpers
  trackFormSubmission(formType: 'early_access' | 'quick_capture', success: boolean) {
    // Placeholder for analytics tracking
    console.log(`Form submission tracked: ${formType}, success: ${success}`);
    
    // Example implementation:
    // gtag('event', 'form_submit', {
    //   form_type: formType,
    //   success: success
    // });
  }

  trackFormError(formType: string, errorMessage: string) {
    console.error(`Form error tracked: ${formType}, error: ${errorMessage}`);
    
    // Example implementation:
    // gtag('event', 'form_error', {
    //   form_type: formType,
    //   error_message: errorMessage
    // });
  }
}

// Export singleton instance
export const leadService = new LeadService();
export default leadService;

// Export types for use in components
export type { LeadFormData, LeadResponse, ApiErrorResponse };