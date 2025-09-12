import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import Layout from '../Layout';
import { useAuthStore } from '@/stores/authStore';

// Mock del auth store
jest.mock('@/stores/authStore');
const mockUseAuthStore = useAuthStore as jest.MockedFunction<
  typeof useAuthStore
>;

// Mock de react-router-dom useLocation
const mockUseLocation = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useLocation: () => mockUseLocation(),
  Outlet: () => <div data-testid='outlet'>Page Content</div>,
}));

const renderLayout = () => {
  return render(
    <BrowserRouter>
      <Layout />
    </BrowserRouter>
  );
};

describe('Layout Component', () => {
  const mockLogout = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseLocation.mockReturnValue({ pathname: '/app/dashboard' });
  });

  test('should render navigation with MeStore branding', () => {
    mockUseAuthStore.mockReturnValue({
      user: { id: '1', email: 'test@test.com' },
      logout: mockLogout,
      isAuthenticated: true,
      token: 'token',
      login: jest.fn(),
      checkAuth: jest.fn(),
    });

    renderLayout();

    expect(screen.getByText('MeStore')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Productos')).toBeInTheDocument();
  });

  test('should highlight active navigation link', () => {
    mockUseAuthStore.mockReturnValue({
      user: { id: '1', email: 'test@test.com' },
      logout: mockLogout,
      isAuthenticated: true,
      token: 'token',
      login: jest.fn(),
      checkAuth: jest.fn(),
    });

    renderLayout();

    const dashboardLink = screen.getByText('Dashboard').closest('a');
    expect(dashboardLink).toHaveClass('bg-blue-100', 'text-blue-700');
  });

  test('should display user email in logout button', () => {
    const testUser = { id: '1', email: 'usuario@test.com' };
    mockUseAuthStore.mockReturnValue({
      user: testUser,
      logout: mockLogout,
      isAuthenticated: true,
      token: 'token',
      login: jest.fn(),
      checkAuth: jest.fn(),
    });

    renderLayout();

    expect(
      screen.getByText('Cerrar Sesión (usuario@test.com)')
    ).toBeInTheDocument();
  });

  test('should call logout when logout button is clicked', () => {
    mockUseAuthStore.mockReturnValue({
      user: { id: '1', email: 'test@test.com' },
      logout: mockLogout,
      isAuthenticated: true,
      token: 'token',
      login: jest.fn(),
      checkAuth: jest.fn(),
    });

    renderLayout();

    const logoutButton = screen.getByText(/Cerrar Sesión/);
    fireEvent.click(logoutButton);

    expect(mockLogout).toHaveBeenCalledTimes(1);
  });

  test('should highlight productos link when on productos page', () => {
    mockUseLocation.mockReturnValue({ pathname: '/app/productos' });
    mockUseAuthStore.mockReturnValue({
      user: { id: '1', email: 'test@test.com' },
      logout: mockLogout,
      isAuthenticated: true,
      token: 'token',
      login: jest.fn(),
      checkAuth: jest.fn(),
    });

    renderLayout();

    const productosLink = screen.getByText('Productos').closest('a');
    expect(productosLink).toHaveClass('bg-blue-100', 'text-blue-700');

    const dashboardLink = screen.getByText('Dashboard').closest('a');
    expect(dashboardLink).toHaveClass('text-gray-500');
  });

  test('should render outlet for page content', () => {
    mockUseAuthStore.mockReturnValue({
      user: { id: '1', email: 'test@test.com' },
      logout: mockLogout,
      isAuthenticated: true,
      token: 'token',
      login: jest.fn(),
      checkAuth: jest.fn(),
    });

    renderLayout();

    expect(screen.getByTestId('outlet')).toBeInTheDocument();
    expect(screen.getByText('Page Content')).toBeInTheDocument();
  });
});
