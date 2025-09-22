import { useState, useEffect, useCallback, useRef } from 'react';
import { debounce } from 'lodash-es';

interface UseAutoSaveReturn<T> {
  savedData: T | null;
  autoSave: (data: T) => void;
  clearSavedData: () => void;
  lastSaved: Date | null;
  isSaving: boolean;
}

export const useAutoSave = <T>(
  key: string,
  saveInterval: number = 5000 // 5 seconds default
): UseAutoSaveReturn<T> => {
  const [savedData, setSavedData] = useState<T | null>(null);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  // Store debounced save function
  const debouncedSave = useRef<((data: T) => void) | null>(null);

  // Load saved data on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(key);
      if (stored) {
        const parsed = JSON.parse(stored);
        setSavedData(parsed.data);
        setLastSaved(new Date(parsed.timestamp));
      }
    } catch (error) {
      console.warn('Failed to load auto-saved data:', error);
      localStorage.removeItem(key); // Clean up corrupted data
    }
  }, [key]);

  // Create debounced save function
  useEffect(() => {
    debouncedSave.current = debounce(async (data: T) => {
      setIsSaving(true);

      try {
        const saveData = {
          data,
          timestamp: new Date().toISOString(),
          version: '1.0'
        };

        localStorage.setItem(key, JSON.stringify(saveData));
        setLastSaved(new Date());

        // Simulate network save for future API integration
        await new Promise(resolve => setTimeout(resolve, 100));

        console.log(`Auto-saved data for ${key}:`, data);
      } catch (error) {
        console.error('Auto-save failed:', error);

        // Try to clean up localStorage if it's full
        if (error instanceof Error && error.name === 'QuotaExceededError') {
          try {
            // Remove old auto-save data
            const keys = Object.keys(localStorage);
            keys.forEach(k => {
              if (k.includes('auto-save') && k !== key) {
                localStorage.removeItem(k);
              }
            });

            // Retry save
            localStorage.setItem(key, JSON.stringify({
              data,
              timestamp: new Date().toISOString(),
              version: '1.0'
            }));
          } catch (retryError) {
            console.error('Auto-save retry failed:', retryError);
          }
        }
      } finally {
        setIsSaving(false);
      }
    }, 1000); // 1 second debounce to avoid too frequent saves

    return () => {
      if (debouncedSave.current) {
        debouncedSave.current.cancel();
      }
    };
  }, [key]);

  // Auto-save function
  const autoSave = useCallback((data: T) => {
    if (debouncedSave.current) {
      debouncedSave.current(data);
    }
  }, []);

  // Clear saved data
  const clearSavedData = useCallback(() => {
    try {
      localStorage.removeItem(key);
      setSavedData(null);
      setLastSaved(null);
      console.log(`Cleared auto-saved data for ${key}`);
    } catch (error) {
      console.error('Failed to clear auto-saved data:', error);
    }
  }, [key]);

  // Periodic save (backup mechanism)
  useEffect(() => {
    if (saveInterval > 0) {
      const interval = setInterval(() => {
        if (savedData && debouncedSave.current) {
          debouncedSave.current(savedData);
        }
      }, saveInterval);

      return () => clearInterval(interval);
    }
  }, [savedData, saveInterval]);

  return {
    savedData,
    autoSave,
    clearSavedData,
    lastSaved,
    isSaving
  };
};

// Utility functions for auto-save management
export const autoSaveUtils = {
  // Check if auto-save data exists
  hasAutoSaveData(key: string): boolean {
    try {
      const stored = localStorage.getItem(key);
      return !!stored;
    } catch {
      return false;
    }
  },

  // Get auto-save timestamp
  getAutoSaveTimestamp(key: string): Date | null {
    try {
      const stored = localStorage.getItem(key);
      if (stored) {
        const parsed = JSON.parse(stored);
        return new Date(parsed.timestamp);
      }
    } catch (error) {
      console.warn('Failed to get auto-save timestamp:', error);
    }
    return null;
  },

  // Clean up old auto-save data
  cleanupOldAutoSaves(maxAge: number = 7 * 24 * 60 * 60 * 1000): void { // 7 days default
    try {
      const keys = Object.keys(localStorage);
      const now = Date.now();

      keys.forEach(key => {
        if (key.includes('auto-save') || key.includes('draft')) {
          try {
            const stored = localStorage.getItem(key);
            if (stored) {
              const parsed = JSON.parse(stored);
              const timestamp = new Date(parsed.timestamp).getTime();

              if (now - timestamp > maxAge) {
                localStorage.removeItem(key);
                console.log(`Cleaned up old auto-save data: ${key}`);
              }
            }
          } catch (error) {
            // Remove corrupted data
            localStorage.removeItem(key);
          }
        }
      });
    } catch (error) {
      console.error('Failed to cleanup old auto-saves:', error);
    }
  },

  // Get storage usage
  getStorageUsage(): { used: number; total: number; percentage: number } {
    try {
      let used = 0;
      const keys = Object.keys(localStorage);

      keys.forEach(key => {
        used += localStorage.getItem(key)?.length || 0;
      });

      // Most browsers have 5-10MB limit for localStorage
      const total = 5 * 1024 * 1024; // 5MB estimate
      const percentage = (used / total) * 100;

      return { used, total, percentage };
    } catch {
      return { used: 0, total: 0, percentage: 0 };
    }
  }
};