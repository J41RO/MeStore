// Interfaces para productos y ranking de ventas
export interface Product {
  id: string;
  name: string;
  price: number;
  thumbnail: string;
  salesCount: number;
  category: string;
  rating?: number;
  sku?: string;
  dimensions?: { length: number; width: number; height: number; unit: string };
  weight?: { value: number; unit: string };
}

export interface TopProduct extends Product {
  rank: number;
  salesGrowth: string;
}

export interface ProductSalesData {
  productId: string;
  totalSales: number;
  salesTrend: 'up' | 'down' | 'stable';
  rankPosition: number;
}

// Tipo para el hook useVendor
export interface VendorTopProducts {
  topProducts: TopProduct[];
  totalProducts: number;
  lastUpdated: string;
}