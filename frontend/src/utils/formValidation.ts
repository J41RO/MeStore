/**
 * Form Validation Utilities
 * Reusable validation functions for form inputs
 */

export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

/**
 * Email validation
 */
export const validateEmail = (email: string): ValidationResult => {
  if (!email) {
    return { isValid: false, error: 'Email es requerido' };
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return { isValid: false, error: 'Email inválido' };
  }

  return { isValid: true };
};

/**
 * Password validation
 * Requirements: min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char
 */
export const validatePassword = (password: string): ValidationResult => {
  if (!password) {
    return { isValid: false, error: 'Contraseña es requerida' };
  }

  if (password.length < 8) {
    return { isValid: false, error: 'Mínimo 8 caracteres' };
  }

  if (!/[A-Z]/.test(password)) {
    return { isValid: false, error: 'Debe contener al menos una mayúscula' };
  }

  if (!/[a-z]/.test(password)) {
    return { isValid: false, error: 'Debe contener al menos una minúscula' };
  }

  if (!/[0-9]/.test(password)) {
    return { isValid: false, error: 'Debe contener al menos un número' };
  }

  if (!/[@$!%*?&]/.test(password)) {
    return { isValid: false, error: 'Debe contener al menos un carácter especial (@$!%*?&)' };
  }

  return { isValid: true };
};

/**
 * Password confirmation validation
 */
export const validatePasswordConfirmation = (
  password: string,
  confirmPassword: string
): ValidationResult => {
  if (!confirmPassword) {
    return { isValid: false, error: 'Confirma tu contraseña' };
  }

  if (password !== confirmPassword) {
    return { isValid: false, error: 'Las contraseñas no coinciden' };
  }

  return { isValid: true };
};

/**
 * Colombian phone validation (10 digits)
 */
export const validateColombianPhone = (phone: string): ValidationResult => {
  if (!phone) {
    return { isValid: false, error: 'Teléfono es requerido' };
  }

  const cleanPhone = phone.replace(/\s/g, '');

  if (!/^\d{10}$/.test(cleanPhone)) {
    return { isValid: false, error: 'Debe tener 10 dígitos (ej: 300 123 4567)' };
  }

  return { isValid: true };
};

/**
 * Name validation (only letters and spaces, min 2 words)
 */
export const validateFullName = (name: string): ValidationResult => {
  if (!name) {
    return { isValid: false, error: 'Nombre es requerido' };
  }

  const trimmedName = name.trim();

  if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(trimmedName)) {
    return { isValid: false, error: 'Solo letras y espacios' };
  }

  const words = trimmedName.split(/\s+/);
  if (words.length < 2) {
    return { isValid: false, error: 'Ingresa nombre y apellido' };
  }

  return { isValid: true };
};

/**
 * Text length validation
 */
export const validateTextLength = (
  text: string,
  minLength: number,
  fieldName: string = 'Campo'
): ValidationResult => {
  if (!text || text.trim().length === 0) {
    return { isValid: false, error: `${fieldName} es requerido` };
  }

  if (text.trim().length < minLength) {
    return {
      isValid: false,
      error: `Mínimo ${minLength} caracteres (${text.trim().length}/${minLength})`
    };
  }

  return { isValid: true };
};

/**
 * Number range validation
 */
export const validateNumberRange = (
  value: number,
  min: number,
  max: number,
  fieldName: string = 'Valor'
): ValidationResult => {
  if (value < min || value > max) {
    return {
      isValid: false,
      error: `${fieldName} debe estar entre ${min} y ${max}`
    };
  }

  return { isValid: true };
};

/**
 * Required field validation
 */
export const validateRequired = (
  value: any,
  fieldName: string = 'Campo'
): ValidationResult => {
  if (!value || (typeof value === 'string' && value.trim().length === 0)) {
    return { isValid: false, error: `${fieldName} es requerido` };
  }

  return { isValid: true };
};

/**
 * Colombian ID (Cedula) validation
 */
export const validateCedulaColombiana = (cedula: string): ValidationResult => {
  if (!cedula) {
    return { isValid: false, error: 'Cédula es requerida' };
  }

  const cleanCedula = cedula.replace(/\D/g, '');

  if (cleanCedula.length < 8 || cleanCedula.length > 10) {
    return {
      isValid: false,
      error: 'Cédula debe tener entre 8 y 10 dígitos'
    };
  }

  return { isValid: true };
};

/**
 * Address validation
 */
export const validateAddress = (address: string): ValidationResult => {
  if (!address) {
    return { isValid: false, error: 'Dirección es requerida' };
  }

  if (address.trim().length < 10) {
    return {
      isValid: false,
      error: 'Dirección debe tener al menos 10 caracteres'
    };
  }

  return { isValid: true };
};

/**
 * Helper function to get password strength
 */
export const getPasswordStrength = (password: string): {
  strength: 'weak' | 'medium' | 'strong';
  score: number;
} => {
  let score = 0;

  if (password.length >= 8) score++;
  if (password.length >= 12) score++;
  if (/[a-z]/.test(password)) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[0-9]/.test(password)) score++;
  if (/[@$!%*?&]/.test(password)) score++;

  if (score <= 2) return { strength: 'weak', score };
  if (score <= 4) return { strength: 'medium', score };
  return { strength: 'strong', score };
};
