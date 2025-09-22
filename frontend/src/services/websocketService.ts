// frontend/src/services/websocketService.ts
// PERFORMANCE_OPTIMIZED: WebSocket service for real-time analytics
// Target: <500ms latency with automatic reconnection

import React from 'react';
import { useAnalyticsStore } from '../stores/analyticsStore';

export interface WebSocketMessage {
  type: 'analytics_update' | 'new_order' | 'metrics_update' | 'connection_status';
  data: any;
  timestamp: string;
}

export interface WebSocketConfig {
  url: string;
  reconnectInterval: number;
  maxReconnectAttempts: number;
  heartbeatInterval: number;
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private isConnecting = false;
  private messageQueue: WebSocketMessage[] = [];
  private latencyTracker: { sent: number; received: number }[] = [];

  private config: WebSocketConfig = {
    url: 'ws://192.168.1.137:8000/api/v1/analytics/ws/vendor/analytics',
    reconnectInterval: 1000, // Faster reconnection for better UX
    maxReconnectAttempts: 10,
    heartbeatInterval: 15000 // More frequent heartbeat for better latency detection
  };

  private listeners: Map<string, Function[]> = new Map();

  constructor(config?: Partial<WebSocketConfig>) {
    if (config) {
      this.config = { ...this.config, ...config };
    }
  }

  // Performance-optimized connection with latency tracking
  async connect(vendorId?: string): Promise<void> {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return;
    }

    this.isConnecting = true;
    const connectStart = performance.now();

    try {
      // Get JWT token from localStorage
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.error('No JWT token found for WebSocket authentication');
        this.isConnecting = false;
        return;
      }

      // Build WebSocket URL with authentication parameters
      const params = new URLSearchParams();
      params.append('token', token);
      if (vendorId) {
        params.append('vendor_id', vendorId);
      }

      const wsUrl = `${this.config.url}?${params.toString()}`;
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        const connectTime = performance.now() - connectStart;
        console.log(`WebSocket connected in ${connectTime.toFixed(2)}ms`);

        this.isConnecting = false;
        this.reconnectAttempts = 0;

        // Update store connection status
        useAnalyticsStore.getState().setConnected(true);

        // Start heartbeat
        this.startHeartbeat();

        // Process queued messages
        this.processMessageQueue();

