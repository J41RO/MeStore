import pytest
import httpx
from httpx import ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_vendedor_async_fixed():
    """Test async correcto con ASGITransport"""
    
    # Crear transport ASGI para conectar httpx con FastAPI
    transport = ASGITransport(app=app)
    
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Test health check
        response = await client.get("/api/v1/vendedores/health")
        print(f"Health status: {response.status_code}")
        assert response.status_code == 200
        
        print("✅ Health check OK")
        
        # Test registro con DB que fallará pero veremos el error específico
        vendedor_data = {
            "email": "async.test@test.com",
            "password": "Password123", 
            "nombre": "Async",
            "apellido": "Test",
            "cedula": "87654321",
            "telefono": "300 987 6543"
        }
        
        response = await client.post("/api/v1/vendedores/registro", json=vendedor_data)
        print(f"Registro status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code != 201:
            print(f"❌ Error en registro, pero endpoint SÍ responde")
        else:
            print(f"✅ ¡REGISTRO EXITOSO!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_vendedor_async_fixed())
