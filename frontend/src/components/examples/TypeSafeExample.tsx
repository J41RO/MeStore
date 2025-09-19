/**
 * TypeSafe Example Component
 * Demonstrates consistent EntityId usage in React components
 */

import React, { useState, useEffect } from 'react';
import type {
  EntityId,
  Product,
  Order,
  User,
  ProductCardProps,
  OrderCardProps,
  OrderStatus,
  PaymentStatus,
} from '../../types';
import {
  useProducts,
  useOrders,
  useProductStore,
  useOrderStore,
  useAuthStore,
} from '../../stores';

// ========================================
// EXAMPLE: PRODUCT CARD WITH TYPE-SAFE IDS
// ========================================

/**
 * ProductCard - Example component with consistent EntityId props
 */
const ProductCard: React.FC<ProductCardProps> = ({
  product,
  showVendor = false,
  showActions = false,
  onClick,
  onEdit,
  onDelete,
  className = '',
}) => {
  const handleProductClick = () => {
    onClick?.(product);
  };

  const handleEditClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onEdit?.(product);
  };

  const handleDeleteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDelete?.(product);
  };

  return (
    <div
      className={`border rounded-lg p-4 cursor-pointer hover:shadow-md transition-shadow ${className}`}
      onClick={handleProductClick}
    >
      {/* Product Image */}
      {product.main_image_url && (
        <img
          src={product.main_image_url}
          alt={product.name}
          className="w-full h-48 object-cover rounded-md mb-4"
        />
      )}

      {/* Product Info */}
      <h3 className="text-lg font-semibold mb-2">{product.name}</h3>
      <p className="text-gray-600 text-sm mb-2 line-clamp-2">{product.description}</p>

      {/* Price and Stock */}
      <div className="flex justify-between items-center mb-2">
        <span className="text-xl font-bold text-green-600">
          ${product.price.toFixed(2)}
        </span>
        <span className={`text-sm ${product.stock > 0 ? 'text-green-600' : 'text-red-600'}`}>
          {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
        </span>
      </div>

      {/* Vendor Info */}
      {showVendor && (
        <div className="text-sm text-gray-500 mb-2">
          Vendor ID: {product.vendor_id}
        </div>
      )}

      {/* Product Metadata */}
      <div className="text-xs text-gray-400 mb-3">
        ID: {product.id} | SKU: {product.sku || 'N/A'}
      </div>

      {/* Actions */}
      {showActions && (
        <div className="flex gap-2">
          <button
            onClick={handleEditClick}
            className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
          >
            Edit
          </button>
          <button
            onClick={handleDeleteClick}
            className="px-3 py-1 bg-red-500 text-white text-sm rounded hover:bg-red-600"
          >
            Delete
          </button>
        </div>
      )}
    </div>
  );
};

// ========================================
// EXAMPLE: ORDER CARD WITH TYPE-SAFE IDS
// ========================================

/**
 * OrderCard - Example component with consistent EntityId props
 */
