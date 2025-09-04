import { describe, it, expect, beforeEach } from '@jest/globals';
import { useAppStore } from '../appStore';

describe('AppStore Simple Tests', () => {
  it('should initialize with correct values', () => {
    const store = useAppStore.getState();
    expect(store.globalError).toBeNull();
    expect(store.hasActiveRequests).toBe(false);
  });

  it('should be able to set global error', () => {
    const { setGlobalError } = useAppStore.getState();
    setGlobalError('Test error');

    const state = useAppStore.getState();
    expect(state.globalError).toBe('Test error');
  });

  it('should be able to clear global error', () => {
    const { setGlobalError, clearGlobalError } = useAppStore.getState();

    setGlobalError('Test error');
    expect(useAppStore.getState().globalError).toBe('Test error');

    clearGlobalError();
    expect(useAppStore.getState().globalError).toBeNull();
  });
});
