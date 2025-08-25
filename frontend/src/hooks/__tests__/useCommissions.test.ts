import { renderHook, act } from '@testing-library/react';
import { useCommissions } from '../useCommissions';
import { CommissionType, CommissionStatus } from '../../types/commission.types';

describe('useCommissions', () => {
  test('should initialize with default values', () => {
    const { result } = renderHook(() => useCommissions());

    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe(null);
    expect(result.current.commissions).toHaveLength(3);
    expect(result.current.totalCommissions).toBeGreaterThan(0);
    expect(result.current.totalSales).toBeGreaterThan(0);
    expect(result.current.commissionCount).toBe(3);
  });

  test('should have correct mock data structure', () => {
    const { result } = renderHook(() => useCommissions());
    const firstCommission = result.current.commissions[0];

    expect(firstCommission).toHaveProperty('id');
    expect(firstCommission).toHaveProperty('productName');
    expect(firstCommission).toHaveProperty('commissionAmount');
    expect(firstCommission).toHaveProperty('commissionType');
    expect(firstCommission).toHaveProperty('status');
    expect(firstCommission.commissionType).toBe(CommissionType.SALE);
    expect(firstCommission.status).toBe(CommissionStatus.CONFIRMED);
  });

  test('should update filters correctly', () => {
    const { result } = renderHook(() => useCommissions());

    act(() => {
      result.current.updateFilters({ searchTerm: 'laptop' });
    });

    expect(result.current.filters.searchTerm).toBe('laptop');
  });

  test('should clear filters correctly', () => {
    const { result } = renderHook(() => useCommissions());

    act(() => {
      result.current.updateFilters({ searchTerm: 'laptop', minAmount: 100 });
    });

    expect(result.current.filters.searchTerm).toBe('laptop');
    expect(result.current.filters.minAmount).toBe(100);

    act(() => {
      result.current.clearFilters();
    });

    expect(result.current.filters).toEqual({});
  });

  test('should handle refresh commissions', async () => {
    const { result } = renderHook(() => useCommissions());

    expect(result.current.isLoading).toBe(false);

    act(() => {
      result.current.refreshCommissions();
    });

    expect(result.current.isLoading).toBe(true);

    // Wait for async operation to complete
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 600));
    });

    expect(result.current.isLoading).toBe(false);
  });

  test('should calculate correct breakdown totals', () => {
    const { result } = renderHook(() => useCommissions());
    const breakdown = result.current.breakdown;

    expect(breakdown.totals.commissionCount).toBe(3);
    expect(breakdown.totals.totalCommissions).toBeGreaterThan(0);
    expect(breakdown.totals.totalSales).toBeGreaterThan(0);
    expect(breakdown.totals.averageCommissionRate).toBeGreaterThan(0);
  });

  test('should initialize with custom filters', () => {
    const initialFilters = { searchTerm: 'test', minAmount: 50 };
    const { result } = renderHook(() => useCommissions(initialFilters));

    expect(result.current.filters.searchTerm).toBe('test');
    expect(result.current.filters.minAmount).toBe(50);
  });

  test('should return mockData correctly', () => {
    const { result } = renderHook(() => useCommissions());

    expect(result.current.mockData).toHaveLength(3);
    expect(result.current.mockData[0].id).toBe('comm-001');
    expect(result.current.mockData[1].id).toBe('comm-002');
    expect(result.current.mockData[2].id).toBe('comm-003');
  });
});