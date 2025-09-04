import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { AuthProvider } from '../AuthContext';
import { UserProvider, useUserContext } from '../UserContext';

const MockAuthProvider = ({ children }: { children: React.ReactNode }) => (
  <AuthProvider>{children}</AuthProvider>
);

const TestComponent = () => {
  const { vendorProfile, isLoading, completionPercentage, loadVendorProfile } =
    useUserContext();

  return (
    <div>
      <span data-testid='loading'>{isLoading ? 'loading' : 'loaded'}</span>
      <span data-testid='store-name'>
        {vendorProfile?.storeName || 'no-store'}
      </span>
      <span data-testid='completion'>{completionPercentage}%</span>
      <button onClick={loadVendorProfile} data-testid='load-btn'>
        Cargar Perfil
      </button>
    </div>
  );
};

describe('UserContext', () => {
  const renderWithProviders = () => {
    return render(
      <MockAuthProvider>
        <UserProvider>
          <TestComponent />
        </UserProvider>
      </MockAuthProvider>
    );
  };

  test('provides initial state correctly', () => {
    renderWithProviders();

    expect(screen.getByTestId('loading')).toHaveTextContent('loaded');
    expect(screen.getByTestId('store-name')).toHaveTextContent('no-store');
    expect(screen.getByTestId('completion')).toHaveTextContent('0%');
  });

  test('loads vendor profile correctly', async () => {
    renderWithProviders();

    const loadBtn = screen.getByTestId('load-btn');
    loadBtn.click();

    await waitFor(
      () => {
        expect(screen.getByTestId('loading')).toHaveTextContent('loaded');
      },
      { timeout: 1000 }
    );
  });
});
