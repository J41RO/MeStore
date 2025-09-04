// ~/src/hooks/useSystemAlerts.ts
// ---------------------------------------------------------------------------------------------
// MESTORE - Hook para gestión de alertas del sistema - Completamente corregido
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------

import { useState, useEffect } from 'react';
import { SystemAlert, AlertType, AlertSeverity } from '../types/alerts.types';

interface UseSystemAlertsReturn {
  systemAlerts: SystemAlert[];
  isLoading: boolean;
  error: string | null;
  refreshSystemAlerts: () => Promise<void>;
  markAsRead: (alertId: string) => void;
  markSystemAlertAsRead: (alertId: string) => void;
  criticalCount: number;
}

// Mock data para errores críticos del sistema
const mockSystemAlerts: SystemAlert[] = [
  {
    id: 'sys-001',
    type: AlertType.SYSTEM,
    severity: AlertSeverity.CRITICAL,
    category: AlertType.API_ERROR,
    systemComponent: 'API Gateway',
    issueDescription: 'El API Gateway principal no responde, afectando todas las operaciones',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
    isRead: false,
    actionRequired: true,
    errorCode: 'API-GW-001'
  },
  {
    id: 'sys-002',
    type: AlertType.SYSTEM,
    severity: AlertSeverity.CRITICAL,
    category: AlertType.AUTHENTICATION_ERROR,
    systemComponent: 'Authentication Service',
    issueDescription: 'El servicio de tokens JWT presenta errores críticos de validación',
    timestamp: new Date(Date.now() - 45 * 60 * 1000),
    isRead: false,
    actionRequired: true,
    errorCode: 'AUTH-JWT-002'
  },
  {
    id: 'sys-003',
    type: AlertType.SYSTEM,
    severity: AlertSeverity.HIGH,
    category: AlertType.DATABASE_ERROR,
    systemComponent: 'PostgreSQL Main',
    issueDescription: 'Pool de conexiones a la base de datos principal alcanzó el límite',
    timestamp: new Date(Date.now() - 30 * 60 * 1000),
    isRead: false,
    actionRequired: true,
    errorCode: 'DB-CONN-003'
  },
  {
    id: 'sys-004',
    type: AlertType.SYSTEM,
    severity: AlertSeverity.MEDIUM,
    category: AlertType.PERFORMANCE_ISSUE,
    systemComponent: 'Application Server',
    issueDescription: 'Uso de CPU sostenido al 85% en el servidor principal',
    timestamp: new Date(Date.now() - 15 * 60 * 1000),
    isRead: true,
    actionRequired: false,
    errorCode: 'PERF-CPU-001'
  }
];

export const useSystemAlerts = (): UseSystemAlertsReturn => {
  const [systemAlerts, setSystemAlerts] = useState<SystemAlert[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSystemAlerts = async (): Promise<void> => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Simular llamada a API de monitoreo
      await new Promise(resolve => setTimeout(resolve, 600));
      
      // En producción, aquí conectaríamos con sistemas de monitoreo
      // const response = await fetch('/api/system-alerts');
      // const data = await response.json();
      
      setSystemAlerts(mockSystemAlerts);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error fetching system alerts');
      console.error('Error fetching system alerts:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const refreshSystemAlerts = async (): Promise<void> => {
    await fetchSystemAlerts();
  };

  const markAsRead = (alertId: string): void => {
    setSystemAlerts(prevAlerts =>
      prevAlerts.map(alert =>
        alert.id === alertId ? { ...alert, isRead: true } : alert
      )
    );
  };

  useEffect(() => {
    fetchSystemAlerts();
    
    // Auto-refresh cada 30 segundos para errores del sistema
    const interval = setInterval(fetchSystemAlerts, 30000);
    
    return () => clearInterval(interval);
  }, []);

  // Calcular alertas críticas no leídas
  const criticalCount = systemAlerts.filter(
    alert => alert.severity === AlertSeverity.CRITICAL
  ).length;

  return {
    systemAlerts,
    isLoading,
    error,
    refreshSystemAlerts,
    markAsRead,
    markSystemAlertAsRead: markAsRead,
    criticalCount
  };
};

export default useSystemAlerts;