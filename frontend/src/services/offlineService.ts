/**
 * Offline Service for MeStocker PWA
 * Handles offline functionality for core Colombian marketplace features
 */

interface OfflineData {
  id: string;
  type: 'order' | 'payment' | 'inventory' | 'product' | 'cart';
  data: any;
  timestamp: number;
  synced: boolean;
}

interface CartItem {
  id: string;
  productId: string;
  name: string;
  price: number;
  quantity: number;
  vendorId: string;
  image?: string;
}

interface OfflineOrder {
  id: string;
  items: CartItem[];
  total: number;
  customerInfo: {
    name: string;
    email: string;
    phone: string;
    address: string;
    city: string;
    department: string;
  };
  paymentMethod: string;
  status: 'pending' | 'processing' | 'synced';
  createdAt: number;
}

interface ProductData {
  id: string;
  name: string;
  description: string;
  price: number;
  stock: number;
  images: string[];
  category: string;
  vendorId: string;
  lastUpdated: number;
}

class OfflineService {
  private dbName = 'MeStockerOfflineDB';
  private dbVersion = 1;
  private db: IDBDatabase | null = null;
  private syncQueue: OfflineData[] = [];

  constructor() {
    this.initializeDB();
    this.setupSyncListener();
  }

  /**
   * Initialize IndexedDB for offline storage
   */
  private async initializeDB(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);

      request.onerror = () => {
        console.error('Error opening offline database');
        reject(request.error);
      };

