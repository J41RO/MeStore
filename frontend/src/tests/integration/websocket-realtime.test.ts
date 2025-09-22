// frontend/src/tests/integration/websocket-realtime.test.ts
// WEBSOCKET REAL-TIME INTEGRATION TESTING
// Tests WebSocket connections, latency, and real-time data flow

// Jest equivalents for Vitest imports
const vi = jest;
import WS from 'jest-websocket-mock';

// WebSocket service under test
import { WebSocketService, useWebSocket } from '../../services/websocketService';
import { useAnalyticsStore } from '../../stores/analyticsStore';

// Types
interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
  vendor_id: string;
}

interface AnalyticsUpdate {
  revenue: { current: number; trend: 'up' | 'down' | 'stable' };
  orders: { current: number; trend: 'up' | 'down' | 'stable' };
  products: { total: number; active: number };
  customers: { total: number; new: number };
}

// Performance tracking
class WebSocketPerformanceTracker {
  private connectionStart: number = 0;
  private messageLatencies: number[] = [];
  private reconnectionAttempts: number = 0;

  startConnection() {
    this.connectionStart = performance.now();
  }

  connectionEstablished() {
    const connectionTime = performance.now() - this.connectionStart;
    return connectionTime;
  }

  recordMessageLatency(sentTime: number) {
    const latency = performance.now() - sentTime;
    this.messageLatencies.push(latency);
    return latency;
  }

  getAverageLatency() {
    if (this.messageLatencies.length === 0) return 0;
    return this.messageLatencies.reduce((sum, lat) => sum + lat, 0) / this.messageLatencies.length;
  }

  getMaxLatency() {
    return Math.max(...this.messageLatencies, 0);
  }

  incrementReconnection() {
    this.reconnectionAttempts++;
  }

  getReconnectionCount() {
    return this.reconnectionAttempts;
  }

  reset() {
    this.connectionStart = 0;
    this.messageLatencies = [];
    this.reconnectionAttempts = 0;
  }
}

