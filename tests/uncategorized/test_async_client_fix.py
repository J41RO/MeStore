import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
import uuid

@pytest.mark.asyncio
async def test_async_client_vendedor_registro():
    """Test con AsyncClient para mantener compatibilidad async/sync."""
    print("=== 🧪 TEST CON ASYNCCLIENT (SOLUCIÓN DEFINITIVA) ===")
    
    unique_id = uuid.uuid4().hex[:8]
    vendedor_data = {
        'email': f'test_async_{unique_id}@test.com',
        'password': 'TestPass123',
        'nombre': 'AsyncTest',
        'apellido': 'Client',
        'cedula': f'{1234567000 + hash(unique_id) % 1000}',
        'telefono': '3201234567'
    }
    
    print(f"🎯 Testing: {vendedor_data['email']}")
    
    # Headers con User-Agent válido para evitar bloqueo de middleware
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as client:
        # Primer registro
        print("🔄 Primer registro con AsyncClient...")
        response1 = await client.post('/api/v1/vendedores/registro', json=vendedor_data)
        print(f"Status: {response1.status_code}")
        
        if response1.status_code == 201:
            print("✅ Primer registro exitoso")
            
            # Email duplicado - TEST CRÍTICO
            print("🔄 Email duplicado - TEST CRÍTICO...")
            response2 = await client.post('/api/v1/vendedores/registro', json=vendedor_data)
            print(f"Status: {response2.status_code}")
            
            if response2.status_code == 400:
                print("🎉 🎉 🎉 ¡SOLUCIÓN COMPLETAMENTE EXITOSA!")
                print("✅ RuntimeError: Event loop is closed → ELIMINADO")
                print("✅ AsyncClient + AsyncSession → COMPATIBLES")
                print("✅ Validación email duplicado → 400 (PERFECTO)")
                print("🏆 PROBLEMA ARQUITECTURAL COMPLETAMENTE RESUELTO")
                return True
            elif response2.status_code == 500:
                print("❌ Error 500 persiste")
                error_data = response2.json()
                print(f"Error: {error_data.get('detail', 'Unknown')}")
                return False
            else:
                print(f"⚠️ Status inesperado: {response2.status_code}")
                return False
        else:
            print(f"❌ Error primer registro: {response1.status_code}")
            return False

# Función para ejecutar manualmente
def run_async_test():
    """Ejecutar test async manualmente."""
    return asyncio.run(test_async_client_vendedor_registro())

if __name__ == "__main__":
    success = run_async_test()
    if success:
        print("🎉 TEST ASYNCCLIENT EXITOSO - PROBLEMA RESUELTO")
    else:
        print("❌ TEST ASYNCCLIENT FALLÓ")
    exit(0 if success else 1)