// frontend/src/tests/integration/websocket-analytics.test.ts
// TDD TESTS: WebSocket Analytics Real-time Integration
// Target: <150ms latency with reliable connection

// Jest equivalents for Vitest imports
const vi = jest;
import { websocketService, WebSocketMessage } from '../../services/websocketService';
import { useAnalyticsStore } from '../../stores/analyticsStore';

// Helper function for async waiting
const waitFor = async (condition: () => boolean, options: { timeout?: number } = {}) => {
  const timeout = options.timeout || 1000;
  const startTime = Date.now();

  while (!condition()) {
    if (Date.now() - startTime > timeout) {
      throw new Error(`waitFor timeout after ${timeout}ms`);
    }
    await new Promise(resolve => setTimeout(resolve, 10));
  }
};

// Mock WebSocket
class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  readyState = MockWebSocket.CONNECTING;
  url: string;
  onopen?: (event: Event) => void;
  onclose?: (event: CloseEvent) => void;
  onmessage?: (event: MessageEvent) => void;
  onerror?: (event: Event) => void;

  constructor(url: string) {
    this.url = url;
    // Simulate connection after a short delay
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN;
      this.onopen?.(new Event('open'));
    }, 10);
  }

  send(data: string) {
    // Simulate message sending
    console.log('WebSocket mock send:', data);
  }

  close(code?: number, reason?: string) {
    this.readyState = MockWebSocket.CLOSED;
    const closeEvent = new CloseEvent('close', { code, reason });
    this.onclose?.(closeEvent);
  }

  // Helper method to simulate receiving messages
  simulateMessage(data: any) {
    if (this.readyState === MockWebSocket.OPEN) {
      const messageEvent = new MessageEvent('message', {
        data: JSON.stringify(data)
      });
      this.onmessage?.(messageEvent);
    }
  }
}

// Mock localStorage
const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
};

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage
});

// Mock global WebSocket
(global as any).WebSocket = MockWebSocket;