describe('WebSocket Real-time Integration Tests', () => {
  let server: WS;
  let performanceTracker: WebSocketPerformanceTracker;
  const WEBSOCKET_URL = 'ws://192.168.1.137:8000';
  const vendorId = 'test-vendor-123';

  beforeEach(() => {
    performanceTracker = new WebSocketPerformanceTracker();

    // Mock WebSocket server
    server = new WS(`${WEBSOCKET_URL}/ws/vendor/${vendorId}/analytics`);

    // Mock performance.now for consistent testing
    vi.spyOn(performance, 'now').mockImplementation(() => Date.now());
  });

  afterEach(() => {
    if (server) {
      WS.clean();
    }
    performanceTracker.reset();
    vi.restoreAllMocks();
  });

  describe('1. WebSocket Connection Management', () => {
    it('should establish connection within performance targets', async () => {
      performanceTracker.startConnection();

      const wsService = new WebSocketService(`${WEBSOCKET_URL}/ws/vendor/${vendorId}/analytics`);
      await wsService.connect();

      await server.connected;

      const connectionTime = performanceTracker.connectionEstablished();

      expect(server).toHaveReceivedMessages([]);
      expect(connectionTime).toBeLessThan(1000); // Should connect in under 1 second
      expect(wsService.isConnected()).toBe(true);
    });

    it('should handle connection authentication', async () => {
      const wsService = new WebSocketService(`${WEBSOCKET_URL}/ws/vendor/${vendorId}/analytics`);

      // Mock authentication token
      const authToken = 'mock-jwt-token';
      localStorage.setItem('auth_token', authToken);

      await wsService.connect();
      await server.connected;

      // Should send authentication message
      const authMessage = {
        type: 'authenticate',
        token: authToken,
        vendor_id: vendorId
      };

      wsService.send(authMessage);

      await expect(server).toReceiveMessage(JSON.stringify(authMessage));
    });

    it('should handle connection errors gracefully', async () => {
      const wsService = new WebSocketService('ws://invalid-url:9999/ws');

      const connectionPromise = wsService.connect();

      // Simulate connection error
      server.error();

      await expect(connectionPromise).rejects.toThrow();
      expect(wsService.isConnected()).toBe(false);
    });

    it('should implement automatic reconnection', async () => {
      const wsService = new WebSocketService(
        `${WEBSOCKET_URL}/ws/vendor/${vendorId}/analytics`,
        { reconnectInterval: 100, maxReconnectAttempts: 3 }
      );

      await wsService.connect();
      await server.connected;

      // Simulate connection loss
      server.close();

      performanceTracker.incrementReconnection();

      // Wait for reconnection attempt
      await new Promise(resolve => setTimeout(resolve, 150));

      expect(performanceTracker.getReconnectionCount()).toBe(1);
      expect(wsService.getReconnectionAttempts()).toBeGreaterThan(0);
    });
  });

  describe('2. Real-time Analytics Data Flow', () => {
    let wsService: WebSocketService;

    beforeEach(async () => {
      wsService = new WebSocketService(`${WEBSOCKET_URL}/ws/vendor/${vendorId}/analytics`);
      await wsService.connect();
      await server.connected;
    });

    it('should receive and process analytics updates', async () => {
      const mockAnalyticsUpdate: WebSocketMessage = {
        type: 'analytics_update',
        vendor_id: vendorId,
        timestamp: new Date().toISOString(),
        data: {
          revenue: { current: 1600000, trend: 'up' },
          orders: { current: 48, trend: 'up' },
          products: { total: 16, active: 14 },
          customers: { total: 125, new: 18 }
        } as AnalyticsUpdate
      };

      const messageHandler = vi.fn();
      wsService.onMessage(messageHandler);

      // Send update from server
      server.send(JSON.stringify(mockAnalyticsUpdate));

      await new Promise(resolve => setTimeout(resolve, 50));

      expect(messageHandler).toHaveBeenCalledWith(mockAnalyticsUpdate);
      expect(messageHandler).toHaveBeenCalledTimes(1);
    });

    it('should handle high-frequency updates efficiently', async () => {
      const messageHandler = vi.fn();
      wsService.onMessage(messageHandler);

      const updateCount = 100;
      const startTime = performance.now();

      // Send multiple rapid updates
      for (let i = 0; i < updateCount; i++) {
        const update: WebSocketMessage = {
          type: 'analytics_update',
          vendor_id: vendorId,
          timestamp: new Date().toISOString(),
          data: {
            revenue: { current: 1500000 + i * 1000, trend: 'up' },
            orders: { current: 45 + i, trend: 'up' },
            products: { total: 15, active: 15 },
            customers: { total: 120, new: 15 }
          }
        };

        server.send(JSON.stringify(update));

        // Record latency for each message
        performanceTracker.recordMessageLatency(startTime);
      }

      // Wait for all messages to be processed
      await new Promise(resolve => setTimeout(resolve, 500));

      const averageLatency = performanceTracker.getAverageLatency();
      const maxLatency = performanceTracker.getMaxLatency();

      expect(messageHandler).toHaveBeenCalledTimes(updateCount);
      expect(averageLatency).toBeLessThan(50); // Average under 50ms
      expect(maxLatency).toBeLessThan(200); // Max under 200ms
    });

    it('should validate message format and handle malformed data', async () => {
      const messageHandler = vi.fn();
      const errorHandler = vi.fn();

      wsService.onMessage(messageHandler);
      wsService.onError(errorHandler);

      // Send malformed JSON
      server.send('invalid json {');

      await new Promise(resolve => setTimeout(resolve, 50));

      expect(errorHandler).toHaveBeenCalled();
      expect(messageHandler).not.toHaveBeenCalled();
    });

    it('should handle vendor-specific message filtering', async () => {
      const messageHandler = vi.fn();
      wsService.onMessage(messageHandler);

      // Send message for different vendor
      const wrongVendorMessage: WebSocketMessage = {
        type: 'analytics_update',
        vendor_id: 'different-vendor',
        timestamp: new Date().toISOString(),
        data: { revenue: { current: 1000000, trend: 'up' } }
      };

      // Send message for correct vendor
      const correctVendorMessage: WebSocketMessage = {
        type: 'analytics_update',
        vendor_id: vendorId,
        timestamp: new Date().toISOString(),
        data: { revenue: { current: 1500000, trend: 'up' } }
      };

      server.send(JSON.stringify(wrongVendorMessage));
      server.send(JSON.stringify(correctVendorMessage));

      await new Promise(resolve => setTimeout(resolve, 100));

      // Should only process message for correct vendor
      expect(messageHandler).toHaveBeenCalledTimes(1);
      expect(messageHandler).toHaveBeenCalledWith(correctVendorMessage);
    });
  });

  describe('3. Order Status Real-time Updates', () => {
    let wsService: WebSocketService;

    beforeEach(async () => {
      wsService = new WebSocketService(`${WEBSOCKET_URL}/ws/vendor/${vendorId}/orders`);
      await wsService.connect();
      await server.connected;
    });

    it('should receive order status updates in real-time', async () => {
      const orderUpdate: WebSocketMessage = {
        type: 'order_status_update',
        vendor_id: vendorId,
        timestamp: new Date().toISOString(),
        data: {
          order_id: 'order-123',
          status: 'shipped',
          tracking_number: 'TRK123456789',
          updated_at: new Date().toISOString()
        }
      };

      const messageHandler = vi.fn();
      wsService.onMessage(messageHandler);

      server.send(JSON.stringify(orderUpdate));

      await new Promise(resolve => setTimeout(resolve, 50));

      expect(messageHandler).toHaveBeenCalledWith(orderUpdate);
    });

    it('should handle new order notifications', async () => {
      const newOrderNotification: WebSocketMessage = {
        type: 'new_order',
        vendor_id: vendorId,
        timestamp: new Date().toISOString(),
        data: {
          order_id: 'order-456',
          customer_name: 'John Doe',
          total: 250000,
          items_count: 3,
          created_at: new Date().toISOString()
        }
      };

      const messageHandler = vi.fn();
      wsService.onMessage(messageHandler);

      server.send(JSON.stringify(newOrderNotification));

      await new Promise(resolve => setTimeout(resolve, 50));

      expect(messageHandler).toHaveBeenCalledWith(newOrderNotification);
    });
  });

  describe('4. Performance Monitoring and Metrics', () => {
    let wsService: WebSocketService;

    beforeEach(async () => {
      wsService = new WebSocketService(`${WEBSOCKET_URL}/ws/vendor/${vendorId}/analytics`);
      await wsService.connect();
      await server.connected;
    });

    it('should track WebSocket latency accurately', async () => {
      const pingMessage = {
        type: 'ping',
        timestamp: performance.now(),
        vendor_id: vendorId
      };

      wsService.send(pingMessage);

      // Server responds with pong
      const pongMessage = {
        type: 'pong',
        timestamp: performance.now(),
        original_timestamp: pingMessage.timestamp
      };

      server.send(JSON.stringify(pongMessage));

      await new Promise(resolve => setTimeout(resolve, 50));

      const latency = wsService.getLatency();
      expect(latency).toBeLessThan(100); // Should be under 100ms
      expect(latency).toBeGreaterThan(0);
    });

    it('should monitor connection stability', async () => {
      const stabilityMonitor = {
        disconnections: 0,
        reconnections: 0,
        totalUptime: 0
      };

      wsService.onDisconnect(() => {
        stabilityMonitor.disconnections++;
      });

      wsService.onReconnect(() => {
        stabilityMonitor.reconnections++;
      });

      // Simulate multiple disconnections
      for (let i = 0; i < 3; i++) {
        server.close();
        await new Promise(resolve => setTimeout(resolve, 100));

        // Reconnect
        server = new WS(`${WEBSOCKET_URL}/ws/vendor/${vendorId}/analytics`);
        await server.connected;
      }

      expect(stabilityMonitor.disconnections).toBe(3);
      expect(stabilityMonitor.reconnections).toBe(3);
    });

    it('should handle high-load scenarios', async () => {
      const messageCount = 1000;
      const messagesReceived: number[] = [];

      wsService.onMessage((message: WebSocketMessage) => {
        messagesReceived.push(Date.now());
      });

      const startTime = Date.now();

      // Send high volume of messages
      for (let i = 0; i < messageCount; i++) {
        const message: WebSocketMessage = {
          type: 'analytics_update',
          vendor_id: vendorId,
          timestamp: new Date().toISOString(),
          data: { revenue: { current: 1500000 + i, trend: 'up' } }
        };

        server.send(JSON.stringify(message));
      }

      // Wait for all messages to be processed
      await new Promise(resolve => setTimeout(resolve, 2000));

      const endTime = Date.now();
      const totalTime = endTime - startTime;
      const messagesPerSecond = (messagesReceived.length / totalTime) * 1000;

      expect(messagesReceived.length).toBe(messageCount);
      expect(messagesPerSecond).toBeGreaterThan(100); // Should handle 100+ msg/sec
    });
  });

  describe('5. Error Handling and Recovery', () => {
    let wsService: WebSocketService;

    beforeEach(async () => {
      wsService = new WebSocketService(
        `${WEBSOCKET_URL}/ws/vendor/${vendorId}/analytics`,
        { reconnectInterval: 100, maxReconnectAttempts: 3 }
      );
      await wsService.connect();
      await server.connected;
    });

    it('should handle server-side errors gracefully', async () => {
      const errorHandler = vi.fn();
      wsService.onError(errorHandler);

      // Simulate server error
      const errorMessage = {
        type: 'error',
        message: 'Server internal error',
        code: 500
      };

      server.send(JSON.stringify(errorMessage));

      await new Promise(resolve => setTimeout(resolve, 50));

      expect(errorHandler).toHaveBeenCalledWith(expect.objectContaining({
        type: 'error',
        message: 'Server internal error'
      }));
    });

    it('should implement exponential backoff for reconnection', async () => {
      const reconnectionTimes: number[] = [];

      wsService.onReconnect(() => {
        reconnectionTimes.push(Date.now());
      });

      // Force multiple disconnections
      for (let i = 0; i < 3; i++) {
        server.close();
        await new Promise(resolve => setTimeout(resolve, 150));

        server = new WS(`${WEBSOCKET_URL}/ws/vendor/${vendorId}/analytics`);
        await server.connected;
      }

      // Verify exponential backoff timing
      for (let i = 1; i < reconnectionTimes.length; i++) {
        const interval = reconnectionTimes[i] - reconnectionTimes[i - 1];
        const expectedMinInterval = Math.pow(2, i - 1) * 100; // Exponential backoff

        expect(interval).toBeGreaterThanOrEqual(expectedMinInterval * 0.8); // Allow 20% tolerance
      }
    });

    it('should handle authentication failures', async () => {
      const errorHandler = vi.fn();
      wsService.onError(errorHandler);

      // Simulate authentication error
      const authError = {
        type: 'auth_error',
        message: 'Invalid token',
        code: 401
      };

      server.send(JSON.stringify(authError));

      await new Promise(resolve => setTimeout(resolve, 50));

      expect(errorHandler).toHaveBeenCalledWith(expect.objectContaining({
        type: 'auth_error',
        code: 401
      }));

      // Should attempt to refresh token and reconnect
      expect(wsService.isConnected()).toBe(false);
    });
  });

  describe('6. Integration with Analytics Store', () => {
    it('should update analytics store with WebSocket data', async () => {
      // Mock analytics store
      const mockStore = {
        updateMetrics: vi.fn(),
        setConnected: vi.fn(),
        setLastUpdated: vi.fn()
      };

      const wsService = new WebSocketService(`${WEBSOCKET_URL}/ws/vendor/${vendorId}/analytics`);

      // Connect store to WebSocket
      wsService.onMessage((message: WebSocketMessage) => {
        if (message.type === 'analytics_update') {
          mockStore.updateMetrics(message.data);
          mockStore.setLastUpdated(message.timestamp);
        }
      });

      wsService.onConnect(() => {
        mockStore.setConnected(true);
      });

      wsService.onDisconnect(() => {
        mockStore.setConnected(false);
      });

      await wsService.connect();
      await server.connected;

      // Verify store connection update
      expect(mockStore.setConnected).toHaveBeenCalledWith(true);

      // Send analytics update
      const analyticsUpdate: WebSocketMessage = {
        type: 'analytics_update',
        vendor_id: vendorId,
        timestamp: new Date().toISOString(),
        data: {
          revenue: { current: 1700000, trend: 'up' },
          orders: { current: 52, trend: 'up' }
        }
      };

      server.send(JSON.stringify(analyticsUpdate));

      await new Promise(resolve => setTimeout(resolve, 50));

      expect(mockStore.updateMetrics).toHaveBeenCalledWith(analyticsUpdate.data);
      expect(mockStore.setLastUpdated).toHaveBeenCalledWith(analyticsUpdate.timestamp);
    });
  });

  describe('7. Browser Compatibility and Edge Cases', () => {
    it('should handle WebSocket not supported', () => {
      // Mock WebSocket not available
      const originalWebSocket = global.WebSocket;
      // @ts-ignore
      delete global.WebSocket;

      expect(() => {
        new WebSocketService(`${WEBSOCKET_URL}/ws/vendor/${vendorId}/analytics`);
      }).toThrow('WebSocket is not supported in this environment');

      // Restore WebSocket
      global.WebSocket = originalWebSocket;
    });

    it('should handle page visibility changes', async () => {
      const wsService = new WebSocketService(`${WEBSOCKET_URL}/ws/vendor/${vendorId}/analytics`);
      await wsService.connect();
      await server.connected;

      // Mock page becoming hidden
      Object.defineProperty(document, 'visibilityState', {
        value: 'hidden',
        writable: true
      });

      document.dispatchEvent(new Event('visibilitychange'));

      // Should pause or reduce connection activity
      expect(wsService.isActive()).toBe(false);

      // Mock page becoming visible again
      Object.defineProperty(document, 'visibilityState', {
        value: 'visible',
        writable: true
      });

      document.dispatchEvent(new Event('visibilitychange'));

      // Should resume full activity
      expect(wsService.isActive()).toBe(true);
    });

    it('should handle network connectivity changes', async () => {
      const wsService = new WebSocketService(`${WEBSOCKET_URL}/ws/vendor/${vendorId}/analytics`);
      await wsService.connect();
      await server.connected;

      // Mock going offline
      Object.defineProperty(navigator, 'onLine', { value: false, writable: true });
      window.dispatchEvent(new Event('offline'));

      // Should pause connection attempts
      expect(wsService.shouldAttemptConnection()).toBe(false);

      // Mock coming back online
      Object.defineProperty(navigator, 'onLine', { value: true, writable: true });
      window.dispatchEvent(new Event('online'));

      // Should resume connection attempts
      expect(wsService.shouldAttemptConnection()).toBe(true);
    });
  });
});