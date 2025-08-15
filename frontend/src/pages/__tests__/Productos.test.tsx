// ~/src/pages/__tests__/Productos.test.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Tests para página Productos
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------

import React from 'react';
import { render, screen } from '@testing-library/react';

// Mock de los servicios API antes de importar componentes
jest.mock('../../services/api', () => ({
  api: {
    products: {
      getWithFilters: jest.fn().mockResolvedValue({
        data: {
          data: [],
          pagination: {
            page: 1,
            limit: 10,
            total: 0,
            totalPages: 0
          }
        }
      })
    }
  }
}));

// Mock del hook useProductList
jest.mock('../../hooks/useProductList', () => ({
  useProductList: () => ({
    products: [],
    loading: false,
    error: null,
    pagination: {
      page: 1,
      limit: 10,
      total: 0,
      totalPages: 0
    },
    filters: {
      search: '',
      category: '',
      sortBy: 'name',
      sortOrder: 'asc'
    },
    applyFilters: jest.fn(),
    changePage: jest.fn(),
    resetFilters: jest.fn(),
    refreshProducts: jest.fn()
  })
}));

import Productos from '../Productos';

describe('Productos Page', () => {
  it('renders without crashing', () => {
    render(<Productos />);
    expect(screen.getByText('Gestión de Productos')).toBeInTheDocument();
  });

  it('renders add product button', () => {
    render(<Productos />);
    expect(screen.getByText('Agregar Producto')).toBeInTheDocument();
  });

  it('renders product filters and table components', () => {
    render(<Productos />);
    expect(screen.getByText('Administra tu catálogo de productos')).toBeInTheDocument();
  });
});