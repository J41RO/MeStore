#!/usr/bin/env python3
"""
Test manual del endpoint de órdenes del vendedor.
"""

import asyncio
import httpx

async def test_orders_endpoint():
    """Test básico del endpoint /vendedores/dashboard/ordenes"""
    
    # Configurar cliente HTTP
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        try:
            # Intentar hacer una llamada directa al endpoint (sin autenticación por simplicidad)
            response = await client.get("/api/v1/vendedores/dashboard/ordenes")
            
            # El endpoint debería retornar 403 (forbidden) porque no hay autenticación
            # Esto confirma que el endpoint existe y la ruta está correcta
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
            # Si retorna 403, el endpoint está configurado correctamente
            if response.status_code == 403:
                print("✅ Endpoint configurado correctamente (requiere autenticación)")
                return True
            else:
                print(f"❌ Status code inesperado: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error conectando al servidor: {str(e)}")
            print("🔍 Asegúrate de que el servidor esté ejecutándose en localhost:8000")
            return False

if __name__ == "__main__":
    print("🚀 Probando endpoint de órdenes del vendedor...")
    
    # Ejecutar test
    result = asyncio.run(test_orders_endpoint())
    
    if result:
        print("\n✅ Test completado exitosamente")
        print("📝 El endpoint /api/v1/vendedores/dashboard/ordenes está disponible")
    else:
        print("\n❌ Test falló")
        print("🔧 Verifica que el servidor esté ejecutándose")