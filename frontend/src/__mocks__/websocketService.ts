// Mock WebSocket Service for tests
// Prevents real WebSocket connections during testing

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

export class WebSocketService {
  private isConnected = false;
  private listeners: Map<string, Function[]> = new Map();
  private mockMessages: WebSocketMessage[] = [];
  private config: Partial<WebSocketConfig>;

  constructor(url?: string, config?: Partial<WebSocketConfig>) {
    this.config = {
      url: url || 'ws://localhost:8000',
      reconnectInterval: 1000,
      maxReconnectAttempts: 5,
      heartbeatInterval: 15000,
      ...config,
    };
  }

  connect = jest.fn().mockImplementation(async (vendorId?: string) => {
    this.isConnected = true;
    this.emit('connected', { connectTime: 10 });
    return Promise.resolve();
  });

  disconnect = jest.fn().mockImplementation(() => {
    this.isConnected = false;
    this.emit('disconnected', {});
  });

  send = jest.fn().mockImplementation((message: WebSocketMessage) => {
    // Simulate sending message
    this.mockMessages.push(message);
  });

  // Event management
  on = jest.fn().mockImplementation((event: string, callback: Function) => {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);
  });

  off = jest.fn().mockImplementation((event: string, callback: Function) => {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      const index = eventListeners.indexOf(callback);
      if (index > -1) {
        eventListeners.splice(index, 1);
      }
    }
  });

  emit(event: string, data: any) {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      eventListeners.forEach(callback => callback(data));
    }
  }

  // Mock methods for testing
  simulateMessage(message: WebSocketMessage) {
    this.emit('message', message);
  }

  simulateConnectionError() {
    this.isConnected = false;
    this.emit('error', new Error('Mock connection error'));
  }

  getConnectionStatus() {
    return this.isConnected;
  }

  // Reset mock state
  resetMock() {
    this.isConnected = false;
    this.listeners.clear();
    this.mockMessages = [];
    jest.clearAllMocks();
  }
}

// Create singleton instance
const mockWebSocketService = new WebSocketService();

// Export the mock instance and constructor
export default mockWebSocketService;

// Hook mock for tests
export const useWebSocket = jest.fn().mockReturnValue({
  isConnected: false,
  connect: mockWebSocketService.connect,
  disconnect: mockWebSocketService.disconnect,
  send: mockWebSocketService.send,
  on: mockWebSocketService.on,
  off: mockWebSocketService.off,
});