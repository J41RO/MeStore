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
