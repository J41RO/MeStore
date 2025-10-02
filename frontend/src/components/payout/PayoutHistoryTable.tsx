import React, { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

interface PayoutHistoryEntry {
  id: number;
  estado_anterior: string | null;
  estado_nuevo: string;
  fecha_cambio: string;
  observaciones: string | null;
  usuario_responsable: number | null;
}

interface PayoutHistoryTableProps {
  payoutId: number;
  className?: string;
}

const estadoColors: Record<string, string> = {
  SOLICITADO: 'bg-yellow-100 text-yellow-800',
  PROCESANDO: 'bg-blue-100 text-blue-800',
  PAGADO: 'bg-green-100 text-green-800',
  RECHAZADO: 'bg-red-100 text-red-800',
};

const PayoutHistoryTable: React.FC<PayoutHistoryTableProps> = ({
  payoutId,
  className = '',
}) => {
  const [historial, setHistorial] = useState<PayoutHistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHistorial = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('access_token');
        const response = await fetch(
          `/api/v1/commissions/payout-history/${payoutId}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          }
        );

        if (!response.ok) {
          throw new Error('Error al cargar el historial');
        }

        const data = await response.json();
        setHistorial(data.historial || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error desconocido');
      } finally {
        setLoading(false);
      }
    };

    if (payoutId) {
      fetchHistorial();
    }
  }, [payoutId]);

  const formatFecha = (fechaStr: string) => {
    try {
      return format(new Date(fechaStr), 'dd/MM/yyyy HH:mm', { locale: es });
    } catch {
      return fechaStr;
    }
  };

  const getEstadoBadge = (estado: string) => {
    const colorClass = estadoColors[estado] || 'bg-gray-100 text-gray-800';
    return (
      <span
        className={`px-2 py-1 rounded-full text-xs font-medium ${colorClass}`}
      >
        {estado}
      </span>
    );
  };

  if (loading) {
    return (
      <div className={`p-4 ${className}`}>
        <div className='animate-pulse'>
          <div className='h-4 bg-gray-200 rounded w-1/4 mb-4'></div>
          <div className='space-y-2'>
            {[...Array(3)].map((_, i) => (
              <div key={i} className='h-10 bg-gray-100 rounded'></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`p-4 ${className}`}>
        <div className='bg-red-50 border border-red-200 rounded-md p-4'>
          <div className='flex'>
            <div className='flex-shrink-0'>
              <svg
                className='h-5 w-5 text-red-400'
                viewBox='0 0 20 20'
                fill='currentColor'
              >
                <path
                  fillRule='evenodd'
                  d='M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z'
                  clipRule='evenodd'
                />
              </svg>
            </div>
            <div className='ml-3'>
              <h3 className='text-sm font-medium text-red-800'>
                Error al cargar historial
              </h3>
              <div className='mt-2 text-sm text-red-700'>{error}</div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!historial.length) {
    return (
      <div className={`p-4 ${className}`}>
        <div className='text-center py-8 text-gray-500'>
          <svg
            className='mx-auto h-12 w-12 text-gray-400'
            fill='none'
            viewBox='0 0 24 24'
            stroke='currentColor'
          >
            <path
              strokeLinecap='round'
              strokeLinejoin='round'
              strokeWidth={2}
              d='M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
            />
          </svg>
          <h3 className='mt-2 text-sm font-medium text-gray-900'>
            Sin historial
          </h3>
          <p className='mt-1 text-sm text-gray-500'>
            No hay cambios registrados para este payout.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`bg-white shadow overflow-hidden sm:rounded-md ${className}`}
    >
      <div className='px-4 py-5 sm:px-6'>
        <h3 className='text-lg leading-6 font-medium text-gray-900'>
          Historial de Transferencia
        </h3>
        <p className='mt-1 max-w-2xl text-sm text-gray-500'>
          Seguimiento completo de cambios de estado del payout.
        </p>
      </div>

      <div className='border-t border-gray-200'>
        <div className='overflow-x-auto'>
          <table className='min-w-full divide-y divide-gray-200'>
            <thead className='bg-gray-50'>
              <tr>
                <th
                  scope='col'
                  className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'
                >
                  Fecha y Hora
                </th>
                <th
                  scope='col'
                  className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'
                >
                  Estado Anterior
                </th>
                <th
                  scope='col'
                  className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'
                >
                  Estado Nuevo
                </th>
                <th
                  scope='col'
                  className='px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider'
                >
                  Observaciones
                </th>
              </tr>
            </thead>
            <tbody className='bg-white divide-y divide-gray-200'>
              {historial.map((entry, index) => (
                <tr
                  key={entry.id}
                  className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
                >
                  <td className='px-6 py-4 whitespace-nowrap text-sm text-gray-900'>
                    {formatFecha(entry.fecha_cambio)}
                  </td>
                  <td className='px-6 py-4 whitespace-nowrap text-sm text-gray-500'>
                    {entry.estado_anterior ? (
                      getEstadoBadge(entry.estado_anterior)
                    ) : (
                      <span className='text-gray-400 italic'>
                        Estado inicial
                      </span>
                    )}
                  </td>
                  <td className='px-6 py-4 whitespace-nowrap text-sm text-gray-900'>
                    {getEstadoBadge(entry.estado_nuevo)}
                  </td>
                  <td className='px-6 py-4 text-sm text-gray-500'>
                    {entry.observaciones || (
                      <span className='text-gray-400 italic'>
                        Sin observaciones
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default PayoutHistoryTable;
