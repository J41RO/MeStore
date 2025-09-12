import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Store, Clock, Star, Mail, Eye } from 'lucide-react';

interface VendorInfo {
  id: number;
  business_name: string;
  email?: string;
  created_at?: string;
}

interface VendorInfoProps {
  vendorId: number;
  vendorName: string;
  vendorInfo: VendorInfo;
}

const VendorInfo: React.FC<VendorInfoProps> = ({
  vendorId,
  vendorName,
  vendorInfo
}) => {
  const navigate = useNavigate();

  const formatTimeAsVendor = (createdAt?: string) => {
    if (!createdAt) return 'Información no disponible';
    
    const createdDate = new Date(createdAt);
    const now = new Date();
    const diffTime = now.getTime() - createdDate.getTime();
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    const diffMonths = Math.floor(diffDays / 30);
    const diffYears = Math.floor(diffDays / 365);

    if (diffYears > 0) {
      return `${diffYears} año${diffYears > 1 ? 's' : ''} como vendedor`;
    } else if (diffMonths > 0) {
      return `${diffMonths} mes${diffMonths > 1 ? 'es' : ''} como vendedor`;
    } else if (diffDays > 0) {
      return `${diffDays} día${diffDays > 1 ? 's' : ''} como vendedor`;
    } else {
      return 'Nuevo vendedor';
    }
  };

  const handleViewMoreProducts = () => {
    // Navigate to search results filtered by this vendor
    navigate(`/marketplace/search?vendor=${vendorId}&q=`);
  };

  const handleContactVendor = () => {
    if (vendorInfo.email) {
      window.location.href = `mailto:${vendorInfo.email}?subject=Consulta sobre producto en MeStore`;
    }
  };

  // Mock rating (in a real app, this would come from the API)
  const mockRating: number = 4.2;
  const mockReviews: number = 18;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-start justify-between mb-6">
        <div className="flex items-start space-x-4">
          {/* Vendor Avatar/Icon */}
          <div className="flex-shrink-0">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
              <Store className="h-8 w-8 text-blue-600" />
            </div>
          </div>

          {/* Vendor Basic Info */}
          <div className="flex-1">
            <h3 className="text-xl font-bold text-gray-900 mb-1">
              {vendorName}
            </h3>
            
            {/* Rating and Reviews */}
            <div className="flex items-center space-x-3 mb-2">
              <div className="flex items-center space-x-1">
                <div className="flex items-center">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <Star
                      key={star}
                      className={`h-4 w-4 ${
                        star <= Math.floor(mockRating)
                          ? 'text-yellow-400 fill-current'
                          : star - 0.5 <= mockRating
                          ? 'text-yellow-400 fill-current opacity-50'
                          : 'text-gray-300'
                      }`}
                    />
                  ))}
                </div>
                <span className="text-sm font-medium text-gray-700">
                  {mockRating.toFixed(1)}
                </span>
              </div>
              <span className="text-sm text-gray-500">
                ({mockReviews} reseña{mockReviews !== 1 ? 's' : ''})
              </span>
            </div>

            {/* Time as Vendor */}
            <div className="flex items-center text-sm text-gray-600 mb-3">
              <Clock className="h-4 w-4 mr-1" />
              {formatTimeAsVendor(vendorInfo.created_at)}
            </div>
          </div>
        </div>
      </div>

      {/* Vendor Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-2xl font-bold text-gray-900">42</div>
          <div className="text-sm text-gray-600">Productos</div>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-2xl font-bold text-gray-900">96%</div>
          <div className="text-sm text-gray-600">Satisfacción</div>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-2xl font-bold text-gray-900">24h</div>
          <div className="text-sm text-gray-600">Tiempo respuesta</div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-4">
        <button
          onClick={handleViewMoreProducts}
          className="flex-1 inline-flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
        >
          <Eye className="h-4 w-4 mr-2" />
          Ver más productos de este vendedor
        </button>
        
        {vendorInfo.email && (
          <button
            onClick={handleContactVendor}
            className="flex-1 inline-flex items-center justify-center px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors font-medium"
          >
            <Mail className="h-4 w-4 mr-2" />
            Contactar vendedor
          </button>
        )}
      </div>

      {/* Trust Badges */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex flex-wrap items-center justify-center space-x-4 text-xs text-gray-500">
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span>Vendedor verificado</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <span>Responde rápido</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
            <span>Envío confiable</span>
          </div>
        </div>
      </div>

      {/* Additional Info */}
      <div className="mt-4 text-center">
        <p className="text-xs text-gray-500">
          Todos los vendedores en MeStore son verificados y cumplen nuestros estándares de calidad
        </p>
      </div>
    </div>
  );
};

export default VendorInfo;