describe('WebSocket Analytics Integration', () => {
  let mockWebSocket: MockWebSocket;

  beforeEach(() => {
    // Reset analytics store
    useAnalyticsStore.getState().setMetrics(null);
    useAnalyticsStore.getState().setConnected(false);
    useAnalyticsStore.getState().setLoading(false);

    // Mock JWT token
    mockLocalStorage.getItem.mockReturnValue('mock-jwt-token');

    // Clean up any existing connections
    websocketService.disconnect();
  });

  afterEach(() => {
    websocketService.disconnect();
    vi.clearAllMocks();
  });

  describe('RED TESTS (TDD Phase 1): Connection Establishment', () => {
    it('should fail to connect without JWT token', async () => {
      // RED: Test should fail initially
      mockLocalStorage.getItem.mockReturnValue(null);

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

      await websocketService.connect('test-vendor-id');

      expect(consoleSpy).toHaveBeenCalledWith(
        'No JWT token found for WebSocket authentication'
      );
      expect(websocketService.isConnected()).toBe(false);

      consoleSpy.mockRestore();
    });

    it('should fail to connect with invalid WebSocket URL format', async () => {
      // RED: Test should fail with malformed URL
      const invalidService = new (websocketService.constructor as any)({
        url: 'invalid-url'
      });

      let connectionError = false;
      try {
        await invalidService.connect('test-vendor-id');
      } catch (error) {
        connectionError = true;
      }

      // This should eventually fail due to invalid URL
      expect(connectionError || !invalidService.isConnected()).toBe(true);
    });

    it('should fail to receive analytics data before connection', async () => {
      // RED: Store should not have data before connection
      const store = useAnalyticsStore.getState();

      expect(store.metrics).toBeNull();
      expect(store.isConnected).toBe(false);
      expect(store.topProducts).toEqual([]);
    });
  });

  describe('GREEN TESTS (TDD Phase 2): Basic Functionality', () => {
    it('should establish WebSocket connection with JWT token', async () => {
      // GREEN: Implement basic connection
      await websocketService.connect('test-vendor-id');

      await waitFor(() => {
        expect(websocketService.isConnected()).toBe(true);
      }, { timeout: 1000 });

      expect(useAnalyticsStore.getState().isConnected).toBe(true);
    });

    it('should receive and process analytics data via WebSocket', async () => {
      // GREEN: Implement data reception
      await websocketService.connect('test-vendor-id');

      await waitFor(() => {
        expect(websocketService.isConnected()).toBe(true);
      });

      // Simulate receiving analytics data
      const mockAnalyticsData = {
        type: 'analytics_update',
        data: {
          metrics: {
            revenue: {
              current: 12750000,
              previous: 9850000,
              trend: 'up' as const,
              percentage: 29.4
            },
            orders: {
              current: 156,
              previous: 134,
              trend: 'up' as const,
              percentage: 16.4
            },
            products: {
              total: 45,
              active: 42,
              lowStock: 8,
              outOfStock: 3
            },
            customers: {
              total: 89,
              new: 23,
              returning: 66
            }
          },
          topProducts: [{
            id: '1',
            name: 'Test Product',
            sales: 23,
            revenue: 2050000,
            image: '/test.jpg',
            trend: 'up' as const
          }]
        },
        timestamp: new Date().toISOString()
      };

      // Get mock WebSocket instance and simulate message
      const wsInstance = (websocketService as any).ws as MockWebSocket;
      wsInstance.simulateMessage(mockAnalyticsData);

      await waitFor(() => {
        const store = useAnalyticsStore.getState();
        expect(store.metrics).not.toBeNull();
        expect(store.metrics?.revenue.current).toBe(12750000);
        expect(store.topProducts).toHaveLength(1);
        expect(store.topProducts[0].name).toBe('Test Product');
      });
    });

    it('should track WebSocket latency under 150ms', async () => {
      // GREEN: Implement latency tracking
      await websocketService.connect('test-vendor-id');

      await waitFor(() => {
        expect(websocketService.isConnected()).toBe(true);
      });

      // Send a message and track timing
      const startTime = performance.now();
      const message: WebSocketMessage = {
        type: 'connection_status',
        data: { type: 'ping' },
        timestamp: new Date().toISOString()
      };

      websocketService.send(message);

      // Simulate pong response
      const wsInstance = (websocketService as any).ws as MockWebSocket;
      wsInstance.simulateMessage({
        type: 'connection_status',
        data: { type: 'pong' },
        timestamp: new Date().toISOString()
      });

      const latency = websocketService.getAverageLatency();
      expect(latency).toBeLessThan(150); // Target: <150ms
    });
  });

  describe('REFACTOR TESTS (TDD Phase 3): Performance and Reliability', () => {
    it('should handle connection failures gracefully with auto-reconnect', async () => {
      // REFACTOR: Test reconnection logic
      await websocketService.connect('test-vendor-id');

      await waitFor(() => {
        expect(websocketService.isConnected()).toBe(true);
      });

      // Simulate connection loss
      const wsInstance = (websocketService as any).ws as MockWebSocket;
      wsInstance.close(1006, 'Connection lost');

      expect(websocketService.isConnected()).toBe(false);
      expect(useAnalyticsStore.getState().isConnected).toBe(false);

      // Should attempt to reconnect
      await waitFor(() => {
        expect(websocketService.getConnectionState()).toBe('connecting');
      }, { timeout: 5000 });
    });

    it('should queue messages when disconnected and send on reconnection', async () => {
      // REFACTOR: Test message queuing
      await websocketService.connect('test-vendor-id');

      // Disconnect
      websocketService.disconnect();

      // Send message while disconnected
      const message: WebSocketMessage = {
        type: 'analytics_update',
        data: { test: true },
        timestamp: new Date().toISOString()
      };

      websocketService.send(message);

      // Message should be queued (internal state check)
      const messageQueue = (websocketService as any).messageQueue;
      expect(messageQueue.length).toBeGreaterThan(0);

      // Reconnect
      await websocketService.connect('test-vendor-id');

      await waitFor(() => {
        expect(websocketService.isConnected()).toBe(true);
      });

      // Queue should be processed (emptied)
      expect(messageQueue.length).toBe(0);
    });

    it('should maintain optimal performance with multiple rapid updates', async () => {
      // REFACTOR: Test performance under load
      await websocketService.connect('test-vendor-id');

      await waitFor(() => {
        expect(websocketService.isConnected()).toBe(true);
      });

      const wsInstance = (websocketService as any).ws as MockWebSocket;
      const updateCount = 50;
      const startTime = performance.now();

      // Send multiple rapid updates
      for (let i = 0; i < updateCount; i++) {
        wsInstance.simulateMessage({
          type: 'analytics_update',
          data: {
            metrics: {
              revenue: { current: 1000000 + i * 1000, previous: 900000, trend: 'up', percentage: 10 },
              orders: { current: 100 + i, previous: 90, trend: 'up', percentage: 10 },
              products: { total: 50, active: 45, lowStock: 5, outOfStock: 0 },
              customers: { total: 80 + i, new: 10, returning: 70 }
            }
          },
          timestamp: new Date().toISOString()
        });
      }

      const processingTime = performance.now() - startTime;

      await waitFor(() => {
        const store = useAnalyticsStore.getState();
        expect(store.metrics?.revenue.current).toBe(1000000 + (updateCount - 1) * 1000);
      });

      // Should handle updates efficiently
      expect(processingTime).toBeLessThan(100); // <100ms for 50 updates
    });

    it('should integrate with analytics store for real-time updates', async () => {
      // REFACTOR: Test store integration
      await websocketService.connect('test-vendor-id');

      await waitFor(() => {
        expect(websocketService.isConnected()).toBe(true);
      });

      // Send analytics update
      const wsInstance = (websocketService as any).ws as MockWebSocket;

      wsInstance.simulateMessage({
        type: 'analytics_update',
        data: {
          metrics: {
            revenue: {
              current: 15000000,
              previous: 12000000,
              trend: 'up',
              percentage: 25.0
            },
            orders: {
              current: 200,
              previous: 160,
              trend: 'up',
              percentage: 25.0
            },
            products: {
              total: 50,
              active: 48,
              lowStock: 5,
              outOfStock: 2
            },
            customers: {
              total: 120,
              new: 30,
              returning: 90
            }
          }
        },
        timestamp: new Date().toISOString()
      });

      // Should update store with new metrics
      await waitFor(() => {
        const store = useAnalyticsStore.getState();
        expect(store.metrics?.orders.current).toBe(200);
        expect(store.metrics?.revenue.current).toBe(15000000);
        expect(store.metrics?.revenue.trend).toBe('up');
      });
    });
  });

  describe('Error Handling and Edge Cases', () => {
    it('should handle malformed WebSocket messages gracefully', async () => {
      await websocketService.connect('test-vendor-id');

      await waitFor(() => {
        expect(websocketService.isConnected()).toBe(true);
      });

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      const wsInstance = (websocketService as any).ws as MockWebSocket;

      // Simulate malformed message
      const malformedEvent = new MessageEvent('message', {
        data: 'invalid-json-data'
      });
      wsInstance.onmessage?.(malformedEvent);

      expect(consoleSpy).toHaveBeenCalledWith(
        'Failed to parse WebSocket message:',
        expect.any(Error)
      );

      consoleSpy.mockRestore();
    });

    it('should respect maximum reconnection attempts', async () => {
      const limitedService = new (websocketService.constructor as any)({
        maxReconnectAttempts: 2,
        reconnectInterval: 100
      });

      // Mock to always fail connection
      const mockFailingWebSocket = class extends MockWebSocket {
        constructor(url: string) {
          super(url);
          setTimeout(() => {
            this.readyState = MockWebSocket.CLOSED;
            this.onclose?.(new CloseEvent('close', { code: 1006 }));
          }, 10);
        }
      };

      (global as any).WebSocket = mockFailingWebSocket;

      await limitedService.connect('test-vendor-id');

      // Should stop trying after max attempts
      await waitFor(() => {
        expect(limitedService.isConnected()).toBe(false);
      }, { timeout: 1000 });

      // Restore original mock
      (global as any).WebSocket = MockWebSocket;
    });
  });
});