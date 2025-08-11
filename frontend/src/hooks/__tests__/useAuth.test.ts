import { renderHook, act } from '@testing-library/react';
import { AuthProvider } from '../../contexts/AuthContext';
import { useAuth } from '../useAuth';
import React from 'react';

const wrapper = ({ children }: { children: React.ReactNode }) => 
  React.createElement(AuthProvider, null, children);

describe('useAuth Hook', () => {
  test('returns initial state correctly', () => {
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBe(null);
    expect(result.current.isLoggedIn).toBe(false);
    expect(result.current.userRole).toBe('guest');
  });

  test('signIn works correctly', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    await act(async () => {
      const response = await result.current.signIn('test@example.com', 'password');
      expect(response.success).toBe(true);
    });
    
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.userEmail).toBe('test@example.com');
    expect(result.current.userName).toBe('test');
  });

  test('signOut works correctly', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    // Login first
    await act(async () => {
      await result.current.signIn('test@example.com', 'password');
    });
    
    expect(result.current.isAuthenticated).toBe(true);
    
    // Then logout
    await act(async () => {
      const response = await result.current.signOut();
      expect(response.success).toBe(true);
    });
    
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBe(null);
  });
});