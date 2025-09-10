import React, { useState, useEffect } from 'react';
import { ClipboardCheck, Package, AlertTriangle, CheckCircle } from 'lucide-react';

interface AuditItem {
  id: string;
  inventory_id: string;
  cantidad_sistema: number;
  cantidad_fisica?: number;
  ubicacion_sistema: string;
  ubicacion_fisica?: string;
  tiene_discrepancia: boolean;
  tipo_discrepancia?: string;
  diferencia_cantidad: number;
  conteo_completado: boolean;
}

interface Audit {
  id: string;
  nombre: string;
  status: string;
  total_items_auditados: number;
  discrepancies_found: number;
  fecha_inicio: string;
}

const InventoryAuditPanel: React.FC = () => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [audits, setAudits] = useState<Audit[]>([]);
  const [selectedAudit, setSelectedAudit] = useState<Audit | null>(null);
  const [auditItems, setAuditItems] = useState<AuditItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [newAuditName, setNewAuditName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [rateLimitCooldown, setRateLimitCooldown] = useState(false);

  // 🛡️ CONTROL ANTI-RATE LIMITING
  const handleRateLimit = async (retryAfter: number = 60) => {
    setRateLimitCooldown(true);
    setError(`Rate limit alcanzado. Esperando ${retryAfter} segundos...`);
    
    // Esperar el tiempo especificado por el servidor
    setTimeout(() => {
      setRateLimitCooldown(false);
      setError(null);
    }, retryAfter * 1000);
  };

  // Función para obtener token con manejo de rate limiting
  const getAuthToken = async (): Promise<string | null> => {
    if (rateLimitCooldown) {
      console.log('Rate limit activo, omitiendo request de auth');
      return null;
    }

    try {
      const response = await fetch('http://192.168.1.137:8000/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': 'Mozilla/5.0 (compatible; API-Client/1.0)'
        },
        body: JSON.stringify({
          email: 'dev@mestore.com',
          password: 'dev123456'
        })
      });
      
      if (response.status === 429) {
        const retryAfter = parseInt(response.headers.get('Retry-After') || '60');
        await handleRateLimit(retryAfter);
        return null;
      }
      
      if (response.ok) {
        const data = await response.json();
        const token = data.access_token;
        setAuthToken(token);
        return token;
      } else {
        console.error('Auth failed:', response.status, response.statusText);
      }
    } catch (error) {
      console.error('Error getting auth token:', error);
    }
    return null;
  };

  // Función auxiliar para crear headers con autenticación
  const getAuthHeaders = async () => {
    let token = authToken;
    if (!token && !rateLimitCooldown) {
      token = await getAuthToken();
    }
    
    const headers: any = {
      'User-Agent': 'Mozilla/5.0 (compatible; API-Client/1.0)'
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    return headers;
  };

  // 🛡️ FUNCIÓN MEJORADA CON RATE LIMITING
  const makeRequestWithRateLimit = async (url: string, options: RequestInit = {}) => {
    if (rateLimitCooldown) {
      throw new Error('Rate limit activo, no se pueden hacer requests');
    }

    const response = await fetch(url, options);
    
    if (response.status === 429) {
      const retryAfter = parseInt(response.headers.get('Retry-After') || '60');
      await handleRateLimit(retryAfter);
      throw new Error(`Rate limit excedido. Reintentando en ${retryAfter} segundos.`);
    }
    
    return response;
  };

  // ✅ CARGA MANUAL - SIN POLLING AUTOMÁTICO
  const loadAudits = async () => {
    if (rateLimitCooldown) {
      setError('Rate limit activo. Espera antes de recargar.');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const headers = await getAuthHeaders();
      const response = await makeRequestWithRateLimit('http://192.168.1.137:8000/api/v1/inventory/audits', {
        headers
      });
      
      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          // Solo un reintento, sin bucles
          const newToken = await getAuthToken();
          if (newToken && !rateLimitCooldown) {
            const retryHeaders = {
              ...headers,
              'Authorization': `Bearer ${newToken}`
            };
            const retryResponse = await makeRequestWithRateLimit('http://192.168.1.137:8000/api/v1/inventory/audits', {
              headers: retryHeaders
            });
            
            if (retryResponse.ok) {
              const data = await retryResponse.json();
              setAudits(Array.isArray(data) ? data : []);
              return;
            }
          }
        }
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (Array.isArray(data)) {
        setAudits(data);
      } else if (data && data.error) {
        setError(`Error del servidor: ${data.error}`);
        setAudits([]);
      } else {
        setError('Formato de datos inesperado del servidor');
        setAudits([]);
      }
    } catch (error) {
      console.error('Error loading audits:', error);
      setError(error instanceof Error ? error.message : 'Error desconocido');
      setAudits([]);
    } finally {
      setLoading(false);
    }
  };

  const createAudit = async () => {
    if (!newAuditName.trim() || rateLimitCooldown) return;
    
    setError(null);
    try {
      const headers = await getAuthHeaders();
      const response = await makeRequestWithRateLimit('http://192.168.1.137:8000/api/v1/inventory/audits', {
        method: 'POST',
        headers: {
          ...headers,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          nombre: newAuditName,
          descripcion: `Auditoría física creada el ${new Date().toLocaleDateString()}`,
          audit_type: 'physical'
        })
      });
      
      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          const newToken = await getAuthToken();
          if (newToken && !rateLimitCooldown) {
            const retryResponse = await makeRequestWithRateLimit('http://192.168.1.137:8000/api/v1/inventory/audits', {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${newToken}`,
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (compatible; API-Client/1.0)'
              },
              body: JSON.stringify({
                nombre: newAuditName,
                descripcion: `Auditoría física creada el ${new Date().toLocaleDateString()}`,
                audit_type: 'physical'
              })
            });
            
            if (retryResponse.ok) {
              setNewAuditName('');
              setShowCreateForm(false);
              // NO auto-reload, usuario debe recargar manualmente
              return;
            }
          }
        }
        
        const errorData = await response.json();
        throw new Error(errorData.detail || `Error ${response.status}`);
      }
      
      setNewAuditName('');
      setShowCreateForm(false);
      // Usuario debe recargar manualmente
    } catch (error) {
      console.error('Error creating audit:', error);
      setError(error instanceof Error ? error.message : 'Error creando auditoría');
    }
  };

  // ✅ CARGA MANUAL DE ITEMS - SIN POLLING
  const loadAuditItems = async (auditId: string) => {
    if (rateLimitCooldown) {
      setError('Rate limit activo. Espera antes de cargar items.');
      return;
    }

    try {
      const headers = await getAuthHeaders();
      const response = await makeRequestWithRateLimit(`http://192.168.1.137:8000/api/v1/inventory/audits/${auditId}/items`, {
        headers
      });
      
      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          const newToken = await getAuthToken();
          if (newToken && !rateLimitCooldown) {
            const retryResponse = await makeRequestWithRateLimit(`http://192.168.1.137:8000/api/v1/inventory/audits/${auditId}/items`, {
              headers: {
                'Authorization': `Bearer ${newToken}`,
                'User-Agent': 'Mozilla/5.0 (compatible; API-Client/1.0)'
              }
            });
            if (retryResponse.ok) {
              const data = await retryResponse.json();
              setAuditItems(Array.isArray(data) ? data : []);
              return;
            }
          }
        }
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setAuditItems(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error loading audit items:', error);
      setAuditItems([]);
      setError(error instanceof Error ? error.message : 'Error cargando items');
    }
  };

  const updatePhysicalCount = async (itemId: string, cantidadFisica: number, ubicacion?: string) => {
    if (rateLimitCooldown) {
      setError('Rate limit activo. Espera antes de actualizar.');
      return;
    }

    try {
      const headers = await getAuthHeaders();
      const response = await makeRequestWithRateLimit(`http://192.168.1.137:8000/api/v1/inventory/audit-items/${itemId}/count`, {
        method: 'PUT',
        headers: {
          ...headers,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          cantidad_fisica: cantidadFisica,
          ubicacion_fisica: ubicacion
        })
      });
      
      if (!response.ok && (response.status === 401 || response.status === 403)) {
        const newToken = await getAuthToken();
        if (newToken && !rateLimitCooldown) {
          const retryResponse = await makeRequestWithRateLimit(`http://192.168.1.137:8000/api/v1/inventory/audit-items/${itemId}/count`, {
            method: 'PUT',
            headers: {
              'Authorization': `Bearer ${newToken}`,
              'Content-Type': 'application/json',
              'User-Agent': 'Mozilla/5.0 (compatible; API-Client/1.0)'
            },
            body: JSON.stringify({
              cantidad_fisica: cantidadFisica,
              ubicacion_fisica: ubicacion
            })
          });
          
          if (retryResponse.ok && selectedAudit) {
            // NO auto-reload, usuario debe refrescar manualmente
            return;
          }
        }
      }
      
      // NO auto-reload automático
    } catch (error) {
      console.error('Error updating count:', error);
      setError(error instanceof Error ? error.message : 'Error actualizando conteo');
    }
  };

  // ✅ USEEFFECT CONTROLADO - SOLO CARGA INICIAL
  useEffect(() => {
    // Solo carga inicial, NO polling continuo
    loadAudits();
  }, []); // Dependencias vacías - solo ejecuta una vez

  // ✅ ELIMINADO: useEffect problemático de selectedAudit
  // Los items se cargan manualmente cuando usuario clickea

  const handleCountInput = (itemId: string, value: string) => {
    const cantidadFisica = parseInt(value);
    if (!isNaN(cantidadFisica) && cantidadFisica >= 0) {
      updatePhysicalCount(itemId, cantidadFisica);
    }
  };

  // ✅ MANEJO MANUAL DE AUDIT SELECTION
  const handleAuditSelect = async (audit: Audit) => {
    setSelectedAudit(audit);
    // Usuario debe cargar items manualmente
  };

  // Vista de detalle de auditoría
  if (selectedAudit) {
    return (
      <div className="inventory-audit-panel p-6 bg-white rounded-lg shadow">
        <div className="header mb-6">
          <div className="flex justify-between items-center">
            <div>
              <button
                onClick={() => setSelectedAudit(null)}
                className="text-blue-600 hover:text-blue-800 mb-2 transition-colors"
              >
                ← Volver a auditorías
              </button>
              <h2 className="text-2xl font-bold flex items-center gap-2">
                <ClipboardCheck className="text-blue-600" />
                {selectedAudit.nombre}
              </h2>
              <p className="text-gray-600">
                Estado: {selectedAudit.status} | Items: {selectedAudit.total_items_auditados} | 
                Discrepancias: {selectedAudit.discrepancies_found}
              </p>
            </div>
            <div className="flex space-x-3">
              {/* ✅ BOTÓN MANUAL PARA CARGAR ITEMS */}
              <button
                onClick={() => loadAuditItems(selectedAudit.id)}
                disabled={rateLimitCooldown}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
              >
                {rateLimitCooldown ? 'Rate Limit...' : 'Cargar Items'}
              </button>
              
              {/* ✅ BOTÓN GENERAR REPORTE - Solo si audit está completada */}
              {(selectedAudit.status === 'COMPLETADA' || selectedAudit.status === 'RECONCILIADA') && (
                <button
                  onClick={() => {
                    // Navegar al componente de reportes con el audit preseleccionado
                    window.location.href = `/admin-secure-portal/reportes-discrepancias?audit=${selectedAudit.id}`;
                  }}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  📊 Generar Reporte
                </button>
              )}
            </div>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 border border-red-200 rounded-lg bg-red-50">
            <div className="flex items-center">
              <AlertTriangle size={16} className="text-red-600 mr-2" />
              <span className="text-red-700">{error}</span>
            </div>
          </div>
        )}

        <div className="audit-items">
          <h3 className="text-lg font-semibold mb-4">Conteo Físico vs Sistema</h3>
          
          {auditItems.length === 0 ? (
            <div className="text-center py-8">
              <Package size={48} className="mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600">No hay items para auditar</p>
              <p className="text-sm text-gray-500 mt-2">Haz clic en "Cargar Items" para ver los datos</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse border border-gray-200">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="border border-gray-200 p-3 text-left">Item</th>
                    <th className="border border-gray-200 p-3 text-center">Cant. Sistema</th>
                    <th className="border border-gray-200 p-3 text-center">Cant. Física</th>
                    <th className="border border-gray-200 p-3 text-center">Diferencia</th>
                    <th className="border border-gray-200 p-3 text-center">Estado</th>
                    <th className="border border-gray-200 p-3 text-left">Ubicación</th>
                  </tr>
                </thead>
                <tbody>
                  {auditItems.map((item) => (
                    <tr key={item.id} className={item.tiene_discrepancia ? 'bg-red-50' : 'bg-white'}>
                      <td className="border border-gray-200 p-3">
                        <div className="font-medium">{item.inventory_id}</div>
                      </td>
                      <td className="border border-gray-200 p-3 text-center">
                        {item.cantidad_sistema}
                      </td>
                      <td className="border border-gray-200 p-3 text-center">
                        <input
                          type="number"
                          min="0"
                          className="w-20 p-1 border rounded text-center focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          placeholder="0"
                          defaultValue={item.cantidad_fisica || ''}
                          onBlur={(e) => handleCountInput(item.id, e.target.value)}
                          onKeyPress={(e) => e.key === 'Enter' && handleCountInput(item.id, (e.target as HTMLInputElement).value)}
                          disabled={rateLimitCooldown}
                        />
                      </td>
                      <td className="border border-gray-200 p-3 text-center">
                        <span className={`font-semibold ${item.diferencia_cantidad !== 0 ? 'text-red-600' : 'text-green-600'}`}>
                          {item.diferencia_cantidad > 0 ? '+' : ''}{item.diferencia_cantidad}
                        </span>
                      </td>
                      <td className="border border-gray-200 p-3 text-center">
                        {item.conteo_completado ? (
                          <div className="flex items-center justify-center">
                            <CheckCircle size={16} className="text-green-600 mr-1" />
                            <span className="text-sm text-green-600">Completo</span>
                          </div>
                        ) : (
                          <span className="text-sm text-gray-500">Pendiente</span>
                        )}
                        {item.tiene_discrepancia && (
                          <div className="flex items-center justify-center mt-1">
                            <AlertTriangle size={14} className="text-red-600 mr-1" />
                            <span className="text-xs text-red-600">{item.tipo_discrepancia}</span>
                          </div>
                        )}
                      </td>
                      <td className="border border-gray-200 p-3">
                        <div className="text-sm">
                          <div>Sistema: {item.ubicacion_sistema}</div>
                          {item.ubicacion_fisica && item.ubicacion_fisica !== item.ubicacion_sistema && (
                            <div className="text-red-600">Física: {item.ubicacion_fisica}</div>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Vista principal de auditorías
  return (
    <div className="inventory-audit-panel p-6 bg-white rounded-lg shadow">
      <div className="header mb-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <ClipboardCheck className="text-blue-600" />
            Auditorías de Inventario
          </h2>
          <div className="flex gap-2">
            {/* ✅ BOTÓN MANUAL PARA RECARGAR */}
            <button
              onClick={loadAudits}
              disabled={rateLimitCooldown}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 transition-colors"
            >
              {rateLimitCooldown ? 'Rate Limit...' : 'Recargar'}
            </button>
            <button
              onClick={() => setShowCreateForm(true)}
              disabled={rateLimitCooldown}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors flex items-center gap-2"
            >
              <Package size={16} />
              Nueva Auditoría
            </button>
          </div>
        </div>
      </div>
      
      {error && (
        <div className="mb-6 p-4 border border-red-200 rounded-lg bg-red-50">
          <div className="flex items-center">
            <AlertTriangle size={16} className="text-red-600 mr-2" />
            <span className="text-red-700">{error}</span>
          </div>
          {!rateLimitCooldown && (
            <button
              onClick={() => {setError(null); loadAudits();}}
              className="mt-2 text-sm text-red-600 hover:text-red-800"
            >
              Reintentar
            </button>
          )}
        </div>
      )}
      
      {showCreateForm && (
        <div className="mb-6 p-4 border rounded-lg bg-blue-50">
          <h3 className="text-lg font-semibold mb-4">Crear Nueva Auditoría</h3>
          <input
            type="text"
            placeholder="Nombre de auditoría"
            value={newAuditName}
            onChange={(e) => setNewAuditName(e.target.value)}
            className="w-full p-2 border rounded mb-4 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            onKeyPress={(e) => e.key === 'Enter' && createAudit()}
            maxLength={200}
            disabled={rateLimitCooldown}
          />
          <div className="flex gap-2">
            <button 
              onClick={createAudit}
              disabled={!newAuditName.trim() || rateLimitCooldown}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {rateLimitCooldown ? 'Rate Limit...' : 'Crear'}
            </button>
            <button 
              onClick={() => {
                setShowCreateForm(false);
                setNewAuditName('');
                setError(null);
              }} 
              className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}

      <div className="audits-list">
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Cargando auditorías...</p>
          </div>
        ) : Array.isArray(audits) && audits.length === 0 ? (
          <div className="text-center py-12">
            <ClipboardCheck size={48} className="mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600">No hay auditorías creadas</p>
            <p className="text-sm text-gray-500 mt-2">
              Haz clic en "Nueva Auditoría" para comenzar
            </p>
          </div>
        ) : Array.isArray(audits) ? (
          <div className="grid gap-4">
            {audits.map((audit) => (
              <div
                key={audit.id}
                className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer hover:border-blue-300"
                onClick={() => handleAuditSelect(audit)}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-lg">{audit.nombre}</h3>
                    <p className="text-gray-600 text-sm">
                      Estado: <span className={`font-medium ${
                        audit.status === 'COMPLETADA' ? 'text-green-600' : 
                        audit.status === 'EN_PROCESO' ? 'text-blue-600' : 'text-yellow-600'
                      }`}>{audit.status}</span>
                    </p>
                    <p className="text-gray-500 text-sm mt-1">
                      Creada: {new Date(audit.fecha_inicio).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-gray-600">
                      Items: {audit.total_items_auditados}
                    </div>
                    {audit.discrepancies_found > 0 && (
                      <div className="flex items-center text-red-600 text-sm mt-1">
                        <AlertTriangle size={14} className="mr-1" />
                        {audit.discrepancies_found} discrepancias
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : null}
      </div>
    </div>
  );
};

export default InventoryAuditPanel;