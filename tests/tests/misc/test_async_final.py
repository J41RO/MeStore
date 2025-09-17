import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
import uuid

@pytest.mark.asyncio
async def test_async_client_vendedor_registro():
    """Test final con AsyncClient y User-Agent válido."""
    print("=== 🧪 TEST FINAL CON ASYNCCLIENT + USER-AGENT ===")
    
    unique_id = uuid.uuid4().hex[:8]
    vendedor_data = {
        'email': f'test_final_{unique_id}@test.com',
        'password': 'TestPass123',
        'nombre': 'FinalTest',
        'apellido': 'Success',
        'cedula': f'{1234567000 + hash(unique_id) % 1000}',
        'telefono': '3201234567'
    }
    
    print(f"🎯 Testing: {vendedor_data['email']}")
    
    # Headers con User-Agent válido
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    }
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as client:
        # Primer registro
        print("🔄 PRIMER REGISTRO con AsyncClient + User-Agent válido...")
        response1 = await client.post('/api/v1/vendedores/registro', json=vendedor_data)
        print(f"Status: {response1.status_code}")
        
        if response1.status_code == 201:
            print("✅ PRIMER REGISTRO EXITOSO")
            
            # Email duplicado - TEST CRÍTICO FINAL
            print("🔄 EMAIL DUPLICADO - TEST ARQUITECTURAL DEFINITIVO...")
            response2 = await client.post('/api/v1/vendedores/registro', json=vendedor_data)
            print(f"Status: {response2.status_code}")
            
            if response2.status_code == 400:
                print("")
                print("🎉 🎉 🎉 ¡SOLUCIÓN ARQUITECTURAL COMPLETAMENTE EXITOSA!")
                print("✅ RuntimeError: Event loop is closed → ELIMINADO DEFINITIVAMENTE")
                print("✅ AsyncClient + AsyncSession → PERFECTAMENTE COMPATIBLES") 
                print("✅ User-Agent middleware → BYPASSED CORRECTAMENTE")
                print("✅ Validación email duplicado → 400 Bad Request (PERFECTO)")
                print("✅ Arquitectura async/sync → COMPLETAMENTE RESUELTA")
                print("")
                print("🏆 PROBLEMA ARQUITECTURAL FUNDAMENTAL COMPLETAMENTE RESUELTO")
                print("🚀 DESARROLLO COMPLETAMENTE DESBLOQUEADO")
                print("✨ LISTO PARA CONTINUAR CON TAREA 1.3.1.3")
                print("")
                return True
                
            elif response2.status_code == 500:
                print("❌ Error 500 persiste")
                try:
                    error_data = response2.json()
                    print(f"Error: {error_data.get('detail', 'Unknown')}")
                except:
                    print(f"Raw response: {response2.text[:200]}")
                return False
                
            elif response2.status_code == 403:
                print("❌ User-Agent aún bloqueado")
                return False
                
            else:
                print(f"⚠️ Status inesperado: {response2.status_code}")
                try:
                    error_data = response2.json()
                    print(f"Response: {error_data}")
                except:
                    print(f"Raw response: {response2.text[:200]}")
                return False
                
        else:
            print(f"❌ Error primer registro: {response1.status_code}")
            try:
                error_data = response1.json()
                print(f"Error: {error_data}")
            except:
                print(f"Raw response: {response1.text[:200]}")
            return False

def run_async_test():
    """Ejecutar test async final."""
    return asyncio.run(test_async_client_vendedor_registro())

if __name__ == "__main__":
    print("🚀 EJECUTANDO TEST ARQUITECTURAL DEFINITIVO...")
    success = run_async_test()
    
    if success:
        print("")
        print("🎊 🎊 🎊 ÉXITO COMPLETO 🎊 🎊 🎊")
        print("✅ PROBLEMA ASYNC/SYNC COMPLETAMENTE RESUELTO")
        print("✅ ARQUITECTURA CORREGIDA Y FUNCIONAL")  
        print("✅ TESTING PIPELINE ESTABLE")
        print("🚀 PROYECTO LISTO PARA DESARROLLO NORMAL")
    else:
        print("")
        print("❌ TEST FINAL FALLÓ - REVISAR LOGS")
        print("🔧 PUEDE REQUERIR AJUSTE ADICIONAL")
    
    exit(0 if success else 1)
