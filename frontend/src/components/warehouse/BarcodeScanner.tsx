import React, { useState } from 'react';
import { Camera, Scan, Check, AlertCircle } from 'lucide-react';
import {
  ScanMode,
  ScanStatus,
  BarcodeScannerProps,
} from '../../types/barcode.types';
import { useBarcodeScanner } from '../../hooks/warehouse/useBarcodeScanner';

export const BarcodeScanner: React.FC<BarcodeScannerProps> = ({
  mode = ScanMode.MANUAL,
  onScan,
  onError,
  className = '',
  disabled = false,
  placeholder = 'Ingresa SKU o código...',
  autoFocus = true,
}) => {
  // Usar hook personalizado para manejo de estado y lógica
  const {
    status: scanStatus,
    isScanning,
    lastScan,
    errors,
    scanItem,
    stats,
  } = useBarcodeScanner(mode, {
    simulationDelay: 1500,
    soundEnabled: true,
    vibrationEnabled: true,
  });

  const [inputValue, setInputValue] = useState('');

  // Simulación de cámara activa
  const [cameraActive] = useState(false);

  // Efectos visuales de escaneo
  const getScannerStyle = () => {
    const baseStyle =
      'relative border-2 rounded-lg p-4 transition-all duration-300';

    switch (scanStatus) {
      case ScanStatus.SCANNING:
        return `${baseStyle} border-blue-500 bg-blue-50 shadow-lg animate-pulse`;
      case ScanStatus.SUCCESS:
        return `${baseStyle} border-green-500 bg-green-50 shadow-lg`;
      case ScanStatus.ERROR:
        return `${baseStyle} border-red-500 bg-red-50 shadow-lg`;
      default:
        return `${baseStyle} border-gray-300 bg-white hover:border-blue-300`;
    }
  };

  const getStatusIcon = () => {
    switch (scanStatus) {
      case ScanStatus.SCANNING:
        return <Scan className='animate-spin text-blue-600' size={20} />;
      case ScanStatus.SUCCESS:
        return <Check className='text-green-600' size={20} />;
      case ScanStatus.ERROR:
        return <AlertCircle className='text-red-600' size={20} />;
      default:
        return <Camera className='text-gray-600' size={20} />;
    }
  };

  const handleManualInput = (value: string) => {
    if (disabled) return;
    setInputValue(value);

    // Auto-submit en modo manual si termina con Enter
    if (value.includes('\n') || value.length >= 13) {
      const cleanValue = value.replace('\n', '').trim();
      if (cleanValue) {
        simulateScanning(cleanValue);
      }
    }
  };

  const simulateScanning = async (sku: string) => {
    try {
      const scannedItem = await scanItem(sku.trim());

      if (scannedItem) {
        onScan(scannedItem);
        setInputValue(''); // Limpiar input después de escaneo exitoso
      } else {
        // Manejar errores desde el hook
        onError?.(errors.join(', ') || 'Error de escaneo');
      }
    } catch (error) {
      onError?.(error instanceof Error ? error.message : 'Error de escaneo');
    }
  };

  const toggleCamera = () => {
    if (disabled) return;
  };

  return (
    <div className={`${getScannerStyle()} ${className}`}>
      {/* Header del Scanner */}
      <div className='flex items-center justify-between mb-4'>
        <div className='flex items-center gap-2'>
          {getStatusIcon()}
          <h3 className='font-medium text-gray-900'>Scanner de Códigos</h3>
        </div>
        <button
          onClick={toggleCamera}
          disabled={disabled || isScanning}
          className={`p-2 rounded-lg transition-colors ${
            cameraActive
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
          }`}
        >
          <Camera size={16} />
        </button>
      </div>
      {/* Área de simulación de cámara */}
      {cameraActive && (
        <div className='mb-4 aspect-video bg-gray-900 rounded-lg flex items-center justify-center relative overflow-hidden'>
          <div className='text-white text-center'>
            <Camera size={48} className='mx-auto mb-2 opacity-50' />
            <p className='text-sm opacity-75'>Cámara Simulada</p>
            {isScanning && (
              <div className='absolute inset-0 border-2 border-red-500 animate-pulse rounded-lg'>
                <div className='absolute top-1/2 left-0 right-0 h-0.5 bg-red-500 animate-pulse' />
              </div>
            )}
          </div>
        </div>
      )}
      {/* Animaciones de escaneo avanzadas */}
      {isScanning && (
        <div className='mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg'>
          <div className='flex items-center gap-3'>
            <Scan className='animate-spin text-blue-600' size={20} />
            <div className='flex-1'>
              <div className='text-sm font-medium text-blue-900'>
                Escaneando código...
              </div>
              <div className='w-full bg-blue-200 rounded-full h-2 mt-1'>
                <div
                  className='bg-blue-600 h-2 rounded-full animate-pulse'
                  style={{ width: '70%' }}
                ></div>
              </div>
            </div>
          </div>
        </div>
      )}
      {/* Resultado del último escaneo con información completa */}
      {lastScan && (
        <div className='mb-4 p-4 bg-green-50 border border-green-200 rounded-lg'>
          <div className='flex items-start gap-3'>
            <Check className='text-green-600 mt-0.5' size={18} />
            <div className='flex-1'>
              <div className='font-semibold text-green-900 mb-1'>
                {lastScan.name}
              </div>
              <div className='grid grid-cols-2 gap-2 text-sm'>
                <div>
                  <span className='font-medium text-green-700'>SKU:</span>
                  <span className='ml-1 text-green-600'>{lastScan.sku}</span>
                </div>
                <div>
                  <span className='font-medium text-green-700'>Código:</span>
                  <span className='ml-1 text-green-600 font-mono text-xs'>
                    {lastScan.barcode}
                  </span>
                </div>
                <div>
                  <span className='font-medium text-green-700'>Ubicación:</span>
                  <span className='ml-1 text-green-600'>
                    {lastScan.location}
                  </span>
                </div>
                <div>
                  <span className='font-medium text-green-700'>Escaneado:</span>
                  <span className='ml-1 text-green-600'>
                    {lastScan.timestamp.toLocaleTimeString()}
                  </span>
                </div>
              </div>
              {lastScan.errors && lastScan.errors.length > 0 && (
                <div className='mt-2 p-2 bg-yellow-100 border border-yellow-300 rounded text-xs'>
                  <span className='font-medium text-yellow-800'>
                    Advertencias:
                  </span>
                  <ul className='mt-1 ml-4 list-disc text-yellow-700'>
                    {lastScan.errors.map((error, index) => (
                      <li key={index}>{error}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      {/* Mostrar errores */}
      {errors.length > 0 && (
        <div className='mb-4 p-3 bg-red-50 border border-red-200 rounded-lg'>
          <div className='flex items-start gap-3'>
            <AlertCircle className='text-red-600 mt-0.5' size={16} />
            <div className='flex-1 text-sm'>
              {errors.map((error, index) => (
                <div key={index} className='text-red-700'>
                  {error}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
      {/* Input manual */}
      <div className='space-y-2'>
        <label className='block text-sm font-medium text-gray-700'>
          Código Manual
        </label>
        <input
          type='text'
          value={inputValue}
          onChange={e => handleManualInput(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && simulateScanning(inputValue)}
          placeholder={placeholder}
          disabled={disabled || isScanning}
          autoFocus={autoFocus}
          className='w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100'
        />
      </div>
      {/* Botón de escaneo manual */}
      <button
        onClick={() => inputValue.trim() && simulateScanning(inputValue.trim())}
        className='w-full mt-3 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors'
      >
        {isScanning ? 'Escaneando...' : 'Escanear Código'}
      </button>
      {/* Panel de estadísticas */}
      {stats.totalScans > 0 && (
        <div className='mt-4 p-3 bg-gray-50 border border-gray-200 rounded-lg'>
          <div className='text-xs font-medium text-gray-700 mb-2'>
            Estadísticas de Sesión
          </div>
          <div className='grid grid-cols-3 gap-4 text-center'>
            <div>
              <div className='text-lg font-bold text-gray-900'>
                {stats.totalScans}
              </div>
              <div className='text-xs text-gray-600'>Total</div>
            </div>
            <div>
              <div className='text-lg font-bold text-green-600'>
                {stats.successfulScans}
              </div>
              <div className='text-xs text-gray-600'>Exitosos</div>
            </div>
            <div>
              <div className='text-lg font-bold text-red-600'>
                {stats.errorScans}
              </div>
              <div className='text-xs text-gray-600'>Errores</div>
            </div>
          </div>
        </div>
      )}{' '}
      {/* Indicador de modo */}
      <div className='mt-3 text-xs text-gray-500 text-center'>
        Modo: {mode.replace('_', ' ').toUpperCase()}
      </div>
    </div>
  );
};

export default BarcodeScanner;
