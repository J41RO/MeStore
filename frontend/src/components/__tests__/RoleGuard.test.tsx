import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, beforeEach } from '@jest/globals';
import RoleGuard, { RoleStrategy } from '../RoleGuard';
import { UserType } from '../../stores/authStore';

// Mock the useRoleAccess hook
const mockUseRoleAccess = jest.fn();
jest.mock('../../hooks/useRoleAccess', () => ({
  useRoleAccess: () => mockUseRoleAccess(),
  getRoleDisplayName: (role: UserType) => {
    const names = {
      [UserType.BUYER]: 'Comprador',
      [UserType.VENDOR]: 'Vendedor',
      [UserType.ADMIN]: 'Administrador',
      [UserType.SUPERUSER]: 'Super Usuario'
    };
    return names[role] || 'Desconocido';
  },
}));

// Mock useLocation
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useLocation: () => ({ pathname: '/test' }),
  Navigate: ({ to }: { to: string }) => <div data-testid="navigate">{to}</div>,
}));

// Wrapper component for testing with router
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('RoleGuard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Access granted scenarios', () => {
    it('should render children when user has exact role', () => {
      mockUseRoleAccess.mockReturnValue({
        hasRole: (role: UserType) => role === UserType.ADMIN,
        hasAnyRole: (roles: UserType[]) => roles.includes(UserType.ADMIN),
        hasAllRoles: (roles: UserType[]) => roles.length === 1 && roles.includes(UserType.ADMIN),
        hasMinimumRole: (minRole: UserType) => true,
        getCurrentRole: () => UserType.ADMIN,
      });

      render(
        <TestWrapper>
          <RoleGuard roles={[UserType.ADMIN]} strategy="exact">
            <div data-testid="protected-content">Protected Content</div>
          </RoleGuard>
        </TestWrapper>
      );

      expect(screen.getByTestId('protected-content')).toBeInTheDocument();
    });

    it('should render children when user has any of required roles', () => {
      mockUseRoleAccess.mockReturnValue({
        hasRole: (role: UserType) => role === UserType.VENDOR,
        hasAnyRole: (roles: UserType[]) => roles.includes(UserType.VENDOR),
        hasAllRoles: (roles: UserType[]) => false,
        hasMinimumRole: (minRole: UserType) => true,
        getCurrentRole: () => UserType.VENDOR,
      });

      render(
        <TestWrapper>
          <RoleGuard roles={[UserType.ADMIN, UserType.VENDOR]} strategy="any">
            <div data-testid="protected-content">Protected Content</div>
          </RoleGuard>
        </TestWrapper>
      );

      expect(screen.getByTestId('protected-content')).toBeInTheDocument();
    });

    it('should render children when user has minimum role', () => {
      mockUseRoleAccess.mockReturnValue({
        hasRole: (role: UserType) => role === UserType.ADMIN,
        hasAnyRole: (roles: UserType[]) => true,
        hasAllRoles: (roles: UserType[]) => false,
        hasMinimumRole: (minRole: UserType) => true,
        getCurrentRole: () => UserType.ADMIN,
      });

      render(
        <TestWrapper>
          <RoleGuard roles={[UserType.VENDOR]} strategy="minimum">
            <div data-testid="protected-content">Protected Content</div>
          </RoleGuard>
        </TestWrapper>
      );

      expect(screen.getByTestId('protected-content')).toBeInTheDocument();
    });
  });

  describe('Access denied scenarios', () => {
    it('should show default fallback when access denied', () => {
      mockUseRoleAccess.mockReturnValue({
        hasRole: (role: UserType) => false,
        hasAnyRole: (roles: UserType[]) => false,
        hasAllRoles: (roles: UserType[]) => false,
        hasMinimumRole: (minRole: UserType) => false,
        getCurrentRole: () => UserType.BUYER,
      });

      render(
        <TestWrapper>
          <RoleGuard roles={[UserType.ADMIN]} strategy="exact">
            <div data-testid="protected-content">Protected Content</div>
          </RoleGuard>
        </TestWrapper>
      );

      expect(screen.getByText('Acceso Restringido')).toBeInTheDocument();
      expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
    });

    it('should show custom fallback when provided', () => {
      mockUseRoleAccess.mockReturnValue({
        hasRole: (role: UserType) => false,
        hasAnyRole: (roles: UserType[]) => false,
        hasAllRoles: (roles: UserType[]) => false,
        hasMinimumRole: (minRole: UserType) => false,
        getCurrentRole: () => UserType.BUYER,
      });

      render(
        <TestWrapper>
          <RoleGuard 
            roles={[UserType.ADMIN]} 
            strategy="exact"
            fallback={<div data-testid="custom-fallback">Custom Fallback</div>}
          >
            <div data-testid="protected-content">Protected Content</div>
          </RoleGuard>
        </TestWrapper>
      );

      expect(screen.getByTestId('custom-fallback')).toBeInTheDocument();
      expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
    });

    it('should redirect when redirectTo is provided', () => {
      mockUseRoleAccess.mockReturnValue({
        hasRole: (role: UserType) => false,
        hasAnyRole: (roles: UserType[]) => false,
        hasAllRoles: (roles: UserType[]) => false,
        hasMinimumRole: (minRole: UserType) => false,
        getCurrentRole: () => UserType.BUYER,
      });

      render(
        <TestWrapper>
          <RoleGuard 
            roles={[UserType.ADMIN]} 
            strategy="exact"
            redirectTo="/unauthorized"
          >
            <div data-testid="protected-content">Protected Content</div>
          </RoleGuard>
        </TestWrapper>
      );

      expect(screen.getByTestId('navigate')).toHaveTextContent('/unauthorized');
      expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
    });
  });

  describe('Strategy validation', () => {
    it('should handle empty roles array', () => {
      mockUseRoleAccess.mockReturnValue({
        hasRole: (role: UserType) => false,
        hasAnyRole: (roles: UserType[]) => false,
        hasAllRoles: (roles: UserType[]) => false,
        hasMinimumRole: (minRole: UserType) => false,
        getCurrentRole: () => UserType.BUYER,
      });

      // Mock console.warn to verify it's called
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});

      render(
        <TestWrapper>
          <RoleGuard roles={[]} strategy="exact">
            <div data-testid="protected-content">Protected Content</div>
          </RoleGuard>
        </TestWrapper>
      );

      expect(consoleSpy).toHaveBeenCalledWith('RoleGuard: No roles specified');
      expect(screen.getByTestId('protected-content')).toBeInTheDocument();

      consoleSpy.mockRestore();
    });

    it('should handle minimum strategy with multiple roles', () => {
      mockUseRoleAccess.mockReturnValue({
        hasRole: (role: UserType) => false,
        hasAnyRole: (roles: UserType[]) => false,
        hasAllRoles: (roles: UserType[]) => false,
        hasMinimumRole: (minRole: UserType) => false,
        getCurrentRole: () => UserType.BUYER,
      });

      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});

      render(
        <TestWrapper>
          <RoleGuard roles={[UserType.ADMIN, UserType.VENDOR]} strategy="minimum">
            <div data-testid="protected-content">Protected Content</div>
          </RoleGuard>
        </TestWrapper>
      );

      expect(consoleSpy).toHaveBeenCalledWith('RoleGuard: minimum strategy requires exactly one role');
      expect(screen.getByText('Acceso Restringido')).toBeInTheDocument();

      consoleSpy.mockRestore();
    });

    it('should handle unknown strategy', () => {
      mockUseRoleAccess.mockReturnValue({
        hasRole: (role: UserType) => false,
        hasAnyRole: (roles: UserType[]) => false,
        hasAllRoles: (roles: UserType[]) => false,
        hasMinimumRole: (minRole: UserType) => false,
        getCurrentRole: () => UserType.BUYER,
      });

      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});

      render(
        <TestWrapper>
          <RoleGuard roles={[UserType.ADMIN]} strategy={'unknown' as RoleStrategy}>
            <div data-testid="protected-content">Protected Content</div>
          </RoleGuard>
        </TestWrapper>
      );

      expect(consoleSpy).toHaveBeenCalledWith('RoleGuard: Unknown strategy "unknown"');
      expect(screen.getByText('Acceso Restringido')).toBeInTheDocument();

      consoleSpy.mockRestore();
    });
  });
});

export {};