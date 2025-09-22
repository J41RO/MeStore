import { useState, useCallback, useRef } from 'react';
import { debounce } from 'lodash-es';

export interface ValidationResult {
  isValid: boolean;
  message?: string;
  suggestions?: string[];
}

interface ValidationResults {
  [fieldName: string]: ValidationResult;
}

interface UseRealTimeValidationReturn {
  validateField: (fieldName: string, value: string, validationType?: string) => Promise<void>;
  validationResults: ValidationResults;
  isValidating: { [fieldName: string]: boolean };
  clearValidation: (fieldName: string) => void;
}

// Validation service for API calls
const validationService = {
  async validateEmail(email: string): Promise<ValidationResult> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 150));

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailRegex.test(email)) {
      return {
        isValid: false,
        message: 'Formato de email inválido',
        suggestions: ['ejemplo@correo.com']
      };
    }

    // Simulate checking if email exists
    const existingEmails = ['admin@mestore.com', 'test@used.com'];
    if (existingEmails.includes(email.toLowerCase())) {
      return {
        isValid: false,
        message: 'Este email ya está registrado',
        suggestions: ['Usar otro email o iniciar sesión']
      };
    }

    return { isValid: true, message: 'Email disponible' };
  },

  async validatePhone(phone: string): Promise<ValidationResult> {
    await new Promise(resolve => setTimeout(resolve, 100));

    const phoneRegex = /^3\d{9}$/;

    if (!phoneRegex.test(phone)) {
      return {
        isValid: false,
        message: 'Formato inválido',
        suggestions: ['Ejemplo: 3001234567']
      };
    }

    return { isValid: true, message: 'Teléfono válido' };
  },

  async validateNIT(nit: string): Promise<ValidationResult> {
    await new Promise(resolve => setTimeout(resolve, 200));

    const nitRegex = /^\d{9}-\d$/;

    if (!nitRegex.test(nit)) {
      return {
        isValid: false,
        message: 'Formato de NIT inválido',
        suggestions: ['Formato correcto: 123456789-0']
      };
    }

    // Simulate NIT verification algorithm
    const digits = nit.replace('-', '');
    const weights = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43];
    let sum = 0;

    for (let i = 0; i < 9; i++) {
      sum += parseInt(digits[i]) * weights[i];
    }

    const remainder = sum % 11;
    const checkDigit = remainder < 2 ? remainder : 11 - remainder;
    const providedCheckDigit = parseInt(digits[9]);

    if (checkDigit !== providedCheckDigit) {
      return {
        isValid: false,
        message: 'NIT inválido - dígito de verificación incorrecto',
        suggestions: ['Verifica el número de NIT']
      };
    }

    return { isValid: true, message: 'NIT válido' };
  },

  async validateBusinessName(name: string): Promise<ValidationResult> {
    await new Promise(resolve => setTimeout(resolve, 120));

    if (name.length < 3) {
      return {
        isValid: false,
        message: 'Muy corto',
        suggestions: ['Mínimo 3 caracteres']
      };
    }

    if (name.length > 100) {
      return {
        isValid: false,
        message: 'Muy largo',
        suggestions: ['Máximo 100 caracteres']
      };
    }

    // Check for inappropriate words (simple example)
    const inappropriateWords = ['test', 'prueba', 'ejemplo'];
    const hasInappropriate = inappropriateWords.some(word =>
      name.toLowerCase().includes(word)
    );

    if (hasInappropriate) {
      return {
        isValid: false,
        message: 'Usa el nombre real de tu empresa',
        suggestions: ['Evita palabras como "test" o "ejemplo"']
      };
    }

    return { isValid: true, message: 'Nombre válido' };
  }
};

export const useRealTimeValidation = (): UseRealTimeValidationReturn => {
  const [validationResults, setValidationResults] = useState<ValidationResults>({});
  const [isValidating, setIsValidating] = useState<{ [fieldName: string]: boolean }>({});

  // Store debounced functions to avoid recreating them
  const debouncedValidators = useRef<{ [key: string]: any }>({});

  const validateField = useCallback(async (
    fieldName: string,
    value: string,
    validationType: string = fieldName
  ) => {
    // Don't validate empty values (except for required field checking)
    if (!value.trim()) {
      setValidationResults(prev => ({ ...prev, [fieldName]: { isValid: false } }));
      return;
    }

    // Create debounced validator if it doesn't exist
    if (!debouncedValidators.current[fieldName]) {
      debouncedValidators.current[fieldName] = debounce(async (val: string) => {
        setIsValidating(prev => ({ ...prev, [fieldName]: true }));

        try {
          let result: ValidationResult;

          switch (validationType) {
            case 'email':
              result = await validationService.validateEmail(val);
              break;
            case 'phone':
              result = await validationService.validatePhone(val);
              break;
            case 'nit':
              result = await validationService.validateNIT(val);
              break;
            case 'businessName':
              result = await validationService.validateBusinessName(val);
              break;
            default:
              result = { isValid: true };
          }

          setValidationResults(prev => ({ ...prev, [fieldName]: result }));
        } catch (error) {
          console.error(`Validation error for ${fieldName}:`, error);
          setValidationResults(prev => ({
            ...prev,
            [fieldName]: {
              isValid: false,
              message: 'Error de conexión',
              suggestions: ['Intenta nuevamente']
            }
          }));
        } finally {
          setIsValidating(prev => ({ ...prev, [fieldName]: false }));
        }
      }, 300); // 300ms debounce for optimal UX
    }

    // Call the debounced validator
    debouncedValidators.current[fieldName](value);
  }, []);

  const clearValidation = useCallback((fieldName: string) => {
    setValidationResults(prev => {
      const newResults = { ...prev };
      delete newResults[fieldName];
      return newResults;
    });

    setIsValidating(prev => {
      const newValidating = { ...prev };
      delete newValidating[fieldName];
      return newValidating;
    });
  }, []);

  return {
    validateField,
    validationResults,
    isValidating,
    clearValidation
  };
};

// Export validation service for testing
export { validationService };