        this.emit('connected', { connectTime });
      };

      this.ws.onmessage = (event) => {
        const receiveTime = performance.now();
        this.handleMessage(event, receiveTime);
      };

      this.ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        this.isConnecting = false;
        useAnalyticsStore.getState().setConnected(false);
        this.stopHeartbeat();

        // Handle authentication errors differently
        if (event.code === 4001 || event.code === 4003) {
          console.error('WebSocket authentication failed:', event.reason);
          this.emit('authenticationFailed', { code: event.code, reason: event.reason });
          // Don't auto-reconnect on auth failures
          return;
        }

        if (!event.wasClean && this.reconnectAttempts < this.config.maxReconnectAttempts) {
          this.scheduleReconnect();
        }

        this.emit('disconnected', { code: event.code, reason: event.reason });
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.isConnecting = false;
        this.emit('error', error);
      };

    } catch (error) {
      this.isConnecting = false;
      console.error('Failed to connect WebSocket:', error);
      this.scheduleReconnect();
    }
  }

  // Performance-optimized message handling with <150ms target
  private handleMessage(event: MessageEvent, receiveTime: number): void {
    const processingStartTime = performance.now();

    try {
      const message: WebSocketMessage = JSON.parse(event.data);

      // Track latency if message has timestamp
      if (message.timestamp) {
        const sentTime = new Date(message.timestamp).getTime();
        const latency = receiveTime - sentTime;
        this.trackLatency(latency);

        // Log warning if latency exceeds target
        if (latency > 150) {
          console.warn(`⚠️ High latency detected: ${latency.toFixed(2)}ms (target: <150ms)`);
        }
      }

      // Route message to appropriate handler (optimized for speed)
      const handlers = {
        'analytics_update': () => this.handleAnalyticsUpdate(message.data),
        'new_order': () => this.handleNewOrder(message.data),
        'metrics_update': () => this.handleMetricsUpdate(message.data),
        'connection_status': () => this.handleConnectionStatus(message.data)
      };

      const handler = handlers[message.type as keyof typeof handlers];
      if (handler) {
        handler();
      } else {
        console.warn('Unknown message type:', message.type);
      }

      this.emit('message', message);

      // Track processing time
      const processingTime = performance.now() - processingStartTime;
      if (processingTime > 10) {
        console.warn(`Slow message processing: ${processingTime.toFixed(2)}ms`);
      }

    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
      this.emit('error', { type: 'parse_error', error });
    }
  }

  // Handle real-time analytics updates
  private handleAnalyticsUpdate(data: any): void {
    const store = useAnalyticsStore.getState();

    // Use the new updateFullAnalyticsData method for better performance
    store.updateFullAnalyticsData({
      metrics: data.metrics,
      topProducts: data.topProducts,
      salesByCategory: data.salesByCategory,
      monthlyTrends: data.monthlyTrends
    });

    this.emit('analyticsUpdate', data);
  }

  // Handle new order notifications
  private handleNewOrder(order: any): void {
    const store = useAnalyticsStore.getState();
    store.addRealTimeOrder({
      value: order.total_amount || order.value,
      category: order.category || 'general'
    });

    this.emit('newOrder', order);
  }

  // Handle metrics updates
  private handleMetricsUpdate(metrics: any): void {
    const store = useAnalyticsStore.getState();
    store.updateRealTimeMetrics(metrics);

    this.emit('metricsUpdate', metrics);
  }

  // Handle connection status updates
  private handleConnectionStatus(status: any): void {
    console.log('Connection status:', status);
    this.emit('connectionStatus', status);
  }

  // Send message with queuing for offline mode
  send(message: WebSocketMessage): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const messageWithTimestamp = {
        ...message,
        timestamp: new Date().toISOString()
      };
      this.ws.send(JSON.stringify(messageWithTimestamp));
    } else {
      // Queue message for when connection is restored
      this.messageQueue.push(message);
    }
  }

  // Process queued messages when connection is restored
  private processMessageQueue(): void {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      if (message) {
        this.send(message);
      }
    }
  }

  // Heartbeat to maintain connection
  private startHeartbeat(): void {
    this.heartbeatTimer = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.send({
          type: 'connection_status',
          data: { type: 'ping' },
          timestamp: new Date().toISOString()
        });
      }
    }, this.config.heartbeatInterval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  // Reconnection logic with exponential backoff and jitter
  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.config.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      this.emit('maxReconnectAttemptsReached');
      return;
    }

    this.reconnectAttempts++;

    // Exponential backoff with jitter to prevent thundering herd
    const baseDelay = this.config.reconnectInterval * Math.pow(1.5, this.reconnectAttempts - 1);
    const jitter = Math.random() * 1000; // Add up to 1 second of jitter
    const delay = Math.min(baseDelay + jitter, 30000); // Cap at 30 seconds

    console.log(`Scheduling reconnect attempt ${this.reconnectAttempts} in ${delay.toFixed(0)}ms`);

    this.reconnectTimer = setTimeout(async () => {
      try {
        // Check if token is still valid before reconnecting
        const token = localStorage.getItem('access_token');
        if (!token) {
          console.error('No valid token available for reconnection');
          this.emit('authenticationRequired');
          return;
        }

        await this.connect();
      } catch (error) {
        console.error('Reconnection failed:', error);
        // Continue with next reconnect attempt
        this.scheduleReconnect();
      }
    }, delay);
  }

  // Latency tracking for performance monitoring
  private trackLatency(latency: number): void {
    this.latencyTracker.push({
      sent: Date.now() - latency,
      received: Date.now()
    });

    // Keep only last 100 latency measurements
    if (this.latencyTracker.length > 100) {
      this.latencyTracker.shift();
    }

    // Log warning if latency exceeds target
    if (latency > 500) {
      console.warn(`High WebSocket latency: ${latency}ms`);
    }
  }

  // Get average latency
  getAverageLatency(): number {
    if (this.latencyTracker.length === 0) return 0;

    const latencies = this.latencyTracker.map(track =>
      track.received - track.sent
    );

    return latencies.reduce((sum, latency) => sum + latency, 0) / latencies.length;
  }

  // Event emitter functionality
  on(event: string, callback: Function): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)?.push(callback);
  }

  off(event: string, callback: Function): void {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  private emit(event: string, data?: any): void {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach(callback => callback(data));
    }
  }

  // Cleanup
  disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    this.stopHeartbeat();

    if (this.ws) {
      this.ws.close(1000, 'Manual disconnect');
      this.ws = null;
    }

    useAnalyticsStore.getState().setConnected(false);
    this.listeners.clear();
  }

  // Get connection status
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  // Get connection state with health information
  getConnectionState(): string {
    if (!this.ws) return 'disconnected';

    switch (this.ws.readyState) {
      case WebSocket.CONNECTING: return 'connecting';
      case WebSocket.OPEN: return 'connected';
      case WebSocket.CLOSING: return 'closing';
      case WebSocket.CLOSED: return 'disconnected';
      default: return 'unknown';
    }
  }

  // Get connection health metrics
  getConnectionHealth(): {
    isHealthy: boolean;
    latency: number;
    reconnectAttempts: number;
    queuedMessages: number;
    connectionState: string;
    uptime: number;
  } {
    const avgLatency = this.getAverageLatency();
    const isHealthy = this.isConnected() && avgLatency < 150 && this.reconnectAttempts === 0;

    return {
      isHealthy,
      latency: avgLatency,
      reconnectAttempts: this.reconnectAttempts,
      queuedMessages: this.messageQueue.length,
      connectionState: this.getConnectionState(),
      uptime: this.isConnected() ? Date.now() - (this.latencyTracker[0]?.sent || Date.now()) : 0
    };
  }

  // Force connection health check
  async performHealthCheck(): Promise<boolean> {
    if (!this.isConnected()) {
      return false;
    }

    try {
      const startTime = performance.now();

      // Send ping and wait for pong
      this.send({
        type: 'connection_status',
        data: { type: 'health_check' },
        timestamp: new Date().toISOString()
      });

      // Wait for response (simplified check)
      await new Promise((resolve, reject) => {
        const timeout = setTimeout(() => reject(new Error('Health check timeout')), 5000);

        const onMessage = () => {
          clearTimeout(timeout);
          this.off('message', onMessage);
          resolve(true);
        };

        this.on('message', onMessage);
      });

      const responseTime = performance.now() - startTime;
      return responseTime < 1000; // Health check should respond within 1 second

    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }
}

