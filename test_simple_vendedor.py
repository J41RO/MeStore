from fastapi.testclient import TestClient
from app.main import app

def test_simple():
    """Test simple sin fixtures"""
    client = TestClient(app)
    
    # Test de health check primero
    response = client.get("/api/v1/vendedores/health")
    print(f"Health check status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Health check OK")
        
        # Ahora test de registro
        vendedor_data = {
            "email": "test@test.com",
            "password": "Password123",
            "nombre": "Test",
            "apellido": "User", 
            "cedula": "12345678",
            "telefono": "300 123 4567"
        }
        
        response = client.post("/api/v1/vendedores/registro", json=vendedor_data)
        print(f"Registro status: {response.status_code}")
        if response.status_code != 201:
            print(f"Error response: {response.text}")
    else:
        print(f"Health check failed: {response.text}")

if __name__ == "__main__":
    test_simple()
