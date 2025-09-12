#!/usr/bin/env python3
"""
Script para probar directamente el endpoint de incoming products queue.
Este script verifica que el endpoint esté funcionando y devolviendo datos.
"""

import sys
import os
import asyncio
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Agregar el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.incoming_product_queue import IncomingProductQueue
from app.schemas.inventory import IncomingProductQueueResponse
from app.core.database import engine

async def test_endpoint_functionality():
    """Probar la funcionalidad del endpoint de forma directa."""
    
    print("🧪 PROBANDO FUNCIONALIDAD DEL ENDPOINT INCOMING PRODUCTS")
    print("=" * 60)
    
    # Crear sesión async
    async with AsyncSession(engine) as db:
        try:
            # 1. Probar query directa desde BD
            print("1️⃣  Probando consulta directa desde base de datos...")
            
            query = select(IncomingProductQueue).order_by(
                IncomingProductQueue.priority.desc(),
                IncomingProductQueue.created_at.desc()
            )
            result = await db.execute(query)
            queue_items = result.scalars().all()
            
            print(f"   ✅ Encontrados {len(queue_items)} productos en BD")
            
            # 2. Probar conversión a dict (como hace el endpoint)
            print("\n2️⃣  Probando conversión a diccionario...")
            
            response_items = []
            for item in queue_items:
                try:
                    item_dict = item.to_dict()
                    response_items.append(item_dict)
                    print(f"   ✅ Convertido: {item.tracking_number}")
                except Exception as e:
                    print(f"   ❌ Error convirtiendo {item.tracking_number}: {str(e)}")
            
            # 3. Probar creación de response schema
            print("\n3️⃣  Probando creación de response schema...")
            
            valid_responses = []
            for item_dict in response_items:
                try:
                    response = IncomingProductQueueResponse(**item_dict)
                    valid_responses.append(response)
                    print(f"   ✅ Schema creado para: {item_dict.get('tracking_number')}")
                except Exception as e:
                    print(f"   ❌ Error en schema para {item_dict.get('tracking_number')}: {str(e)}")
            
            # 4. Mostrar datos de ejemplo que devolvería el endpoint
            print("\n4️⃣  DATOS QUE DEVOLVERÍA EL ENDPOINT:")
            print("-" * 50)
            
            if valid_responses:
                for response in valid_responses:
                    # Convertir a dict para mostrar
                    response_dict = response.model_dump()
                    
                    print(f"🔸 {response_dict['tracking_number']}")
                    print(f"   ID: {response_dict['id']}")
                    print(f"   Estado: {response_dict['verification_status']}")
                    print(f"   Prioridad: {response_dict['priority']}")
                    print(f"   Carrier: {response_dict['carrier']}")
                    print(f"   Días en cola: {response_dict.get('days_in_queue', 'N/A')}")
                    print(f"   Es retrasado: {response_dict['is_delayed']}")
                    print()
            
            # 5. Crear JSON como lo haría FastAPI
            print("5️⃣  Probando serialización JSON (como FastAPI)...")
            
            try:
                json_data = [response.model_dump() for response in valid_responses]
                json_str = json.dumps(json_data, default=str, indent=2)
                print(f"   ✅ JSON creado exitosamente ({len(json_str)} caracteres)")
                
                # Mostrar una muestra del JSON
                if len(json_str) > 500:
                    print(f"   📄 Muestra del JSON:\n{json_str[:500]}...")
                else:
                    print(f"   📄 JSON completo:\n{json_str}")
                    
            except Exception as e:
                print(f"   ❌ Error en serialización JSON: {str(e)}")
            
            return len(valid_responses) > 0
            
        except Exception as e:
            print(f"❌ Error en prueba: {str(e)}")
            return False

async def test_frontend_data_structure():
    """Verificar que la estructura de datos sea compatible con el frontend."""
    
    print("\n🎯 VERIFICANDO COMPATIBILIDAD CON FRONTEND")
    print("=" * 50)
    
    async with AsyncSession(engine) as db:
        try:
            # Obtener un producto de prueba
            query = select(IncomingProductQueue).limit(1)
            result = await db.execute(query)
            item = result.scalar_one_or_none()
            
            if not item:
                print("❌ No hay productos para probar")
                return False
            
            # Convertir como lo hace el endpoint
            item_dict = item.to_dict()
            response = IncomingProductQueueResponse(**item_dict)
            frontend_data = response.model_dump()
            
            # Verificar campos que espera el frontend
            required_frontend_fields = [
                'id', 'product_id', 'vendor_id', 'expected_arrival', 
                'verification_status', 'priority', 'tracking_number', 
                'carrier', 'is_delayed', 'days_in_queue', 'status_display', 
                'priority_display'
            ]
            
            print("📋 Verificando campos requeridos por el frontend:")
            missing_fields = []
            
            for field in required_frontend_fields:
                if field in frontend_data:
                    print(f"   ✅ {field}: {frontend_data[field]}")
                else:
                    print(f"   ❌ {field}: FALTANTE")
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"\n⚠️  CAMPOS FALTANTES: {', '.join(missing_fields)}")
                return False
            else:
                print(f"\n✅ TODOS LOS CAMPOS REQUERIDOS ESTÁN PRESENTES")
                return True
                
        except Exception as e:
            print(f"❌ Error verificando compatibilidad: {str(e)}")
            return False

async def main():
    """Función principal de pruebas."""
    
    endpoint_ok = await test_endpoint_functionality()
    frontend_ok = await test_frontend_data_structure()
    
    print("\n🎯 RESUMEN DE PRUEBAS:")
    print("=" * 30)
    print(f"Funcionalidad del endpoint: {'✅ OK' if endpoint_ok else '❌ ERROR'}")
    print(f"Compatibilidad frontend:    {'✅ OK' if frontend_ok else '❌ ERROR'}")
    
    if endpoint_ok and frontend_ok:
        print("\n✅ ENDPOINT LISTO PARA USO")
        print("🌐 El problema podría ser en autenticación o configuración de frontend")
        return True
    else:
        print("\n❌ HAY PROBLEMAS EN EL ENDPOINT")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)