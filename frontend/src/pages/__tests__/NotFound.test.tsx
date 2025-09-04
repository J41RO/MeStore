import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import NotFound from '../NotFound';

const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('NotFound Component', () => {
  test('renders 404 message correctly', () => {
    renderWithRouter(<NotFound />);

    expect(screen.getByText('404')).toBeInTheDocument();
    expect(screen.getByText('Página no encontrada')).toBeInTheDocument();
    expect(
      screen.getByText('La página que buscas no existe o ha sido movida.')
    ).toBeInTheDocument();
  });

  test('renders navigation buttons', () => {
    renderWithRouter(<NotFound />);

    expect(screen.getByText('Volver atrás')).toBeInTheDocument();
    expect(screen.getByText('Ir al Dashboard')).toBeInTheDocument();
  });

  test('dashboard link has correct href', () => {
    renderWithRouter(<NotFound />);

    const dashboardLink = screen.getByText('Ir al Dashboard');
    expect(dashboardLink.closest('a')).toHaveAttribute('href', '/dashboard');
  });
});
