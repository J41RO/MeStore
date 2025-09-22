// ~/src/hooks/useMobileOptimization.ts
// ---------------------------------------------------------------------------------------------
// MeStore - Mobile Optimization Hook for Touch Interfaces
// Copyright (c) 2025 Jairo. Todos los derechos reservados.
// Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
// ---------------------------------------------------------------------------------------------
//
// Nombre del Archivo: useMobileOptimization.ts
// Ruta: ~/src/hooks/useMobileOptimization.ts
// Autor: Frontend Performance AI
// Fecha de Creación: 2025-09-19
// Última Actualización: 2025-09-19
// Versión: 1.0.0
// Propósito: Optimizaciones avanzadas para móviles con 90+ Lighthouse score
//
// Mobile Features:
// - Touch gesture recognition
// - Viewport optimization
// - Performance throttling detection
// - Battery status optimization
// - Network-aware loading
// - Haptic feedback integration
// ---------------------------------------------------------------------------------------------

import { useState, useEffect, useCallback, useMemo, useRef } from 'react';

interface DeviceInfo {
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  screenSize: {
    width: number;
    height: number;
  };
  devicePixelRatio: number;
  orientation: 'portrait' | 'landscape';
  hasTouch: boolean;
  platform: string;
  browser: string;
  connectionType?: string;
  batteryLevel?: number;
  isCharging?: boolean;
}

interface TouchOptimizations {
  touchDelay: number;
  scrollThrottling: number;
  gestureMinDistance: number;
  doubleTapThreshold: number;
  longPressDelay: number;
}

interface PerformanceSettings {
  enableImageLazyLoading: boolean;
  enableVirtualScrolling: boolean;
  reducedAnimations: boolean;
  lowPowerMode: boolean;
  networkAdaptive: boolean;
}

interface GestureHandlers {
  onTouchStart: (e: TouchEvent) => void;
  onTouchMove: (e: TouchEvent) => void;
  onTouchEnd: (e: TouchEvent) => void;
  onSwipeLeft: () => void;
  onSwipeRight: () => void;
  onSwipeUp: () => void;
  onSwipeDown: () => void;
  onPinch: (scale: number) => void;
  onLongPress: () => void;
  onDoubleTap: () => void;
}

interface ViewportOptimizations {
  safeAreaTop: number;
  safeAreaBottom: number;
  safeAreaLeft: number;
  safeAreaRight: number;
  availableHeight: number;
  availableWidth: number;
  isFullscreen: boolean;
  keyboardHeight: number;
}