// Singleton instance
export const websocketService = new WebSocketService();

// React hook for WebSocket integration
export const useWebSocket = (vendorId?: string) => {
  const isConnected = useAnalyticsStore(state => state.isConnected);
  const [authError, setAuthError] = React.useState<string | null>(null);

  const connect = React.useCallback(() => {
    setAuthError(null);
    websocketService.connect(vendorId);
  }, [vendorId]);

  const disconnect = React.useCallback(() => {
    websocketService.disconnect();
  }, []);

  const send = React.useCallback((message: WebSocketMessage) => {
    websocketService.send(message);
  }, []);

  React.useEffect(() => {
    // Listen for authentication failures
    const handleAuthFailure = (event: { code: number; reason: string }) => {
      setAuthError(`Authentication failed: ${event.reason}`);
    };

    const handleAuthRequired = () => {
      setAuthError('Authentication required - please login again');
    };

    websocketService.on('authenticationFailed', handleAuthFailure);
    websocketService.on('authenticationRequired', handleAuthRequired);

    // Auto-connect when hook is used
    if (!isConnected && !websocketService.isConnected()) {
      connect();
    }

    // Cleanup on unmount
    return () => {
      websocketService.off('authenticationFailed', handleAuthFailure);
      websocketService.off('authenticationRequired', handleAuthRequired);
      // Don't disconnect on unmount as other components might be using it
      // websocketService.disconnect();
    };
  }, [connect, isConnected]);

  return {
    isConnected,
    authError,
    connect,
    disconnect,
    send,
    getLatency: () => websocketService.getAverageLatency(),
    getConnectionState: () => websocketService.getConnectionState(),
    getConnectionHealth: () => websocketService.getConnectionHealth(),
    performHealthCheck: () => websocketService.performHealthCheck()
  };
};

export default websocketService;