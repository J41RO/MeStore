import sys
import os
sys.path.append('.')

def test_arquitectural():
    print("=== 🧪 TEST ARQUITECTURAL SIMPLE ===")
    
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        from app.core.database import get_db
        from tests.test_dependencies_simple import get_test_db, create_test_tables
        import uuid
        
        # Setup
        app.dependency_overrides[get_db] = get_test_db
        create_test_tables()
        client = TestClient(app)
        
        # Test data
        unique_id = uuid.uuid4().hex[:8]
        data = {
            'email': f'test_{unique_id}@test.com',
            'password': 'TestPass123',
            'nombre': 'Test',
            'apellido': 'Simple',
            'cedula': f'{1234567000 + hash(unique_id) % 1000}',
            'telefono': '3201234567'
        }
        
        print(f"🎯 Testing: {data['email']}")
        
        # Primer registro
        r1 = client.post('/api/v1/vendedores/registro', json=data)
        print(f"Primer registro: {r1.status_code}")
        
        if r1.status_code == 201:
            # Email duplicado
            r2 = client.post('/api/v1/vendedores/registro', json=data)
            print(f"Email duplicado: {r2.status_code}")
            
            if r2.status_code == 400:
                print("🎉 ÉXITO: RuntimeError eliminado, validación correcta!")
                return True
            elif r2.status_code == 500:
                print("❌ Error 500 persiste")
                return False
            else:
                print(f"⚠️ Status inesperado: {r2.status_code}")
                return False
        else:
            print(f"❌ Error primer registro: {r1.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        try:
            app.dependency_overrides.clear()
        except:
            pass

if __name__ == "__main__":
    success = test_arquitectural()
    exit(0 if success else 1)
