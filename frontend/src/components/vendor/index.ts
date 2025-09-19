/**
 * Vendor Components Index
 * Central export point for all vendor-related components
 *
 * Usage:
 * import { ProductsManagementPage, ProductList, ProductForm } from '@/components/vendor';
 */

// Main container components
export { default as ProductsManagementPage } from '../../pages/vendor/ProductsManagementPage';

// Product management components
export { default as ProductList } from './ProductList';
export { default as ProductCard } from './ProductCard';
export { default as ProductForm } from './ProductForm';
export { default as ProductFilters } from './ProductFilters';
export { default as ProductStats } from './ProductStats';

// Bulk operations
export { default as BulkActions } from './BulkActions';

// Existing vendor components
export { VendorOrderDashboard } from './VendorOrderDashboard';
export { VendorProductDashboard } from './VendorProductDashboard';
export { VendorProductForm } from './VendorProductForm';
export { VendorAnalytics } from './VendorAnalytics';
export { VendorMobileNavigation } from './VendorMobileNavigation';
export { default as VendorAccessibility } from './VendorAccessibility';