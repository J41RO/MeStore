import { useState, useEffect } from 'react';
import { Alert, AlertType, AlertSeverity, AlertCategory } from '../types/alerts.types';

export interface SystemAlert extends Alert {
  errorCode: string;
  errorType: 'api_error' | 'connectivity' | 'authentication' | 'database' | 'performance';
  affectedService: string;
  resolution?: string;
  estimatedDowntime?: number;
  usersAffected?: number;
}

interface UseSystemAlertsReturn {
  systemAlerts: SystemAlert[];
  isLoading: boolean;
  error: string | null;
  refreshSystemAlerts: () => Promise<void>;
  markAsRead: (alertId: string) => void;
  criticalCount: number;
}

// Mock data para errores críticos del sistema
const mockSystemAlerts: SystemAlert[] = [
  {
    id: 'sys-001',
    type: 'SYSTEM' as AlertType,
    severity: 'critical' as AlertSeverity,
    category: 'system' as AlertCategory,
    title: 'API Gateway Down - Servicio Principal',
    message: 'El API Gateway principal no responde, afectando todas las operaciones',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
    isRead: false,
    errorCode: 'API-GW-001',
    errorType: 'api_error',
    affectedService: 'API Gateway',
    usersAffected: 1250,
    estimatedDowntime: 120
  },
  {
    id: 'sys-002',
    type: 'SYSTEM' as AlertType,
    severity: 'critical' as AlertSeverity,
    category: 'security' as AlertCategory,
    title: 'Fallo de Autenticación - JWT Token Service',
    message: 'El servicio de tokens JWT presenta errores críticos de validación',
    timestamp: new Date(Date.now() - 45 * 60 * 1000),
    isRead: false,
    errorCode: 'AUTH-JWT-002',
    errorType: 'authentication',
    affectedService: 'Authentication Service',
    resolution: 'Reiniciar servicio de tokens',
    usersAffected: 800
  },
  {
    id: 'sys-003',
    type: 'SYSTEM' as AlertType,
    severity: 'high' as AlertSeverity,
    category: 'system' as AlertCategory,
    title: 'Base de Datos - Conexiones Agotadas',
    message: 'Pool de conexiones a la base de datos principal alcanzó el límite',
    timestamp: new Date(Date.now() - 30 * 60 * 1000),
    isRead: false,
    errorCode: 'DB-CONN-003',
    errorType: 'database',
    affectedService: 'PostgreSQL Main',
    resolution: 'Escalar pool de conexiones',
    usersAffected: 500
  },
  {
    id: 'sys-004',
    type: 'SYSTEM' as AlertType,
    severity: 'medium' as AlertSeverity,
    category: 'performance' as AlertCategory,
    title: 'Alto Uso de CPU - Servidor de Aplicaciones',
    message: 'Uso de CPU sostenido al 85% en el servidor principal',
    timestamp: new Date(Date.now() - 15 * 60 * 1000),
    isRead: true,
    errorCode: 'PERF-CPU-001',
    errorType: 'performance',
    affectedService: 'Application Server',
    usersAffected: 200
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
    alert => alert.severity === 'critical'
  ).length;

  return {
    systemAlerts,
    isLoading,
    error,
    refreshSystemAlerts,
    markAsRead,
    criticalCount
  };
};

export default useSystemAlerts;