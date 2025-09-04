import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { AuthProvider, useAuthContext } from '../AuthContext';

// Componente de prueba
const TestComponent = () => {
  const { isAuthenticated, user, login, logout } = useAuthContext();

  return (
    <div>
      <span data-testid='auth-status'>
        {isAuthenticated ? 'authenticated' : 'not-authenticated'}
      </span>
      <span data-testid='user-email'>{user?.email || 'no-user'}</span>
      <button
        onClick={() => login('test-token', { id: '1', email: 'test@test.com' })}
        data-testid='login-btn'
      >
        Login
      </button>
      <button onClick={() => logout()} data-testid='logout-btn'>
        Logout
      </button>
    </div>
  );
};

describe('AuthContext', () => {
  const renderWithProvider = () => {
    return render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );
  };

  test('provides authentication state correctly', () => {
    renderWithProvider();

    expect(screen.getByTestId('auth-status')).toHaveTextContent(
      'not-authenticated'
    );
    expect(screen.getByTestId('user-email')).toHaveTextContent('no-user');
  });

  test('handles login correctly', async () => {
    renderWithProvider();

    const loginBtn = screen.getByTestId('login-btn');
    loginBtn.click();

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent(
        'authenticated'
      );
      expect(screen.getByTestId('user-email')).toHaveTextContent(
        'test@test.com'
      );
    });
  });

  test('handles logout correctly', async () => {
    renderWithProvider();

    // Login first
    const loginBtn = screen.getByTestId('login-btn');
    loginBtn.click();

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent(
        'authenticated'
      );
    });

    // Then logout
    const logoutBtn = screen.getByTestId('logout-btn');
    logoutBtn.click();

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent(
        'not-authenticated'
      );
      expect(screen.getByTestId('user-email')).toHaveTextContent('no-user');
    });
  });
});
