#!/usr/bin/env python3
"""
Script para crear datos mock temporales que permitan ver el frontend funcionando
mientras se resuelve el rate limiting del servidor.
"""

import json
import os

def create_mock_data():
    """Crear datos mock para el frontend"""
    
    print("🔧 CREANDO DATOS MOCK PARA FRONTEND")
    print("=" * 40)
    
    # Datos mock que coinciden exactamente con lo que está en la BD
    mock_data = [
        {
            "id": "faaedce4-332c-4cef-a8de-0df8589c6d02",
            "product_id": "d2500220-ceb6-487b-94f4-abe759caae43",
            "vendor_id": "1c90b7b0-9223-4fc8-ba03-94c20cd34763",
            "expected_arrival": "2025-09-12T16:42:55.830851+00:00",
            "actual_arrival": None,
            "verification_status": "PENDING",
            "priority": "HIGH",
            "assigned_to": None,
            "assigned_at": None,
            "deadline": "2025-09-15T16:42:55.830851+00:00",
            "tracking_number": "TRK-001-2024-HIGH",
            "carrier": "DHL Express",
            "is_delayed": False,
            "delay_reason": None,
            "notes": "Producto prioritario - Cliente VIP",
            "verification_notes": None,
            "quality_score": None,
            "quality_issues": None,
            "processing_started_at": None,
            "processing_completed_at": None,
            "verification_attempts": 0,
            "created_at": "2025-09-10T16:42:55.830851",
            "updated_at": "2025-09-10T16:42:55.830851",
            "deleted_at": None,
            "days_in_queue": 0,
            "processing_time_hours": None,
            "is_high_priority": True,
            "status_display": "Pendiente",
            "priority_display": "Alta",
            "is_overdue": False
        },
        {
            "id": "0abd7b8d-a689-4a3c-ba52-ad39e6fb5647",
            "product_id": "51e6f51e-8d47-4c65-9d02-9a3fbe97a099",
            "vendor_id": "c761efc0-b922-43d5-bdc0-caf4aab21e91",
            "expected_arrival": "2025-09-15T16:42:55.830869+00:00",
            "actual_arrival": None,
            "verification_status": "ASSIGNED",
            "priority": "NORMAL",
            "assigned_to": "c923f9d1-4022-43c1-8a45-fb8dab660731",
            "assigned_at": "2025-09-10T14:42:55.830869+00:00",
            "deadline": "2025-09-18T16:42:55.830869+00:00",
            "tracking_number": "TRK-002-2024-NORM",
            "carrier": "FedEx",
            "is_delayed": False,
            "delay_reason": None,
            "notes": "Envío estándar - Verificación rutinaria",
            "verification_notes": "Asignado para verificación por admin",
            "quality_score": None,
            "quality_issues": None,
            "processing_started_at": None,
            "processing_completed_at": None,
            "verification_attempts": 1,
            "created_at": "2025-09-10T16:42:55.830869",
            "updated_at": "2025-09-10T16:42:55.830869",
            "deleted_at": None,
            "days_in_queue": 0,
            "processing_time_hours": None,
            "is_high_priority": False,
            "status_display": "Asignado",
            "priority_display": "Normal",
            "is_overdue": False
        },
        {
            "id": "696c744e-85c0-4922-abde-0f7aa25a96db",
            "product_id": "df1fac2c-1bb9-4696-a6be-77c0fccade81",
            "vendor_id": "00610b91-fb46-4e44-935f-bde2098284d0",
            "expected_arrival": "2025-09-11T16:42:55.830869+00:00",
            "actual_arrival": "2025-09-13T16:42:55.830871+00:00",
            "verification_status": "IN_PROGRESS",
            "priority": "CRITICAL",
            "assigned_to": "c923f9d1-4022-43c1-8a45-fb8dab660731",
            "assigned_at": "2025-09-09T16:42:55.830869+00:00",
            "deadline": "2025-09-11T04:42:55.830869+00:00",
            "tracking_number": "TRK-003-2024-CRIT",
            "carrier": "UPS",
            "is_delayed": True,
            "delay_reason": "TRANSPORT",
            "notes": "Producto crítico con retraso en transporte",
            "verification_notes": "Iniciada verificación - Retraso documentado",
            "quality_score": None,
            "quality_issues": None,
            "processing_started_at": "2025-09-10T10:42:55.830869+00:00",
            "processing_completed_at": None,
            "verification_attempts": 2,
            "created_at": "2025-09-10T16:42:55.830869",
            "updated_at": "2025-09-10T16:42:55.830869",
            "deleted_at": None,
            "days_in_queue": 0,
            "processing_time_hours": 6.0,
            "is_high_priority": True,
            "status_display": "En Proceso",
            "priority_display": "Crítica",
            "is_overdue": True
        }
    ]
    
    # Stats mock
    mock_stats = {
        "total_items": 3,
        "pending": 1,
        "assigned": 1,
        "in_progress": 1,
        "completed": 0,
        "overdue": 1,
        "delayed": 1,
        "average_processing_time": 6.0,
        "queue_efficiency": 85.5
    }
    
    return mock_data, mock_stats

