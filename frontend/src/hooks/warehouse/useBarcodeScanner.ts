import { useState, useCallback } from 'react';
import { 
  ScanMode, 
  ScanStatus, 
  ScannedItem, 
  PickingSession,
  ScanValidationResult,
  ScannerConfig 
} from '../../types/barcode.types';
import { 
  InventoryStatus, 
  LocationZone, 
  LocationInfo 
} from '../../types/inventory.types';

// Configuración por defecto del scanner
const defaultConfig: ScannerConfig = {
  simulationDelay: 1200,
  autoSubmit: false,
  soundEnabled: true,
  vibrationEnabled: true,
  strictValidation: false
};

export const useBarcodeScanner = (
  mode: ScanMode = ScanMode.MANUAL,
  config: Partial<ScannerConfig> = {}
) => {
  const [status, setStatus] = useState<ScanStatus>(ScanStatus.IDLE);
  const [scannedItems, setScannedItems] = useState<ScannedItem[]>([]);
  const [isScanning, setIsScanning] = useState(false);
  const [lastScan, setLastScan] = useState<ScannedItem | null>(null);
  const [errors, setErrors] = useState<string[]>([]);
  const [currentSession, setCurrentSession] = useState<PickingSession | null>(null);

  const scannerConfig = { ...defaultConfig, ...config };

  // Simulador de base de datos
  const mockInventoryDatabase = [
    {
      sku: 'PROD001',
      name: 'Smartphone Galaxy Pro',
      barcode: '1234567890123',
      stock: 25,
      status: InventoryStatus.IN_STOCK,
      location: {
        zone: LocationZone.WAREHOUSE_A,
        aisle: 'A1',
        shelf: 'S3',
        position: 'P2'
      }
    }
  ];

  const searchInventoryItem = async (sku: string) => {
    await new Promise(resolve => setTimeout(resolve, 200));
    return mockInventoryDatabase.find(product => product.sku === sku.toUpperCase()) || null;
  };

  const scanItem = useCallback(async (sku: string): Promise<ScannedItem | null> => {
    setIsScanning(true);
    setStatus(ScanStatus.SCANNING);
    setErrors([]);
    
    try {
      await new Promise(resolve => setTimeout(resolve, scannerConfig.simulationDelay));
      
      const inventoryItem = await searchInventoryItem(sku);
      
      if (inventoryItem) {
        const item: ScannedItem = {
          id: Date.now().toString(),
          sku: inventoryItem.sku,
          name: inventoryItem.name,
          barcode: inventoryItem.barcode,
          quantity: 1,
          location: inventoryItem.location.zone + '-' + inventoryItem.location.aisle,
          timestamp: new Date(),
          status: ScanStatus.SUCCESS
        };
        
        setStatus(ScanStatus.SUCCESS);
        setLastScan(item);
        setScannedItems(prev => [...prev, item]);
        return item;
      } else {
        setStatus(ScanStatus.ERROR);
        setErrors(['Producto no encontrado']);
        return null;
      }
    } catch (error) {
      setStatus(ScanStatus.ERROR);
      setErrors(['Error de escaneo']);
      return null;
    } finally {
      setIsScanning(false);
    }
  }, [scannerConfig.simulationDelay]);

  const startPickingSession = useCallback((sessionConfig?: Partial<PickingSession>) => {
    const session: PickingSession = {
      id: Date.now().toString(),
      startTime: new Date(),
      items: [],
      totalItems: 0,
      completedItems: 0,
      mode,
      status: 'active',
      ...sessionConfig
    };
    setCurrentSession(session);
    return session;
  }, [mode]);

  const completePickingSession = useCallback(() => {
    const completedSession = { ...currentSession, endTime: new Date(), status: 'completed' as const };
    setCurrentSession(null);
    return completedSession;
  }, [currentSession]);

  const removeScannedItem = useCallback((itemId: string) => {
    setScannedItems(prev => prev.filter(item => item.id !== itemId));
  }, []);

  const resetScanner = useCallback(() => {
    setStatus(ScanStatus.IDLE);
    setScannedItems([]);
    setLastScan(null);
    setErrors([]);
    setIsScanning(false);
    setCurrentSession(null);
  }, []);

  return {
    status,
    isScanning,
    currentSession,
    scannedItems,
    lastScan,
    errors,
    scanItem,
    startPickingSession,
    completePickingSession,
    removeScannedItem,
    resetScanner,
    config: scannerConfig,
    stats: {
      totalScans: scannedItems.length,
      successfulScans: scannedItems.filter(item => item.status === ScanStatus.SUCCESS).length,
      errorScans: scannedItems.filter(item => item.status === ScanStatus.ERROR).length
    }
  };
};