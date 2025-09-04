import { useState, useMemo, useCallback } from 'react';
import {
  Commission,
  CommissionBreakdown,
  CommissionFilters,
  CommissionType,
  CommissionStatus,
} from '../types/commission.types';

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
    customerName: 'Juan Pérez',
  },
  {
    id: 'comm-002',
    productId: 'prod-002',
    productName: 'iPhone 15 Pro Max',
    productCategory: 'Celulares',
    saleAmount: 999.99,
    commissionRate: 0.06,
    commissionAmount: 59.99,
    commissionType: CommissionType.PRODUCT,
    status: CommissionStatus.PAID,
    saleDate: new Date('2025-08-05'),
    paidDate: new Date('2025-08-10'),
    vendorId: 'vendor-001',
    vendorName: 'Vendedor Principal',
    orderId: 'order-002',
    customerName: 'María González',
  },
  {
    id: 'comm-003',
    productId: 'prod-003',
    productName: 'Smart TV 65" OLED',
    productCategory: 'Televisores',
    saleAmount: 1599.99,
    commissionRate: 0.1,
    commissionAmount: 159.99,
    commissionType: CommissionType.VOLUME,
    status: CommissionStatus.CONFIRMED,
    saleDate: new Date('2025-08-10'),
    vendorId: 'vendor-001',
    vendorName: 'Vendedor Principal',
    orderId: 'order-003',
    customerName: 'Carlos Rodríguez',
  },
];

export const useCommissions = (initialFilters: CommissionFilters = {}) => {
  const [filters, setFilters] = useState<CommissionFilters>(initialFilters);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const filteredCommissions = useMemo(() => {
    return [...mockCommissionsData];
  }, [filters]);

  const commissionBreakdown = useMemo(() => {
    const totalCommissions = filteredCommissions.reduce(
      (sum, c) => sum + c.commissionAmount,
      0
    );
    const totalSales = filteredCommissions.reduce(
      (sum, c) => sum + c.saleAmount,
      0
    );

    const breakdown: CommissionBreakdown = {
      byProduct: [],
      byPeriod: [],
      byType: [],
      byCategory: {},
      totals: {
        totalCommissions,
        totalSales,
        commissionCount: filteredCommissions.length,
        averageCommissionRate:
          totalSales > 0 ? totalCommissions / totalSales : 0,
        topProduct: '',
        topCategory: '',
      },
    };

    return breakdown;
  }, [filteredCommissions]);

  const updateFilters = useCallback(
    (newFilters: Partial<CommissionFilters>) => {
      setFilters(prev => ({ ...prev, ...newFilters }));
    },
    []
  );

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
    totalCommissions: filteredCommissions.reduce(
      (sum, c) => sum + c.commissionAmount,
      0
    ),
    totalSales: filteredCommissions.reduce((sum, c) => sum + c.saleAmount, 0),
    commissionCount: filteredCommissions.length,
    mockData: mockCommissionsData,
  };
};
