import { renderHook } from '@testing-library/react';
import { AuthProvider } from '../../contexts/AuthContext';
import { UserProvider } from '../../contexts/UserContext';
import { useVendor } from '../useVendor';
import React from 'react';

const wrapper = ({ children }: { children: React.ReactNode }) =>
  React.createElement(
    AuthProvider,
    null,
    React.createElement(UserProvider, null, children)
  );

describe('useVendor Hook', () => {
  test('returns initial state correctly', () => {
    const { result } = renderHook(() => useVendor(), { wrapper });

    expect(result.current.storeName).toBe('Mi Tienda');
    expect(result.current.isLoading).toBe(false);
    expect(result.current.completionPercentage).toBe(0);
    expect(result.current.metrics.totalSales).toBe(0);
  });

  test('provides business summary correctly', () => {
    const { result } = renderHook(() => useVendor(), { wrapper });

    const summary = result.current.getBusinessSummary();

    expect(summary).toHaveProperty('totalSales');
    expect(summary).toHaveProperty('revenue');
    expect(summary).toHaveProperty('products');
    expect(summary).toHaveProperty('rating');
    expect(summary.revenue).toContain('$');
  });

  test('provides completion status correctly', () => {
    const { result } = renderHook(() => useVendor(), { wrapper });

    const status = result.current.getCompletionStatus();

    expect(status).toHaveProperty('percentage');
    expect(status).toHaveProperty('isComplete');
    expect(status).toHaveProperty('missingFields');
    expect(status).toHaveProperty('canPublish');
    expect(typeof status.percentage).toBe('number');
    expect(typeof status.isComplete).toBe('boolean');
  });

  test('provides vendor data properties correctly', () => {
    const { result } = renderHook(() => useVendor(), { wrapper });

    expect(result.current).toHaveProperty('storeName');
    expect(result.current).toHaveProperty('storeSlug');
    expect(result.current).toHaveProperty('isVerified');
    expect(result.current).toHaveProperty('isActive');
    expect(result.current).toHaveProperty('metrics');
    expect(result.current).toHaveProperty('notifications');
    expect(result.current).toHaveProperty('preferences');
    expect(result.current).toHaveProperty('contactInfo');
  });

  test('provides vendor action methods correctly', () => {
    const { result } = renderHook(() => useVendor(), { wrapper });

    expect(typeof result.current.updateStoreName).toBe('function');
    expect(typeof result.current.updateStoreDescription).toBe('function');
    expect(typeof result.current.updateContactInfo).toBe('function');
    expect(typeof result.current.toggleNotification).toBe('function');
    expect(typeof result.current.updateTheme).toBe('function');
    expect(typeof result.current.refreshMetrics).toBe('function');
  });
});
