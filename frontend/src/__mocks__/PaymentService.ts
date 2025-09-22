// Mock Payment Service for tests
// Prevents real payment processing during testing

export interface PaymentInfo {
  method: 'pse' | 'credit_card';
  email: string;
  total_amount?: number;

  // PSE specific
  bank_code?: string;
  bank_name?: string;
  user_type?: 'natural' | 'juridica';
  identification_type?: 'CC' | 'CE' | 'NIT';
  identification_number?: string;

  // Credit card specific
  card_number?: string;
  card_holder_name?: string;
  expiry_month?: string;
  expiry_year?: string;
  cvv?: string;
}

export interface PaymentValidation {
  valid: boolean;
  errors: Record<string, string>;
}

class MockPaymentService {
  // Validation methods
  validatePaymentInfo = jest.fn().mockImplementation((paymentInfo: PaymentInfo): PaymentValidation => {
    const errors: Record<string, string> = {};

    // Basic validation
    if (!paymentInfo.email) {
      errors.email = 'Email is required';
    }

    // PSE validation
    if (paymentInfo.method === 'pse') {
      if (!paymentInfo.bank_code) {
        errors.bank_code = 'Bank selection is required';
      }
      if (!paymentInfo.identification_type) {
        errors.identification_type = 'Identification type is required';
      }
      if (!paymentInfo.identification_number) {
        errors.identification_number = 'Identification number is required';
      }
    }

    // Credit card validation
    if (paymentInfo.method === 'credit_card') {
      if (!paymentInfo.card_number) {
        errors.card_number = 'Card number is required';
      }
      if (!paymentInfo.card_holder_name) {
        errors.card_holder_name = 'Card holder name is required';
      }
      if (!paymentInfo.expiry_month) {
        errors.expiry_month = 'Expiry month is required';
      }
      if (!paymentInfo.expiry_year) {
        errors.expiry_year = 'Expiry year is required';
      }
      if (!paymentInfo.cvv) {
        errors.cvv = 'CVV is required';
      }
    }

    return {
      valid: Object.keys(errors).length === 0,
      errors,
    };
  });

  // Health check
  healthCheck = jest.fn().mockResolvedValue(true);

  // Processing methods
  processPayment = jest.fn().mockResolvedValue({
    success: true,
    transaction_id: 'mock-txn-123',
    payment_url: 'https://mock-payment.com/pay/123',
  });

  // Static validation methods
  static validateCardNumber = jest.fn().mockImplementation((cardNumber: string): boolean => {
    // Mock Luhn algorithm validation
    const validTestCards = [
      '4111111111111111', // Visa test card
      '5555555555554444', // MasterCard test card
      '4000000000000002', // Another valid test card
    ];
    return validTestCards.includes(cardNumber);
  });

  static formatCardNumber = jest.fn().mockImplementation((cardNumber: string): string => {
    return cardNumber.replace(/(\d{4})(?=\d)/g, '$1 ');
  });

  static getCardType = jest.fn().mockImplementation((cardNumber: string): string => {
    if (cardNumber.startsWith('4')) return 'visa';
    if (cardNumber.startsWith('5')) return 'mastercard';
    if (cardNumber.startsWith('3')) return 'amex';
    return 'unknown';
  });

  // Reset mock state
  resetMock() {
    jest.clearAllMocks();
  }
}

// Create singleton instance
const mockPaymentService = new MockPaymentService();

// Export the mock service
export const paymentService = mockPaymentService;
export { MockPaymentService };
export default mockPaymentService;

// Export static methods for compatibility
export const validateCardNumber = MockPaymentService.validateCardNumber;
export const formatCardNumber = MockPaymentService.formatCardNumber;
export const getCardType = MockPaymentService.getCardType;