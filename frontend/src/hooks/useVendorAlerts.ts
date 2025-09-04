import { useState, useEffect } from 'react';
import { Alert, AlertType, AlertSeverity, AlertCategory } from '../types/alerts.types';

export interface VendorAlert extends Alert {
  vendorId: string;
  vendorName: string;
  vendorEmail: string;
  pendingAction: 'payment' | 'documents' | 'activation' | 'verification';
  pendingAmount?: number;
  documentType?: string;
  daysOverdue: number;
}

interface UseVendorAlertsReturn {
  vendorAlerts: VendorAlert[];
  isLoading: boolean;
  error: string | null;
  refreshVendorAlerts: () => Promise<void>;
  markAsRead: (alertId: string) => void;
  criticalCount: number;
}

// Mock data para vendedores con tareas pendientes
const mockVendorAlerts: VendorAlert[] = [
  {
    id: 'vendor-001',
    type: 'VENDOR' as AlertType,
    severity: 'critical' as AlertSeverity,
    category: 'financial' as AlertCategory,
    title: 'Pago Pendiente - Vendor Premium',
    message: 'El vendedor tiene un pago pendiente de $2,500 desde hace 15 días',
    timestamp: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000),
    isRead: false,
    vendorId: 'vnd-001',
    vendorName: 'Tech Solutions Corp',
    vendorEmail: 'admin@techsolutions.com',
    pendingAction: 'payment',
    pendingAmount: 2500,
    daysOverdue: 15
  },
  {
    id: 'vendor-002',
    type: 'VENDOR' as AlertType,
    severity: 'high' as AlertSeverity,
    category: 'compliance' as AlertCategory,
    title: 'Documentos Faltantes - Registro Fiscal',
    message: 'Faltan documentos fiscales requeridos para completar el registro',
    timestamp: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000),
    isRead: false,
    vendorId: 'vnd-002',
    vendorName: 'Digital Commerce Ltd',
    vendorEmail: 'docs@digitalcommerce.com',
    pendingAction: 'documents',
    documentType: 'Tax Registration',
    daysOverdue: 8
  },
  {
    id: 'vendor-003',
    type: 'VENDOR' as AlertType,
    severity: 'critical' as AlertSeverity,
    category: 'system' as AlertCategory,
    title: 'Activación Requerida - Cuenta Suspendida',
    message: 'La cuenta del vendedor requiere activación manual urgente',
    timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
    isRead: false,
    vendorId: 'vnd-003',
    vendorName: 'Mobile Accessories Pro',
    vendorEmail: 'support@mobileacc.com',
    pendingAction: 'activation',
    daysOverdue: 3
  }
];

export const useVendorAlerts = (): UseVendorAlertsReturn => {
  const [vendorAlerts, setVendorAlerts] = useState<VendorAlert[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchVendorAlerts = async (): Promise<void> => {
    try {
      setIsLoading(true);
      setError(null);
      await new Promise(resolve => setTimeout(resolve, 800));
      setVendorAlerts(mockVendorAlerts);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error fetching vendor alerts');
    } finally {
      setIsLoading(false);
    }
  };

  const refreshVendorAlerts = async (): Promise<void> => {
    await fetchVendorAlerts();
  };

  const markAsRead = (alertId: string): void => {
    setVendorAlerts(prevAlerts =>
      prevAlerts.map(alert =>
        alert.id === alertId ? { ...alert, isRead: true } : alert
      )
    );
  };

  useEffect(() => {
    fetchVendorAlerts();
  }, []);

  const criticalCount = vendorAlerts.filter(
  ).length;

  return {
    vendorAlerts,
    isLoading,
    error,
    refreshVendorAlerts,
    markAsRead,
    criticalCount
  };
};

export default useVendorAlerts;