import pytest
import httpx
from app.main import app

@pytest.mark.asyncio
async def test_vendedor_async():
    """Test async correcto con httpx"""
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        # Test health check
        response = await client.get("/api/v1/vendedores/health")
        print(f"Health status: {response.status_code}")
        assert response.status_code == 200
        
        # Test registro con DB mockeada
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

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_vendedor_async())
