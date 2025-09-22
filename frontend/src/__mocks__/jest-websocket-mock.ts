// Mock for jest-websocket-mock library

export default class MockWS {
  static clean() {
    // Mock cleanup method
  }

  constructor(url?: string, options?: any) {
    // Mock constructor
  }

  on(event: string, handler: Function) {
    // Mock event listener
  }

  send(data: any) {
    // Mock send method
  }

  close() {
    // Mock close method
  }

  // Add any other methods that might be used
  emit(event: string, data?: any) {
    // Mock emit method
  }

  connected = true;
  url = 'ws://localhost:8000';
}

export { MockWS as WS };