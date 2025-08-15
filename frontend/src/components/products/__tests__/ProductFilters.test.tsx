// ~/src/components/products/__tests__/ProductFilters.test.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Tests para ProductFilters
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------

import React from 'react';
import { render, screen } from '@testing-library/react';
import ProductFilters from '../ProductFilters';

const mockFilters = {
  search: '',
  category: '',
  sortBy: 'name' as const,
  sortOrder: 'asc' as const
};

describe('ProductFilters', () => {
  it('renders without crashing', () => {
    render(
      <ProductFilters
        filters={mockFilters}
        onFiltersChange={() => {}}
        onReset={() => {}}
      />
    );
    expect(screen.getByText('Buscar productos')).toBeInTheDocument();
  });

  it('renders category filter', () => {
    render(
      <ProductFilters
        filters={mockFilters}
        onFiltersChange={() => {}}
        onReset={() => {}}
      />
    );
    expect(screen.getByText('Categoría')).toBeInTheDocument();
  });
});