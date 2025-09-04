// ~/src/components/products/__tests__/ProductTable.test.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Tests para ProductTable
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------

import React from 'react';
import { render, screen } from '@testing-library/react';
import ProductTable from '../ProductTable';

// Mock data
const mockProducts = [
  {
    id: '1',
    name: 'Producto Test',
    description: 'Descripción test',
    price: 100,
    stock: 10,
    category: 'Test',
    imageUrl: '',
    createdAt: '2025-01-01',
    updatedAt: '2025-01-01',
  },
];

const mockPagination = {
  page: 1,
  limit: 10,
  total: 1,
  totalPages: 1,
};

describe('ProductTable', () => {
  it('renders without crashing', () => {
    render(
      <ProductTable
        products={mockProducts}
        loading={false}
        pagination={mockPagination}
        onPageChange={() => {}}
      />
    );
    expect(screen.getByText('Producto Test')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    render(
      <ProductTable
        products={[]}
        loading={true}
        pagination={mockPagination}
        onPageChange={() => {}}
      />
    );
    expect(screen.getByText('Cargando productos...')).toBeInTheDocument();
  });

  it('shows empty state', () => {
    render(
      <ProductTable
        products={[]}
        loading={false}
        pagination={mockPagination}
        onPageChange={() => {}}
      />
    );
    expect(screen.getByText('No hay productos')).toBeInTheDocument();
  });
});
