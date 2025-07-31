# Crear archivo: tests/test_verification_async.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
import uuid
import hashlib
import hashlib

@pytest.mark.asyncio
async def test_email_duplicado_async():
    """Test definitivo con AsyncClient para verificar corrección async/sync."""
    
    transport = ASGITransport(app=app)
    headers = {"User-Agent": "pytest-asyncclient/1.0"}
    
    async with AsyncClient(transport=transport, base_url="http://test", headers=headers) as client:
        
        # Datos únicos
        unique_id = uuid.uuid4().hex[:8]
        hash_num = int(hashlib.md5(unique_id.encode()).hexdigest()[:4], 16) % 10000
        test_email = f'async_test_{unique_id}@test.com'
        test_cedula = f'987654{hash_num:04d}'
        
        vendedor_data = {
            'email': test_email,
            'password': 'AsyncTest123!',
            'nombre': 'Async',
            'apellido': 'Test',
            'cedula': test_cedula,
            'telefono': '3201234567'
        }
        
        # PRIMER REGISTRO
        response1 = await client.post('/api/v1/vendedores/registro', json=vendedor_data)
        assert response1.status_code == 201
        
        # EMAIL DUPLICADO - DEBE SER 400, NO 500
        response2 = await client.post('/api/v1/vendedores/registro', json=vendedor_data)
        assert response2.status_code == 400  # NO 500
        
        # CÉDULA DUPLICADA
        vendedor_data['email'] = f'different_{unique_id}@test.com'
        response3 = await client.post('/api/v1/vendedores/registro', json=vendedor_data)
        assert response3.status_code == 400  # NO 500