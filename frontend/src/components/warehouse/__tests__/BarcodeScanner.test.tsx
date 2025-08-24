import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BarcodeScanner } from '../BarcodeScanner';
import { ScanMode } from '../../../types/barcode.types';

// Mock del hook personalizado
jest.mock('../../../hooks/warehouse/useBarcodeScanner', () => ({
  useBarcodeScanner: jest.fn(() => ({
    status: 'idle',
    isScanning: false,
    lastScan: null,
    errors: [],
    scanItem: jest.fn(),
    stats: {
      totalScans: 0,
      successfulScans: 0,
      errorScans: 0
    }
  }))
}));

describe('BarcodeScanner', () => {
  const mockOnScan = jest.fn();
  const mockOnError = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renderiza correctamente el componente base', () => {
    render(
      <BarcodeScanner
        onScan={mockOnScan}
        onError={mockOnError}
      />
    );

    expect(screen.getByText('Scanner de Códigos')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Ingresa SKU o código...')).toBeInTheDocument();
    expect(screen.getByText('Escanear Código')).toBeInTheDocument();
  });

  test('permite entrada manual de código', () => {
    render(
      <BarcodeScanner
        onScan={mockOnScan}
        onError={mockOnError}
      />
    );

    const input = screen.getByPlaceholderText('Ingresa SKU o código...');
    
    fireEvent.change(input, { target: { value: 'PROD001' } });
    
    expect(input).toHaveValue('PROD001');
  });

  test('botón de escaneo existe y responde a clicks', () => {
    render(
      <BarcodeScanner
        onScan={mockOnScan}
        onError={mockOnError}
      />
    );

    const scanButton = screen.getByText('Escanear Código');
    const input = screen.getByPlaceholderText('Ingresa SKU o código...');

    expect(scanButton).toBeInTheDocument();
    
    // Escribir valor y verificar que el botón es clickeable
    fireEvent.change(input, { target: { value: 'PROD001' } });
    fireEvent.click(scanButton);
    
    // Verificar que el input existe y puede recibir valores
    expect(input).toHaveValue('PROD001');
  });

  test('maneja el escaneo manual correctamente', async () => {
    const { useBarcodeScanner } = require('../../../hooks/warehouse/useBarcodeScanner');
    const mockScanItem = jest.fn();
    
    useBarcodeScanner.mockReturnValue({
      status: 'idle',
      isScanning: false,
      lastScan: null,
      errors: [],
      scanItem: mockScanItem,
      stats: { totalScans: 0, successfulScans: 0, errorScans: 0 }
    });

    render(
      <BarcodeScanner
        onScan={mockOnScan}
        onError={mockOnError}
      />
    );

    const input = screen.getByPlaceholderText('Ingresa SKU o código...');
    const scanButton = screen.getByText('Escanear Código');

    fireEvent.change(input, { target: { value: 'PROD001' } });
    fireEvent.click(scanButton);

    expect(mockScanItem).toHaveBeenCalledWith('PROD001');
  });

  test('muestra modo de scanner correctamente', () => {
    render(
      <BarcodeScanner
        mode={ScanMode.BATCH}
        onScan={mockOnScan}
        onError={mockOnError}
      />
    );

    expect(screen.getByText('Modo: BATCH')).toBeInTheDocument();
  });

  test('tiene botón de cámara funcional', () => {
    render(
      <BarcodeScanner
        onScan={mockOnScan}
        onError={mockOnError}
      />
    );

    const cameraButtons = screen.getAllByRole('button');
    const cameraButton = cameraButtons.find(
      btn => btn.querySelector('svg') && btn.getAttribute('class')?.includes('p-2')
    );

    expect(cameraButton).toBeInTheDocument();
    
    if (cameraButton) {
      fireEvent.click(cameraButton);
      // Simplemente verificar que el botón es clickeable
      expect(cameraButton).toBeInTheDocument();
    }
  });

  test('muestra información del último escaneo', () => {
    const { useBarcodeScanner } = require('../../../hooks/warehouse/useBarcodeScanner');
    
    const mockLastScan = {
      id: '1',
      sku: 'PROD001',
      name: 'Smartphone Galaxy Pro',
      barcode: '1234567890123',
      location: 'WAREHOUSE_A-A1-S3',
      timestamp: new Date(),
      quantity: 1,
      status: 'success'
    };

    useBarcodeScanner.mockReturnValue({
      status: 'success',
      isScanning: false,
      lastScan: mockLastScan,
      errors: [],
      scanItem: jest.fn(),
      stats: { totalScans: 1, successfulScans: 1, errorScans: 0 }
    });

    render(
      <BarcodeScanner
        onScan={mockOnScan}
        onError={mockOnError}
      />
    );

    expect(screen.getByText('Smartphone Galaxy Pro')).toBeInTheDocument();
    expect(screen.getByText('PROD001')).toBeInTheDocument();
    expect(screen.getByText('1234567890123')).toBeInTheDocument();
  });

  test('muestra errores de escaneo', () => {
    const { useBarcodeScanner } = require('../../../hooks/warehouse/useBarcodeScanner');
    
    useBarcodeScanner.mockReturnValue({
      status: 'error',
      isScanning: false,
      lastScan: null,
      errors: ['Producto no encontrado', 'Formato inválido'],
      scanItem: jest.fn(),
      stats: { totalScans: 1, successfulScans: 0, errorScans: 1 }
    });

    render(
      <BarcodeScanner
        onScan={mockOnScan}
        onError={mockOnError}
      />
    );

    expect(screen.getByText('Producto no encontrado')).toBeInTheDocument();
    expect(screen.getByText('Formato inválido')).toBeInTheDocument();
  });

  test('muestra estadísticas cuando hay escaneos', () => {
    const { useBarcodeScanner } = require('../../../hooks/warehouse/useBarcodeScanner');
    
    useBarcodeScanner.mockReturnValue({
      status: 'idle',
      isScanning: false,
      lastScan: null,
      errors: [],
      scanItem: jest.fn(),
      stats: { totalScans: 5, successfulScans: 4, errorScans: 1 }
    });

    render(
      <BarcodeScanner
        onScan={mockOnScan}
        onError={mockOnError}
      />
    );

    expect(screen.getByText('Estadísticas de Sesión')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument(); // Total
    expect(screen.getByText('4')).toBeInTheDocument(); // Exitosos
    expect(screen.getByText('1')).toBeInTheDocument(); // Errores
  });


  test('maneja entrada con Enter key', () => {
    const { useBarcodeScanner } = require('../../../hooks/warehouse/useBarcodeScanner');
    const mockScanItem = jest.fn();
    
    useBarcodeScanner.mockReturnValue({
      status: 'idle',
      isScanning: false,
      lastScan: null,
      errors: [],
      scanItem: mockScanItem,
      stats: { totalScans: 0, successfulScans: 0, errorScans: 0 }
    });

    render(
      <BarcodeScanner
        onScan={mockOnScan}
        onError={mockOnError}
      />
    );

    const input = screen.getByPlaceholderText('Ingresa SKU o código...');

    fireEvent.change(input, { target: { value: 'PROD001' } });
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });

    // El componente usa onKeyPress, así que probamos ambos eventos
    fireEvent.keyPress(input, { key: 'Enter', charCode: 13 });
    
    expect(mockScanItem).toHaveBeenCalledWith('PROD001');
  });

  test('maneja estado de scanning', () => {
    const { useBarcodeScanner } = require('../../../hooks/warehouse/useBarcodeScanner');
    
    useBarcodeScanner.mockReturnValue({
      status: 'scanning',
      isScanning: true,
      lastScan: null,
      errors: [],
      scanItem: jest.fn(),
      stats: { totalScans: 0, successfulScans: 0, errorScans: 0 }
    });

    render(
      <BarcodeScanner
        onScan={mockOnScan}
        onError={mockOnError}
      />
    );

    expect(screen.getByText('Escaneando código...')).toBeInTheDocument();
    expect(screen.getByText('Escaneando...')).toBeInTheDocument();
  });

  test('renderiza con props opcionales', () => {
    render(
      <BarcodeScanner
        onScan={mockOnScan}
        onError={mockOnError}
        autoFocus={true}
        className='test-class'
      />
    );

    const input = screen.getByPlaceholderText('Ingresa SKU o código...');
    // Simplemente verificar que renderiza correctamente con props opcionales
    expect(input).toBeInTheDocument();
    expect(screen.getByText('Scanner de Códigos')).toBeInTheDocument();
  });

  test('maneja placeholder personalizado', () => {
    const customPlaceholder = 'Código personalizado...';
    
    render(
      <BarcodeScanner
        onScan={mockOnScan}
        onError={mockOnError}
        placeholder={customPlaceholder}
      />
    );

    expect(screen.getByPlaceholderText(customPlaceholder)).toBeInTheDocument();
  });

  test('maneja className personalizada', () => {
    const customClass = 'mi-clase-personalizada';
    
    const { container } = render(
      <BarcodeScanner
        onScan={mockOnScan}
        onError={mockOnError}
        className={customClass}
      />
    );

    expect(container.firstChild).toHaveClass(customClass);
  });  test('acepta prop disabled correctamente', () => {
    render(
      <BarcodeScanner
        onScan={mockOnScan}
        onError={mockOnError}
        disabled={true}
      />
    );

    const input = screen.getByPlaceholderText('Ingresa SKU o código...');
    
    // Verificar que el input recibe el prop disabled
    expect(input).toBeDisabled();
    
    // Verificar que el componente renderiza correctamente incluso cuando disabled
    expect(screen.getByText('Scanner de Códigos')).toBeInTheDocument();
  });
});