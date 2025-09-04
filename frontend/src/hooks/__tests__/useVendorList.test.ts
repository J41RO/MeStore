// ~/src/hooks/__tests__/useVendorList.test.ts
// ---------------------------------------------------------------------------------------------
// MESTORE - Tests para useVendorList
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
import { renderHook } from '@testing-library/react';
import { useVendorList } from '../useVendorList';

const mockVendors = [];

describe('useVendorList', () => {
  it('returns initial state correctly', () => {
    const { result } = renderHook(() => useVendorList(mockVendors));
    expect(result.current.selectedEstado).toBe('todos');
    expect(result.current.selectedTipo).toBe('todos');
  });
});