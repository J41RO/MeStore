/**
 * Frontend Logger System v1.0
 * Logging dual: console enriquecido + envío remoto opcional
 * Captura errores globales y contexto del usuario
 */

// Tipos para el sistema de logging
export interface LogEntry {
  level: 'debug' | 'info' | 'warn' | 'error';
  message: string;
  timestamp: string;
  url: string;
  userAgent: string;
  userId?: string;
  sessionId: string;
  extra?: Record<string, any>;
}

export interface LoggerConfig {
  enableRemote: boolean;
  remoteEndpoint: string;
  minLevel: 'debug' | 'info' | 'warn' | 'error';
  enableConsole: boolean;
  batchSize: number;
  flushInterval: number;
}

class FrontendLogger {
  private config: LoggerConfig;
  private logQueue: LogEntry[] = [];
  private sessionId: string;
  private flushTimer?: number;

  constructor(config: Partial<LoggerConfig> = {}) {
    this.config = {
      enableRemote:
        import.meta.env.PROD && import.meta.env.VITE_LOG_REMOTE === 'true',
      remoteEndpoint: import.meta.env.VITE_LOG_ENDPOINT || '/api/v1/logs',
      minLevel: import.meta.env.PROD ? 'warn' : 'debug',
      enableConsole: true,
      batchSize: 10,
      flushInterval: 5000,
      ...config,
    };

    this.sessionId = this.generateSessionId();
    this.initializeGlobalErrorHandlers();
    this.startFlushTimer();

    console.log('🚀 Frontend Logger initialized:', {
      remote: this.config.enableRemote,
      endpoint: this.config.remoteEndpoint,
      minLevel: this.config.minLevel,
    });
  }

  private generateSessionId(): string {
    return 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  private shouldLog(level: string): boolean {
    const levels = ['debug', 'info', 'warn', 'error'];
    const currentIndex = levels.indexOf(level);
    const minIndex = levels.indexOf(this.config.minLevel);
    return currentIndex >= minIndex;
  }

  private createLogEntry(
    level: LogEntry['level'],
    message: string,
    extra?: Record<string, any>
  ): LogEntry {
    return {
      level,
      message,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent,
      userId: this.getCurrentUserId(),
      sessionId: this.sessionId,
      extra,
    };
  }

  private getCurrentUserId(): string | undefined {
    try {
      const user =
        localStorage.getItem('user') || sessionStorage.getItem('user');
      if (user) {
        const userData = JSON.parse(user);
        return userData.id || userData.email || 'unknown';
      }
    } catch (e) {
      // Ignorar errores de parsing
    }
    return undefined;
  }

  private logToConsole(entry: LogEntry): void {
    if (!this.config.enableConsole) return;

    const timestamp = new Date(entry.timestamp).toLocaleTimeString();
    const prefix = `[LOGGER ${timestamp}] ${entry.url.split('/').pop()}`;

    switch (entry.level) {
      case 'debug':
        console.debug(`${prefix} 🐛`, entry.message, entry.extra || '');
        break;
      case 'info':
        console.info(`${prefix} ℹ️`, entry.message, entry.extra || '');
        break;
      case 'warn':
        console.warn(`${prefix} ⚠️`, entry.message, entry.extra || '');
        break;
      case 'error':
        console.error(`${prefix} ❌`, entry.message, entry.extra || '');
        break;
    }
  }

  private addToQueue(entry: LogEntry): void {
    if (!this.config.enableRemote) return;

    this.logQueue.push(entry);

    if (this.logQueue.length >= this.config.batchSize) {
      this.flush();
    }
  }

  private async flush(): Promise<void> {
    if (this.logQueue.length === 0 || !this.config.enableRemote) return;

    const logsToSend = [...this.logQueue];
    this.logQueue = [];

    try {
      const response = await fetch(this.config.remoteEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          logs: logsToSend,
          source: 'frontend',
          timestamp: new Date().toISOString(),
        }),
      });

      if (!response.ok) {
        console.warn(
          'Failed to send logs to remote endpoint:',
          response.status,
          response.statusText
        );
        this.logQueue.unshift(...logsToSend);
      }
    } catch (error) {
      console.warn('Error sending logs to remote endpoint:', error);
      this.logQueue.unshift(...logsToSend);
    }
  }

  private startFlushTimer(): void {
    this.flushTimer = window.setInterval(() => {
      this.flush();
    }, this.config.flushInterval);
  }

  private initializeGlobalErrorHandlers(): void {
    window.onerror = (message, source, lineno, colno, error) => {
      this.error('Unhandled JavaScript Error', {
        message: message?.toString(),
        source,
        lineno,
        colno,
        stack: error?.stack,
        type: 'javascript_error',
      });
      return false;
    };

    window.addEventListener('unhandledrejection', event => {
      this.error('Unhandled Promise Rejection', {
        reason: event.reason?.toString(),
        stack: event.reason?.stack,
        type: 'promise_rejection',
      });
    });

    window.addEventListener(
      'error',
      event => {
        if (event.target !== window) {
          this.error('Resource Loading Error', {
            elementType: (event.target as any)?.tagName,
            source: (event.target as any)?.src || (event.target as any)?.href,
            type: 'resource_error',
          });
        }
      },
      true
    );
  }

  // Métodos públicos para logging
  debug(message: string, extra?: Record<string, any>): void {
    if (!this.shouldLog('debug')) return;

    const entry = this.createLogEntry('debug', message, extra);
    this.logToConsole(entry);
    this.addToQueue(entry);
  }

  info(message: string, extra?: Record<string, any>): void {
    if (!this.shouldLog('info')) return;

    const entry = this.createLogEntry('info', message, extra);
    this.logToConsole(entry);
    this.addToQueue(entry);
  }

  warn(message: string, extra?: Record<string, any>): void {
    if (!this.shouldLog('warn')) return;

    const entry = this.createLogEntry('warn', message, extra);
    this.logToConsole(entry);
    this.addToQueue(entry);
  }

  error(message: string, extra?: Record<string, any>): void {
    if (!this.shouldLog('error')) return;

    const entry = this.createLogEntry('error', message, extra);
    this.logToConsole(entry);
    this.addToQueue(entry);
  }

  logEvent(eventName: string, data?: Record<string, any>): void {
    this.info(`Event: ${eventName}`, { eventType: 'user_action', ...data });
  }

  destroy(): void {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
    }
    this.flush();
  }
}

export const logger = new FrontendLogger();
export default logger;
