// frontend/src/components/orders/OrderStatusIndicator.tsx
// PRODUCTION_READY: Indicador visual de estados de órdenes

import React from 'react';
import {
  Clock,
  CheckCircle,
  Package,
  Truck,
  MapPin,
  XCircle,
  RotateCcw,
  AlertCircle
} from 'lucide-react';
import { OrderStatus, ORDER_STATUS_LABELS, ORDER_STATUS_COLORS } from '../../types/orders';

interface OrderStatusIndicatorProps {
  status: string;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
  showProgress?: boolean;
  className?: string;
}

export const OrderStatusIndicator: React.FC<OrderStatusIndicatorProps> = ({
  status,
  size = 'md',
  showIcon = true,
  showProgress = false,
  className = ''
}) => {
  const getStatusIcon = (status: string) => {
    const iconSize = size === 'sm' ? 'h-3 w-3' : size === 'md' ? 'h-4 w-4' : 'h-5 w-5';

    switch (status.toLowerCase()) {
      case 'pending':
        return <Clock className={`${iconSize} text-yellow-600`} />;
      case 'confirmed':
        return <CheckCircle className={`${iconSize} text-blue-600`} />;
      case 'processing':
        return <Package className={`${iconSize} text-purple-600`} />;
      case 'shipped':
        return <Truck className={`${iconSize} text-indigo-600`} />;
      case 'delivered':
        return <MapPin className={`${iconSize} text-green-600`} />;
      case 'cancelled':
        return <XCircle className={`${iconSize} text-red-600`} />;
      case 'refunded':
        return <RotateCcw className={`${iconSize} text-orange-600`} />;
      default:
        return <AlertCircle className={`${iconSize} text-gray-600`} />;
    }
  };

  const getProgressPercentage = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return 10;
      case 'confirmed':
        return 25;
      case 'processing':
        return 50;
      case 'shipped':
        return 75;
      case 'delivered':
        return 100;
      case 'cancelled':
      case 'refunded':
        return 0;
      default:
        return 0;
    }
  };

  const statusKey = status as keyof typeof ORDER_STATUS_COLORS;
  const colorClass = ORDER_STATUS_COLORS[statusKey] || 'bg-gray-100 text-gray-800';
  const label = ORDER_STATUS_LABELS[statusKey] || status;

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-0.5 text-xs',
    lg: 'px-3 py-1 text-sm'
  };

  return (
    <div className={`inline-flex flex-col ${className}`}>
      <div className="flex items-center space-x-1">
        {showIcon && getStatusIcon(status)}
        <span className={`inline-flex items-center rounded-full font-medium ${colorClass} ${sizeClasses[size]}`}>
          {label}
        </span>
      </div>

      {showProgress && (
        <div className="mt-2 w-full bg-gray-200 rounded-full h-1.5">
          <div
            className={`h-1.5 rounded-full transition-all duration-300 ${
              status.toLowerCase() === 'cancelled' || status.toLowerCase() === 'refunded'
                ? 'bg-red-400'
                : status.toLowerCase() === 'delivered'
                ? 'bg-green-500'
                : 'bg-blue-500'
            }`}
            style={{ width: `${getProgressPercentage(status)}%` }}
          />
        </div>
      )}
    </div>
  );
};

// Timeline de estados para mostrar progreso visual
interface OrderStatusTimelineProps {
  currentStatus: string;
  className?: string;
  compact?: boolean;
}

export const OrderStatusTimeline: React.FC<OrderStatusTimelineProps> = ({
  currentStatus,
  className = '',
  compact = false
}) => {
  const statusSteps = [
    { key: 'pending', label: 'Pendiente', icon: Clock },
    { key: 'confirmed', label: 'Confirmada', icon: CheckCircle },
    { key: 'processing', label: 'Procesando', icon: Package },
    { key: 'shipped', label: 'Enviada', icon: Truck },
    { key: 'delivered', label: 'Entregada', icon: MapPin }
  ];

  const getCurrentStepIndex = (status: string) => {
    return statusSteps.findIndex(step => step.key === status.toLowerCase());
  };

  const currentStepIndex = getCurrentStepIndex(currentStatus);
  const isCancelled = currentStatus.toLowerCase() === 'cancelled';
  const isRefunded = currentStatus.toLowerCase() === 'refunded';

  return (
    <div className={`${className}`}>
      {(isCancelled || isRefunded) ? (
        <div className="flex items-center justify-center py-4">
          <div className="flex items-center space-x-2 text-red-600">
            {isCancelled ? <XCircle className="h-5 w-5" /> : <RotateCcw className="h-5 w-5" />}
            <span className="font-medium">
              {isCancelled ? 'Orden Cancelada' : 'Orden Reembolsada'}
            </span>
          </div>
        </div>
      ) : (
        <div className={`flex items-center ${compact ? 'space-x-2' : 'space-x-4'}`}>
          {statusSteps.map((step, index) => {
            const isActive = index <= currentStepIndex;
            const isCurrent = index === currentStepIndex;
            const IconComponent = step.icon;

            return (
              <React.Fragment key={step.key}>
                <div className="flex flex-col items-center">
                  <div
                    className={`
                      rounded-full p-2 ${compact ? 'p-1.5' : 'p-2'}
                      ${isActive
                        ? isCurrent
                          ? 'bg-blue-600 text-white'
                          : 'bg-green-500 text-white'
                        : 'bg-gray-200 text-gray-400'
                      }
                    `}
                  >
                    <IconComponent className={compact ? 'h-3 w-3' : 'h-4 w-4'} />
                  </div>
                  {!compact && (
                    <span
                      className={`
                        mt-2 text-xs font-medium
                        ${isActive ? 'text-gray-900' : 'text-gray-500'}
                      `}
                    >
                      {step.label}
                    </span>
                  )}
                </div>

                {index < statusSteps.length - 1 && (
                  <div className={`flex-1 ${compact ? 'h-0.5' : 'h-1'} ${isActive ? 'bg-green-300' : 'bg-gray-200'} rounded`} />
                )}
              </React.Fragment>
            );
          })}
        </div>
      )}
    </div>
  );
};

// Componente para mostrar tiempo estimado
interface OrderEtaIndicatorProps {
  estimatedDays?: number;
  shippedAt?: string;
  className?: string;
}

export const OrderEtaIndicator: React.FC<OrderEtaIndicatorProps> = ({
  estimatedDays,
  shippedAt,
  className = ''
}) => {
  const calculateEta = () => {
    if (!estimatedDays) return null;

    const baseDate = shippedAt ? new Date(shippedAt) : new Date();
    const etaDate = new Date(baseDate);
    etaDate.setDate(etaDate.getDate() + estimatedDays);

    return etaDate;
  };

  const etaDate = calculateEta();

  if (!etaDate) return null;

  const isOverdue = etaDate < new Date();
  const daysUntilEta = Math.ceil((etaDate.getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <Clock className={`h-4 w-4 ${isOverdue ? 'text-red-500' : 'text-blue-500'}`} />
      <span className={`text-sm ${isOverdue ? 'text-red-600' : 'text-blue-600'}`}>
        {isOverdue ? (
          `Retrasado por ${Math.abs(daysUntilEta)} días`
        ) : daysUntilEta === 0 ? (
          'Entrega estimada hoy'
        ) : daysUntilEta === 1 ? (
          'Entrega estimada mañana'
        ) : (
          `Entrega en ${daysUntilEta} días`
        )}
      </span>
    </div>
  );
};

export default OrderStatusIndicator;