import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ActivityMapWidget from '../ActivityMapWidget';

// Mock de react-leaflet para tests
jest.mock('react-leaflet', () => ({
  MapContainer: ({ children }: any) => (
    <div data-testid='map-container'>{children}</div>
  ),
  TileLayer: () => <div data-testid='tile-layer' />,
  Marker: ({ children }: any) => <div data-testid='marker'>{children}</div>,
  Popup: ({ children }: any) => <div data-testid='popup'>{children}</div>,
}));

// Mock de leaflet
jest.mock('leaflet', () => ({
  Icon: {
    Default: {
      prototype: {},
      mergeOptions: jest.fn(),
    },
  },
}));

describe('ActivityMapWidget', () => {
  test('renders without crashing', () => {
    render(<ActivityMapWidget />);
    expect(
      screen.getByText('Actividad por Región - Colombia')
    ).toBeInTheDocument();
  });

  test('displays national metrics', () => {
    render(<ActivityMapWidget />);
    expect(screen.getByText('Métricas Nacionales')).toBeInTheDocument();
    expect(screen.getByText('Ventas Totales:')).toBeInTheDocument();
    expect(screen.getByText('Usuarios Activos:')).toBeInTheDocument();
    expect(screen.getAllByText('Pedidos:')).toHaveLength(6); // 1 nacional + 5 ciudades
  });

  test('renders map container', () => {
    render(<ActivityMapWidget />);
    expect(screen.getByTestId('map-container')).toBeInTheDocument();
    expect(screen.getByTestId('tile-layer')).toBeInTheDocument();
  });

  test('renders markers for Colombian cities', () => {
    render(<ActivityMapWidget />);
    const markers = screen.getAllByTestId('marker');
    expect(markers).toHaveLength(5); // Bogotá, Medellín, Cali, Barranquilla, Cartagena
  });

  test('displays filter controls', () => {
    render(<ActivityMapWidget />);
    expect(screen.getByText('Filtros')).toBeInTheDocument();
    expect(screen.getByText('Tipo de Actividad')).toBeInTheDocument();
    expect(screen.getByText('Período')).toBeInTheDocument();
  });

  test('activity filter works correctly', () => {
    render(<ActivityMapWidget />);
    const activitySelect = screen.getByDisplayValue('Todas las Actividades');
    fireEvent.change(activitySelect, { target: { value: 'sales' } });
    expect(activitySelect).toHaveValue('sales');
  });

  test('period filter works correctly', () => {
    render(<ActivityMapWidget />);
    const periodSelect = screen.getByDisplayValue('Último Mes');
    fireEvent.change(periodSelect, { target: { value: 'week' } });
    expect(periodSelect).toHaveValue('week');
  });

  test('component is memoized with React.memo', () => {
    const Component = require('../ActivityMapWidget').default;
    expect(Component.$$typeof).toBeDefined(); // React.memo components have this property
  });
});
