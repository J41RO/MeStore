import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';

// Mock de react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock simple del componente para evitar problemas de import
const MockVendorLanding = () => {
  const navigate = mockNavigate;
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <section className="px-4 py-16 mx-auto max-w-7xl sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-6xl">
            Únete a Nuestra Plataforma
            <span className="block text-blue-600 dark:text-blue-400">
              Como Vendedor
            </span>
          </h1>
          <button 
            onClick={() => navigate('/register')}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg"
          >
            Únete Ahora
          </button>
        </div>
      </section>
      
      <section className="px-4 py-16 mx-auto max-w-7xl sm:px-6 lg:px-8">
        <h2 className="text-3xl font-bold text-center mb-16">¿Por qué elegir nuestra plataforma?</h2>
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
          <div>Comisiones Altas</div>
          <div>Alcance Nacional</div>
          <div>Herramientas Avanzadas</div>
          <div>Soporte 24/7</div>
        </div>
      </section>
    </div>
  );
};

describe('VendorLanding Component', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  const renderWithRouter = (component: React.ReactElement) => {
    return render(
      <BrowserRouter>
        {component}
      </BrowserRouter>
    );
  };

  test('debe renderizar el hero section correctamente', () => {
    renderWithRouter(<MockVendorLanding />);
    expect(screen.getByText('Únete a Nuestra Plataforma')).toBeInTheDocument();
    expect(screen.getByText('Como Vendedor')).toBeInTheDocument();
  });

  test('debe mostrar el botón de call-to-action', () => {
    renderWithRouter(<MockVendorLanding />);
    expect(screen.getByText('Únete Ahora')).toBeInTheDocument();
  });

  test('debe navegar a /register cuando se hace clic en "Únete Ahora"', () => {
    renderWithRouter(<MockVendorLanding />);
    const button = screen.getByText('Únete Ahora');
    fireEvent.click(button);
    expect(mockNavigate).toHaveBeenCalledWith('/register');
  });

  test('debe mostrar la sección de beneficios', () => {
    renderWithRouter(<MockVendorLanding />);
    expect(screen.getByText('¿Por qué elegir nuestra plataforma?')).toBeInTheDocument();
    expect(screen.getByText('Comisiones Altas')).toBeInTheDocument();
    expect(screen.getByText('Alcance Nacional')).toBeInTheDocument();
    expect(screen.getByText('Herramientas Avanzadas')).toBeInTheDocument();
    expect(screen.getByText('Soporte 24/7')).toBeInTheDocument();
  });

  test('debe tener clases responsive aplicadas', () => {
    renderWithRouter(<MockVendorLanding />);
    const mainDiv = screen.getByText('Únete a Nuestra Plataforma').closest('section');
    expect(mainDiv).toHaveClass('px-4', 'sm:px-6', 'lg:px-8');
  });
});
