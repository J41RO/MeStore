import React from 'react';
import { Trash2, Package, MapPin, Clock } from 'lucide-react';
import { ScannedItem, PickingSession } from '../../types/barcode.types';

interface PickingListProps {
  items: ScannedItem[];
  session: PickingSession | null;
  onRemoveItem: (itemId: string) => void;
  onCompleteSession?: () => void;
  className?: string;
}

export const PickingList: React.FC<PickingListProps> = ({
  items,
  session,
  onRemoveItem,
  onCompleteSession,
  className = ''
}) => {
  const totalItems = items.length;

    return (
      <div className={'p-4 text-center text-gray-500 ' + className}>
        <Package size={48} className="mx-auto mb-2 opacity-50" />
        <p>No hay sesión de picking activa</p>
      </div>
    );
  }

  return (
    <div className={'bg-white border border-gray-200 rounded-lg ' + className}>
      <div className="p-4 border-b border-gray-200">
        <h3 className="font-semibold text-gray-900 mb-3">Lista de Picking</h3>
        <div className="text-sm text-gray-600">
          Sesión: {session.id} | Items: {totalItems}
        </div>
      </div>

      <div className="max-h-96 overflow-y-auto">
        {items.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <Package size={32} className="mx-auto mb-2 opacity-50" />
            <p>No hay items escaneados</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {items.map((item, index) => (
              <div key={item.id} className="p-3 hover:bg-gray-50">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3 flex-1">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-medium text-sm">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">{item.name}</div>
                      <div className="text-sm text-gray-600">
                        SKU: {item.sku} | {item.location}
                      </div>
                      <div className="text-xs text-gray-500">
                        {item.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => onRemoveItem(item.id)}
                    className="p-1 text-red-500 hover:bg-red-50 rounded"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {items.length > 0 && onCompleteSession && (
        <div className="p-4 border-t bg-gray-50">
          <button
            onClick={onCompleteSession}
            className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
          >
            Completar Picking ({totalItems} items)
          </button>
        </div>
      )}
    </div>
  );
};

export default PickingList;