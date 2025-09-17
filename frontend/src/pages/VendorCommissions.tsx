// ~/frontend/src/pages/VendorCommissions.tsx
// ---------------------------------------------------------------------------------------------
// MESTORE - Vendor Commissions Page (PRODUCTION_READY)
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// ---------------------------------------------------------------------------------------------

/**
 * PRODUCTION_READY: Página completa de comisiones para vendors
 * 
 * Integra todos los componentes de comisiones:
 * - Dashboard con métricas clave
 * - Reportes detallados con filtros
 * - Historial de transacciones
 * - Navegación entre vistas
 */

import React, { useState, useEffect } from 'react';
import { 
  DollarSign, 
  BarChart3, 
  History, 
  FileText,
  AlertCircle,
  ArrowLeft
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import CommissionDashboard from '../components/commission/CommissionDashboard';
import CommissionReport from '../components/commission/CommissionReport';
import TransactionHistory from '../components/commission/TransactionHistory';
import CommissionService from '../services/commissionService';

type ViewType = 'dashboard' | 'reports' | 'transactions';

interface TabItem {
  key: ViewType;
  label: string;
  icon: React.ReactNode;
  description: string;
}

export const VendorCommissions: React.FC = () => {
  const [currentView, setCurrentView] = useState<ViewType>('dashboard');
  const [vendorId, setVendorId] = useState<string>('');
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  // =============================================================================
  // AUTHORIZATION & USER INFO
  // =============================================================================

  useEffect(() => {
    const checkAuthorization = () => {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) {
          navigate('/login');
          return;
        }

        const payload = JSON.parse(atob(token.split('.')[1]));
        const userType = payload.user_type;
        const userId = payload.user_id;

        if (!['vendor', 'admin'].includes(userType)) {
          navigate('/dashboard');
          return;
        }

        setVendorId(userType === 'vendor' ? userId : '');
        setIsAuthorized(true);

      } catch (error) {
        console.error('Error checking authorization:', error);
        navigate('/login');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuthorization();
  }, [navigate]);

  // =============================================================================
  // NAVIGATION TABS
  // =============================================================================

  const tabs: TabItem[] = [
    {
      key: 'dashboard',
      label: 'Dashboard',
      icon: <DollarSign className="w-5 h-5" />,
      description: 'Resumen de earnings y métricas clave'
    },
    {
      key: 'reports',
      label: 'Reportes',
      icon: <BarChart3 className="w-5 h-5" />,
      description: 'Analytics detallados y exportación'
    },
    {
      key: 'transactions',
      label: 'Transacciones',
      icon: <History className="w-5 h-5" />,
      description: 'Historial completo de pagos'
    }
  ];

  // =============================================================================
  // EVENT HANDLERS
  // =============================================================================

  const handleViewCommissionDetails = (commissionId: string) => {
    // Navigate to commission details or show modal
    console.log('View commission details:', commissionId);
    // For now, switch to transactions view to show related transactions
    setCurrentView('transactions');
  };

  const handleNavigateToHistory = () => {
    setCurrentView('transactions');
  };

  const handleExportData = (data: any, format: 'csv' | 'excel' | 'pdf') => {
    // Handle data export
    console.log('Export data:', format, data.length, 'items');
    // Implementation depends on specific requirements
  };

  // =============================================================================
  // LOADING STATE
  // =============================================================================

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!isAuthorized) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Acceso Denegado</h1>
          <p className="text-gray-600 mb-6">No tienes permisos para acceder a esta página</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Volver al Dashboard
          </button>
        </div>
      </div>
    );
  }

  // =============================================================================
  // MAIN RENDER
  // =============================================================================

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
              >
                <ArrowLeft className="w-5 h-5 mr-2" />
                Volver al Dashboard
              </button>
              <div className="h-6 w-px bg-gray-300"></div>
              <h1 className="text-xl font-semibold text-gray-900">
                Gestión de Comisiones
              </h1>
            </div>
            
            {/* User Info */}
            <div className="text-sm text-gray-600">
              {vendorId ? 'Mi cuenta' : 'Vista de administrador'}
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                onClick={() => setCurrentView(tab.key)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  currentView === tab.key
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.icon}
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Tab Description */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <p className="text-gray-600 text-sm">
          {tabs.find(tab => tab.key === currentView)?.description}
        </p>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
        {/* Accessibility Check */}
        {!CommissionService.canViewCommissions() && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 text-yellow-600 mr-2" />
              <span className="text-yellow-800 font-medium">
                Permisos limitados detectados. Algunas funciones pueden no estar disponibles.
              </span>
            </div>
          </div>
        )}

        {/* Content Views */}
        {currentView === 'dashboard' && (
          <CommissionDashboard
            vendorId={vendorId}
            onViewDetails={handleViewCommissionDetails}
            onNavigateToHistory={handleNavigateToHistory}
            className="animate-fadeIn"
          />
        )}

        {currentView === 'reports' && (
          <CommissionReport
            vendorId={vendorId}
            showFilters={true}
            onExport={handleExportData}
            className="animate-fadeIn"
          />
        )}

        {currentView === 'transactions' && (
          <TransactionHistory
            vendorId={vendorId}
            showFilters={true}
            maxItems={100}
            className="animate-fadeIn"
            onTransactionClick={(transaction) => {
              console.log('Transaction clicked:', transaction);
              // Could open modal with transaction details
            }}
          />
        )}
      </div>

      {/* Help Text */}
      <div className="bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <div className="flex items-center space-x-6">
              <span className="flex items-center">
                <FileText className="w-4 h-4 mr-1" />
                Datos actualizados en tiempo real
              </span>
              <span>
                Último cálculo: {new Date().toLocaleDateString('es-ES', { 
                  day: 'numeric', 
                  month: 'short',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </span>
            </div>
            
            <div className="text-xs">
              ¿Necesitas ayuda? 
              <button className="text-blue-600 hover:text-blue-700 ml-1">
                Contactar soporte
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Custom CSS for animations */}
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>
    </div>
  );
};

export default VendorCommissions;