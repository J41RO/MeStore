// ~/src/hooks/useVendorAlerts.ts
// ---------------------------------------------------------------------------------------------
// MESTORE - Hook para gestión de alertas de vendedores - Completamente corregido
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------

import { useState, useEffect } from 'react';
import { VendorAlert, AlertType, AlertSeverity } from '../types/alerts.types';

interface UseVendorAlertsReturn {
  vendorAlerts: VendorAlert[];
  isLoading: boolean;
  error: string | null;
  refreshVendorAlerts: () => Promise<void>;
  markAsRead: (alertId: string) => void;
  markVendorAlertAsRead: (alertId: string) => void;
  criticalCount: number;
}

// Mock data para vendedores con tareas pendientes
const mockVendorAlerts: VendorAlert[] = [
  {
    id: 'vendor-001',
    type: AlertType.VENDOR,
    severity: AlertSeverity.CRITICAL,
    category: AlertType.PAYMENT_PENDING,
    vendorId: 'vnd-001',
    vendorName: 'Tech Solutions Corp',
    issueDescription: 'El vendedor tiene un pago pendiente de $2,500 desde hace 15 días',
    timestamp: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000),
    isRead: false,
    actionRequired: true
  },
  {
    id: 'vendor-002',
    type: AlertType.VENDOR,
    severity: AlertSeverity.HIGH,
    category: AlertType.DOCUMENTS_MISSING,
    vendorId: 'vnd-002',
    vendorName: 'Digital Commerce Ltd',
    issueDescription: 'Faltan documentos fiscales requeridos para completar el registro',
    timestamp: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000),
    isRead: false,
    actionRequired: true
  },
  {
    id: 'vendor-003',
    type: AlertType.VENDOR,
    severity: AlertSeverity.CRITICAL,
    category: AlertType.ACTIVATION_REQUIRED,
    vendorId: 'vnd-003',
    vendorName: 'Mobile Accessories Pro',
    issueDescription: 'La cuenta del vendedor requiere activación manual urgente',
    timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
    isRead: false,
    actionRequired: true
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
    alert => alert.severity === AlertSeverity.CRITICAL
  ).length;

  return {
    vendorAlerts,
    isLoading,
    error,
    refreshVendorAlerts,
    markAsRead,
    markVendorAlertAsRead: markAsRead,
    criticalCount
  };
};

export default useVendorAlerts;