def create_temporary_override():
    """Crear override temporal para el frontend"""
    
    mock_data, mock_stats = create_mock_data()
    
    # Crear archivo JavaScript con datos mock
    override_script = f"""
// DATOS MOCK TEMPORALES PARA TESTING
// Este archivo será removido cuando el rate limiting se resuelva

console.log('🔧 ACTIVANDO DATOS MOCK TEMPORALES');

// Override del fetch original
const originalFetch = window.fetch;
window.fetch = function(...args) {{
    const [url, options] = args;
    
    // Interceptar llamadas a la API de productos
    if (url.includes('/api/v1/inventory/queue/incoming-products')) {{
        console.log('📦 Retornando datos mock para incoming-products');
        return Promise.resolve({{
            ok: true,
            status: 200,
            json: () => Promise.resolve({json.dumps(mock_data, indent=2)})
        }});
    }}
    
    // Interceptar llamadas a stats
    if (url.includes('/api/v1/inventory/queue/stats')) {{
        console.log('📊 Retornando stats mock');
        return Promise.resolve({{
            ok: true,
            status: 200,
            json: () => Promise.resolve({json.dumps(mock_stats, indent=2)})
        }});
    }}
    
    // Para todas las demás llamadas, usar fetch original
    return originalFetch.apply(this, args);
}};

// Mensaje en consola
console.log('✅ Datos mock activados - Deberías ver 3 productos en la lista');
console.log('🔸 TRK-001-2024-HIGH (DHL Express) - Pendiente');
console.log('🔸 TRK-002-2024-NORM (FedEx) - Asignado');
console.log('🔸 TRK-003-2024-CRIT (UPS) - En Proceso');
"""
    
    # Escribir archivo
    frontend_public_path = "/home/admin-jairo/MeStore/frontend/public"
    override_file = os.path.join(frontend_public_path, "mock-data-override.js")
    
    try:
        os.makedirs(frontend_public_path, exist_ok=True)
        with open(override_file, 'w') as f:
            f.write(override_script)
        
        print(f"✅ Archivo mock creado: {override_file}")
        return override_file
        
    except Exception as e:
        print(f"❌ Error creando override: {e}")
        return None

def create_instructions():
    """Crear instrucciones para usar los datos mock"""
    
    print("\n🎯 INSTRUCCIONES PARA VER EL SISTEMA FUNCIONANDO")
    print("=" * 50)
    
    print("1️⃣  ACTIVAR DATOS MOCK:")
    print("   🌐 Ir a: http://192.168.1.137:5173/admin-secure-portal/cola-productos-entrantes")
    print("   🔧 Abrir DevTools (F12)")
    print("   📝 En la pestaña Console, pegar y ejecutar:")
    print()
    print("   // CÓDIGO PARA COPIAR Y PEGAR:")
    
    mock_data, mock_stats = create_mock_data()
    
    console_code = f"""
const originalFetch = window.fetch;
window.fetch = function(...args) {{
    const [url, options] = args;
    
    if (url.includes('/api/v1/inventory/queue/incoming-products')) {{
        console.log('📦 Mock data: incoming-products');
        return Promise.resolve({{
            ok: true,
            status: 200,
            json: () => Promise.resolve({json.dumps(mock_data)})
        }});
    }}
    
    if (url.includes('/api/v1/inventory/queue/stats')) {{
        console.log('📊 Mock data: stats');
        return Promise.resolve({{
            ok: true,
            status: 200,
            json: () => Promise.resolve({json.dumps(mock_stats)})
        }});
    }}
    
    return originalFetch.apply(this, args);
}};

// Refrescar datos
window.location.reload();
"""
    
    print(f"   {console_code}")
    print()
    
    print("2️⃣  DESPUÉS DE EJECUTAR EL CÓDIGO:")
    print("   🔄 La página se refrescará automáticamente")
    print("   📦 Deberías ver 3 productos en la lista")
    print("   ✅ El botón de verificación debería aparecer")
    print()
    
    print("3️⃣  PROBAR EL WORKFLOW:")
    print("   🔸 TRK-001-2024-HIGH - Hacer clic en ✅ para verificación")
    print("   🔸 TRK-002-2024-NORM - Hacer clic en ✅ para verificación")
    print("   🔸 TRK-003-2024-CRIT - Hacer clic en ✅ para verificación")
    print()
    
    print("4️⃣  QUÉ DEBERÍAS VER:")
    print("   📊 Estadísticas en la parte superior")
    print("   📋 Lista con 3 productos")
    print("   🎯 Modal de workflow al hacer clic en verificación")
    print("   🔄 Stepper con pasos del workflow")

def main():
    """Función principal"""
    
    print("🚀 CREANDO SOLUCIÓN TEMPORAL PARA RATE LIMITING")
    print("=" * 50)
    
    # Crear override
    override_file = create_temporary_override()
    
    # Crear instrucciones
    create_instructions()
    
    print(f"\n✅ SOLUCIÓN TEMPORAL LISTA")
    print(f"🎯 Sigue las instrucciones arriba para ver el sistema funcionando")
    print(f"⚠️  Esta es una solución temporal mientras se resuelve el rate limiting")
    print(f"🔄 Una vez que el servidor permita las requests, todo funcionará normalmente")

if __name__ == "__main__":
    main()