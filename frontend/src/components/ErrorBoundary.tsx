import { Component, ErrorInfo, ReactNode } from 'react';
import { errorHandler } from '../utils/errorHandler';

export type ErrorSeverity = 'critical' | 'error' | 'warning';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  severity?: ErrorSeverity;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  showDetails?: boolean;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
  errorCount: number;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      errorCount: 0
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log to console
    console.error('Error boundary caught an error:', error, errorInfo);

    // Update state
    this.setState((prevState) => ({
      error,
      errorInfo,
      errorCount: prevState.errorCount + 1
    }));

    // Log to error handler
    const appError = errorHandler.createError(
      'REACT_ERROR_BOUNDARY',
      error.message,
      'unknown',
      {
        stack: error.stack,
        componentStack: errorInfo.componentStack,
        errorCount: this.state.errorCount + 1
      }
    );
    errorHandler.logError(appError);

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // In production, send to monitoring service
    if (import.meta.env.MODE === 'production') {
      this.logToMonitoringService(error, errorInfo);
    }
  }

  logToMonitoringService = (error: Error, errorInfo: ErrorInfo) => {
    // TODO: Integrate with error monitoring service (Sentry, LogRocket, etc.)
    console.info('Would send to monitoring:', {
      error: error.message,
      componentStack: errorInfo.componentStack
    });
  };

  handleReset = () => {
    this.setState({
      hasError: false,
      error: undefined,
      errorInfo: undefined
    });
  };

  handleReload = () => {
    window.location.reload();
  };

  getSeverityIcon = () => {
    const severity = this.props.severity || 'error';
    const iconClasses = 'w-8 h-8';

    switch (severity) {
      case 'critical':
        return (
          <div className='mx-auto w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mb-4'>
            <svg className={`${iconClasses} text-red-600`} fill='none' stroke='currentColor' viewBox='0 0 24 24'>
              <path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.996-.833-2.766 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z' />
            </svg>
          </div>
        );
      case 'warning':
        return (
          <div className='mx-auto w-20 h-20 bg-yellow-100 rounded-full flex items-center justify-center mb-4'>
            <svg className={`${iconClasses} text-yellow-600`} fill='none' stroke='currentColor' viewBox='0 0 24 24'>
              <path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.996-.833-2.766 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z' />
            </svg>
          </div>
        );
      default:
        return (
          <div className='mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4'>
            <svg className={`${iconClasses} text-red-600`} fill='none' stroke='currentColor' viewBox='0 0 24 24'>
              <path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.996-.833-2.766 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z' />
            </svg>
          </div>
        );
    }
  };

  render() {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      const showDetails = this.props.showDetails !== false;
      const isDevMode = import.meta.env.MODE === 'development';

      return (
        <div className='min-h-screen flex items-center justify-center bg-gray-50 p-4'>
          <div className='max-w-2xl w-full'>
            <div className='bg-white rounded-lg shadow-xl p-8'>
              {/* Error Icon */}
              <div className='text-center mb-6'>
                {this.getSeverityIcon()}

                <h2 className='text-2xl font-bold text-gray-900 mb-2'>
                  Algo salió mal
                </h2>

                <p className='text-gray-600 mb-4'>
                  Se produjo un error inesperado en la aplicación.
                  Puedes intentar las siguientes acciones:
                </p>

                {/* Error count warning */}
                {this.state.errorCount > 1 && (
                  <div className='mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg'>
                    <p className='text-sm text-yellow-800'>
                      Este error ha ocurrido {this.state.errorCount} veces.
                      Considera recargar la página completamente.
                    </p>
                  </div>
                )}
              </div>

              {/* Action buttons */}
              <div className='space-y-3 mb-6'>
                <button
                  onClick={this.handleReset}
                  className='w-full px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
                >
                  Intentar nuevamente
                </button>

                <button
                  onClick={this.handleReload}
                  className='w-full px-6 py-3 border-2 border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2'
                >
                  Recargar página completa
                </button>

                <button
                  onClick={() => window.history.back()}
                  className='w-full px-6 py-3 text-gray-600 font-medium rounded-lg hover:bg-gray-100 transition-colors focus:outline-none'
                >
                  Volver a la página anterior
                </button>
              </div>

              {/* Error details for development */}
              {isDevMode && showDetails && this.state.error && (
                <details className='mt-6'>
                  <summary className='cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900 mb-2'>
                    Detalles técnicos del error (solo visible en desarrollo)
                  </summary>
                  <div className='mt-3 space-y-3'>
                    {/* Error message */}
                    <div className='p-4 bg-red-50 border border-red-200 rounded-lg'>
                      <h4 className='text-sm font-semibold text-red-900 mb-2'>Error:</h4>
                      <pre className='text-xs text-red-800 whitespace-pre-wrap break-words'>
                        {this.state.error.toString()}
                      </pre>
                    </div>

                    {/* Stack trace */}
                    {this.state.error.stack && (
                      <div className='p-4 bg-gray-100 border border-gray-200 rounded-lg'>
                        <h4 className='text-sm font-semibold text-gray-900 mb-2'>Stack Trace:</h4>
                        <pre className='text-xs text-gray-700 whitespace-pre-wrap break-words overflow-auto max-h-48'>
                          {this.state.error.stack}
                        </pre>
                      </div>
                    )}

                    {/* Component stack */}
                    {this.state.errorInfo?.componentStack && (
                      <div className='p-4 bg-blue-50 border border-blue-200 rounded-lg'>
                        <h4 className='text-sm font-semibold text-blue-900 mb-2'>Component Stack:</h4>
                        <pre className='text-xs text-blue-800 whitespace-pre-wrap break-words overflow-auto max-h-48'>
                          {this.state.errorInfo.componentStack}
                        </pre>
                      </div>
                    )}
                  </div>
                </details>
              )}

              {/* Help text */}
              <div className='mt-6 pt-6 border-t border-gray-200'>
                <p className='text-sm text-gray-500 text-center'>
                  Si el problema persiste, por favor contacta a soporte técnico.
                </p>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
