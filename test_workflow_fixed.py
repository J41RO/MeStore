#!/usr/bin/env python3
"""
Script para verificar que las correcciones del workflow están funcionando.
"""

import requests
import json
import sys
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Agregar path
sys.path.append('/home/admin-jairo/MeStore')

from app.models.incoming_product_queue import IncomingProductQueue
from app.core.database import engine

async def test_database_products():
    """Verificar que los productos existen en la BD"""
    print("🗄️  VERIFICANDO PRODUCTOS EN BD")
    print("-" * 35)
    
    async with AsyncSession(engine) as db:
        try:
            result = await db.execute(select(IncomingProductQueue))
            products = result.scalars().all()
            
            print(f"   📦 Productos encontrados: {len(products)}")
            
            product_ids = []
            for product in products:
                print(f"      🔸 ID: {product.id}")
                print(f"         Tracking: {product.tracking_number}")
                print(f"         Estado: {product.verification_status}")
                product_ids.append(str(product.id))
                print()
            
            return product_ids if len(products) > 0 else []
            
        except Exception as e:
            print(f"   ❌ Error BD: {e}")
            return []

def test_auth():
    """Obtener token de autenticación"""
    print("🔑 OBTENIENDO TOKEN DE AUTENTICACIÓN")
    print("-" * 40)
    
    base_url = "http://192.168.1.137:8000"
    
    credentials = {
        "email": "admin@mestore.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/auth/login",
            json=credentials,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (compatible workflow test)"
            },
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"   ✅ Token obtenido: {token[:30]}...")
            return token
        else:
            print(f"   ❌ Auth falló: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error auth: {e}")
        return None

def test_workflow_endpoint(token, product_id):
    """Probar endpoint del workflow"""
    print(f"🔄 PROBANDO WORKFLOW ENDPOINT PARA {product_id}")
    print("-" * 50)
    
    base_url = "http://192.168.1.137:8000"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (compatible workflow test)"
    }
    
    try:
        # Test current-step endpoint
        url = f"{base_url}/api/v1/admin/incoming-products/{product_id}/verification/current-step"
        print(f"   🌐 URL: {url}")
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Workflow endpoint funciona")
            print(f"   📋 Datos: {json.dumps(data, indent=2)[:200]}...")
            return True
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

async def main():
    """Función principal"""
    print("🧪 TESTING WORKFLOW CORREGIDO")
    print("=" * 40)
    
    # 1. Verificar productos en BD
    product_ids = await test_database_products()
    
    if not product_ids:
        print("❌ No hay productos para testing")
        return False
    
    # 2. Obtener token
    token = test_auth()
    
    if not token:
        print("❌ No se pudo autenticar")
        return False
    
    # 3. Probar workflow endpoint con el primer producto
    test_product_id = product_ids[0]
    workflow_ok = test_workflow_endpoint(token, test_product_id)
    
    # Resumen
    print(f"\n📊 RESUMEN:")
    print(f"-" * 20)
    print(f"Base de datos:     {'✅ OK' if product_ids else '❌ ERROR'}")
    print(f"Autenticación:     {'✅ OK' if token else '❌ ERROR'}")
    print(f"Workflow endpoint: {'✅ OK' if workflow_ok else '❌ ERROR'}")
    
    if product_ids and token and workflow_ok:
        print(f"\n✅ TODAS LAS CORRECCIONES FUNCIONANDO")
        print(f"🎯 URL de testing: http://192.168.1.137:5173/admin-secure-portal/cola-productos-entrantes")
        print(f"📧 Usuario: admin@mestore.com")
        print(f"🔑 Password: admin123")
        print(f"🔧 Mock data está automáticamente activado")
        
        print(f"\n📋 INSTRUCCIONES:")
        print(f"1. Ir a la URL arriba")
        print(f"2. Hacer login")
        print(f"3. Hacer clic en el botón verde ✅ de cualquier producto")
        print(f"4. Debería abrir el modal de workflow SIN errores 401 o NaN")
        
        return True
    else:
        print(f"\n❌ HAY PROBLEMAS QUE NECESITAN RESOLUCIÓN")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)