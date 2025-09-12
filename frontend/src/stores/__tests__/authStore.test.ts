import { renderHook, act } from '@testing-library/react';
import { useAuthStore, UserType } from '../authStore';

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
};
Object.defineProperty(window, 'localStorage', { value: mockLocalStorage });

describe('AuthStore', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset store state
    useAuthStore.getState().logout();
  });

  test('should initialize with default state', () => {
    const { result } = renderHook(() => useAuthStore());

    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });

  test('should login user and set authentication state', () => {
    const { result } = renderHook(() => useAuthStore());
    const mockUser = { id: '1', email: 'test@example.com', name: 'Test User' };
    const mockToken = 'mock-token-123';

    act(() => {
      result.current.login(mockToken, mockUser);
    });

    expect(result.current.user).toEqual(mockUser);
    expect(result.current.token).toBe(mockToken);
    expect(result.current.isAuthenticated).toBe(true);
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
      'auth_token',
      mockToken
    );
  });

  test('should logout user and clear state', () => {
    const { result } = renderHook(() => useAuthStore());

    // First login
    act(() => {
      result.current.login('token', { id: '1', email: 'test@test.com' });
    });

    // Then logout
    act(() => {
      result.current.logout();
    });

    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('auth_token');
  });

  test('should check auth from localStorage', () => {
    mockLocalStorage.getItem.mockReturnValue('existing-token');
    const { result } = renderHook(() => useAuthStore());

    // Primero necesitamos establecer un usuario para que checkAuth funcione correctamente
    act(() => {
      result.current.login('initial-token', {
        id: 1,
        email: 'test@example.com',
        user_type: UserType.VENDEDOR,
        tipo_usuario: 'vendedor',
        is_active: true
      });
    });

    act(() => {
      const isAuthenticated = result.current.checkAuth();
      expect(isAuthenticated).toBe(true);
    });

    expect(result.current.token).toBe('existing-token');
    expect(result.current.isAuthenticated).toBe(true);
  });

  test('should return false when no token in localStorage', () => {
    mockLocalStorage.getItem.mockReturnValue(null);
    const { result } = renderHook(() => useAuthStore());

    act(() => {
      const isAuthenticated = result.current.checkAuth();
      expect(isAuthenticated).toBe(false);
    });

    expect(result.current.token).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });
});