const OrderCard: React.FC<OrderCardProps> = ({
  order,
  showCustomer = false,
  showActions = false,
  onClick,
  onStatusUpdate,
  onCancel,
  className = '',
}) => {
  const handleOrderClick = () => {
    onClick?.(order);
  };

  const handleStatusUpdate = (newStatus: OrderStatus) => {
    onStatusUpdate?.(order, newStatus);
  };

  const handleCancel = (e: React.MouseEvent) => {
    e.stopPropagation();
    onCancel?.(order);
  };

  const getStatusColor = (status: OrderStatus) => {
    switch (status) {
      case OrderStatus.PENDING:
        return 'bg-yellow-100 text-yellow-800';
      case OrderStatus.CONFIRMED:
        return 'bg-blue-100 text-blue-800';
      case OrderStatus.PROCESSING:
        return 'bg-orange-100 text-orange-800';
      case OrderStatus.SHIPPED:
        return 'bg-purple-100 text-purple-800';
      case OrderStatus.DELIVERED:
        return 'bg-green-100 text-green-800';
      case OrderStatus.CANCELLED:
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div
      className={`border rounded-lg p-4 cursor-pointer hover:shadow-md transition-shadow ${className}`}
      onClick={handleOrderClick}
    >
      {/* Order Header */}
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="text-lg font-semibold">Order #{order.order_number}</h3>
          <p className="text-sm text-gray-500">ID: {order.id}</p>
        </div>
        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(order.status)}`}>
          {order.status}
        </span>
      </div>

      {/* Customer Info */}
      {showCustomer && (
        <div className="mb-3">
          <p className="text-sm">
            <span className="font-semibold">Customer:</span> {order.customer_name}
          </p>
          <p className="text-sm text-gray-600">{order.customer_email}</p>
        </div>
      )}

      {/* Order Details */}
      <div className="grid grid-cols-2 gap-4 mb-3">
        <div>
          <p className="text-sm text-gray-600">Total Amount</p>
          <p className="font-semibold">${order.total_amount.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Items</p>
          <p className="font-semibold">{order.items.length} items</p>
        </div>
      </div>

      {/* Payment Status */}
      <div className="mb-3">
        <span className="text-sm text-gray-600">Payment: </span>
        <span className={`text-sm font-semibold ${
          order.payment_status === PaymentStatus.COMPLETED ? 'text-green-600' : 'text-orange-600'
        }`}>
          {order.payment_status}
        </span>
      </div>

      {/* Tracking Number */}
      {order.tracking_number && (
        <div className="mb-3">
          <p className="text-sm text-gray-600">
            Tracking: <span className="font-mono">{order.tracking_number}</span>
          </p>
        </div>
      )}

      {/* Order Metadata */}
      <div className="text-xs text-gray-400 mb-3">
        Created: {new Date(order.created_at).toLocaleDateString()}
        {order.updated_at !== order.created_at && (
          <> | Updated: {new Date(order.updated_at).toLocaleDateString()}</>
        )}
      </div>

      {/* Actions */}
      {showActions && (
        <div className="flex gap-2">
          <select
            onChange={(e) => handleStatusUpdate(e.target.value as OrderStatus)}
            className="px-2 py-1 border rounded text-sm"
            value={order.status}
            onClick={(e) => e.stopPropagation()}
          >
            {Object.values(OrderStatus).map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>

          {order.status !== OrderStatus.CANCELLED && order.status !== OrderStatus.DELIVERED && (
            <button
              onClick={handleCancel}
              className="px-3 py-1 bg-red-500 text-white text-sm rounded hover:bg-red-600"
            >
              Cancel
            </button>
          )}
        </div>
      )}
    </div>
  );
};

// ========================================
// EXAMPLE: TYPE-SAFE STORE USAGE
// ========================================

/**
 * TypeSafeStoreExample - Demonstrates type-safe store usage with EntityId
 */
const TypeSafeStoreExample: React.FC = () => {
  const [selectedProductId, setSelectedProductId] = useState<EntityId | null>(null);
  const [selectedOrderId, setSelectedOrderId] = useState<EntityId | null>(null);

  // Type-safe store hooks
  const products = useProducts();
  const orders = useOrders();
  const { fetchProducts, selectProduct, deleteProduct } = useProductStore();
  const { fetchOrders, updateOrderStatus, cancelOrder } = useOrderStore();
  const { user, isAuthenticated } = useAuthStore();

  // Load data on mount
  useEffect(() => {
    if (isAuthenticated) {
      fetchProducts();
      fetchOrders();
    }
  }, [isAuthenticated, fetchProducts, fetchOrders]);

  // Type-safe event handlers
  const handleProductClick = (product: Product) => {
    setSelectedProductId(product.id);
    selectProduct(product);
  };

  const handleProductEdit = (product: Product) => {
    console.log('Edit product:', product.id);
    // Navigate to edit page with type-safe ID
  };

  const handleProductDelete = async (product: Product) => {
    if (window.confirm(`Delete product ${product.name}?`)) {
      await deleteProduct(product.id);
    }
  };

  const handleOrderClick = (order: Order) => {
    setSelectedOrderId(order.id);
  };

  const handleOrderStatusUpdate = async (order: Order, newStatus: OrderStatus) => {
    await updateOrderStatus(order.id, newStatus);
  };

  const handleOrderCancel = async (order: Order) => {
    if (window.confirm(`Cancel order ${order.order_number}?`)) {
      await cancelOrder(order.id, 'Cancelled by user');
    }
  };

  // Type-safe ID comparisons
  const isProductSelected = (productId: EntityId) => productId === selectedProductId;
  const isOrderSelected = (orderId: EntityId) => orderId === selectedOrderId;

  if (!isAuthenticated) {
    return (
      <div className="p-8 text-center">
        <h2 className="text-2xl font-bold mb-4">Authentication Required</h2>
        <p>Please log in to view products and orders.</p>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">TypeSafe Component Examples</h1>

      {/* User Info */}
      {user && (
        <div className="mb-6 p-4 bg-blue-50 rounded-lg">
          <h2 className="text-lg font-semibold mb-2">Current User</h2>
          <p><strong>ID:</strong> {user.id}</p>
          <p><strong>Email:</strong> {user.email}</p>
          <p><strong>Type:</strong> {user.user_type}</p>
        </div>
      )}

      {/* Products Section */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-4">Products</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {products.slice(0, 6).map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              showVendor={user?.user_type === 'ADMIN'}
              showActions={user?.user_type === 'VENDEDOR' || user?.user_type === 'ADMIN'}
              onClick={handleProductClick}
              onEdit={handleProductEdit}
              onDelete={handleProductDelete}
              className={isProductSelected(product.id) ? 'ring-2 ring-blue-500' : ''}
            />
          ))}
        </div>
        {products.length === 0 && (
          <p className="text-gray-500 text-center py-8">No products found.</p>
        )}
      </section>

      {/* Orders Section */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-4">Orders</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {orders.slice(0, 4).map((order) => (
            <OrderCard
              key={order.id}
              order={order}
              showCustomer={user?.user_type === 'VENDEDOR' || user?.user_type === 'ADMIN'}
              showActions={user?.user_type === 'VENDEDOR' || user?.user_type === 'ADMIN'}
              onClick={handleOrderClick}
              onStatusUpdate={handleOrderStatusUpdate}
              onCancel={handleOrderCancel}
              className={isOrderSelected(order.id) ? 'ring-2 ring-green-500' : ''}
            />
          ))}
        </div>
        {orders.length === 0 && (
          <p className="text-gray-500 text-center py-8">No orders found.</p>
        )}
      </section>

      {/* Type Safety Demonstration */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-4">Type Safety Examples</h2>
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="font-semibold mb-2">Selected IDs (Type-Safe)</h3>
          <p><strong>Product ID:</strong> {selectedProductId || 'None'}</p>
          <p><strong>Order ID:</strong> {selectedOrderId || 'None'}</p>

          <div className="mt-4">
            <h4 className="font-semibold mb-2">Type Demonstrations:</h4>
            <code className="block bg-white p-2 rounded text-sm">
              {`// All IDs are consistently typed as EntityId (string)
const productId: EntityId = "${selectedProductId || 'uuid-string'}";
const orderId: EntityId = "${selectedOrderId || 'uuid-string'}";
const userId: EntityId = "${user?.id || 'uuid-string'}";

// Type-safe comparisons
const isSameProduct = productId === selectedProductId;
const isSameOrder = orderId === selectedOrderId;`}
            </code>
          </div>
        </div>
      </section>
    </div>
  );
};

// ========================================
// EXPORTS
// ========================================

export default TypeSafeStoreExample;
export { ProductCard, OrderCard };