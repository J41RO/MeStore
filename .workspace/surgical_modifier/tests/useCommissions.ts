import { useState, useMemo, useCallback } from 'react';
import { Commission, CommissionBreakdown, CommissionFilters, CommissionType, CommissionStatus } from '../../../frontend/src/types/commission.types';

// Mock data básico
const mockCommissionsData: Commission[] = [
  {
    id: 'comm-001',
    productId: 'prod-001',
    productName: 'Laptop Gaming RGB Pro',
    productCategory: 'Computadoras',
    saleAmount: 1299.99,
    commissionRate: 0.08,
    commissionAmount: 103.99,
    commissionType: CommissionType.SALE,
    status: CommissionStatus.CONFIRMED,
    saleDate: new Date('2025-08-01'),
    vendorId: 'vendor-001',
    vendorName: 'Vendedor Principal',
    orderId: 'order-001',
    customerName: 'Juan Pérez'
  }
];

export const useCommissions = (initialFilters: CommissionFilters = {}) => {
  const [filters, setFilters] = useState<CommissionFilters>(initialFilters);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const filteredCommissions = useMemo(() => {
    return [...mockCommissionsData];
  }, [filters]);

  const commissionBreakdown = useMemo(() => {
    const totalCommissions = filteredCommissions.reduce((sum, c) => sum + c.commissionAmount, 0);
    const totalSales = filteredCommissions.reduce((sum, c) => sum + c.saleAmount, 0);
    
    const breakdown: CommissionBreakdown = {
      byProduct: [],
      byPeriod: [],
      byType: [],
      byCategory: {},
      totals: {
        totalCommissions,
        totalSales,
        commissionCount: filteredCommissions.length,
        averageCommissionRate: totalSales > 0 ? totalCommissions / totalSales : 0,
        topProduct: '',
        topCategory: ''
      }
    };
    
    return breakdown;
  }, [filteredCommissions]);

  const updateFilters = useCallback((newFilters: Partial<CommissionFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  const clearFilters = useCallback(() => {
    setFilters({});
  }, []);

  const refreshCommissions = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
    } catch (err) {
      setError('Error cargando comisiones');
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    commissions: filteredCommissions,
    breakdown: commissionBreakdown,
    filters,
    isLoading,
    error,
    updateFilters,
    clearFilters,
    refreshCommissions,
    totalCommissions: filteredCommissions.reduce((sum, c) => sum + c.commissionAmount, 0),
    totalSales: filteredCommissions.reduce((sum, c) => sum + c.saleAmount, 0),
    commissionCount: filteredCommissions.length,
    mockData: mockCommissionsData
  };
};