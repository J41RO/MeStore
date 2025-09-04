// ~/src/components/vendors/__tests__/VendorList.test.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Tests para VendorList
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
import React from 'react';
import { render, screen } from '@testing-library/react';
import VendorList from '../VendorList';

const mockVendors = [];

describe('VendorList', () => {
  it('renders without crashing', () => {
    render(<VendorList vendors={mockVendors} loading={false} />);
    expect(screen.getByText('Vendor List')).toBeInTheDocument();
  });
});