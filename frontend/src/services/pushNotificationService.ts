/**
 * Push Notification Service for MeStocker PWA
 * Handles push notifications for Colombian marketplace features
 */

interface NotificationPermissionResult {
  granted: boolean;
  message: string;
}

interface PushSubscriptionData {
  endpoint: string;
  keys: {
    p256dh: string;
    auth: string;
  };
  userId?: string;
  userRole?: 'customer' | 'vendor' | 'admin';
}

interface NotificationPayload {
  title: string;
  body: string;
  icon?: string;
  badge?: string;
  image?: string;
  url?: string;
  type?: 'order' | 'payment' | 'inventory' | 'promotion' | 'general';
  data?: Record<string, any>;
  actions?: Array<{
    action: string;
    title: string;
    icon?: string;
  }>;
}

class PushNotificationService {
  private vapidKey = 'BEl62iUYgUivxIkv69yViEuiBIa-Ib9-SkvMeAtA3LFgDzkrxZJjSgSnfckjBJuBkr3qBUYIHBQFLXYp5Nksh8U';
  private registration: ServiceWorkerRegistration | null = null;
  private subscription: PushSubscription | null = null;

  constructor() {
    this.initializeServiceWorker();
  }

  private async initializeServiceWorker(): Promise<void> {
    if ('serviceWorker' in navigator) {
      try {
        this.registration = await navigator.serviceWorker.ready;
        console.log('Service Worker ready for push notifications');
      } catch (error) {
        console.error('Error initializing service worker:', error);
      }
    }
  }

  /**
   * Request notification permission from user
   */
  async requestPermission(): Promise<NotificationPermissionResult> {
    if (!('Notification' in window)) {
      return {
        granted: false,
        message: 'Este navegador no soporta notificaciones'
      };
    }

    let permission = Notification.permission;

    if (permission === 'default') {
      permission = await Notification.requestPermission();
    }

    if (permission === 'granted') {
      return {
        granted: true,
        message: 'Permisos de notificación concedidos'
      };
    } else if (permission === 'denied') {
      return {
        granted: false,
        message: 'Permisos de notificación denegados. Habilita las notificaciones en la configuración del navegador.'
      };
    } else {
      return {
        granted: false,
        message: 'Permisos de notificación no concedidos'
      };
    }
  }

  /**
   * Subscribe user to push notifications
   */
  async subscribe(userId?: string, userRole?: string): Promise<PushSubscriptionData | null> {
    if (!this.registration) {
      console.error('Service Worker not registered');
      return null;
    }

    try {
      // Check if already subscribed
      this.subscription = await this.registration.pushManager.getSubscription();

      if (!this.subscription) {
        // Create new subscription
        this.subscription = await this.registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: this.urlBase64ToUint8Array(this.vapidKey)
        });
      }

      // Convert subscription to our format
      const subscriptionData: PushSubscriptionData = {
        endpoint: this.subscription.endpoint,
        keys: {
          p256dh: this.arrayBufferToBase64(this.subscription.getKey('p256dh')!),
          auth: this.arrayBufferToBase64(this.subscription.getKey('auth')!)
        },
        userId,
        userRole: userRole as any
      };

      // Save subscription to backend
      await this.saveSubscriptionToServer(subscriptionData);

