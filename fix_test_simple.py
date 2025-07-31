# Simplificar el test para usar async_session directamente
import re

with open('tests/test_vendedores_registro.py', 'r') as f:
    content = f.read()

# Reemplazar la función problemática con una versión simple que funcione
old_test = """    def test_registro_vendedor_exitoso(self, override_get_db_async):
        \"\"\"Test registro exitoso de vendedor con todos los campos\"\"\"
        
        client = TestClient(app)
        vendedor_data = {"""

new_test = """    def test_registro_vendedor_exitoso(self, async_session):
        \"\"\"Test registro exitoso de vendedor con todos los campos\"\"\"
        
        # Manual override con async_session
        def get_test_db():
            try:
                yield async_session
            finally:
                pass
        
        app.dependency_overrides[get_db] = get_test_db
        
        try:
            client = TestClient(app)
            vendedor_data = {"""

content = content.replace(old_test, new_test)

# Agregar cleanup al final del test
content = content.replace(
    "            assert data[\"vendedor\"][\"is_verified\"] is False",
    """            assert data[\"vendedor\"][\"is_verified\"] is False
        finally:
            # Cleanup override
            app.dependency_overrides.clear()"""
)

with open('tests/test_vendedores_registro.py', 'w') as f:
    f.write(content)

print("✅ Test simplificado para usar async_session directamente")
