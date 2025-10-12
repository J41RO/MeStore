/**
 * Test Data Fixtures for E2E Testing
 *
 * @author e2e-testing-ai
 * @date 2025-10-01
 */

export const TEST_USER = {
  email: 'test@mestore.com',
  password: 'Test123456',
  name: 'Test Customer',
  phone: '+57 300 123 4567'
};

export const WOMPI_TEST_CARDS = {
  APPROVED: {
    number: '4242424242424242',
    expiry: '12/25',
    cvv: '123',
    holderName: 'Test Customer'
  },
  DECLINED: {
    number: '4000000000000002',
    expiry: '12/25',
    cvv: '123',
    holderName: 'Test Customer'
  },
  INSUFFICIENT_FUNDS: {
    number: '4000000000009995',
    expiry: '12/25',
    cvv: '123',
    holderName: 'Test Customer'
  }
};

export const TEST_SHIPPING_ADDRESS = {
  name: 'Juan Pérez',
  phone: '3001234567',
  address: 'Calle 123 # 45-67',
  city: 'Bogotá',
  department: 'Cundinamarca',
  postal_code: '110111',
  additional_info: 'Apartamento 301, Torre A'
};

export const COLOMBIAN_CONSTANTS = {
  IVA_RATE: 0.19,
  FREE_SHIPPING_THRESHOLD: 200000,
  SHIPPING_COST: 15000
};

export const TEST_PRODUCTS = {
  basic: {
    name: 'Producto Test Básico',
    price: 50000,
    sku: 'TEST-BASIC-001',
    stock: 10
  },
  expensive: {
    name: 'Producto Test Premium',
    price: 250000,
    sku: 'TEST-PREMIUM-001',
    stock: 5
  },
  limited_stock: {
    name: 'Producto Stock Limitado',
    price: 30000,
    sku: 'TEST-LIMITED-001',
    stock: 2
  }
};

export const PAYMENT_METHODS = {
  CREDIT_CARD: 'credit_card',
  PSE: 'pse',
  BANK_TRANSFER: 'bank_transfer',
  CASH_ON_DELIVERY: 'cash_on_delivery'
} as const;

export const PSE_TEST_BANKS = {
  BANCOLOMBIA: {
    code: '1007',
    name: 'Bancolombia'
  },
  BANCO_DE_BOGOTA: {
    code: '1001',
    name: 'Banco de Bogotá'
  }
};

export const IDENTIFICATION_TYPES = {
  CC: 'Cédula de Ciudadanía',
  CE: 'Cédula de Extranjería',
  NIT: 'NIT',
  TI: 'Tarjeta de Identidad',
  PP: 'Pasaporte'
};

/**
 * SMS Verification Test Data
 * @author e2e-testing-ai
 * @date 2025-10-12
 */
export const SMS_TEST_PHONES = {
  VALID_COLOMBIA: '+573001234567',
  VALID_COLOMBIA_ALT: '+573009876543',
  VALID_COLOMBIA_RATE_LIMIT: '+573009999999',
  VALID_USA: '+15551234567',
  INVALID_NO_PLUS: '3001234567',
  INVALID_TOO_SHORT: '+123',
  INVALID_LETTERS: '+57abc1234567',
  INVALID_SPECIAL_CHARS: '+570-123-4567'
};

export const SMS_TEST_CODES = {
  VALID_CODE: '123456',
  INVALID_TOO_SHORT: '12345',
  INVALID_TOO_LONG: '1234567',
  INVALID_WITH_LETTERS: 'abc123',
  TWILIO_TEST_CODE: '000000' // Twilio Verify test mode code
};

export const SMS_TEST_REGISTRATION_DATA = {
  vendorPersonaNatural: {
    nombre: 'E2E Test Vendor Natural',
    email: `e2evendor${Date.now()}@mestore.com`,
    password: 'TestPass123!',
    phoneNumber: '3001234567',
    countryCode: '+57',
    // Step 3 additional data
    apellido: 'Test Apellido',
    cedula: '1234567890',
    direccion: 'Calle Test 123',
    ciudad: 'Bogotá',
    departamento: 'Cundinamarca',
    direccion_fiscal: 'Calle Fiscal 456',
    ciudad_fiscal: 'Bogotá',
    departamento_fiscal: 'Cundinamarca'
  },
  vendorPersonaJuridica: {
    nombre: 'E2E Test Empresa',
    email: `e2eempresa${Date.now()}@mestore.com`,
    password: 'TestPass123!',
    phoneNumber: '3009876543',
    countryCode: '+57',
    // Step 3 additional data
    razon_social: 'Test Company SAS',
    nombre_comercial: 'Test Company',
    nit: '123456789-0',
    representante_legal: 'Juan Test',
    cedula_representante: '9876543210',
    email_representante: 'rep@testcompany.com',
    telefono_empresa: '+573001111111',
    direccion_fiscal: 'Carrera Empresa 789',
    ciudad_fiscal: 'Medellín',
    departamento_fiscal: 'Antioquia'
  },
  buyer: {
    nombre: 'E2E Test Buyer',
    email: `e2ebuyer${Date.now()}@mestore.com`,
    password: 'TestPass123!',
    phoneNumber: '3005555555',
    countryCode: '+57',
    // Step 3 additional data (optional for buyers)
    apellido: 'Buyer Apellido',
    ciudad: 'Cali',
    direccion: 'Avenida Test 321'
  }
};

export const SMS_RATE_LIMITING = {
  MAX_ATTEMPTS_PER_PHONE: 3,
  WINDOW_MINUTES: 10,
  MAX_ATTEMPTS_PER_IP: 10,
  WINDOW_HOURS: 1
};

export const SMS_ERROR_MESSAGES = {
  RATE_LIMIT_PHONE: 'Demasiados intentos. Por favor espera 10 minutos',
  RATE_LIMIT_IP: 'Demasiados intentos desde esta conexión',
  INVALID_PHONE: 'Formato de teléfono inválido',
  INVALID_CODE: 'Código incorrecto o expirado',
  CODE_EXPIRED: 'El código ha expirado. Solicita uno nuevo',
  NETWORK_ERROR: 'Error al enviar SMS. Por favor intenta de nuevo'
};
