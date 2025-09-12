// ~/frontend/src/pages/admin/OrdersManagement.tsx
// PRODUCTION_READY: Página de gestión de órdenes para administradores

import React from 'react';
import { OrderManagement } from '../../components/orders';
// import { useAuthStore } from '../../stores/authStore'; // Future: for admin-specific features

const OrdersManagement: React.FC = () => {
  // const { user } = useAuthStore(); // Future: for admin-specific features

  return (
    <div className="h-full">
      <OrderManagement 
        userRole="admin"
        // Admin can see all orders, no buyer filter
      />
    </div>
  );
};

export default OrdersManagement;