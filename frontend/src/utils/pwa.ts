/**
 * PWA Utilities for MeStocker
 * Handles service worker registration, app installation, and offline capabilities
 */

import { Workbox } from 'workbox-window';

export interface PWAInstallPrompt {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

class PWAManager {
  private wb: Workbox | null = null;
  private installPrompt: PWAInstallPrompt | null = null;
  private isOffline = false;
  private offlineCallbacks: (() => void)[] = [];
  private onlineCallbacks: (() => void)[] = [];

  constructor() {
    this.initServiceWorker();
    this.initInstallPrompt();
    this.initNetworkStatusListener();
  }

  private initServiceWorker() {
    if ('serviceWorker' in navigator) {
      this.wb = new Workbox('/sw.js');

      // Service worker update available
      this.wb.addEventListener('waiting', (event) => {
        console.log('Nueva versión de la app disponible');
        this.showUpdateNotification();
      });

      // Service worker activated
      this.wb.addEventListener('controlling', (event) => {
        console.log('Service worker actualizado y activo');
        window.location.reload();
      });

      // Register service worker
      this.wb.register()
        .then((registration) => {
          console.log('Service Worker registrado exitosamente:', registration);
        })
        .catch((error) => {
          console.log('Error registrando Service Worker:', error);
        });
    }
  }

  private initInstallPrompt() {
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      this.installPrompt = e as any;
      console.log('PWA installation prompt ready');
      this.showInstallBanner();
    });

    window.addEventListener('appinstalled', (e) => {
      console.log('PWA installed successfully');
      this.hideInstallBanner();
    });
  }

  private initNetworkStatusListener() {
    window.addEventListener('online', () => {
      this.isOffline = false;
      this.onlineCallbacks.forEach(callback => callback());
      console.log('Conexión restaurada');
    });

    window.addEventListener('offline', () => {
      this.isOffline = true;
      this.offlineCallbacks.forEach(callback => callback());
      console.log('Sin conexión - modo offline activado');
    });

    this.isOffline = !navigator.onLine;
  }

  public async installApp(): Promise<boolean> {
    if (!this.installPrompt) {
      console.log('Install prompt not available');
      return false;
    }

    try {
      await this.installPrompt.prompt();
      const choiceResult = await this.installPrompt.userChoice;

      if (choiceResult.outcome === 'accepted') {
        console.log('User accepted app installation');
        this.installPrompt = null;
        return true;
      } else {
        console.log('User dismissed app installation');
        return false;
      }
    } catch (error) {
      console.error('Error during app installation:', error);
      return false;
    }
  }

  public isInstallable(): boolean {
    return this.installPrompt !== null;
  }

  public isAppInstalled(): boolean {
    return window.matchMedia('(display-mode: standalone)').matches ||
           (window.navigator as any).standalone === true;
  }

  public getOfflineStatus(): boolean {
    return this.isOffline;
  }

  public onOffline(callback: () => void): void {
    this.offlineCallbacks.push(callback);
  }

  public onOnline(callback: () => void): void {
    this.onlineCallbacks.push(callback);
  }

  private showInstallBanner(): void {
    // Create install banner for mobile users
    const banner = document.createElement('div');
    banner.id = 'pwa-install-banner';
    banner.className = 'fixed bottom-4 left-4 right-4 bg-blue-600 text-white p-4 rounded-lg shadow-lg z-50 md:max-w-sm md:left-auto';
    banner.innerHTML = `
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
          </svg>
          <div>
            <p class="font-semibold text-sm">¡Instala MeStocker!</p>
            <p class="text-xs opacity-90">Acceso rápido desde tu inicio</p>
          </div>
        </div>
        <div class="flex space-x-2">
          <button id="pwa-install-btn" class="bg-white text-blue-600 px-3 py-1 rounded text-sm font-semibold">
            Instalar
          </button>
          <button id="pwa-dismiss-btn" class="text-white opacity-75 hover:opacity-100">
            ✕
          </button>
        </div>
      </div>
    `;

    document.body.appendChild(banner);

    // Add event listeners
    document.getElementById('pwa-install-btn')?.addEventListener('click', () => {
      this.installApp();
    });

    document.getElementById('pwa-dismiss-btn')?.addEventListener('click', () => {
      this.hideInstallBanner();
    });

    // Auto-hide after 10 seconds
    setTimeout(() => {
      this.hideInstallBanner();
    }, 10000);
  }

  private hideInstallBanner(): void {
    const banner = document.getElementById('pwa-install-banner');
    if (banner) {
      banner.remove();
    }
  }

  private showUpdateNotification(): void {
    const notification = document.createElement('div');
    notification.id = 'pwa-update-notification';
    notification.className = 'fixed top-4 left-4 right-4 bg-green-600 text-white p-4 rounded-lg shadow-lg z-50 md:max-w-sm md:left-auto';
    notification.innerHTML = `
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
          <div>
            <p class="font-semibold text-sm">Nueva versión disponible</p>
            <p class="text-xs opacity-90">Actualiza para nuevas funciones</p>
          </div>
        </div>
        <button id="pwa-update-btn" class="bg-white text-green-600 px-3 py-1 rounded text-sm font-semibold">
          Actualizar
        </button>
      </div>
    `;

    document.body.appendChild(notification);

    document.getElementById('pwa-update-btn')?.addEventListener('click', () => {
      if (this.wb) {
        this.wb.messageSkipWaiting();
      }
      notification.remove();
    });

    // Auto-hide after 15 seconds
    setTimeout(() => {
      if (notification.parentNode) {
        notification.remove();
      }
    }, 15000);
  }

  public async shareContent(shareData: {
    title: string;
    text: string;
    url: string;
  }): Promise<boolean> {
    if (navigator.share) {
      try {
        await navigator.share(shareData);
        return true;
      } catch (error) {
        console.log('Error sharing:', error);
        return false;
      }
    } else {
      // Fallback to clipboard for unsupported browsers
      try {
        await navigator.clipboard.writeText(shareData.url);
        return true;
      } catch (error) {
        console.log('Clipboard not available');
        return false;
      }
    }
  }
}

// Export singleton instance
export const pwaManager = new PWAManager();

// Utility functions for React components
export const usePWAInstall = () => {
  return {
    isInstallable: pwaManager.isInstallable(),
    isInstalled: pwaManager.isAppInstalled(),
    install: () => pwaManager.installApp()
  };
};

export const usePWAOffline = () => {
  return {
    isOffline: pwaManager.getOfflineStatus(),
    onOffline: (callback: () => void) => pwaManager.onOffline(callback),
    onOnline: (callback: () => void) => pwaManager.onOnline(callback)
  };
};