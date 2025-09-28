/**
 * Admin Analytics Pages Index
 */

export { default as AnalyticsDashboard } from './AnalyticsDashboard';
export { default as SalesReportsPage } from './SalesReportsPage';
export { default as FinancialReportsPage } from './FinancialReportsPage';
export { default as PerformanceMetricsPage } from './PerformanceMetricsPage';
export { default as CustomReportsPage } from './CustomReportsPage';

export const analyticsPagesMetadata = {
  dashboard: { path: '/admin-secure-portal/analytics', title: 'Analytics Dashboard', component: 'AnalyticsDashboard' },
  sales: { path: '/admin-secure-portal/sales-reports', title: 'Sales Reports', component: 'SalesReportsPage' },
  financial: { path: '/admin-secure-portal/financial-reports', title: 'Financial Reports', component: 'FinancialReportsPage' },
  performance: { path: '/admin-secure-portal/performance', title: 'Performance Metrics', component: 'PerformanceMetricsPage' },
  custom: { path: '/admin-secure-portal/custom-reports', title: 'Custom Reports', component: 'CustomReportsPage' }
};