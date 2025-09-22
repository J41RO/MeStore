export const authService = {
  login: jest.fn().mockResolvedValue({
    success: true,
    data: { access_token: 'mock-token' }
  }),

  adminLogin: jest.fn().mockResolvedValue({
    success: true,
    data: { access_token: 'mock-admin-token' }
  }),

  register: jest.fn().mockResolvedValue({
    success: true,
    data: { access_token: 'mock-token' }
  }),

  logout: jest.fn().mockResolvedValue(undefined),

  getCurrentUser: jest.fn().mockResolvedValue({
    success: true,
    data: {
      id: '1',
      email: 'test@example.com',
      user_type: 'BUYER',
      nombre: 'Test User',
      email_verified: true,
      phone_verified: false,
      is_active: true
    }
  }),

  validateToken: jest.fn().mockResolvedValue(true),

  getToken: jest.fn().mockReturnValue('mock-token'),

  setToken: jest.fn(),

  removeToken: jest.fn()
};