// ~/frontend/src/pages/VendorOrders.tsx  
// PRODUCTION_READY: Página de gestión de órdenes para vendedores

import React from 'react';
import { OrderManagement } from '../components/orders';
// import { useAuthStore } from '../stores/authStore'; // Future: for vendor-specific filtering

const VendorOrders: React.FC = () => {
  // const { user } = useAuthStore(); // Future: for vendor-specific filtering

  return (
    <div className="h-full">
      <OrderManagement 
        userRole="vendor"
        // Vendor can see all orders but with vendor-focused UI
      />
    </div>
  );
};

export default VendorOrders;