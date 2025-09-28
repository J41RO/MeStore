/**
 * Admin Vendors Pages Index
 *
 * Centralized export for all vendor management pages.
 * Provides easy imports and consistent API access.
 *
 * @version 1.0.0
 * @author UX Specialist AI
 */

// Vendor Management Pages
export { default as VendorsPage } from './VendorsPage';
export { default as VendorApplicationsPage } from './VendorApplicationsPage';
export { default as VendorProductsPage } from './VendorProductsPage';
export { default as VendorOrdersPage } from './VendorOrdersPage';
export { default as VendorCommissionsPage } from './VendorCommissionsPage';

/**
 * Page metadata for routing and navigation
 */
export const vendorsPagesMetadata = {
  vendors: {
    path: '/admin-secure-portal/vendors',
    title: 'Vendor Directory',
    description: 'View and manage all registered vendors',
    component: 'VendorsPage'
  },
  applications: {
    path: '/admin-secure-portal/vendor-applications',
    title: 'Vendor Applications',
    description: 'Review and approve new vendor registration applications',
    component: 'VendorApplicationsPage'
  },
  products: {
    path: '/admin-secure-portal/vendor-products',
    title: 'Product Catalog',
    description: 'Manage vendor products and inventory oversight',
    component: 'VendorProductsPage'
  },
  orders: {
    path: '/admin-secure-portal/vendor-orders',
    title: 'Vendor Orders',
    description: 'Monitor and manage vendor order fulfillment',
    component: 'VendorOrdersPage'
  },
  commissions: {
    path: '/admin-secure-portal/vendor-commissions',
    title: 'Commission Management',
    description: 'Manage vendor commissions and payout schedules',
    component: 'VendorCommissionsPage'
  }
};

/**
 * Required permissions for each page
 */
export const vendorsPagePermissions = {
  vendors: ['vendors.view'],
  applications: ['vendors.approve'],
  products: ['vendors.view', 'products.view'],
  orders: ['vendors.view', 'orders.view'],
  commissions: ['vendors.view', 'financial.view']
};