export const useMobileOptimization = (enabled: boolean = true) => {
  const [deviceInfo, setDeviceInfo] = useState<DeviceInfo>({
    isMobile: false,
    isTablet: false,
    isDesktop: true,
    screenSize: { width: 0, height: 0 },
    devicePixelRatio: 1,
    orientation: 'landscape',
    hasTouch: false,
    platform: '',
    browser: '',
  });

  const [performanceSettings, setPerformanceSettings] = useState<PerformanceSettings>({
    enableImageLazyLoading: true,
    enableVirtualScrolling: false,
    reducedAnimations: false,
    lowPowerMode: false,
    networkAdaptive: true,
  });

  const [viewportOptimizations, setViewportOptimizations] = useState<ViewportOptimizations>({
    safeAreaTop: 0,
    safeAreaBottom: 0,
    safeAreaLeft: 0,
    safeAreaRight: 0,
    availableHeight: 0,
    availableWidth: 0,
    isFullscreen: false,
    keyboardHeight: 0,
  });

  const touchStartRef = useRef<{ x: number; y: number; time: number } | null>(null);
  const touchTimerRef = useRef<NodeJS.Timeout>();
  const performanceObserverRef = useRef<PerformanceObserver>();
  const networkInfoRef = useRef<any>();

  // Detect device capabilities
  const detectDevice = useCallback(() => {
    const userAgent = navigator.userAgent.toLowerCase();
    const screenWidth = window.innerWidth;
    const screenHeight = window.innerHeight;

    const isMobile = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent)
      || screenWidth <= 768;
    const isTablet = /ipad|tablet|android(?!.*mobile)/i.test(userAgent)
      || (screenWidth > 768 && screenWidth <= 1024);
    const isDesktop = !isMobile && !isTablet;

    const platform = /android/i.test(userAgent) ? 'android'
      : /iphone|ipad|ipod/i.test(userAgent) ? 'ios'
      : /windows/i.test(userAgent) ? 'windows'
      : /mac/i.test(userAgent) ? 'mac'
      : 'unknown';

    const browser = /chrome/i.test(userAgent) ? 'chrome'
      : /firefox/i.test(userAgent) ? 'firefox'
      : /safari/i.test(userAgent) ? 'safari'
      : /edge/i.test(userAgent) ? 'edge'
      : 'unknown';

    return {
      isMobile,
      isTablet,
      isDesktop,
      screenSize: {
        width: screenWidth,
        height: screenHeight,
      },
      devicePixelRatio: window.devicePixelRatio || 1,
      orientation: screenWidth > screenHeight ? 'landscape' : 'portrait',
      hasTouch: 'ontouchstart' in window || navigator.maxTouchPoints > 0,
      platform,
      browser,
    };
  }, []);

  // Detect network conditions
  const detectNetworkConditions = useCallback(() => {
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      networkInfoRef.current = connection;

      const updateSettings = () => {
        const effectiveType = connection.effectiveType;
        const saveData = connection.saveData;

        setPerformanceSettings(prev => ({
          ...prev,
          enableImageLazyLoading: effectiveType === 'slow-2g' || effectiveType === '2g' || saveData,
          enableVirtualScrolling: prev.enableVirtualScrolling || effectiveType === 'slow-2g',
          lowPowerMode: saveData,
          networkAdaptive: true,
        }));

        setDeviceInfo(prev => ({
          ...prev,
          connectionType: effectiveType,
        }));
      };

      connection.addEventListener('change', updateSettings);
      updateSettings();

      return () => connection.removeEventListener('change', updateSettings);
    }
  }, []);

  // Detect battery status
  const detectBatteryStatus = useCallback(() => {
    if ('getBattery' in navigator) {
      (navigator as any).getBattery().then((battery: any) => {
        const updateBatteryInfo = () => {
          setDeviceInfo(prev => ({
            ...prev,
            batteryLevel: battery.level,
            isCharging: battery.charging,
          }));

          // Enable power optimizations when battery is low
          if (battery.level < 0.2 && !battery.charging) {
            setPerformanceSettings(prev => ({
              ...prev,
              reducedAnimations: true,
              lowPowerMode: true,
              enableVirtualScrolling: true,
            }));
          }
        };

        battery.addEventListener('levelchange', updateBatteryInfo);
        battery.addEventListener('chargingchange', updateBatteryInfo);
        updateBatteryInfo();
      });
    }
  }, []);

  // Calculate safe areas and viewport optimizations
  const calculateViewportOptimizations = useCallback(() => {
    const safeAreaTop = parseInt(getComputedStyle(document.documentElement)
      .getPropertyValue('--safe-area-inset-top') || '0');
    const safeAreaBottom = parseInt(getComputedStyle(document.documentElement)
      .getPropertyValue('--safe-area-inset-bottom') || '0');
    const safeAreaLeft = parseInt(getComputedStyle(document.documentElement)
      .getPropertyValue('--safe-area-inset-left') || '0');
    const safeAreaRight = parseInt(getComputedStyle(document.documentElement)
      .getPropertyValue('--safe-area-inset-right') || '0');

    const availableHeight = window.innerHeight - safeAreaTop - safeAreaBottom;
    const availableWidth = window.innerWidth - safeAreaLeft - safeAreaRight;

    // Detect virtual keyboard (mobile)
    const keyboardHeight = Math.max(0, window.screen.height - window.visualViewport?.height || window.innerHeight);

    setViewportOptimizations({
      safeAreaTop,
      safeAreaBottom,
      safeAreaLeft,
      safeAreaRight,
      availableHeight,
      availableWidth,
      isFullscreen: document.fullscreenElement !== null,
      keyboardHeight,
    });
  }, []);

  // Performance monitoring
  const monitorPerformance = useCallback(() => {
    if ('PerformanceObserver' in window) {
      performanceObserverRef.current = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          // Monitor long tasks that might indicate performance issues
          if (entry.entryType === 'longtask' && entry.duration > 50) {
            console.warn('Long task detected:', entry.duration + 'ms');

            // Enable performance optimizations
            setPerformanceSettings(prev => ({
              ...prev,
              reducedAnimations: true,
              enableVirtualScrolling: true,
            }));
          }

          // Monitor layout shifts
          if (entry.entryType === 'layout-shift' && (entry as any).value > 0.1) {
            console.warn('Layout shift detected:', (entry as any).value);
          }
        }
      });

      performanceObserverRef.current.observe({ entryTypes: ['longtask', 'layout-shift'] });
    }
  }, []);

  // Touch gesture recognition
  const createGestureHandlers = useCallback((callbacks: Partial<GestureHandlers> = {}): GestureHandlers => {
    const onTouchStart = (e: TouchEvent) => {
      if (e.touches.length === 1) {
        const touch = e.touches[0];
        touchStartRef.current = {
          x: touch.clientX,
          y: touch.clientY,
          time: Date.now(),
        };

        // Long press detection
        touchTimerRef.current = setTimeout(() => {
          callbacks.onLongPress?.();
          // Haptic feedback if available
          if ('vibrate' in navigator) {
            navigator.vibrate(50);
          }
        }, 500);
      }
    };

    const onTouchMove = (e: TouchEvent) => {
      if (touchTimerRef.current) {
        clearTimeout(touchTimerRef.current);
        touchTimerRef.current = undefined;
      }

      // Prevent default for better performance on mobile
      if (deviceInfo.isMobile) {
        e.preventDefault();
      }
    };

    const onTouchEnd = (e: TouchEvent) => {
      if (touchTimerRef.current) {
        clearTimeout(touchTimerRef.current);
        touchTimerRef.current = undefined;
      }

      if (!touchStartRef.current) return;

      const touch = e.changedTouches[0];
      const deltaX = touch.clientX - touchStartRef.current.x;
      const deltaY = touch.clientY - touchStartRef.current.y;
      const deltaTime = Date.now() - touchStartRef.current.time;

      const distance = Math.sqrt(deltaX ** 2 + deltaY ** 2);
      const velocity = distance / deltaTime;

      // Double tap detection
      if (deltaTime < 300 && distance < 10) {
        callbacks.onDoubleTap?.();
      }

      // Swipe detection
      if (distance > 30 && velocity > 0.3) {
        const angle = Math.atan2(deltaY, deltaX) * 180 / Math.PI;

        if (Math.abs(angle) < 45) {
          callbacks.onSwipeRight?.();
        } else if (Math.abs(angle) > 135) {
          callbacks.onSwipeLeft?.();
        } else if (angle > 45 && angle < 135) {
          callbacks.onSwipeDown?.();
        } else if (angle < -45 && angle > -135) {
          callbacks.onSwipeUp?.();
        }

        // Haptic feedback for swipe
        if ('vibrate' in navigator) {
          navigator.vibrate(30);
        }
      }

      touchStartRef.current = null;
    };

    const onPinch = (scale: number) => {
      callbacks.onPinch?.(scale);
    };

    return {
      onTouchStart,
      onTouchMove,
      onTouchEnd,
      onSwipeLeft: callbacks.onSwipeLeft || (() => {}),
      onSwipeRight: callbacks.onSwipeRight || (() => {}),
      onSwipeUp: callbacks.onSwipeUp || (() => {}),
      onSwipeDown: callbacks.onSwipeDown || (() => {}),
      onPinch,
      onLongPress: callbacks.onLongPress || (() => {}),
      onDoubleTap: callbacks.onDoubleTap || (() => {}),
    };
  }, [deviceInfo.isMobile]);

  // Touch optimizations
  const touchOptimizations = useMemo((): TouchOptimizations => {
    const baseOptimizations = {
      touchDelay: 0,
      scrollThrottling: 16,
      gestureMinDistance: 30,
      doubleTapThreshold: 300,
      longPressDelay: 500,
    };

    if (deviceInfo.isMobile) {
      return {
        ...baseOptimizations,
        touchDelay: performanceSettings.lowPowerMode ? 100 : 0,
        scrollThrottling: performanceSettings.lowPowerMode ? 32 : 16,
      };
    }

    return baseOptimizations;
  }, [deviceInfo.isMobile, performanceSettings.lowPowerMode]);

  // CSS custom properties for mobile optimizations
  const setCSSProperties = useCallback(() => {
    const root = document.documentElement;

    // Viewport units
    root.style.setProperty('--vh', `${window.innerHeight * 0.01}px`);
    root.style.setProperty('--vw', `${window.innerWidth * 0.01}px`);

    // Safe areas
    root.style.setProperty('--safe-area-top', `${viewportOptimizations.safeAreaTop}px`);
    root.style.setProperty('--safe-area-bottom', `${viewportOptimizations.safeAreaBottom}px`);
    root.style.setProperty('--safe-area-left', `${viewportOptimizations.safeAreaLeft}px`);
    root.style.setProperty('--safe-area-right', `${viewportOptimizations.safeAreaRight}px`);

    // Touch optimization classes
    if (deviceInfo.isMobile) {
      document.body.classList.add('mobile-optimized');

      if (performanceSettings.reducedAnimations) {
        document.body.classList.add('reduced-motion');
      }

      if (performanceSettings.lowPowerMode) {
        document.body.classList.add('low-power-mode');
      }
    }
  }, [deviceInfo.isMobile, performanceSettings, viewportOptimizations]);

  // Initialize mobile optimizations
  useEffect(() => {
    if (!enabled) return;

    const cleanup1 = detectNetworkConditions();
    detectBatteryStatus();
    monitorPerformance();

    const handleResize = () => {
      setDeviceInfo(detectDevice());
      calculateViewportOptimizations();
    };

    const handleOrientationChange = () => {
      // Delay to allow the viewport to settle
      setTimeout(() => {
        setDeviceInfo(detectDevice());
        calculateViewportOptimizations();
      }, 100);
    };

    // Initial detection
    setDeviceInfo(detectDevice());
    calculateViewportOptimizations();

    // Event listeners
    window.addEventListener('resize', handleResize, { passive: true });
    window.addEventListener('orientationchange', handleOrientationChange, { passive: true });

    if (window.visualViewport) {
      window.visualViewport.addEventListener('resize', calculateViewportOptimizations, { passive: true });
    }

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('orientationchange', handleOrientationChange);

      if (window.visualViewport) {
        window.visualViewport.removeEventListener('resize', calculateViewportOptimizations);
      }

      if (performanceObserverRef.current) {
        performanceObserverRef.current.disconnect();
      }

      if (touchTimerRef.current) {
        clearTimeout(touchTimerRef.current);
      }

      if (cleanup1) cleanup1();
    };
  }, [enabled, detectDevice, detectNetworkConditions, detectBatteryStatus, monitorPerformance, calculateViewportOptimizations]);

  // Update CSS properties when viewport changes
  useEffect(() => {
    setCSSProperties();
  }, [setCSSProperties]);

  // Adaptive image loading based on device conditions
  const getImageLoadingStrategy = useCallback(() => {
    if (!deviceInfo.isMobile) return 'eager';

    if (performanceSettings.lowPowerMode || deviceInfo.connectionType === 'slow-2g') {
      return 'lazy';
    }

    return 'auto';
  }, [deviceInfo.isMobile, deviceInfo.connectionType, performanceSettings.lowPowerMode]);

  // Adaptive component rendering
  const shouldRenderComponent = useCallback((componentType: 'heavy' | 'medium' | 'light') => {
    if (!deviceInfo.isMobile) return true;

    if (performanceSettings.lowPowerMode) {
      return componentType === 'light';
    }

    if (deviceInfo.connectionType === 'slow-2g') {
      return componentType !== 'heavy';
    }

    return true;
  }, [deviceInfo.isMobile, deviceInfo.connectionType, performanceSettings.lowPowerMode]);

  return {
    // Device information
    deviceInfo,
    isMobile: deviceInfo.isMobile,
    isTablet: deviceInfo.isTablet,
    isDesktop: deviceInfo.isDesktop,

    // Performance settings
    performanceSettings,
    setPerformanceSettings,

    // Viewport optimizations
    viewportOptimizations,

    // Touch handling
    touchOptimizations,
    createGestureHandlers,

    // Adaptive strategies
    getImageLoadingStrategy,
    shouldRenderComponent,

    // Utilities
    isLowPowerMode: performanceSettings.lowPowerMode,
    isSlowConnection: deviceInfo.connectionType === 'slow-2g' || deviceInfo.connectionType === '2g',
    isOnline: navigator.onLine,
  };
};