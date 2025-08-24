import React, { useState } from 'react';
import { Play, Square, Download, RotateCcw } from 'lucide-react';
import { ScanMode, ScannedItem, PickingSession } from '../../types/barcode.types';
import { BarcodeScanner } from './BarcodeScanner';
import { PickingList } from './PickingList';
import { useBarcodeScanner } from '../../hooks/warehouse/useBarcodeScanner';

interface BarcodeScannerWithPickingProps {
  mode?: ScanMode;
  className?: string;
}

export const BarcodeScannerWithPicking: React.FC<BarcodeScannerWithPickingProps> = ({
  mode = ScanMode.MANUAL,
  className = ''
}) => {
  const {
    currentSession,
    scannedItems,
    startPickingSession,
    completePickingSession,
    removeScannedItem,
    resetScanner,
    stats
  } = useBarcodeScanner(mode);

  const [completedSessions, setCompletedSessions] = useState<PickingSession[]>([]);

  const handleStartSession = () => {
    const session = startPickingSession({
      operator: 'Usuario Actual',
      location: mode === ScanMode.LOCATION_BASED ? 'WAREHOUSE_A' : undefined
    });
    console.log('Nueva sesión iniciada:', session);
  };

  const handleCompleteSession = () => {
    const session = completePickingSession();
    if (session) {
      setCompletedSessions(prev => [...prev, session]);
      console.log('Sesión completada:', session);
    }
  };

  const handleScanItem = (item: ScannedItem) => {
    console.log('Item escaneado:', item);
  };

  const handleScanError = (error: string) => {
    console.error('Error de escaneo:', error);
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header con controles */}
      <div className="bg-white p-4 border border-gray-200 rounded-lg">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">
            Sistema de Picking con Scanner
          </h2>
          
          <div className="flex items-center gap-2">
            {currentSession ? (
              <>
                <button
                  onClick={handleCompleteSession}
                  className="flex items-center gap-2 px-3 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 transition-colors"
                >
                  <Square size={16} />
                  Finalizar
                </button>
                
                <button
                  onClick={resetScanner}
                  className="flex items-center gap-2 px-3 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
                >
                  <RotateCcw size={16} />
                  Reset
                </button>
              </>
            ) : (
              <button
                onClick={handleStartSession}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                <Play size={16} />
                Iniciar Picking
              </button>
            )}
          </div>
        </div>

        {/* Indicadores de estado */}
        <div className="grid grid-cols-4 gap-4 text-center">
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              {completedSessions.length}
            </div>
            <div className="text-xs text-blue-700">Sesiones</div>
          </div>
          
          <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {stats.successfulScans}
            </div>
            <div className="text-xs text-green-700">Exitosos</div>
          </div>
          
          <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
            <div className="text-2xl font-bold text-amber-600">
              {scannedItems.length}
            </div>
            <div className="text-xs text-amber-700">Items</div>
          </div>
          
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
            <div className="text-2xl font-bold text-red-600">
              {stats.errorScans}
            </div>
            <div className="text-xs text-red-700">Errores</div>
          </div>
        </div>
      </div>

      {/* Layout principal: Scanner + Lista */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <BarcodeScanner
            mode={mode}
            onScan={handleScanItem}
            onError={handleScanError}
            placeholder={currentSession ? 'Escanea código de producto...' : 'Inicia una sesión para escanear'}
          />
        </div>

        <div>
          <PickingList
            items={scannedItems}
            session={currentSession}
            onRemoveItem={removeScannedItem}
            onCompleteSession={handleCompleteSession}
          />
        </div>
      </div>

      {/* Modo de operación */}
      <div className="text-center text-sm text-gray-500">
        Modo: {mode.replace('_', ' ').toUpperCase()}
        {currentSession && (
          <span className="ml-4">
            Sesión: {currentSession.id}
          </span>
        )}
      </div>
    </div>
  );
};

export default BarcodeScannerWithPicking;