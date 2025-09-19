/**
 * Security Utilities
 * Frontend Security AI Implementation
 *
 * Funciones de seguridad para el frontend
 * Incluye validaciones, sanitización y protección XSS
 */

// Content Security Policy helper
export const initCSP = () => {
  const cspMeta = document.createElement('meta');
  cspMeta.httpEquiv = 'Content-Security-Policy';
  cspMeta.content = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: https:",
    "font-src 'self' https:",
    "connect-src 'self' http://192.168.1.137:8000 ws: wss:",
    "frame-ancestors 'none'",
    "form-action 'self'",
    "base-uri 'self'"
  ].join('; ');

  document.head.appendChild(cspMeta);
};

// XSS Protection
export const sanitizeInput = (input: string): string => {
  return input
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;');
};

// Validate email format
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email) && email.length <= 254;
};

// Password strength validation
export const validatePasswordStrength = (password: string): {
  isValid: boolean;
  score: number;
  feedback: string[];
} => {
  const feedback: string[] = [];
  let score = 0;

  if (password.length >= 8) {
    score += 1;
  } else {
    feedback.push('Debe tener al menos 8 caracteres');
  }

  if (/[a-z]/.test(password)) {
    score += 1;
  } else {
    feedback.push('Debe incluir letras minúsculas');
  }

  if (/[A-Z]/.test(password)) {
    score += 1;
  } else {
    feedback.push('Debe incluir letras mayúsculas');
  }

  if (/\d/.test(password)) {
    score += 1;
  } else {
    feedback.push('Debe incluir números');
  }

  if (/[^A-Za-z0-9]/.test(password)) {
    score += 1;
  } else {
    feedback.push('Debe incluir caracteres especiales');
  }

  return {
    isValid: score >= 3,
    score,
    feedback
  };
};

// Rate limiting helper
class RateLimiter {
  private attempts: Map<string, { count: number; lastAttempt: number }> = new Map();
  private readonly maxAttempts: number;
  private readonly windowMs: number;

  constructor(maxAttempts: number = 5, windowMs: number = 15 * 60 * 1000) {
    this.maxAttempts = maxAttempts;
    this.windowMs = windowMs;
  }

  canAttempt(identifier: string): boolean {
    const now = Date.now();
    const record = this.attempts.get(identifier);

    if (!record) {
      this.attempts.set(identifier, { count: 1, lastAttempt: now });
      return true;
    }

    // Reset if window has passed
    if (now - record.lastAttempt > this.windowMs) {
      this.attempts.set(identifier, { count: 1, lastAttempt: now });
      return true;
    }

    // Check if max attempts reached
    if (record.count >= this.maxAttempts) {
      return false;
    }

    // Increment attempt count
    record.count++;
    record.lastAttempt = now;
    return true;
  }

  getRemainingTime(identifier: string): number {
    const record = this.attempts.get(identifier);
    if (!record || record.count < this.maxAttempts) {
      return 0;
    }

    const timeLeft = this.windowMs - (Date.now() - record.lastAttempt);
    return Math.max(0, timeLeft);
  }

  reset(identifier: string): void {
    this.attempts.delete(identifier);
  }
}

// Global rate limiter instances
export const loginRateLimiter = new RateLimiter(5, 15 * 60 * 1000); // 5 attempts per 15 minutes
export const apiRateLimiter = new RateLimiter(100, 60 * 1000); // 100 requests per minute

// JWT Token utilities
export const parseJWT = (token: string): any => {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Error parsing JWT:', error);
    return null;
  }
};

export const isTokenExpired = (token: string): boolean => {
  try {
    const payload = parseJWT(token);
    if (!payload || !payload.exp) {
      return true;
    }
    const currentTime = Math.floor(Date.now() / 1000);
    return payload.exp < currentTime;
  } catch (error) {
    return true;
  }
};

// Secure storage utilities
export const secureStorage = {
  setItem: (key: string, value: string): void => {
    try {
      // For sensitive data, consider implementing encryption here
      localStorage.setItem(key, value);
    } catch (error) {
      console.error('Error storing data:', error);
    }
  },

  getItem: (key: string): string | null => {
    try {
      return localStorage.getItem(key);
    } catch (error) {
      console.error('Error retrieving data:', error);
      return null;
    }
  },

  removeItem: (key: string): void => {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Error removing data:', error);
    }
  },

  clear: (): void => {
    try {
      // Only clear auth-related items, not all localStorage
      const authKeys = ['access_token', 'refresh_token', 'auth_token', 'auth-storage'];
      authKeys.forEach(key => localStorage.removeItem(key));
    } catch (error) {
      console.error('Error clearing auth data:', error);
    }
  }
};

// Input validation helpers
export const validateInput = {
  email: (email: string): { isValid: boolean; message?: string } => {
    if (!email) {
      return { isValid: false, message: 'Email es requerido' };
    }
    if (!isValidEmail(email)) {
      return { isValid: false, message: 'Formato de email inválido' };
    }
    return { isValid: true };
  },

  password: (password: string): { isValid: boolean; message?: string } => {
    if (!password) {
      return { isValid: false, message: 'Contraseña es requerida' };
    }
    if (password.length < 6) {
      return { isValid: false, message: 'Mínimo 6 caracteres' };
    }
    return { isValid: true };
  },

  name: (name: string): { isValid: boolean; message?: string } => {
    if (!name || name.trim().length < 2) {
      return { isValid: false, message: 'Nombre debe tener al menos 2 caracteres' };
    }
    if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(name)) {
      return { isValid: false, message: 'Solo se permiten letras y espacios' };
    }
    return { isValid: true };
  }
};

// CSRF Protection
export const generateCSRFToken = (): string => {
  return Array.from(crypto.getRandomValues(new Uint8Array(32)))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
};

// Security headers for API requests
export const getSecurityHeaders = (): Record<string, string> => {
  return {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'strict-origin-when-cross-origin'
  };
};

// Initialize security measures
export const initSecurity = (): void => {
  // Set security headers
  initCSP();

  // Disable right-click in production
  if (import.meta.env.MODE === 'production') {
    document.addEventListener('contextmenu', (e) => e.preventDefault());
    document.addEventListener('selectstart', (e) => e.preventDefault());
    document.addEventListener('dragstart', (e) => e.preventDefault());
  }

  // Detect and warn about developer tools
  if (import.meta.env.MODE === 'production') {
    setInterval(() => {
      const start = performance.now();
      debugger;
      const end = performance.now();
      if (end - start > 100) {
        console.warn('⚠️ Developer tools detected. This application contains sensitive information.');
      }
    }, 1000);
  }
};

export default {
  sanitizeInput,
  isValidEmail,
  validatePasswordStrength,
  loginRateLimiter,
  apiRateLimiter,
  parseJWT,
  isTokenExpired,
  secureStorage,
  validateInput,
  generateCSRFToken,
  getSecurityHeaders,
  initSecurity
};