      console.log('Push notification subscription successful');
      return subscriptionData;
    } catch (error) {
      console.error('Error subscribing to push notifications:', error);
      return null;
    }
  }

  /**
   * Unsubscribe from push notifications
   */
  async unsubscribe(): Promise<boolean> {
    if (!this.subscription) {
      return true;
    }

    try {
      await this.subscription.unsubscribe();
      await this.removeSubscriptionFromServer();
      this.subscription = null;
      console.log('Push notification unsubscription successful');
      return true;
    } catch (error) {
      console.error('Error unsubscribing from push notifications:', error);
      return false;
    }
  }

  /**
   * Check if user is subscribed to push notifications
   */
  async isSubscribed(): Promise<boolean> {
    if (!this.registration) {
      return false;
    }

    try {
      this.subscription = await this.registration.pushManager.getSubscription();
      return this.subscription !== null;
    } catch (error) {
      console.error('Error checking subscription status:', error);
      return false;
    }
  }

  /**
   * Show local notification (for testing or fallback)
   */
  async showLocalNotification(payload: NotificationPayload): Promise<void> {
    if (!('Notification' in window) || Notification.permission !== 'granted') {
      console.warn('Notification permission not granted');
      return;
    }

    const options: NotificationOptions = {
      body: payload.body,
      icon: payload.icon || '/pwa-192x192.png',
      badge: payload.badge || '/pwa-192x192.png',
      image: payload.image,
      tag: payload.type || 'general',
      vibrate: [100, 50, 100],
      data: {
        url: payload.url || '/',
        type: payload.type || 'general',
        ...payload.data
      },
      actions: payload.actions || [],
      requireInteraction: payload.type === 'payment' || payload.type === 'order'
    };

    new Notification(payload.title, options);
  }

  /**
   * Send push notification through server
   */
  async sendPushNotification(
    targetUsers: string[],
    payload: NotificationPayload
  ): Promise<boolean> {
    try {
      const response = await fetch('/api/v1/notifications/push', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          targetUsers,
          payload
        })
      });

      return response.ok;
    } catch (error) {
      console.error('Error sending push notification:', error);
      return false;
    }
  }

  /**
   * Subscribe to specific notification topics for Colombian features
   */
  async subscribeToTopics(topics: string[]): Promise<boolean> {
    try {
      const response = await fetch('/api/v1/notifications/topics/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ topics })
      });

      return response.ok;
    } catch (error) {
      console.error('Error subscribing to topics:', error);
      return false;
    }
  }

  /**
   * Unsubscribe from notification topics
   */
  async unsubscribeFromTopics(topics: string[]): Promise<boolean> {
    try {
      const response = await fetch('/api/v1/notifications/topics/unsubscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ topics })
      });

      return response.ok;
    } catch (error) {
      console.error('Error unsubscribing from topics:', error);
      return false;
    }
  }

  /**
   * Get available notification topics for Colombian market
   */
  getColombianTopics(): Array<{ id: string; name: string; description: string }> {
    return [
      {
        id: 'orders-all',
        name: 'Todos los Pedidos',
        description: 'Recibe notificaciones de todos los pedidos'
      },
      {
        id: 'orders-vendor',
        name: 'Pedidos de Vendedor',
        description: 'Notificaciones cuando recibas nuevos pedidos'
      },
      {
        id: 'payments-confirmed',
        name: 'Pagos Confirmados',
        description: 'Notificaciones de pagos exitosos'
      },
      {
        id: 'payments-failed',
        name: 'Pagos Fallidos',
        description: 'Notificaciones de pagos rechazados'
      },
      {
        id: 'inventory-low',
        name: 'Inventario Bajo',
        description: 'Alerta cuando el stock esté bajo'
      },
      {
        id: 'inventory-updates',
        name: 'Actualizaciones de Inventario',
        description: 'Cambios en el inventario de productos'
      },
      {
        id: 'promotions-bucaramanga',
        name: 'Promociones Bucaramanga',
        description: 'Ofertas especiales en tu ciudad'
      },
      {
        id: 'system-maintenance',
        name: 'Mantenimiento del Sistema',
        description: 'Notificaciones de mantenimiento programado'
      }
    ];
  }

  /**
   * Colombian-specific notification templates
   */
  getColombianNotificationTemplates() {
    return {
      newOrder: (orderNumber: string, amount: number): NotificationPayload => ({
        title: '🛒 Nuevo Pedido Recibido',
        body: `Pedido #${orderNumber} por $${amount.toLocaleString('es-CO')} COP`,
        type: 'order',
        icon: '/pwa-192x192.png',
        url: `/orders/${orderNumber}`,
        actions: [
          { action: 'view', title: 'Ver Pedido' },
          { action: 'process', title: 'Procesar' }
        ]
      }),

      paymentConfirmed: (amount: number, method: string): NotificationPayload => ({
        title: '💳 Pago Confirmado',
        body: `Pago de $${amount.toLocaleString('es-CO')} COP via ${method}`,
        type: 'payment',
        icon: '/pwa-192x192.png',
        actions: [
          { action: 'view', title: 'Ver Detalle' },
          { action: 'receipt', title: 'Ver Recibo' }
        ]
      }),

      lowInventory: (productName: string, stock: number): NotificationPayload => ({
        title: '📦 Stock Bajo',
        body: `${productName} - Solo quedan ${stock} unidades`,
        type: 'inventory',
        icon: '/pwa-192x192.png',
        actions: [
          { action: 'restock', title: 'Reabastecer' },
          { action: 'view', title: 'Ver Producto' }
        ]
      }),

      promotionBucaramanga: (title: string, discount: number): NotificationPayload => ({
        title: '🎉 Oferta Especial Bucaramanga',
        body: `${title} - ${discount}% de descuento`,
        type: 'promotion',
        icon: '/pwa-192x192.png',
        actions: [
          { action: 'view', title: 'Ver Oferta' },
          { action: 'share', title: 'Compartir' }
        ]
      })
    };
  }

  // Utility methods
  private urlBase64ToUint8Array(base64String: string): Uint8Array {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/\-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }

  private arrayBufferToBase64(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
  }

  private async saveSubscriptionToServer(subscription: PushSubscriptionData): Promise<void> {
    try {
      await fetch('/api/v1/notifications/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(subscription)
      });
    } catch (error) {
      console.error('Error saving subscription to server:', error);
    }
  }

  private async removeSubscriptionFromServer(): Promise<void> {
    try {
      await fetch('/api/v1/notifications/unsubscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
    } catch (error) {
      console.error('Error removing subscription from server:', error);
    }
  }
}

// Export singleton instance
export const pushNotificationService = new PushNotificationService();

// React hooks for push notifications
export const usePushNotifications = () => {
  return {
    requestPermission: () => pushNotificationService.requestPermission(),
    subscribe: (userId?: string, userRole?: string) =>
      pushNotificationService.subscribe(userId, userRole),
    unsubscribe: () => pushNotificationService.unsubscribe(),
    isSubscribed: () => pushNotificationService.isSubscribed(),
    showLocalNotification: (payload: NotificationPayload) =>
      pushNotificationService.showLocalNotification(payload),
    subscribeToTopics: (topics: string[]) =>
      pushNotificationService.subscribeToTopics(topics),
    unsubscribeFromTopics: (topics: string[]) =>
      pushNotificationService.unsubscribeFromTopics(topics),
    getColombianTopics: () => pushNotificationService.getColombianTopics(),
    getTemplates: () => pushNotificationService.getColombianNotificationTemplates()
  };
};