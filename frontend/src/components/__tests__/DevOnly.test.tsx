import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { DevOnly, DevOnlyConsole, useDevOnly } from '../DevOnly';

// Mock import.meta.env
const mockImportMeta = (dev: boolean, prod: boolean) => {
  Object.defineProperty(import.meta, 'env', {
    value: { DEV: dev, PROD: prod },
    configurable: true,
  });
};

describe('DevOnly Component', () => {
  it('should render children in development mode', () => {
    mockImportMeta(true, false);

    render(
      <DevOnly>
        <div data-testid="debug-panel">Debug Panel</div>
      </DevOnly>
    );

    expect(screen.getByTestId('debug-panel')).toBeInTheDocument();
  });

  it('should NOT render children in production mode', () => {
    mockImportMeta(false, true);

    render(
      <DevOnly>
        <div data-testid="debug-panel">Debug Panel</div>
      </DevOnly>
    );

    expect(screen.queryByTestId('debug-panel')).not.toBeInTheDocument();
  });

  it('should NOT render if both DEV and PROD are false', () => {
    mockImportMeta(false, false);

    render(
      <DevOnly>
        <div data-testid="debug-panel">Debug Panel</div>
      </DevOnly>
    );

    expect(screen.queryByTestId('debug-panel')).not.toBeInTheDocument();
  });

  it('should prioritize PROD flag over DEV flag', () => {
    // Even if DEV is true, if PROD is true, should not render
    mockImportMeta(true, true);

    render(
      <DevOnly>
        <div data-testid="debug-panel">Debug Panel</div>
      </DevOnly>
    );

    expect(screen.queryByTestId('debug-panel')).not.toBeInTheDocument();
  });
});

describe('DevOnlyConsole', () => {
  const consoleLogSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
  const consoleWarnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
  const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

  afterEach(() => {
    consoleLogSpy.mockClear();
    consoleWarnSpy.mockClear();
    consoleErrorSpy.mockClear();
  });

  it('should log in development mode', () => {
    mockImportMeta(true, false);

    DevOnlyConsole.log('Test message');

    expect(consoleLogSpy).toHaveBeenCalledWith('[DEV]', 'Test message');
  });

  it('should NOT log in production mode', () => {
    mockImportMeta(false, true);

    DevOnlyConsole.log('Test message');

    expect(consoleLogSpy).not.toHaveBeenCalled();
  });

  it('should handle warn in development', () => {
    mockImportMeta(true, false);

    DevOnlyConsole.warn('Warning message');

    expect(consoleWarnSpy).toHaveBeenCalledWith('[DEV]', 'Warning message');
  });

  it('should handle error in development', () => {
    mockImportMeta(true, false);

    DevOnlyConsole.error('Error message');

    expect(consoleErrorSpy).toHaveBeenCalledWith('[DEV]', 'Error message');
  });
});

describe('useDevOnly Hook', () => {
  function TestComponent() {
    const isDev = useDevOnly();
    return <div data-testid="result">{isDev ? 'development' : 'production'}</div>;
  }

  it('should return true in development mode', () => {
    mockImportMeta(true, false);

    render(<TestComponent />);

    expect(screen.getByTestId('result')).toHaveTextContent('development');
  });

  it('should return false in production mode', () => {
    mockImportMeta(false, true);

    render(<TestComponent />);

    expect(screen.getByTestId('result')).toHaveTextContent('production');
  });

  it('should prioritize PROD flag (return false even if DEV is true)', () => {
    mockImportMeta(true, true);

    render(<TestComponent />);

    expect(screen.getByTestId('result')).toHaveTextContent('production');
  });
});