      request.onsuccess = () => {
        this.db = request.result;
        console.log('Offline database initialized successfully');
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        // Cart store
        if (!db.objectStoreNames.contains('cart')) {
          const cartStore = db.createObjectStore('cart', { keyPath: 'id' });
          cartStore.createIndex('productId', 'productId', { unique: false });
        }

        // Orders store
        if (!db.objectStoreNames.contains('orders')) {
          const ordersStore = db.createObjectStore('orders', { keyPath: 'id' });
          ordersStore.createIndex('status', 'status', { unique: false });
          ordersStore.createIndex('timestamp', 'createdAt', { unique: false });
        }

        // Products store (for offline browsing)
        if (!db.objectStoreNames.contains('products')) {
          const productsStore = db.createObjectStore('products', { keyPath: 'id' });
          productsStore.createIndex('category', 'category', { unique: false });
          productsStore.createIndex('vendorId', 'vendorId', { unique: false });
          productsStore.createIndex('lastUpdated', 'lastUpdated', { unique: false });
        }

        // Sync queue store
        if (!db.objectStoreNames.contains('syncQueue')) {
          const syncStore = db.createObjectStore('syncQueue', { keyPath: 'id' });
          syncStore.createIndex('type', 'type', { unique: false });
          syncStore.createIndex('synced', 'synced', { unique: false });
          syncStore.createIndex('timestamp', 'timestamp', { unique: false });
        }

        // User preferences store
        if (!db.objectStoreNames.contains('preferences')) {
          db.createObjectStore('preferences', { keyPath: 'key' });
        }

        console.log('Offline database schema updated');
      };
    });
  }

  /**
   * Setup sync listener for when connection is restored
   */
  private setupSyncListener(): void {
    window.addEventListener('online', () => {
      console.log('Connection restored - starting sync process');
      this.syncOfflineData();
    });
  }

  /**
   * Save cart items for offline access
   */
  async saveCartOffline(items: CartItem[]): Promise<boolean> {
    if (!this.db) return false;

    try {
      const transaction = this.db.transaction(['cart'], 'readwrite');
      const store = transaction.objectStore('cart');

      // Clear existing cart
      await store.clear();

      // Add all items
      for (const item of items) {
        await store.add(item);
      }

      console.log(`Saved ${items.length} cart items offline`);
      return true;
    } catch (error) {
      console.error('Error saving cart offline:', error);
      return false;
    }
  }

  /**
   * Get cart items from offline storage
   */
  async getOfflineCart(): Promise<CartItem[]> {
    if (!this.db) return [];

    try {
      const transaction = this.db.transaction(['cart'], 'readonly');
      const store = transaction.objectStore('cart');
      const request = store.getAll();

      return new Promise((resolve, reject) => {
        request.onsuccess = () => {
          resolve(request.result || []);
        };
        request.onerror = () => {
          reject(request.error);
        };
      });
    } catch (error) {
      console.error('Error getting offline cart:', error);
      return [];
    }
  }

  /**
   * Save order offline when connection is not available
   */
  async saveOrderOffline(order: Omit<OfflineOrder, 'id' | 'status' | 'createdAt'>): Promise<string> {
    if (!this.db) throw new Error('Database not initialized');

    const offlineOrder: OfflineOrder = {
      ...order,
      id: `offline_order_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      status: 'pending',
      createdAt: Date.now()
    };

    try {
      const transaction = this.db.transaction(['orders', 'syncQueue'], 'readwrite');
      const ordersStore = transaction.objectStore('orders');
      const syncStore = transaction.objectStore('syncQueue');

      // Save order
      await ordersStore.add(offlineOrder);

      // Add to sync queue
      const syncItem: OfflineData = {
        id: `sync_${offlineOrder.id}`,
        type: 'order',
        data: offlineOrder,
        timestamp: Date.now(),
        synced: false
      };
      await syncStore.add(syncItem);

      console.log('Order saved offline:', offlineOrder.id);
      return offlineOrder.id;
    } catch (error) {
      console.error('Error saving order offline:', error);
      throw error;
    }
  }

  /**
   * Get offline orders
   */
  async getOfflineOrders(): Promise<OfflineOrder[]> {
    if (!this.db) return [];

    try {
      const transaction = this.db.transaction(['orders'], 'readonly');
      const store = transaction.objectStore('orders');
      const request = store.getAll();

      return new Promise((resolve, reject) => {
        request.onsuccess = () => {
          resolve(request.result || []);
        };
        request.onerror = () => {
          reject(request.error);
        };
      });
    } catch (error) {
      console.error('Error getting offline orders:', error);
      return [];
    }
  }

  /**
   * Cache products for offline browsing
   */
  async cacheProducts(products: ProductData[]): Promise<boolean> {
    if (!this.db) return false;

    try {
      const transaction = this.db.transaction(['products'], 'readwrite');
      const store = transaction.objectStore('products');

      for (const product of products) {
        product.lastUpdated = Date.now();
        await store.put(product);
      }

      console.log(`Cached ${products.length} products for offline browsing`);
      return true;
    } catch (error) {
      console.error('Error caching products:', error);
      return false;
    }
  }

  /**
   * Get cached products for offline browsing
   */
  async getCachedProducts(limit: number = 50): Promise<ProductData[]> {
    if (!this.db) return [];

    try {
      const transaction = this.db.transaction(['products'], 'readonly');
      const store = transaction.objectStore('products');
      const index = store.index('lastUpdated');
      const request = index.openCursor(null, 'prev'); // Most recent first

      return new Promise((resolve, reject) => {
        const products: ProductData[] = [];
        let count = 0;

        request.onsuccess = (event) => {
          const cursor = (event.target as IDBRequest).result;
          if (cursor && count < limit) {
            products.push(cursor.value);
            count++;
            cursor.continue();
          } else {
            resolve(products);
          }
        };

        request.onerror = () => {
          reject(request.error);
        };
      });
    } catch (error) {
      console.error('Error getting cached products:', error);
      return [];
    }
  }

  /**
   * Search cached products offline
   */
  async searchOfflineProducts(query: string, category?: string): Promise<ProductData[]> {
    const products = await this.getCachedProducts(100);
    const lowerQuery = query.toLowerCase();

    return products.filter(product => {
      const matchesQuery = product.name.toLowerCase().includes(lowerQuery) ||
                          product.description.toLowerCase().includes(lowerQuery);
      const matchesCategory = !category || product.category === category;
      return matchesQuery && matchesCategory;
    });
  }

  /**
   * Save user preferences offline
   */
  async savePreference(key: string, value: any): Promise<boolean> {
    if (!this.db) return false;

    try {
      const transaction = this.db.transaction(['preferences'], 'readwrite');
      const store = transaction.objectStore('preferences');
      await store.put({ key, value, timestamp: Date.now() });
      return true;
    } catch (error) {
      console.error('Error saving preference:', error);
      return false;
    }
  }

  /**
   * Get user preference
   */
  async getPreference(key: string): Promise<any> {
    if (!this.db) return null;

    try {
      const transaction = this.db.transaction(['preferences'], 'readonly');
      const store = transaction.objectStore('preferences');
      const request = store.get(key);

      return new Promise((resolve, reject) => {
        request.onsuccess = () => {
          resolve(request.result?.value || null);
        };
        request.onerror = () => {
          reject(request.error);
        };
      });
    } catch (error) {
      console.error('Error getting preference:', error);
      return null;
    }
  }

  /**
   * Sync offline data when connection is restored
   */
  async syncOfflineData(): Promise<void> {
    if (!this.db || !navigator.onLine) return;

    try {
      const transaction = this.db.transaction(['syncQueue'], 'readonly');
      const store = transaction.objectStore('syncQueue');
      const index = store.index('synced');
      const request = index.getAll(false);

      request.onsuccess = async () => {
        const pendingItems = request.result as OfflineData[];
        console.log(`Syncing ${pendingItems.length} offline items`);

        for (const item of pendingItems) {
          try {
            await this.syncItem(item);
            await this.markAsSynced(item.id);
          } catch (error) {
            console.error(`Error syncing item ${item.id}:`, error);
          }
        }

        console.log('Offline sync completed');
      };
    } catch (error) {
      console.error('Error during offline sync:', error);
    }
  }

  /**
   * Sync individual item
   */
  private async syncItem(item: OfflineData): Promise<void> {
    const endpoint = this.getSyncEndpoint(item.type);
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(item.data)
    });

    if (!response.ok) {
      throw new Error(`Sync failed: ${response.statusText}`);
    }

    console.log(`Successfully synced ${item.type} item:`, item.id);
  }

  /**
   * Get sync endpoint for item type
   */
  private getSyncEndpoint(type: string): string {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

    switch (type) {
      case 'order':
        return `${baseUrl}/api/v1/orders/sync`;
      case 'payment':
        return `${baseUrl}/api/v1/payments/sync`;
      case 'inventory':
        return `${baseUrl}/api/v1/inventory/sync`;
      default:
        throw new Error(`Unknown sync type: ${type}`);
    }
  }

  /**
   * Mark item as synced
   */
  private async markAsSynced(itemId: string): Promise<void> {
    if (!this.db) return;

    const transaction = this.db.transaction(['syncQueue'], 'readwrite');
    const store = transaction.objectStore('syncQueue');
    const item = await store.get(itemId);

    if (item) {
      item.synced = true;
      await store.put(item);
    }
  }

  /**
   * Get offline storage statistics
   */
  async getOfflineStats(): Promise<{
    cartItems: number;
    pendingOrders: number;
    cachedProducts: number;
    pendingSync: number;
    storageUsed: number;
  }> {
    if (!this.db) {
      return {
        cartItems: 0,
        pendingOrders: 0,
        cachedProducts: 0,
        pendingSync: 0,
        storageUsed: 0
      };
    }

    try {
      const transaction = this.db.transaction(['cart', 'orders', 'products', 'syncQueue'], 'readonly');

      const [cartItems, orders, products, syncQueue] = await Promise.all([
        this.countRecords(transaction.objectStore('cart')),
        this.countRecords(transaction.objectStore('orders')),
        this.countRecords(transaction.objectStore('products')),
        this.countRecords(transaction.objectStore('syncQueue').index('synced'), false)
      ]);

      const pendingOrders = orders; // All stored orders are pending until synced

      // Estimate storage usage
      const estimate = await navigator.storage?.estimate?.();
      const storageUsed = estimate?.usage || 0;

      return {
        cartItems,
        pendingOrders,
        cachedProducts: products,
        pendingSync: syncQueue,
        storageUsed
      };
    } catch (error) {
      console.error('Error getting offline stats:', error);
      return {
        cartItems: 0,
        pendingOrders: 0,
        cachedProducts: 0,
        pendingSync: 0,
        storageUsed: 0
      };
    }
  }

  /**
   * Clear offline data (for reset or cleanup)
   */
  async clearOfflineData(types?: string[]): Promise<boolean> {
    if (!this.db) return false;

    try {
      const storesToClear = types || ['cart', 'orders', 'products', 'syncQueue', 'preferences'];
      const transaction = this.db.transaction(storesToClear, 'readwrite');

      for (const storeName of storesToClear) {
        const store = transaction.objectStore(storeName);
        await store.clear();
      }

      console.log('Offline data cleared:', storesToClear);
      return true;
    } catch (error) {
      console.error('Error clearing offline data:', error);
      return false;
    }
  }

  /**
   * Utility function to count records in a store
   */
  private countRecords(store: IDBObjectStore | IDBIndex, query?: any): Promise<number> {
    return new Promise((resolve, reject) => {
      const request = query !== undefined ? store.count(query) : store.count();
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Check if offline mode is available and functional
   */
  isOfflineAvailable(): boolean {
    return 'indexedDB' in window && 'serviceWorker' in navigator;
  }

  /**
   * Export offline data for backup
   */
  async exportOfflineData(): Promise<string> {
    const stats = await this.getOfflineStats();
    const cart = await this.getOfflineCart();
    const orders = await this.getOfflineOrders();
    const products = await this.getCachedProducts();

    const exportData = {
      timestamp: Date.now(),
      stats,
      data: {
        cart,
        orders,
        products: products.slice(0, 10) // Limit for size
      }
    };

    return JSON.stringify(exportData, null, 2);
  }
}

// Export singleton instance
export const offlineService = new OfflineService();

// React hooks for offline functionality
export const useOfflineService = () => {
  return {
    saveCartOffline: (items: CartItem[]) => offlineService.saveCartOffline(items),
    getOfflineCart: () => offlineService.getOfflineCart(),
    saveOrderOffline: (order: Omit<OfflineOrder, 'id' | 'status' | 'createdAt'>) =>
      offlineService.saveOrderOffline(order),
    getOfflineOrders: () => offlineService.getOfflineOrders(),
    cacheProducts: (products: ProductData[]) => offlineService.cacheProducts(products),
    getCachedProducts: (limit?: number) => offlineService.getCachedProducts(limit),
    searchOfflineProducts: (query: string, category?: string) =>
      offlineService.searchOfflineProducts(query, category),
    savePreference: (key: string, value: any) => offlineService.savePreference(key, value),
    getPreference: (key: string) => offlineService.getPreference(key),
    syncOfflineData: () => offlineService.syncOfflineData(),
    getOfflineStats: () => offlineService.getOfflineStats(),
    clearOfflineData: (types?: string[]) => offlineService.clearOfflineData(types),
    isOfflineAvailable: () => offlineService.isOfflineAvailable(),
    exportOfflineData: () => offlineService.exportOfflineData()
  };
};

// Types export
export type { OfflineData, CartItem, OfflineOrder, ProductData };