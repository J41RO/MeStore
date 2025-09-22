// ValidationService for form validation
// Frontend validation service for vendor registration and form validation

export interface ValidationResult {
  isValid: boolean;
  message?: string;
}

export interface ValidationService {
  validateEmail: (email: string) => Promise<ValidationResult>;
  validateBusinessName: (name: string) => Promise<ValidationResult>;
  validatePhone: (phone: string) => Promise<ValidationResult>;
  validateDocument: (document: string) => Promise<ValidationResult>;
}

class ValidationServiceImpl implements ValidationService {
  async validateEmail(email: string): Promise<ValidationResult> {
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!email) {
      return { isValid: false, message: 'Email es requerido' };
    }

    if (!emailRegex.test(email)) {
      return { isValid: false, message: 'Email no tiene formato válido' };
    }

    // Simulate async validation (e.g., checking if email exists)
    await new Promise(resolve => setTimeout(resolve, 100));

    return { isValid: true };
  }

  async validateBusinessName(name: string): Promise<ValidationResult> {
    if (!name) {
      return { isValid: false, message: 'Nombre del negocio es requerido' };
    }

    if (name.length < 3) {
      return { isValid: false, message: 'Nombre del negocio debe tener al menos 3 caracteres' };
    }

    if (name.length > 100) {
      return { isValid: false, message: 'Nombre del negocio no puede tener más de 100 caracteres' };
    }

    // Simulate async validation
    await new Promise(resolve => setTimeout(resolve, 100));

    return { isValid: true };
  }

  async validatePhone(phone: string): Promise<ValidationResult> {
    if (!phone) {
      return { isValid: false, message: 'Teléfono es requerido' };
    }

    // Colombian phone number format
    const phoneRegex = /^(\+57)?[0-9]{10}$/;

    if (!phoneRegex.test(phone.replace(/\s/g, ''))) {
      return { isValid: false, message: 'Teléfono debe tener formato válido colombiano' };
    }

    // Simulate async validation
    await new Promise(resolve => setTimeout(resolve, 100));

    return { isValid: true };
  }

  async validateDocument(document: string): Promise<ValidationResult> {
    if (!document) {
      return { isValid: false, message: 'Documento es requerido' };
    }

    // Colombian ID validation
    const docRegex = /^[0-9]{8,11}$/;

    if (!docRegex.test(document)) {
      return { isValid: false, message: 'Documento debe tener entre 8 y 11 dígitos' };
    }

    // Simulate async validation
    await new Promise(resolve => setTimeout(resolve, 100));

    return { isValid: true };
  }
}

export const validationService = new ValidationServiceImpl();
export default validationService;