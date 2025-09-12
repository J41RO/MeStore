import React from 'react';
import MarketplaceNavbar from './MarketplaceNavbar';
import MarketplaceFooter from './MarketplaceFooter';
import { ShoppingCart } from 'lucide-react';

interface MarketplaceLayoutProps {
  children: React.ReactNode;
  showCartButton?: boolean;
}

const MarketplaceLayout: React.FC<MarketplaceLayoutProps> = ({ 
  children, 
  showCartButton = true 
}) => {
  return (
    <div className="min-h-screen bg-white">
      {/* Marketplace Navigation */}
      <MarketplaceNavbar />
      
      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>
      
      {/* Floating Cart Button */}
      {showCartButton && (
        <div className="fixed bottom-6 right-6 z-50">
          <button className="bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-full shadow-lg transition-all hover:scale-105">
            <ShoppingCart className="w-6 h-6" />
            <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center">
              0
            </span>
          </button>
        </div>
      )}
      
      {/* Marketplace Footer */}
      <MarketplaceFooter />
    </div>
  );
};

export default MarketplaceLayout;