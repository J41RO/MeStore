// ~/frontend/src/pages/BuyerOrdersNew.tsx
// PRODUCTION_READY: Página mejorada de órdenes para compradores

import React from 'react';
import { OrderManagement } from '../components/orders';
import { useAuthStore } from '../stores/authStore';

const BuyerOrdersNew: React.FC = () => {
  const { user } = useAuthStore();

  return (
    <div className="h-full">
      <OrderManagement 
        userRole="buyer"
        buyerId={user?.id} // Filter orders for current buyer
      />
    </div>
  );
};

export default BuyerOrdersNew;