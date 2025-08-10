import { renderHook, act } from '@testing-library/react';
import { useTheme } from '../useTheme';

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
};
Object.defineProperty(window, 'localStorage', { value: mockLocalStorage });

// Mock matchMedia
const mockMatchMedia = jest.fn();
Object.defineProperty(window, 'matchMedia', { value: mockMatchMedia });

describe('useTheme Hook', () => {
  const mockMediaQuery = {
    matches: false,
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockMatchMedia.mockReturnValue(mockMediaQuery);
    document.documentElement.className = '';
  });

  test('should initialize with system theme by default', () => {
    mockLocalStorage.getItem.mockReturnValue(null);
    mockMediaQuery.matches = false;
    
    const { result } = renderHook(() => useTheme());
    
    expect(result.current.theme).toBe('system');
    expect(result.current.systemTheme).toBe('light');
    expect(result.current.effectiveTheme).toBe('light');
  });

  test('should load saved theme from localStorage', () => {
    mockLocalStorage.getItem.mockReturnValue('dark');
    
    const { result } = renderHook(() => useTheme());
    
    expect(result.current.theme).toBe('dark');
    expect(result.current.effectiveTheme).toBe('dark');
    expect(mockLocalStorage.getItem).toHaveBeenCalledWith('mestocker-theme');
  });

  test('should detect system dark theme', () => {
    mockLocalStorage.getItem.mockReturnValue(null);
    mockMediaQuery.matches = true;
    
    const { result } = renderHook(() => useTheme());
    
    expect(result.current.systemTheme).toBe('dark');
    expect(result.current.effectiveTheme).toBe('dark');
  });

  test('should set specific theme and save to localStorage', () => {
    const { result } = renderHook(() => useTheme());
    
    act(() => {
      result.current.setTheme('dark');
    });
    
    expect(result.current.theme).toBe('dark');
    expect(result.current.effectiveTheme).toBe('dark');
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith('mestocker-theme', 'dark');
  });

  test('should toggle theme in correct sequence', () => {
    mockLocalStorage.getItem.mockReturnValue('light');
    const { result } = renderHook(() => useTheme());
    
    // light → dark
    act(() => {
      result.current.toggleTheme();
    });
    expect(result.current.theme).toBe('dark');
    
    // dark → system
    act(() => {
      result.current.toggleTheme();
    });
    expect(result.current.theme).toBe('system');
    
    // system → light
    act(() => {
      result.current.toggleTheme();
    });
    expect(result.current.theme).toBe('light');
  });

  test('should apply dark class to document when dark theme', () => {
    const { result } = renderHook(() => useTheme());
    
    act(() => {
      result.current.setTheme('dark');
    });
    
    expect(document.documentElement.classList.contains('dark')).toBe(true);
    expect(document.documentElement.classList.contains('light')).toBe(false);
  });

  test('should apply light class when light theme', () => {
    const { result } = renderHook(() => useTheme());
    
    act(() => {
      result.current.setTheme('light');
    });
    
    expect(document.documentElement.classList.contains('light')).toBe(true);
    expect(document.documentElement.classList.contains('dark')).toBe(false);
  });

  test('should handle system theme with effective theme calculation', () => {
    mockLocalStorage.getItem.mockReturnValue('system');
    mockMediaQuery.matches = true; // System is dark
    
    const { result } = renderHook(() => useTheme());
    
    expect(result.current.theme).toBe('system');
    expect(result.current.systemTheme).toBe('dark');
    expect(result.current.effectiveTheme).toBe('dark');
  });

  test('should ignore invalid localStorage values', () => {
    mockLocalStorage.getItem.mockReturnValue('invalid-theme');
    
    const { result } = renderHook(() => useTheme());
    
    // Should keep default system theme
    expect(result.current.theme).toBe('system');
  });

  test('should listen to system theme changes', () => {
    const { result } = renderHook(() => useTheme());
    
    // Simulate system theme change
    const changeHandler = mockMediaQuery.addEventListener.mock.calls[0][1];
    act(() => {
      changeHandler({ matches: true });
    });
    
    expect(result.current.systemTheme).toBe('dark');
  });
});
